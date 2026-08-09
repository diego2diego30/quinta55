"""Cost reporting and hard spend safeguards for the Quinta55 instance --
mirrors diego-inc/tests/test_cost.py since hermes/cost.py is duplicated
(not shared) between the two repos per the isolation requirement.
"""
from __future__ import annotations

import time

import pytest

from hermes.cost import (
    BudgetConfig,
    BudgetExceeded,
    CostLedger,
    RunLock,
    UsageRecord,
    cost_from_claude_response,
)


class TestCostFromClaudeResponse:
    def test_uses_the_clis_own_reported_cost(self):
        raw = {
            "total_cost_usd": 0.0123,
            "usage": {"input_tokens": 100, "output_tokens": 50},
        }
        record = cost_from_claude_response("research", "claude-haiku-4-5-20251001", raw, run_id="r1")
        assert record.cost_usd == 0.0123
        assert record.role == "research"
        assert record.run_id == "r1"

    def test_falls_back_to_price_table_when_cli_reports_no_cost(self):
        raw = {"usage": {"input_tokens": 1_000_000, "output_tokens": 1_000_000}}
        record = cost_from_claude_response("build", "claude-sonnet-5", raw)
        assert record.cost_usd == pytest.approx(18.0)

    def test_unknown_model_reports_zero_not_a_guess(self):
        raw = {"usage": {"input_tokens": 1_000_000, "output_tokens": 1_000_000}}
        record = cost_from_claude_response("research", "some-future-model", raw)
        assert record.cost_usd == 0.0


class TestCostLedger:
    def test_records_and_sums_month_to_date(self):
        ledger = CostLedger()
        ledger.record(UsageRecord(role="research", model="claude-haiku-4-5-20251001", cost_usd=0.10, run_id="r1"))
        ledger.record(UsageRecord(role="review", model="claude-sonnet-5", cost_usd=0.25, run_id="r1"))
        assert ledger.month_to_date_usd() == pytest.approx(0.35)

    def test_empty_ledger_reports_zero_not_an_error(self):
        report = CostLedger().report()
        assert report.month_to_date_usd == 0.0
        assert report.runs_this_month == 0
        assert report.by_role == {}

    def test_as_text_is_labeled_for_quinta55(self):
        ledger = CostLedger()
        text = ledger.report().as_text()
        assert "Quinta55" in text


class TestBudgetCaps:
    def test_assert_within_budget_raises_when_monthly_cap_hit(self):
        config = BudgetConfig(monthly_usd_cap=10.0, max_runs_per_day=10)
        ledger = CostLedger(config=config)
        ledger.record(UsageRecord(role="research", model="claude-haiku-4-5-20251001", cost_usd=10.0, run_id="r1"))
        with pytest.raises(BudgetExceeded):
            ledger.assert_within_budget()

    def test_assert_within_budget_raises_when_daily_run_limit_hit(self):
        config = BudgetConfig(monthly_usd_cap=1000.0, max_runs_per_day=1)
        ledger = CostLedger(config=config)
        ledger.record(UsageRecord(role="research", model="claude-haiku-4-5-20251001", cost_usd=0.01, run_id="run-a"))
        with pytest.raises(BudgetExceeded):
            ledger.assert_within_budget()

    def test_assert_run_within_cap_raises_when_single_run_too_expensive(self):
        config = BudgetConfig(per_run_usd_cap=1.0)
        ledger = CostLedger(config=config)
        with pytest.raises(BudgetExceeded):
            ledger.assert_run_within_cap(1.5)


class TestRunLock:
    def test_overlapping_acquire_raises(self):
        lock = RunLock()
        lock.acquire()
        try:
            with pytest.raises(BudgetExceeded):
                RunLock().acquire()
        finally:
            lock.release()

    def test_context_manager_releases_even_on_exception(self):
        with pytest.raises(ValueError):
            with RunLock():
                raise ValueError("boom")
        RunLock().acquire()
        RunLock().release()

    def test_stale_lock_is_reclaimed(self):
        lock = RunLock(stale_after_seconds=0)
        lock.acquire()
        time.sleep(0.01)
        RunLock(stale_after_seconds=0).acquire()
