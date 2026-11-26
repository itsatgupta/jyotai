"""NEXT-PROVISIONAL-01: build the final expert review pack of every provisional rule.

Usage (from ``apps/api``)::

    uv run python -m astrologer.knowledge.review_pack            # Markdown only
    uv run python -m astrologer.knowledge.review_pack --pdf      # + PDF export

Writes ``research/final-review/review-pack.md`` (repository root) and, with ``--pdf``,
``~/Desktop/jyotai-review/review-pack.pdf`` (plus the HTML it was printed from), using a
local headless Chrome.  The pack lists every provisional rule grouped by domain, with its
full justification and a decision line "☐ Approve ☐ Change ☐ Reject".  NEXT-MARRIAGE-02:
it also lists every provisional signification term (with its domain tags) the same way.
It reads records only: building it never changes a rule, and ticking a box in it admits
nothing.  A rule
becomes REVIEWED only through ``provisional.promote_to_reviewed`` with a reviewer record.
"""

import argparse
import html
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Final

from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import ProvisionalCorpus, ProvisionalRule
from astrologer.knowledge.provisional_pack_v2 import ACTIVE_PROVISIONAL_CORPUS, NOT_DRAFTED
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    ProvisionalSignification,
    ProvisionalSignificationCorpus,
)
from astrologer.rules.models import ConditionDefinition, ConditionKind, ConditionOperation

DECISION_LINE: Final = "☐ Approve ☐ Change ☐ Reject"
PACK_RELATIVE_PATH: Final = Path("research/final-review/review-pack.md")
PDF_DIRECTORY: Final = Path.home() / "Desktop" / "jyotai-review"
_CHROME_CANDIDATES: Final = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
)
_DOMAIN_LABELS: Final = {JyotishDomain.TRAVEL: "Travel (residence away from birthplace)"}


def _domain_label(domain: JyotishDomain) -> str:
    return _DOMAIN_LABELS.get(domain, domain.value.title())


def describe_condition(condition: ConditionDefinition) -> str:
    """A plain rendering of a declarative condition (facts and expected values only)."""
    if condition.kind is ConditionKind.LEAF:
        operation = condition.operation
        if operation is ConditionOperation.EQUALS:
            return f"`{condition.fact_id}` = {condition.expected_value}"
        if operation is ConditionOperation.IN:
            values = ", ".join(str(value) for value in condition.expected_values or ())
            return f"`{condition.fact_id}` in {{{values}}}"
        return f"`{condition.fact_id}` {operation.value if operation else '?'}"
    joined = f" {condition.kind.value.upper()} ".join(
        f"({describe_condition(child)})" for child in condition.children
    )
    return f"NOT ({joined})" if condition.kind is ConditionKind.NOT else joined


def _quote(text: str) -> list[str]:
    return [f"> {line}" if line else ">" for line in text.splitlines()]


def _rule_section(number: int, rule: ProvisionalRule) -> list[str]:
    j = rule.justification
    lines = [
        f"### {number}. {rule.rule.name}",
        "",
        f"- **Rule id:** `{rule.rule_id}` ({rule.rule.rule_version})",
        f"- **Condition:** {describe_condition(rule.rule.condition)} (D1/Rashi, static, "
        "contextual; no timing, polarity or weight)",
        f"- **Source:** {j.source_work}",
        f"- **Verse / locator:** {j.locator}",
        f"- **Confidence (author's):** {j.confidence.value}",
        f"- **Author:** {j.author}",
        f"- **Status:** {j.status.value} — pending expert review",
        *(
            [f"- **Wording:** held in the app — {rule.held_reason}"]
            if rule.wording == "held"
            else []
        ),
        "",
        "**Original text**",
        "",
        *_quote(j.original_text),
        "",
        "**Draft translation**",
        "",
        *_quote(j.draft_translation),
        "",
        "**Statement shown in the app (with the provisional badge)**",
        "",
        *_quote(rule.statement),
        "",
        "**Interpretive reasoning**",
        "",
        j.interpretive_reasoning,
        "",
        "**Conventions used**",
        "",
        *[f"- {item}" for item in j.conventions],
        "",
    ]
    if j.transcription_notes:
        lines += ["**Transcription notes**", "", j.transcription_notes, ""]
    return lines + _decision_lines()


def _decision_lines() -> list[str]:
    return [
        f"**Decision:** {DECISION_LINE}",
        "",
        "Changed wording or condition (if Change): ______________________________",
        "",
        "Reason (if Reject): ______________________________",
        "",
        "Reviewer name, qualification, date: ______________________________",
        "",
        "---",
        "",
    ]


def _subject_label(term: ProvisionalSignification) -> str:
    if term.subject_kind == "graha":
        return term.subject.title()
    house = int(term.subject)
    suffix = "th" if 10 <= house % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(house % 10, "th")
    return f"{house}{suffix} house"


def _signification_section(number: int, term: ProvisionalSignification) -> list[str]:
    j = term.justification
    tags = ", ".join(f"{_domain_label(tag.domain)} ({tag.status})" for tag in term.tags)
    lines = [
        f"### S{number}. {_subject_label(term)}: {term.sanskrit} ({term.display})",
        "",
        f"- **Term id:** `{term.term_id}` ({term.term_version})",
        f"- **Subject:** {term.subject_kind} {term.subject}",
        f"- **Domain tags:** {tags}",
        f"- **Source:** {j.source_work}",
        f"- **Verse / locator:** {j.locator}",
        f"- **Confidence (author's):** {j.confidence.value}",
        f"- **Author:** {j.author}",
        f"- **Status:** {j.status.value} — pending expert review",
        *(
            [f"- **Translation:** not shown in the app — {term.translation_held_reason}"]
            if term.translation_held_reason
            else []
        ),
        "",
        "**Original text**",
        "",
        *_quote(j.original_text),
        "",
        "**Draft translation**",
        "",
        *_quote(j.draft_translation),
        "",
        "**Statement shown in the app (with the provisional badge)**",
        "",
        *_quote(term.statement),
        "",
        "**Interpretive reasoning**",
        "",
        j.interpretive_reasoning,
        "",
        "**Conventions used**",
        "",
        *[f"- {item}" for item in j.conventions],
        "",
    ]
    if j.transcription_notes:
        lines += ["**Transcription notes**", "", j.transcription_notes, ""]
    return lines + _decision_lines()


def latest_record_date(
    corpus: ProvisionalCorpus, significations: ProvisionalSignificationCorpus | None = None
) -> date:
    """The pack's date: the latest justification record date (deterministic)."""
    dates = [rule.justification.recorded_at.date() for rule in corpus.rules]
    if significations is not None:
        dates += [term.justification.recorded_at.date() for term in significations.terms]
    return max(dates) if dates else date(2026, 11, 24)


def build_markdown(
    corpus: ProvisionalCorpus,
    generated_on: date,
    not_drafted: Mapping[str, Sequence[str]] | None = None,
    significations: ProvisionalSignificationCorpus | None = None,
) -> str:
    """The review pack as Markdown; deterministic for a given corpus and date.

    ``not_drafted`` lists, per domain, located verses that yield no rule, with the reason.
    ``significations`` adds the provisional signification terms (NEXT-MARRIAGE-02).
    """
    not_drafted = not_drafted or {}
    domains = [domain for domain in JyotishDomain if corpus.for_domain(domain.value)]
    empty = [domain for domain in JyotishDomain if not corpus.for_domain(domain.value)]
    lines = [
        "# JyotAI final expert review pack: provisional rules",
        "",
        f"Corpus `{corpus.release_id}` · {len(corpus.rules)} provisional rules · generated "
        f"{generated_on.isoformat()} by `python -m astrologer.knowledge.review_pack`.",
        "",
        "**Nothing in this pack is reviewed.** Every rule below is a provisional rule pending "
        'this review. Its author line says who wrote it: "drafted_by: AI agent; adopted_by: '
        'project owner (pending)" means an AI agent drafted it and the project owner has not '
        'yet adopted it; "project owner, provisional" means the project owner wrote it. '
        "In the app a provisional rule is "
        'shown only when the user turns on "Show provisional interpretations (beta)", '
        "and always with a badge naming the author's confidence, e.g. \"Provisional · medium "
        'confidence".',
        "",
        "## How to decide",
        "",
        "For each rule, tick one box:",
        "",
        "- **Approve:** the source reading, translation, condition and statement are right "
        "as written. The rule is then admitted as REVIEWED under your name.",
        "- **Change:** write the corrected wording or condition. The rule is admitted with "
        "your wording.",
        "- **Reject:** the rule is removed from the provisional corpus.",
        "",
        "A rule marked **Wording: held** has a located verse whose domain clause is "
        "fear-based, accusatory or a health statement. The app shows only the held notice "
        "in its place. To approve it, write the wording the app should show (Change).",
        "",
        "Ticking a box admits nothing by itself: engineering records your decision and runs "
        "the existing admission flow with your review record.",
        "",
        "**Provisional significations** (after the rules) are single graha or house terms "
        "drafted for one domain, e.g. Marriage. Each carries domain tags: an answer shows "
        "only the terms tagged for the asked domain. The reviewed signification terms already "
        "in the app are tagged Career (reviewed) only, so a Marriage answer shows none of "
        "them. Approving a provisional term tags it for its domain as reviewed.",
        "",
        "## Summary",
        "",
        "| Domain | Provisional rules | Wording held |",
        "| --- | --- | --- |",
        *[
            f"| {_domain_label(domain)} | {len(corpus.for_domain(domain.value))} | "
            f"{sum(rule.wording == 'held' for rule in corpus.for_domain(domain.value))} |"
            for domain in domains
        ],
        "",
    ]
    if empty:
        lines += [
            "Domains with no provisional rule yet: "
            + ", ".join(_domain_label(domain) for domain in empty)
            + ".",
            "",
        ]
    number = 0
    for domain in domains:
        lines += [f"## {_domain_label(domain)}", ""]
        for rule in corpus.for_domain(domain.value):
            number += 1
            lines += _rule_section(number, rule)
        if notes := not_drafted.get(domain.value):
            lines += [
                f"### Located, not drafted ({_domain_label(domain)})",
                "",
                *[f"- {note}" for note in notes],
                "",
            ]
    if significations is not None and significations.terms:
        for domain in JyotishDomain:
            terms = significations.for_domain(domain.value)
            if not terms:
                continue
            lines += [
                f"## Provisional significations: {_domain_label(domain)}",
                "",
                f"Corpus `{significations.release_id}` · {len(terms)} terms.",
                "",
            ]
            for index, term in enumerate(terms, start=1):
                lines += _signification_section(index, term)
    return "\n".join(lines).rstrip() + "\n"


def markdown_to_html(markdown: str, title: str) -> str:
    """A minimal converter for the pack's own Markdown subset, for PDF printing."""
    body: list[str] = []
    in_list = False
    in_quote: list[str] = []
    in_table = False

    def inline(text: str) -> str:
        escaped = html.escape(text)
        parts = escaped.split("**")
        escaped = "".join(
            f"<strong>{part}</strong>" if index % 2 else part for index, part in enumerate(parts)
        )
        parts = escaped.split("`")
        return "".join(
            f"<code>{part}</code>" if index % 2 else part for index, part in enumerate(parts)
        )

    def close() -> None:
        nonlocal in_list, in_table
        if in_list:
            body.append("</ul>")
            in_list = False
        if in_quote:
            body.append(f"<blockquote>{'<br>'.join(inline(q) for q in in_quote)}</blockquote>")
            in_quote.clear()
        if in_table:
            body.append("</table>")
            in_table = False

    for line in markdown.splitlines():
        if line.startswith(">"):
            if not in_quote:
                close()
            in_quote.append(line[1:].strip())
            continue
        if line.startswith("| "):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if set("".join(cells)) <= {"-", " "}:
                continue
            if not in_table:
                close()
                body.append("<table>")
                in_table = True
                body.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                body.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if line.startswith("- "):
            if not in_list:
                close()
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{inline(line[2:])}</li>")
            continue
        close()
        if line.startswith("### "):
            body.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            body.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{inline(line[2:])}</h1>")
        elif line == "---":
            body.append("<hr>")
        elif line.strip():
            body.append(f"<p>{inline(line)}</p>")
    close()
    style = (
        "body{font-family:'Noto Serif Devanagari','Kohinoor Devanagari',Georgia,serif;"
        "max-width:46rem;margin:2rem auto;line-height:1.5;color:#1d1b16}"
        "h1{font-size:1.6rem}h2{border-bottom:1px solid #b9a47a;padding-bottom:.2rem;"
        "margin-top:2rem}h3{margin-top:1.5rem;break-after:avoid}"
        "blockquote{border-left:3px solid #c98a2b;margin:.5rem 0;padding:.2rem .8rem;"
        "background:#faf5ea}code{font-size:.85em}table{border-collapse:collapse}"
        "td,th{border:1px solid #b9a47a;padding:.2rem .6rem}hr{margin:2rem 0}"
        "@page{margin:18mm}"
    )
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)}</title><style>{style}</style></head><body>"
        + "\n".join(body)
        + "</body></html>\n"
    )


def find_repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "apps").is_dir():
            return candidate
    raise FileNotFoundError("repository root (AGENTS.md + apps/) not found")


def export_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = next(
        (path for path in _CHROME_CANDIDATES if Path(path).exists() or shutil.which(path)), None
    )
    if chrome is None:
        raise RuntimeError("PDF export needs a local Chrome/Chromium; none was found")
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Chrome did not write {pdf_path}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--pdf", action="store_true", help="also export a PDF")
    parser.add_argument("--output", type=Path, help="Markdown path (default: repo pack path)")
    parser.add_argument("--pdf-dir", type=Path, default=PDF_DIRECTORY)
    parser.add_argument(
        "--date", type=date.fromisoformat, help="default: the latest record date in the corpus"
    )
    args = parser.parse_args(argv)
    output: Path = args.output or find_repository_root(Path.cwd()) / PACK_RELATIVE_PATH
    markdown = build_markdown(
        ACTIVE_PROVISIONAL_CORPUS,
        args.date
        or latest_record_date(ACTIVE_PROVISIONAL_CORPUS, ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS),
        NOT_DRAFTED,
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    print(f"wrote {output}")
    if args.pdf:
        directory: Path = args.pdf_dir
        directory.mkdir(parents=True, exist_ok=True)
        html_path = directory / "review-pack.html"
        html_path.write_text(
            markdown_to_html(markdown, "JyotAI final expert review pack"), encoding="utf-8"
        )
        pdf_path = directory / "review-pack.pdf"
        try:
            export_pdf(html_path, pdf_path)
        except (RuntimeError, subprocess.SubprocessError, OSError) as error:
            print(f"PDF export failed: {error}", file=sys.stderr)
            return 1
        print(f"wrote {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
