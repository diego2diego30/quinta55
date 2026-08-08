"""Runs the Research -> Build -> Review chain via headless `claude -p`
subprocess calls, one process per role, each scoped to its own CLAUDE.md
and --allowedTools -- same separation principle as the trading instance's
six-role chain, generalized to three roles per execution-plan.md Section
7 ("apply the same role-separation pattern... to business workflows").

Real cadence/trigger (cron schedule, event-driven, etc.) is undefined
until Diego specifies actual Quinta55 workflows -- see the TODO in
quinta55/CLAUDE.md. `run_chain` here is a general-purpose entrypoint any
future trigger can call with a specific task description.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Optional

from hermes.business_action_guard import BusinessWriteNotAuthorized, assert_write_authorized
from hermes.config import DEFAULT_MODEL_BY_ROLE, Paths
from hermes.logging_utils import RoleLogEntry, RunLogger
from hermes.state import AuthorizationState

ROLE_ALLOWED_TOOLS = {
    "research": ["Read", "Grep", "Glob"],
    "build": ["Read"],
    "review": ["Read"],
}


class ChainError(RuntimeError):
    pass


@dataclass
class RoleResult:
    role: str
    text: str
    raw: dict


def _run_role(role: str, prompt: str, paths: Paths) -> RoleResult:
    role_dir = paths.roles_dir / role
    if not role_dir.exists():
        raise ChainError(f"No role directory for {role!r} at {role_dir}")

    model = DEFAULT_MODEL_BY_ROLE[role]
    allowed = ",".join(ROLE_ALLOWED_TOOLS[role])

    cmd = [
        "claude", "-p", prompt,
        "--model", model,
        "--allowedTools", allowed,
        "--output-format", "json",
    ]
    proc = subprocess.run(cmd, cwd=str(role_dir), capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise ChainError(f"Role {role!r} failed (exit {proc.returncode}): {proc.stderr[:2000]}")

    try:
        raw = json.loads(proc.stdout)
        text = raw.get("result", proc.stdout)
    except json.JSONDecodeError:
        raw = {"raw_stdout": proc.stdout}
        text = proc.stdout

    return RoleResult(role=role, text=text, raw=raw)


def run_chain(
    task_description: str,
    target_integration: Optional[str] = None,
    paths: Optional[Paths] = None,
) -> dict:
    """One Research -> Build -> Review cycle for a given task. If the
    resulting draft would need to write to a live system, pass its
    integration name in `target_integration` -- the guard check result is
    logged and returned, but nothing in this function actually performs
    that write (see hermes/business_action_guard.py).
    """
    paths = paths or Paths()
    logger = RunLogger(paths=paths)
    auth_state = AuthorizationState.load()

    logger.log_event("chain_start", f"task={task_description!r} target_integration={target_integration}")

    try:
        research = _run_role("research", f"Research task: {task_description}", paths)
        logger.log_role(RoleLogEntry(role="research", model=DEFAULT_MODEL_BY_ROLE["research"],
                                      reasoning=research.text, output=research.raw))

        build = _run_role(
            "build",
            f"Research output:\n{research.text}\n\nProduce a concrete draft for: {task_description}",
            paths,
        )
        logger.log_role(RoleLogEntry(role="build", model=DEFAULT_MODEL_BY_ROLE["build"],
                                      reasoning=build.text, output=build.raw))

        review = _run_role(
            "review",
            f"Research:\n{research.text}\n\nDraft:\n{build.text}\n\nApprove, reject, or escalate.",
            paths,
        )
        logger.log_role(RoleLogEntry(role="review", model=DEFAULT_MODEL_BY_ROLE["review"],
                                      reasoning=review.text, output=review.raw))

        write_authorized = False
        if target_integration:
            try:
                assert_write_authorized(target_integration, auth_state)
                write_authorized = True
            except BusinessWriteNotAuthorized as exc:
                logger.log_event("business_write_blocked", str(exc))

        logger.log_event("chain_end", f"write_authorized={write_authorized}")

        return {
            "target_integration": target_integration,
            "write_authorized": write_authorized,
            "review_summary": review.text,
            "log_path": str(logger.log_path),
        }
    except Exception as exc:  # noqa: BLE001
        logger.log_event("chain_error", str(exc))
        raise
