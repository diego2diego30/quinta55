"""Environment-driven configuration. No secrets or real values hard-coded
here — everything comes from the environment (see `deploy/.env.example`).
Deliberately structured in parallel with the trading instance's
hermes/config.py, but this is a separate package in a separate repo with
its own credential set — nothing here imports from or references the
trading instance.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


class MissingConfigError(RuntimeError):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise MissingConfigError(
            f"{name} is not set. See deploy/.env.example — copy it to "
            f"deploy/.env on the VPS and fill in real values. Refusing to "
            f"start with a fabricated placeholder."
        )
    return value


@dataclass(frozen=True)
class Paths:
    repo_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def quinta_root(self) -> Path:
        return self.repo_root / "quinta55"

    @property
    def roles_dir(self) -> Path:
        return self.quinta_root / "roles"

    @property
    def logs_dir(self) -> Path:
        return self.quinta_root / "logs"

    @property
    def memory_dir(self) -> Path:
        return self.quinta_root / "memory"

    @property
    def claude_md(self) -> Path:
        return self.quinta_root / "CLAUDE.md"

    @property
    def data_dir(self) -> Path:
        # Own data volume, separate from quinta55/ (context files) and
        # entirely separate from the trading instance's data volume in
        # the other repo/container.
        d = Path(os.environ.get("HERMES_DATA_DIR", self.repo_root / "data"))
        d.mkdir(parents=True, exist_ok=True)
        return d


@dataclass(frozen=True)
class TelegramConfig:
    # Distinct env var names from the trading instance (which uses
    # TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID) so the two can run side by
    # side on the same VPS without collision, and so Diego gets separate
    # bots/threads per execution-plan.md Section 6.
    bot_token: str = field(default_factory=lambda: _require("QUINTA55_TELEGRAM_BOT_TOKEN"))
    chat_id: str = field(default_factory=lambda: _require("QUINTA55_TELEGRAM_CHAT_ID"))


DEFAULT_MODEL_BY_ROLE = {
    "research": os.environ.get("MODEL_RESEARCH", "claude-haiku-4-5-20251001"),
    "build": os.environ.get("MODEL_BUILD", "claude-sonnet-5"),
    "review": os.environ.get("MODEL_REVIEW", "claude-sonnet-5"),
    "chat": os.environ.get("MODEL_CHAT", "claude-haiku-4-5-20251001"),
}

ROLE_CHAIN = ["research", "build", "review"]
