"""
ui_theme.py
------------
Sunwise's visual identity, kept separate from app logic.

Design language (see README for the full rationale):
  - Palette grounded in the subject: dusk-navy background, a sun/heat
    gradient (teal -> yellow -> amber -> red -> magenta) that mirrors the
    OSHA/NWS heat-index bands, and a safety-yellow accent as a nod to
    real hi-vis workwear.
  - Type: Space Grotesk (display), IBM Plex Sans (body/UI), IBM Plex Mono
    (numeric readouts -- temperatures read like an instrument gauge).
  - Signature element: a semicircular "gauge" for the risk verdict, and a
    rising heat-bar loading animation (standing in for heat shimmer) while
    the AI briefing streams in.
  - Motion is deliberate and limited to those two places, and everything
    respects `prefers-reduced-motion`.

Only small, self-authored HTML snippets (no user/AI text) are ever rendered
with unsafe_allow_html=True. Streamed AI text is always rendered with plain
st.markdown elsewhere in app.py.
"""

from __future__ import annotations

import math

import heat_safety

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

CSS_BLOCK = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {
  --sw-bg: #0B1220;
  --sw-panel: #131B2C;
  --sw-panel-2: #1B2540;
  --sw-line: #2A3550;
  --sw-text: #F4F6FB;
  --sw-muted: #8B95AF;
  --sw-hivis: #FFB100;
  --sw-teal: #2FD3C7;
  --sw-yellow: #FFC93C;
  --sw-amber: #F5941B;
  --sw-red: #E5383B;
  --sw-magenta: #9B2FAE;
}

/* Background: deep dusk navy with a soft ambient glow, evoking early
   morning / dusk sky when a lot of outdoor shifts start or end. */
.stApp {
  background:
    radial-gradient(1100px 520px at 12% -8%, rgba(245,148,27,0.10), transparent 60%),
    radial-gradient(900px 500px at 100% 0%, rgba(47,211,199,0.08), transparent 55%),
    var(--sw-bg);
}

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans', -apple-system, sans-serif;
}

/* ---- Sidebar: framed like an instrument/control panel ---- */
[data-testid="stSidebar"] {
  background: var(--sw-panel);
  border-right: 1px solid var(--sw-line);
}
[data-testid="stSidebar"] > div:first-child {
  border-left: 3px solid var(--sw-hivis);
}

/* ---- Buttons ---- */
.stButton > button[kind="primary"] {
  background: linear-gradient(90deg, var(--sw-amber), var(--sw-red));
  border: none;
  font-weight: 600;
  letter-spacing: 0.01em;
  transition: filter 150ms ease, transform 150ms ease;
}
.stButton > button[kind="primary"]:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}

/* ---- Brand header ---- */
.sw-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 2px;
}
.sw-brand-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 2.1rem;
  letter-spacing: -0.01em;
  line-height: 1.1;
  background: linear-gradient(90deg, var(--sw-teal), var(--sw-yellow), var(--sw-amber), var(--sw-red));
  background-size: 250% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: sw-gradient-shift 9s ease infinite;
}
.sw-tagline {
  color: var(--sw-muted);
  font-size: 0.98rem;
  margin-top: -2px;
}

@keyframes sw-gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ---- Generic panel/card ---- */
.sw-card {
  background: var(--sw-panel);
  border: 1px solid var(--sw-line);
  border-radius: 18px;
  padding: 22px 20px;
}

/* ---- Data-source badge ---- */
.sw-source-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  color: var(--sw-muted);
  background: var(--sw-panel-2);
  border: 1px solid var(--sw-line);
  border-radius: 999px;
  padding: 5px 12px;
}
.sw-source-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 8px currentColor;
}

/* ---- Risk pill ---- */
.sw-risk-pill {
  display: inline-block;
  padding: 7px 16px;
  border-radius: 999px;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #0B1220;
}

/* ---- Gauge reveal animation (keyframes injected per-render alongside it) ---- */
@media (prefers-reduced-motion: reduce) {
  .sw-gauge-fill { animation: none !important; }
}

/* ---- Heat-wave loading state ---- */
.sw-loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px 20px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(245,148,27,0.07), rgba(229,56,59,0.04));
  border: 1px solid rgba(255,177,0,0.20);
}
.sw-heat-bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 48px;
}
.sw-heat-bars span {
  display: block;
  width: 7px;
  border-radius: 4px;
  background: linear-gradient(180deg, var(--sw-yellow), var(--sw-amber), var(--sw-red));
  animation: sw-heat-rise 1.15s ease-in-out infinite;
}
.sw-heat-bars span:nth-child(1) { animation-delay: 0.00s; }
.sw-heat-bars span:nth-child(2) { animation-delay: 0.10s; }
.sw-heat-bars span:nth-child(3) { animation-delay: 0.20s; }
.sw-heat-bars span:nth-child(4) { animation-delay: 0.30s; }
.sw-heat-bars span:nth-child(5) { animation-delay: 0.20s; }
.sw-heat-bars span:nth-child(6) { animation-delay: 0.10s; }
.sw-heat-bars span:nth-child(7) { animation-delay: 0.00s; }

@keyframes sw-heat-rise {
  0%, 100% { height: 10px; opacity: 0.5; }
  50% { height: 48px; opacity: 1; }
}

.sw-loading-label {
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  background: linear-gradient(90deg, var(--sw-yellow), var(--sw-amber), var(--sw-red), var(--sw-yellow));
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: sw-gradient-shift-fast 3.2s ease infinite;
}

@keyframes sw-gradient-shift-fast {
  0% { background-position: 0% 50%; }
  100% { background-position: 300% 50%; }
}

@media (prefers-reduced-motion: reduce) {
  .sw-heat-bars span, .sw-loading-label { animation: none !important; opacity: 1 !important; height: 30px !important; }
}

.sw-footnote {
  color: var(--sw-muted);
  font-size: 0.82rem;
  line-height: 1.5;
}
</style>
"""


# ---------------------------------------------------------------------------
# Small HTML / SVG builders (self-authored content only -- safe for
# unsafe_allow_html=True; never used to render AI or user free-text)
# ---------------------------------------------------------------------------

def sun_icon_svg(size: int = 36) -> str:
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="17" cy="17" r="7" fill="#FFC93C"/>
      <g stroke="#FFC93C" stroke-width="2" stroke-linecap="round">
        <line x1="17" y1="1" x2="17" y2="5"/>
        <line x1="17" y1="29" x2="17" y2="33"/>
        <line x1="1" y1="17" x2="5" y2="17"/>
        <line x1="29" y1="17" x2="33" y2="17"/>
        <line x1="5.5" y1="5.5" x2="8.3" y2="8.3"/>
        <line x1="25.7" y1="25.7" x2="28.5" y2="28.5"/>
        <line x1="5.5" y1="28.5" x2="8.3" y2="25.7"/>
        <line x1="25.7" y1="8.3" x2="28.5" y2="5.5"/>
      </g>
    </svg>
    """


def brand_header_html() -> str:
    return f"""
    <div class="sw-header-row">
      {sun_icon_svg(38)}
      <div>
        <div class="sw-brand-title">Sunwise</div>
      </div>
    </div>
    <div class="sw-tagline">Outdoor work safety, before you step outside.</div>
    """


def gauge_svg(hi_c: float, risk: "heat_safety.RiskBand") -> str:
    """A semicircular gauge showing the heat index against the OSHA/NWS
    risk spectrum, with a one-time fill-in animation."""
    frac = heat_safety.gauge_fraction(hi_c)
    radius = 92.0
    circumference = math.pi * radius
    progress_len = circumference * frac
    path = "M 18 120 A 92 92 0 0 1 202 120"

    return f"""
    <style>
    @keyframes sw-gauge-reveal-{int(frac*1000)} {{
      from {{ stroke-dasharray: 0 {circumference:.2f}; }}
      to   {{ stroke-dasharray: {progress_len:.2f} {circumference:.2f}; }}
    }}
    </style>
    <svg viewBox="0 0 220 140" width="100%" style="max-width:320px;display:block;margin:0 auto;">
      <defs>
        <linearGradient id="sw-gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#2FD3C7"/>
          <stop offset="25%" stop-color="#FFC93C"/>
          <stop offset="50%" stop-color="#F5941B"/>
          <stop offset="75%" stop-color="#E5383B"/>
          <stop offset="100%" stop-color="#9B2FAE"/>
        </linearGradient>
      </defs>
      <path d="{path}" fill="none" stroke="#2A3550" stroke-width="16" stroke-linecap="round"/>
      <path d="{path}" fill="none" stroke="url(#sw-gauge-grad)" stroke-width="16" stroke-linecap="round"
            class="sw-gauge-fill"
            style="stroke-dasharray:{progress_len:.2f} {circumference:.2f}; animation: sw-gauge-reveal-{int(frac*1000)} 1.1s ease-out forwards;"/>
      <text x="110" y="92" text-anchor="middle" font-family="'IBM Plex Mono', monospace"
            font-size="40" font-weight="600" fill="{risk.color}">{hi_c:.0f}&#176;</text>
      <text x="110" y="113" text-anchor="middle" font-family="'IBM Plex Sans', sans-serif"
            font-size="12" fill="#8B95AF" letter-spacing="0.03em">FEELS LIKE &#176;C</text>
    </svg>
    """


def risk_pill_html(risk: "heat_safety.RiskBand") -> str:
    gradient = f"linear-gradient(90deg, {risk.gradient[0]}, {risk.gradient[1]})"
    return f'<div class="sw-risk-pill" style="background:{gradient};">{risk.level}</div>'


def source_badge_html(source: str) -> str:
    is_live = source == "live"
    color = "#2FD3C7" if is_live else "#8B95AF"
    label = "LIVE FORTYGUARD DATA" if is_live else "DEMO / SIMULATED DATA"
    return (
        '<div class="sw-source-badge">'
        f'<span class="sw-source-dot" style="background:{color}; color:{color};"></span>'
        f"{label}</div>"
    )


def loading_card_html(message: str = "Reading conditions & preparing your safety briefing") -> str:
    bars = "".join("<span></span>" for _ in range(7))
    return f"""
    <div class="sw-loading-card">
      <div class="sw-heat-bars">{bars}</div>
      <div class="sw-loading-label">{message}&hellip;</div>
    </div>
    """
