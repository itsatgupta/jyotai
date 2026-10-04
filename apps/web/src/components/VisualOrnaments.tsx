import type { ReactNode } from "react";
import type { DashboardDomain } from "../lib/contracts";

const icons: Record<DashboardDomain, string> = {
  career: "↗", wealth: "✦", education: "⌁", business: "◇",
  children: "◌", spirituality: "✺", travel: "⌘", friends: "◉",
};

export function CelestialBackdrop({ compact = false }: { compact?: boolean }) {
  return <div className={compact ? "celestial-backdrop compact" : "celestial-backdrop"} aria-hidden="true">
    <svg viewBox="0 0 360 240" focusable="false">
      <circle cx="218" cy="120" r="86" /><circle cx="218" cy="120" r="56" />
      <path d="M132 120h172M218 34v172M157 59l122 122M279 59 157 181" />
      <circle className="ornament-sun" cx="218" cy="120" r="23" />
      <path className="ornament-arc" d="M36 167c32-66 82-99 150-99" />
      <circle className="ornament-star" cx="76" cy="62" r="3" /><circle className="ornament-star" cx="108" cy="185" r="2" />
    </svg>
  </div>;
}

export function DomainIllustration({ domain }: { domain: DashboardDomain }) {
  return <span className={`domain-illustration domain-${domain}`} aria-hidden="true"><span>{icons[domain]}</span></span>;
}

export function TrustMark({ children }: { children: ReactNode }) {
  return <span className="trust-mark"><span aria-hidden="true">✦</span>{children}</span>;
}
