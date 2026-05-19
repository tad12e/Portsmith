"""Tests for the Portsmith service registry."""

from pathlib import Path

import pytest

from core.registry import ServiceRegistry


def test_loads_services_from_yaml() -> None:
    registry = ServiceRegistry.load(Path("configs") / "services.yaml")

    assert registry.names() == ["auth", "api"]
    assert registry.as_dict() == {
        "auth": {"port": 5001, "domain": "auth.local"},
        "api": {"port": 8000, "domain": "api.local"},
    }
    assert registry.get("auth").command == "python auth.py"


def test_rejects_missing_services_block(tmp_path: Path) -> None:
    config_path = tmp_path / "services.yaml"
    config_path.write_text("name: demo\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non-empty 'services' mapping"):
        ServiceRegistry.load(config_path)
