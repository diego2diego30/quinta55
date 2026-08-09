"""Telegram bridge for the Quinta55 instance. Deliberately a distinct bot
from the trading instance's (separate token/chat id, see hermes/config.py)
per execution-plan.md Section 6: "keep them as separate bots/threads if
possible so a glance at your phone tells you which domain a message is
about."
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Callable, Optional

import requests

from hermes.config import TelegramConfig

API_BASE = "https://api.telegram.org/bot{token}"


@dataclass
class TelegramBridge:
    config: TelegramConfig

    def _url(self, method: str) -> str:
        return f"{API_BASE.format(token=self.config.bot_token)}/{method}"

    def send_status(self, text: str) -> None:
        resp = requests.post(
            self._url("sendMessage"),
            json={"chat_id": self.config.chat_id, "text": text},
            timeout=15,
        )
        resp.raise_for_status()

    def set_commands(self, commands: list[tuple[str, str]]) -> None:
        """Registers Telegram's native "/" autocomplete menu. Only ever
        list commands `handle()` actually acts on (see cli.py) -- a menu
        entry for something that doesn't do anything from Telegram would
        be a UI lie, not a convenience.
        """
        resp = requests.post(
            self._url("setMyCommands"),
            json={"commands": [{"command": c, "description": d} for c, d in commands]},
            timeout=15,
        )
        resp.raise_for_status()

    def send_chain_summary(self, chain_result: dict) -> None:
        lines = [
            "[quinta55] cycle complete",
            f"Target integration: {chain_result.get('target_integration')}",
            f"Write authorized: {chain_result.get('write_authorized')}",
            "",
            chain_result.get("review_summary", "")[:1500],
        ]
        self.send_status("\n".join(lines))

    def poll_for_replies(
        self,
        on_message: Callable[[str], None],
        stop_after_seconds: Optional[int] = None,
    ) -> None:
        offset = None
        start = time.monotonic()
        while stop_after_seconds is None or (time.monotonic() - start) < stop_after_seconds:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset
            resp = requests.get(self._url("getUpdates"), params=params, timeout=40)
            resp.raise_for_status()
            for update in resp.json().get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                if str(message.get("chat", {}).get("id")) != str(self.config.chat_id):
                    continue
                text = message.get("text")
                if text:
                    # The handler (hermes/cli.py) already guards its own
                    # risky calls, but this is the backstop: an uncaught
                    # exception here must not kill the long-poll loop --
                    # that would silence the bot until systemd notices and
                    # restarts it, losing every message in between.
                    try:
                        on_message(text)
                    except Exception as exc:  # noqa: BLE001
                        print(f"warning: on_message handler raised: {exc}", file=sys.stderr)
