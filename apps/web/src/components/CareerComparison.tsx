import "./CareerComparison.css";
import type { CareerYearColumn, CareerYearComparison, ComparisonSentence } from "../lib/contracts";

type ExplainYear = (question: string, label: string) => void;

const STATUS_LABEL: Record<CareerYearColumn["timing_status"], string> = {
  MATCH: "Reviewed timing indication applies",
  NO_MATCH: "No reviewed timing indication applies",
  UNKNOWN: "Timing could not be evaluated",
  UNSUPPORTED: "Timing not evaluated",
  NOT_EVALUATED: "Timing not evaluated",
};

function Sentences({ items }: { items: ComparisonSentence[] }) {
  return <>{items.map((item, index) => <p key={`${index}-${item.text}`}>{item.text}</p>)}</>;
}

/**
 * NEXT-COMPARE-02 side-by-side view. Order: direct line, "What differs", "Same in both years
 * (natal)", the full columns in a disclosure, why no ranking, limitations. All text comes from
 * the server's comparison-view-v1 sentences; nothing is ranked, tallied, or reworded here.
 */
export function CareerComparison({ comparison, onExplainYear, disabled = false }: { comparison: CareerYearComparison; onExplainYear?: ExplainYear; disabled?: boolean }) {
  const [a, b] = comparison.years;
  return <div className="career-comparison" data-comparison-mode={comparison.comparison_mode}>
    <section className="comparison-direct direct-answer"><h4>Overview</h4><Sentences items={comparison.direct} /></section>
    <section className="comparison-differs" aria-labelledby={`differs-${a}-${b}`}><h4 id={`differs-${a}-${b}`}>What differs between {a} and {b}</h4><ul>{comparison.differences.map((item, index) => <li key={`${index}-${item.text}`} className={item.basis === "fixed" ? "comparison-fixed" : undefined}>{item.text}</li>)}</ul></section>
    <section className="comparison-natal"><h4>Same in both years (natal)</h4><Sentences items={comparison.natal_shared} /></section>
    <details className="comparison-columns-disclosure"><summary>Full side-by-side: {a} and {b}</summary>
      <div className="comparison-columns" role="group" aria-label={`Side-by-side facts for ${a} and ${b}`}>{comparison.columns.map((column) => <ComparisonColumn key={column.year} column={column} onExplainYear={onExplainYear} disabled={disabled} />)}</div>
    </details>
    <section className="comparison-why"><h4>Why no ranking</h4><Sentences items={comparison.why_no_ranking} /></section>
    <section className="comparison-limits"><h4>Limitations</h4><Sentences items={comparison.limitations} /></section>
  </div>;
}

function ComparisonColumn({ column, onExplainYear, disabled }: { column: CareerYearColumn; onExplainYear?: ExplainYear; disabled: boolean }) {
  return <article className="comparison-column" aria-labelledby={`column-${column.year}`}>
    <header><h5 id={`column-${column.year}`}>{column.year}</h5><span className="comparison-status">{STATUS_LABEL[column.timing_status]}</span></header>
    <h6>Calculated periods</h6><Sentences items={column.periods} />
    <h6>Reviewed timing</h6><Sentences items={column.timing} />
    <h6>Co-reference links</h6><Sentences items={column.co_references} />
    <details className="comparison-lord-facts"><summary>Calculated Dasha lord relationships</summary><Sentences items={column.lord_facts} /><p>{column.dasha_interpretation.text}</p></details>
    <details className="comparison-provenance"><summary>Methodology and versions</summary><dl><dt>Release</dt><dd>{column.manifest_id} {column.manifest_version}</dd><dt>Timing release</dt><dd>{column.timing_release_id} {column.timing_release_version}</dd><dt>Methodology</dt><dd>{column.methodology_version}</dd><dt>Synthesis</dt><dd>{column.synthesis_version ?? "—"}</dd><dt>Answer plan</dt><dd>{column.answer_plan_version ?? "—"}</dd></dl></details>
    {onExplainYear && <button type="button" className="comparison-explain" disabled={disabled} onClick={() => onExplainYear(`Explain ${column.year}`, `Explain ${column.year}`)}>Explain {column.year}</button>}
  </article>;
}
