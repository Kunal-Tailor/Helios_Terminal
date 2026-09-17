"""Tests for app.agents.scenario_match."""

from app.agents.scenario_match import resolve_scenario_name

_KNOWN = [
    "PATH 1: Pure Proprietary In-House Foundation Model Scaling",
    "PATH 2: Hardware-Constrained Model Architecture Co-Design",
    "PATH 3: Fleet-Driven Data-First Training Strategy",
    "PATH 4: Custom Training Cluster Infrastructure Provisioning",
]


def test_exact_match():
    assert resolve_scenario_name(_KNOWN[2], _KNOWN) == _KNOWN[2]


def test_path_number_short_form():
    assert resolve_scenario_name("Path 3", _KNOWN) == _KNOWN[2]
    assert resolve_scenario_name("PATH 1", _KNOWN) == _KNOWN[0]


def test_substring_match():
    assert (
        resolve_scenario_name("Fleet-Driven Data-First Training Strategy", _KNOWN)
        == _KNOWN[2]
    )


def test_unresolved_returns_none():
    assert resolve_scenario_name("Completely Unknown Path", _KNOWN) is None
    assert resolve_scenario_name("", _KNOWN) is None
