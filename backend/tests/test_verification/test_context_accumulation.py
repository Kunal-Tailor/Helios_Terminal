"""
Unit tests for app.verification.recalibration — accumulate_ingestion_context (Phase 7.5.4).

Covers:
  - Prior context survives a re-ingestion pass:
      * Initial context summary preserved and appended with recalibration update
      * Initial key facts remain present and in order
      * Initial sources remain present and in order
      * Initial raw_retrieved_content remains present
      * entity and capability are preserved
  - New targeted data correctly appended:
      * New facts appended after existing facts
      * Duplicate facts from new pass are deduplicated
      * New sources appended after existing sources
      * Duplicate sources are deduplicated
      * New raw content concatenated
  - Edge cases:
      * Empty new_partial: leaves existing context intact
      * Empty existing: absorbs new_partial cleanly
      * Repeated accumulation passes: multi-turn recalibration survival
"""

import pytest

from app.agents.ingestion.sub_agents.context_synthesis_sub_agent import IngestionContext
from app.verification.recalibration import accumulate_ingestion_context


class TestAccumulateIngestionContext:
    def test_prior_context_survives_reingestion_pass(self):
        """Original context (summary, facts, sources, raw content) survives completely."""
        existing = IngestionContext(
            entity="Defense Corp",
            capability="Target Recognition",
            options=["Build", "Buy"],
            context_summary="Initial summary of Defense Corp capabilities.",
            key_facts=["Fact 1: Defense Corp has legacy radar.", "Fact 2: GPU cluster available."],
            sources=["https://example.com/source1", "https://example.com/source2"],
            raw_retrieved_content="Raw snippet 1 about Defense Corp.",
        )

        new_partial = IngestionContext(
            entity="Defense Corp",
            capability="Target Recognition",
            options=["Partner"],
            context_summary="Scoped gap findings regarding edge inference hardware.",
            key_facts=["Fact 3: Edge TPU inference tested."],
            sources=["https://example.com/source3"],
            raw_retrieved_content="Raw snippet 2 about edge hardware.",
        )

        accumulated = accumulate_ingestion_context(existing, new_partial)

        # Entity and capability preserved
        assert accumulated.entity == "Defense Corp"
        assert accumulated.capability == "Target Recognition"

        # Prior context summary is intact, with new update appended
        assert "Initial summary of Defense Corp capabilities." in accumulated.context_summary
        assert "[Recalibration Update]" in accumulated.context_summary
        assert "Scoped gap findings regarding edge inference hardware." in accumulated.context_summary

        # Prior facts survive and new fact is appended
        assert accumulated.key_facts[0] == "Fact 1: Defense Corp has legacy radar."
        assert accumulated.key_facts[1] == "Fact 2: GPU cluster available."
        assert accumulated.key_facts[2] == "Fact 3: Edge TPU inference tested."
        assert len(accumulated.key_facts) == 3

        # Prior sources survive and new source is appended
        assert accumulated.sources[0] == "https://example.com/source1"
        assert accumulated.sources[1] == "https://example.com/source2"
        assert accumulated.sources[2] == "https://example.com/source3"
        assert len(accumulated.sources) == 3

        # Prior raw content survives
        assert "Raw snippet 1 about Defense Corp." in accumulated.raw_retrieved_content
        assert "Raw snippet 2 about edge hardware." in accumulated.raw_retrieved_content

        # Options accumulated preserving order
        assert accumulated.options == ["Build", "Buy", "Partner"]

    def test_deduplication_of_facts_and_sources(self):
        """Duplicate facts and sources in the new partial pass are deduplicated."""
        existing = IngestionContext(
            entity="Org",
            capability="NLP",
            key_facts=["Fact A", "Fact B"],
            sources=["http://src1.org", "http://src2.org"],
            options=["Opt1"],
        )

        new_partial = IngestionContext(
            entity="Org",
            capability="NLP",
            key_facts=["Fact B", "Fact C"],  # Fact B is duplicate
            sources=["http://src2.org", "http://src3.org"],  # src2 is duplicate
            options=["Opt1", "Opt2"],
        )

        accumulated = accumulate_ingestion_context(existing, new_partial)

        assert accumulated.key_facts == ["Fact A", "Fact B", "Fact C"]
        assert accumulated.sources == ["http://src1.org", "http://src2.org", "http://src3.org"]
        assert accumulated.options == ["Opt1", "Opt2"]

    def test_empty_new_partial(self):
        """Empty new partial does not wipe out or corrupt existing context."""
        existing = IngestionContext(
            entity="Org",
            capability="CV",
            context_summary="Summary text.",
            key_facts=["Fact 1"],
            sources=["http://example.com"],
            raw_retrieved_content="Content text.",
        )

        new_partial = IngestionContext(
            entity="Org",
            capability="CV",
            context_summary="",
            key_facts=[],
            sources=[],
            raw_retrieved_content="",
        )

        accumulated = accumulate_ingestion_context(existing, new_partial)

        assert accumulated.context_summary == "Summary text."
        assert accumulated.key_facts == ["Fact 1"]
        assert accumulated.sources == ["http://example.com"]
        assert accumulated.raw_retrieved_content == "Content text."

    def test_empty_existing(self):
        """Empty existing context safely takes on new_partial values."""
        existing = IngestionContext(
            entity="Org",
            capability="Audio",
            context_summary="",
            key_facts=[],
            sources=[],
            raw_retrieved_content="",
        )

        new_partial = IngestionContext(
            entity="Org",
            capability="Audio",
            context_summary="New summary.",
            key_facts=["New fact."],
            sources=["http://new.org"],
            raw_retrieved_content="New raw text.",
        )

        accumulated = accumulate_ingestion_context(existing, new_partial)

        assert accumulated.context_summary == "New summary."
        assert accumulated.key_facts == ["New fact."]
        assert accumulated.sources == ["http://new.org"]
        assert accumulated.raw_retrieved_content == "New raw text."

    def test_multi_pass_accumulation(self):
        """Multiple consecutive recalibration passes accumulate cumulatively."""
        base = IngestionContext(
            entity="Org",
            capability="Robotics",
            context_summary="Pass 0.",
            key_facts=["F0"],
            sources=["S0"],
            raw_retrieved_content="R0",
        )

        pass1 = IngestionContext(
            entity="Org",
            capability="Robotics",
            context_summary="Pass 1.",
            key_facts=["F1"],
            sources=["S1"],
            raw_retrieved_content="R1",
        )

        pass2 = IngestionContext(
            entity="Org",
            capability="Robotics",
            context_summary="Pass 2.",
            key_facts=["F2"],
            sources=["S2"],
            raw_retrieved_content="R2",
        )

        step1 = accumulate_ingestion_context(base, pass1)
        step2 = accumulate_ingestion_context(step1, pass2)

        assert "Pass 0." in step2.context_summary
        assert "Pass 1." in step2.context_summary
        assert "Pass 2." in step2.context_summary
        assert step2.key_facts == ["F0", "F1", "F2"]
        assert step2.sources == ["S0", "S1", "S2"]
        assert "R0" in step2.raw_retrieved_content
        assert "R1" in step2.raw_retrieved_content
        assert "R2" in step2.raw_retrieved_content
