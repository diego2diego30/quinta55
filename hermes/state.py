"""Persisted state: which live-business-system integrations Diego has
explicitly authorized. No trading-style gate ladder here — Section 6/7
don't define one for Quinta55, and inventing one would be fabricating
scope (see TODO in quinta55/CLAUDE.md). What *is* specified (Section B
instruction 2's "real business-system writes" clause) is that nothing
writes to a live system without explicit confirmation, so that part is
implemented now, in parallel with the trading instance's gate mechanism.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from hermes.config import Paths


class InvalidAuthorization(RuntimeError):
    pass


@dataclass
class AuthorizationState:
    """Maps an integration name (e.g. "email", "accounting", "pos") to
    whether Diego has explicitly authorized this instance to write to it.
    Empty by default -- nothing is authorized until Diego says so.
    """

    authorized_integrations: Dict[str, str] = field(default_factory=dict)  # name -> ISO timestamp authorized

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "AuthorizationState":
        path = path or (Paths().data_dir / "authorization_state.json")
        if not path.exists():
            return cls()
        return cls(**json.loads(path.read_text()))

    def save(self, path: Optional[Path] = None) -> None:
        path = path or (Paths().data_dir / "authorization_state.json")
        path.write_text(json.dumps(asdict(self), indent=2))

    def is_authorized(self, integration: str) -> bool:
        return integration in self.authorized_integrations

    def authorize(self, integration: str, confirmed_by: str) -> "AuthorizationState":
        """The only way this codebase marks an integration writable.
        Called exclusively from a human-invoked CLI
        (`hermes/cli.py authorize-integration`), never from the
        orchestrator or any role's output.
        """
        if confirmed_by != "diego":
            raise InvalidAuthorization(
                "Integration authorization requires explicit confirmation "
                "attributed to diego. Refusing an anonymous/automated authorization."
            )
        self.authorized_integrations[integration] = datetime.now(timezone.utc).isoformat()
        return self

    def revoke(self, integration: str) -> "AuthorizationState":
        self.authorized_integrations.pop(integration, None)
        return self
