"""Helpers for matching LLM-emitted scenario names to canonical scenario names."""

from __future__ import annotations

import re


def resolve_scenario_name(raw: str, known_names: list[str]) -> str | None:
    """Map a free-form LLM scenario label onto one of *known_names*.

    Handles exact matches, substring matches, and ``Path N`` / leading-number
    variants so risk factors and lock-ins still attach when the model shortens
    names like ``PATH 3: Fleet-Driven Data-First Training Strategy`` to
    ``Path 3``.
    """
    if not raw or not known_names:
        return None

    raw_l = raw.strip().lower()
    if not raw_l:
        return None

    for name in known_names:
        if name.lower() == raw_l:
            return name

    for name in known_names:
        name_l = name.lower()
        if raw_l in name_l or name_l in raw_l:
            return name

    path_match = re.search(r"\bpath\s*(\d+)\b", raw_l)
    if path_match:
        num = path_match.group(1)
        for name in known_names:
            name_l = name.lower()
            if re.search(rf"\bpath\s*{num}\b", name_l):
                return name
            if re.match(rf"{num}[\.:\s\-]", name_l):
                return name

    return None
