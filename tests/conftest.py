from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolated_hermes_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_DATA_DIR", str(tmp_path / "data"))
