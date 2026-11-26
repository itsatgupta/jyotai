"""NEXT-PROVISIONAL-01: the final review pack lists every provisional rule for decision."""

from datetime import date
from pathlib import Path

from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import ProvisionalCorpus
from astrologer.knowledge.provisional_pack_v2 import ACTIVE_PROVISIONAL_CORPUS, NOT_DRAFTED
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS as SIGNIFICATIONS,
)
from astrologer.knowledge.review_pack import (
    DECISION_LINE,
    build_markdown,
    find_repository_root,
    latest_record_date,
    main,
    markdown_to_html,
)

_ROOT = find_repository_root(Path(__file__).resolve())
_COMMITTED = _ROOT / "research" / "final-review" / "review-pack.md"


def _pack() -> str:
    return build_markdown(
        ACTIVE_PROVISIONAL_CORPUS,
        latest_record_date(ACTIVE_PROVISIONAL_CORPUS, SIGNIFICATIONS),
        NOT_DRAFTED,
        SIGNIFICATIONS,
    )


def test_every_provisional_rule_appears_once_with_its_justification_and_decision() -> None:
    pack = _pack()
    assert len(ACTIVE_PROVISIONAL_CORPUS.rules) == 12
    assert pack.count(DECISION_LINE) == 12 + len(SIGNIFICATIONS.terms) == 15
    assert DECISION_LINE == "☐ Approve ☐ Change ☐ Reject"
    for rule in ACTIVE_PROVISIONAL_CORPUS.rules:
        j = rule.justification
        assert pack.count(f"`{rule.rule_id}`") == 1
        for text in (j.original_text, j.draft_translation, j.interpretive_reasoning, j.locator):
            assert text in pack
        assert all(item in pack for item in j.conventions)
        assert rule.statement in pack
        if rule.wording == "held":
            assert f"- **Wording:** held in the app — {rule.held_reason}" in pack
    assert "**Author:** drafted_by: AI agent; adopted_by: project owner (pending)" in pack
    assert "**Nothing in this pack is reviewed.**" in pack


def test_rules_are_grouped_by_domain_in_domain_order() -> None:
    pack = _pack()
    headings = [line[3:] for line in pack.splitlines() if line.startswith("## ")]
    assert headings == [
        "How to decide",
        "Summary",
        "Education",
        "Wealth",
        "Spirituality",
        "Marriage",
        "Provisional significations: Marriage",
    ]
    wealth = pack.index("## Wealth")
    assert pack.index("house_lord.7.equals_5.wealth") > wealth
    assert pack.index("house_lord.5.equals_4.education") < wealth
    assert "Domains with no provisional rule yet: General, Career," in pack
    marriage = pack.index("## Marriage")
    assert pack.index("house_lord.7.equals_12.marriage") > marriage
    assert "| Marriage | 9 | 8 |" in pack
    located = pack.index("### Located, not drafted (Marriage)")
    assert located > pack.index("house_lord.7.equals_12.marriage")
    for note in NOT_DRAFTED["marriage"]:
        assert f"- {note}" in pack


def test_pack_is_deterministic_and_the_committed_pack_is_current() -> None:
    assert _pack() == _pack()
    assert _COMMITTED.read_text(encoding="utf-8") == _pack()


def test_an_empty_corpus_still_builds() -> None:
    empty = ProvisionalCorpus(corpus_id="jyotish.provisional", corpus_version="v0")
    pack = build_markdown(empty, date(2026, 11, 24))
    assert DECISION_LINE not in pack
    assert all(domain.value.title() in pack for domain in JyotishDomain if domain.value != "travel")


def test_html_for_pdf_escapes_and_keeps_the_devanagari() -> None:
    html = markdown_to_html(_pack(), "Pack <x>")
    assert "<title>Pack &lt;x&gt;</title>" in html
    assert "सुतेशे मातृभवने" in html
    assert html.count("☐ Approve ☐ Change ☐ Reject") == 15
    assert "<blockquote>" in html and "<table>" in html


def test_cli_writes_the_markdown_to_the_requested_path(tmp_path: Path) -> None:
    output = tmp_path / "pack.md"
    assert main(["--output", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == _pack()


def test_every_provisional_signification_appears_with_its_tags_and_justification() -> None:
    # NEXT-MARRIAGE-02.
    pack = _pack()
    section = pack[pack.index("## Provisional significations: Marriage") :]
    for term in SIGNIFICATIONS.terms:
        j = term.justification
        assert section.count(f"`{term.term_id}`") == 1
        assert "- **Domain tags:** Marriage (provisional)" in section
        for text in (j.original_text, j.draft_translation, j.interpretive_reasoning, j.locator):
            assert text in section
        assert term.statement in section
        if term.translation_held_reason:
            assert f"not shown in the app — {term.translation_held_reason}" in section
    assert "tagged Career (reviewed) only" in pack
