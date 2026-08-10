"""Command-line entrypoints.

    python -m hermes.cli run-chain --task "..." [--target-integration email]
    python -m hermes.cli authorize-integration --integration email --confirmed-by diego
    python -m hermes.cli cost-report
    python -m hermes.cli telegram-daemon
"""
from __future__ import annotations

import argparse
import sys

from hermes import chat
from hermes.config import Paths
from hermes.cost import CostLedger
from hermes.orchestrator import run_chain
from hermes.state import AuthorizationState
from hermes.telegram_bridge import TelegramBridge, TelegramConfig

# Same on-demand cost-report trigger words as diego-inc -- kept identical
# so the behavior is predictable across both bots, even though the two
# CostLedger instances are fully separate (different repo/container/data
# volume, per execution-plan.md Section A/6 isolation).
COST_REPORT_TRIGGERS = {"cost", "/cost", "cost report", "costs", "usage", "spend"}

# On-demand check that HTML parse_mode is rendering as expected -- see the
# same trigger/message in diego-inc's hermes/cli.py.
HTML_TEST_TRIGGERS = {"html test", "/htmltest", "htmltest"}

# Deliberately exercises every HTML tag Telegram's Bot API supports except
# <tg-emoji> and tg://user inline mentions -- both need a live custom-emoji
# id / real user id this hard-coded test can't safely fabricate, and a bad
# one would 400 the whole message instead of just degrading gracefully.
HTML_DEMO_MESSAGE = (
    "<b>HTML formatting test</b> ([quinta55] bot)\n\n"
    "<b>Basic styles</b>\n"
    "<b>Bold</b> / <strong>Bold</strong>\n"
    "<i>Italic</i> / <em>Italic</em>\n"
    "<u>Underline</u> / <ins>Underline</ins>\n"
    "<s>Strikethrough</s> / <strike>Strikethrough</strike> / <del>Strikethrough</del>\n"
    "<span class=\"tg-spoiler\">Spoiler (tap to reveal)</span> / <tg-spoiler>Spoiler</tg-spoiler>\n\n"
    "<b>Nested combination</b>\n"
    "<b>bold, <i>italic bold, <s>italic bold strikethrough, "
    "<span class=\"tg-spoiler\">italic bold strikethrough spoiler</span></s>, "
    "<u>underline italic bold</u></i>, bold</b>\n\n"
    "<b>Links</b>\n"
    "<a href=\"https://telegram.org\">Inline link</a>\n"
    "<b><a href=\"https://core.telegram.org/bots/api#html-style\">Bold inline link</a></b>\n\n"
    "<b>Code</b>\n"
    "<code>inline fixed-width code</code>\n\n"
    "<pre>Pre-formatted block\nno syntax highlighting</pre>\n\n"
    "<pre><code class=\"language-python\">def hello(name: str) -&gt; str:\n"
    "    return f\"Hello, {name}!\"</code></pre>\n\n"
    "<pre><code class=\"language-bash\">echo \"bot online\" &amp;&amp; exit 0</code></pre>\n\n"
    "<b>Quotes</b>\n"
    "<blockquote>Regular blockquote -- always visible, no interaction.</blockquote>\n\n"
    "<blockquote expandable>Expandable blockquote first line\n"
    "Second line, still visible\n"
    "Third line -- tap to expand and see the rest\n"
    "Fourth line, only visible when expanded\n"
    "Fifth and last line of the quote.</blockquote>\n\n"
    "<b>Escaped literal characters</b>\n"
    "5 &lt; 10, 10 &gt; 5, cats &amp; dogs."
)


def cmd_run_chain(args: argparse.Namespace) -> int:
    result = run_chain(task_description=args.task, target_integration=args.target_integration)
    try:
        bridge = TelegramBridge(config=TelegramConfig())
        bridge.send_chain_summary(result)
    except Exception as exc:  # noqa: BLE001
        print(f"warning: chain completed but Telegram notify failed: {exc}", file=sys.stderr)
    print(result)
    return 0


def cmd_authorize_integration(args: argparse.Namespace) -> int:
    state = AuthorizationState.load()
    state.authorize(args.integration, confirmed_by=args.confirmed_by)
    state.save()
    print(f"Integration {args.integration!r} authorized (confirmed by {args.confirmed_by})")
    return 0


def cmd_cost_report(args: argparse.Namespace) -> int:
    report = CostLedger().report()
    print(report.as_text())
    return 0


BOT_COMMANDS = [
    ("cost", "Show this month's spend report"),
    ("htmltest", "Send an HTML formatting demo"),
]


def cmd_telegram_daemon(args: argparse.Namespace) -> int:
    bridge = TelegramBridge(config=TelegramConfig())
    try:
        bridge.set_commands(BOT_COMMANDS)
    except Exception as exc:  # noqa: BLE001 - cosmetic; must not block the daemon starting
        print(f"warning: setting bot command menu failed: {exc}", file=sys.stderr)

    def handle(text: str) -> None:
        print(f"received from Diego: {text}")

        if text.strip().lower() in COST_REPORT_TRIGGERS:
            report = CostLedger().report()
            try:
                bridge.send_status(report.as_text())
            except Exception as exc:  # noqa: BLE001 - a failed reply must not crash the daemon
                print(f"warning: cost report reply failed: {exc}", file=sys.stderr)
            return

        if text.strip().lower() in HTML_TEST_TRIGGERS:
            try:
                bridge.send_status(HTML_DEMO_MESSAGE, escape=False)
            except Exception as exc:  # noqa: BLE001 - a failed reply must not crash the daemon
                print(f"warning: html test reply failed: {exc}", file=sys.stderr)
            return

        # Anything else: conversational fallback (hermes/chat.py). No tools,
        # billed through the same CostLedger as the chain roles -- see that
        # module's docstring. A failed reply must not crash the daemon, same
        # as the cost-report path above.
        try:
            reply = chat.reply_to_message(text, paths=Paths())
            bridge.send_status(reply)
        except Exception as exc:  # noqa: BLE001 - a failed reply must not crash the daemon
            print(f"warning: chat reply failed: {exc}", file=sys.stderr)

    bridge.poll_for_replies(handle)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="hermes")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run-chain", help="Run one Research->Build->Review cycle")
    p_run.add_argument("--task", required=True)
    p_run.add_argument("--target-integration", default=None)
    p_run.set_defaults(func=cmd_run_chain)

    p_auth = sub.add_parser("authorize-integration", help="Authorize a live business-system write -- human-only")
    p_auth.add_argument("--integration", required=True)
    p_auth.add_argument("--confirmed-by", required=True, help="Must be 'diego'")
    p_auth.set_defaults(func=cmd_authorize_integration)

    p_cost = sub.add_parser("cost-report", help="Print month-to-date spend, projection, and cap status")
    p_cost.set_defaults(func=cmd_cost_report)

    p_tg = sub.add_parser("telegram-daemon", help="Long-running process that listens for Diego's replies")
    p_tg.set_defaults(func=cmd_telegram_daemon)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
