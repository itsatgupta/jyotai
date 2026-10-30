import { useEffect, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

export function OrbitArtwork({ compact = false }: { compact?: boolean }) {
  const [rotation, setRotation] = useState(0);
  const [autoEnabled, setAutoEnabled] = useState(true);
  const [reducedMotion, setReducedMotion] = useState(() => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false);
  const [dragging, setDragging] = useState(false);
  const [resetVersion, setResetVersion] = useState(0);
  const activePointer = useRef<{ id: number; angle: number | null } | null>(null);
  const autoPlaying = autoEnabled && !reducedMotion && !dragging;

  useEffect(() => {
    const preference = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!preference) return;
    const update = () => setReducedMotion(preference.matches);
    preference.addEventListener?.("change", update);
    return () => preference.removeEventListener?.("change", update);
  }, []);

  function pointerAngle(event: PointerEvent<HTMLDivElement>): number | null {
    const bounds = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - bounds.left - bounds.width / 2;
    const y = event.clientY - bounds.top - bounds.height / 2;
    if (Math.hypot(x, y) < bounds.width * .12) return null;
    return Math.atan2(y, x) * 180 / Math.PI;
  }

  function beginDrag(event: PointerEvent<HTMLDivElement>) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    activePointer.current = { id: event.pointerId, angle: pointerAngle(event) };
    setDragging(true);
    event.currentTarget.setPointerCapture?.(event.pointerId);
  }

  function moveDrag(event: PointerEvent<HTMLDivElement>) {
    const pointer = activePointer.current;
    if (!pointer || pointer.id !== event.pointerId) return;
    const next = pointerAngle(event);
    if (next === null) return;
    if (pointer.angle !== null) {
      const shortestTurn = ((next - pointer.angle + 540) % 360) - 180;
      const step = Math.max(-45, Math.min(45, shortestTurn));
      setRotation((current) => current + step);
    }
    pointer.angle = next;
  }

  function endDrag(event: PointerEvent<HTMLDivElement>) {
    if (activePointer.current?.id !== event.pointerId) return;
    activePointer.current = null;
    setDragging(false);
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
  }

  function reset() {
    setRotation(0);
    setResetVersion((version) => version + 1);
  }

  function handleKey(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
      event.preventDefault();
      setRotation((current) => current + (event.key === "ArrowRight" ? 15 : -15));
    } else if (event.key === "Home") {
      event.preventDefault();
      reset();
    }
  }

  const glyphs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
  const starPoints = Array.from({ length: 24 }, (_, index) => {
    const angle = (index * 15 - 90) * Math.PI / 180;
    return { x: 280 + 251 * Math.cos(angle), y: 280 + 251 * Math.sin(angle) };
  });
  return <><div className={`orbit-art ${compact ? "orbit-art-compact" : ""}`} role="group" tabIndex={0} aria-label="Decorative zodiac wheel" aria-describedby="orbit-instructions" data-auto-rotation={autoPlaying ? "playing" : "paused"} data-dragging={dragging} onPointerDown={beginDrag} onPointerMove={moveDrag} onPointerUp={endDrag} onPointerCancel={endDrag} onLostPointerCapture={endDrag} onKeyDown={handleKey}>
    <span className="orbit-instructions" id="orbit-instructions">Drag or swipe to rotate. Left and right arrow keys rotate by 15 degrees; Home resets. This artwork does not represent chart calculations.</span>
    <div className="orbit-manual" style={{ transform: `rotate(${rotation}deg)` }}><div key={resetVersion} className="orbit-auto" style={{ animationPlayState: autoPlaying ? "running" : "paused" }}>
    <svg viewBox="0 0 560 560" aria-hidden="true" focusable="false">
      <defs>
        <radialGradient id="preview-sun"><stop stopColor="#fff9d3"/><stop offset=".36" stopColor="#ffcc70"/><stop offset=".8" stopColor="#ef8b67"/><stop offset="1" stopColor="#ad5d9d"/></radialGradient>
        <linearGradient id="preview-ring" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#f9dd9f"/><stop offset=".48" stopColor="#b4a2eb"/><stop offset="1" stopColor="#6ee0d6"/></linearGradient>
        <radialGradient id="preview-halo"><stop stopColor="#ffe6b3" stopOpacity=".28"/><stop offset=".6" stopColor="#8a83c7" stopOpacity=".1"/><stop offset="1" stopColor="#8a83c7" stopOpacity="0"/></radialGradient>
      </defs>
      <circle cx="280" cy="280" r="270" fill="url(#preview-halo)"/>
      <g className="orbit-architecture"><path d="M280 18 542 280 280 542 18 280Z"/><path d="M280 68 492 280 280 492 68 280Z"/><path d="M280 18 492 280 280 542 68 280Z"/></g>
      <circle cx="280" cy="280" r="259" className="orbit-outer"/>
      <circle cx="280" cy="280" r="235" className="orbit-ring"/>
      <circle cx="280" cy="280" r="206" className="orbit-ring orbit-ring-soft"/>
      <circle cx="280" cy="280" r="175" className="orbit-dash"/>
      <circle cx="280" cy="280" r="142" className="orbit-ring"/>
      <circle cx="280" cy="280" r="121" className="orbit-inner-dash"/>
      <path className="orbit-rays" d="M280 36v488M36 280h488M107 107l346 346M453 107 107 453"/>
      {starPoints.map((point, index) => <circle key={index} cx={point.x} cy={point.y} r={index % 3 === 0 ? 2.1 : 1} className="orbit-star-point"/>)}
      {glyphs.map((glyph, index) => { const a = (index * 30 - 90) * Math.PI / 180; return <text key={glyph} x={280 + 221 * Math.cos(a)} y={287 + 221 * Math.sin(a)} textAnchor="middle" className="orbit-glyph">{glyph}</text>; })}
      <path d="M128 216a164 164 0 0 1 125-96M364 138a164 164 0 0 1 77 102M432 340a164 164 0 0 1-94 86" className="orbit-accent-arc"/>
      <circle cx="119" cy="249" r="4" className="orbit-satellite"/><circle cx="415" cy="374" r="3" className="orbit-satellite orbit-satellite-secondary"/>
      <circle cx="280" cy="280" r="94" className="orbit-glow"/><circle cx="280" cy="280" r="69" fill="url(#preview-sun)" className="orbit-sun"/>
      <circle cx="280" cy="280" r="55" className="orbit-sun-inner"/>
      <path d="M280 236v88M236 280h88M249 249l62 62M311 249l-62 62" className="orbit-sun-rays"/>
      <circle cx="280" cy="280" r="18" className="orbit-sun-core"/>
      <path d="M280 7v9M280 544v9M7 280h9M544 280h9" className="orbit-ticks"/>
    </svg>
    </div></div>
  </div><div className="orbit-controls" role="group" aria-label="Decorative wheel controls">
    <button type="button" onClick={() => setRotation((current) => current - 15)} aria-label="Rotate wheel anticlockwise 15 degrees" title="Rotate anticlockwise">↶</button>
    <button type="button" onClick={() => setAutoEnabled((enabled) => !enabled)} disabled={reducedMotion} aria-label={autoPlaying ? "Pause automatic wheel rotation" : "Play automatic wheel rotation"} title={reducedMotion ? "Automatic rotation is off for reduced motion" : autoPlaying ? "Pause rotation" : "Play rotation"}>{autoPlaying ? "Ⅱ Pause" : "▶ Play"}</button>
    <button type="button" onClick={() => setRotation((current) => current + 15)} aria-label="Rotate wheel clockwise 15 degrees" title="Rotate clockwise">↷</button>
    <button type="button" onClick={reset} aria-label="Reset decorative wheel rotation" title="Reset rotation">Reset</button>
  </div></>;
}
