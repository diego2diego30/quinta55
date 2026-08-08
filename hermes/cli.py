"""Command-line entrypoints.

    python -m hermes.cli run-chain --task "..." [--target-integration email]
    python -m hermes.cli authorize-integration --integration email --confirmed-by diego
    python -m hermes.cli telegram-daemon
"""
from __future__ import annotations

import argparse
import sys

from hermes.orchestrator import run_chain
from hermes.state import AuthorizationState
from hermes.telegram_bridge import TelegramBridge, TelegramConfig


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


def cmd_telegram_daemon(args: argparse.Namespace) -> int:
    bridge = TelegramBridge(config=TelegramConfig())

    def handle(text: str) -> None:
        print(f"received from Diego: {text}")

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

    p_tg = sub.add_parser("telegram-daemon", help="Long-running process that listens for Diego's replies")
    p_tg.set_defaults(func=cmd_telegram_daemon)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
