"""Coverage for the one piece of enforcement logic this scaffold does
define: no live business-system write without an explicit, human-attributed
authorization (execution-plan.md Section B instruction 2).
"""
from __future__ import annotations

import pytest

from hermes.business_action_guard import BusinessWriteNotAuthorized, assert_write_authorized, publish_or_send
from hermes.state import AuthorizationState, InvalidAuthorization


class TestAuthorizationState:
    def test_nothing_authorized_by_default(self):
        state = AuthorizationState()
        assert not state.is_authorized("email")

    def test_authorize_requires_diego_confirmation(self):
        state = AuthorizationState()
        with pytest.raises(InvalidAuthorization):
            state.authorize("email", confirmed_by="hermes")
        assert not state.is_authorized("email")

    def test_authorize_succeeds_with_diego_confirmation(self):
        state = AuthorizationState()
        state.authorize("email", confirmed_by="diego")
        assert state.is_authorized("email")

    def test_authorizing_one_integration_does_not_authorize_another(self):
        state = AuthorizationState()
        state.authorize("email", confirmed_by="diego")
        assert not state.is_authorized("accounting")

    def test_revoke_clears_authorization(self):
        state = AuthorizationState()
        state.authorize("email", confirmed_by="diego")
        state.revoke("email")
        assert not state.is_authorized("email")


class TestBusinessActionGuard:
    def test_blocks_unauthorized_integration(self):
        state = AuthorizationState()
        with pytest.raises(BusinessWriteNotAuthorized):
            assert_write_authorized("email", state)

    def test_allows_authorized_integration(self):
        state = AuthorizationState()
        state.authorize("email", confirmed_by="diego")
        assert_write_authorized("email", state)  # does not raise

    def test_publish_or_send_always_raises(self):
        """No live-write code path exists yet, full stop -- fails loudly
        if anyone "fills this in" without updating this test.
        """
        with pytest.raises(NotImplementedError):
            publish_or_send()
