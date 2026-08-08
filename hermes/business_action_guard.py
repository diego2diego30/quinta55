"""Business-action guard — the chokepoint between a Review-role
"approved" decision and anything touching a real, live business system
(email send, accounting write, e-commerce/POS write, etc.).

Mirrors the trading instance's hermes/execution_guard.py: no publish/send
function exists yet, not stubbed behind a flag. `publish_or_send` always
raises. When Diego defines a real workflow and integration for a specific
system, that integration should call through this guard, and
`AuthorizationState` should be extended per-integration rather than
loosened globally.
"""
from __future__ import annotations

from hermes.state import AuthorizationState


class BusinessWriteNotAuthorized(RuntimeError):
    pass


def assert_write_authorized(integration: str, auth_state: AuthorizationState) -> None:
    if not auth_state.is_authorized(integration):
        raise BusinessWriteNotAuthorized(
            f"Integration {integration!r} is not authorized for live writes. "
            f"Requires Diego to run hermes/cli.py authorize-integration "
            f"--integration {integration} --confirmed-by diego. "
            f"Draft/propose-only until then."
        )


def publish_or_send(*_args, **_kwargs):
    """Not implemented. No live business-system write exists in this
    codebase yet — see docs/execution-plan.md Section B instruction 2
    (the "real business-system writes" clause applies here, not just to
    trading) and the TODO in quinta55/CLAUDE.md for why the underlying
    workflows aren't defined yet either.
    """
    raise NotImplementedError(
        "No live business-system write path exists in this codebase. "
        "This is intentional, not a bug -- see docs/execution-plan.md "
        "Section B instruction 2."
    )
