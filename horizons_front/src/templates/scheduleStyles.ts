export const SHARED_STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', sans-serif;
    background: #0f1623;
    color: #e2e8f0;
    padding: 40px;
    min-height: 100vh;
  }

  .page { max-width: 900px; margin: 0 auto; }

  /* ── Header ── */
  .header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 40px;
    padding-bottom: 28px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }

  .festival-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(6,182,212,0.12);
    border: 1px solid rgba(6,182,212,0.25);
    color: #22d3ee;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 100px;
    margin-bottom: 14px;
  }

  .festival-tag::before {
    content: '';
    width: 5px; height: 5px;
    background: #22d3ee;
    border-radius: 50%;
  }

  h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.15;
    margin-bottom: 6px;
  }

  .subtitle { font-size: 0.85rem; color: #64748b; }

  .header-meta { text-align: right; }

  .meta-badge {
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 16px;
    text-align: center;
  }

  .meta-badge .count {
    font-size: 1.6rem;
    font-weight: 700;
    color: #22d3ee;
    line-height: 1;
    display: block;
  }

  .meta-badge .label {
    font-size: 10px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
    display: block;
  }

  /* ── Section title ── */
  .section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 14px;
  }

  .section-title .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22d3ee;
    flex-shrink: 0;
  }

  .section-title h2 {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94a3b8;
  }

  .section-title .line {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
  }

  /* ── Table ── */
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07);
  }

  thead tr { background: rgba(255,255,255,0.04); }

  th {
    padding: 11px 14px;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    border-bottom: 1px solid rgba(255,255,255,0.07);
  }

  td {
    padding: 12px 14px;
    font-size: 0.82rem;
    color: #cbd5e1;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    vertical-align: middle;
  }

  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.02); }

  /* ── Badges ── */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
  }

  .badge-day     { background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.2); }
  .badge-time    { background: rgba(6,182,212,0.12);  color: #67e8f9; border: 1px solid rgba(6,182,212,0.18); }
  .badge-full    { background: rgba(34,197,94,0.12);  color: #86efac; border: 1px solid rgba(34,197,94,0.2); }
  .badge-partial { background: rgba(234,179,8,0.12);  color: #fde047; border: 1px solid rgba(234,179,8,0.2); }
  .badge-empty   { background: rgba(239,68,68,0.12);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.2); }

  .category-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
    background: rgba(255,255,255,0.06);
    color: #94a3b8;
    border: 1px solid rgba(255,255,255,0.08);
  }

  /* ── Volunteer chips ── */
  .volunteer-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    align-items: center;
  }

  .volunteer-chip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 500;
    background: rgba(148,163,184,0.08);
    color: #94a3b8;
    border: 1px solid rgba(148,163,184,0.15);
    white-space: nowrap;
  }

  .volunteer-chip--self {
    background: rgba(6,182,212,0.14);
    color: #67e8f9;
    border-color: rgba(6,182,212,0.28);
    font-weight: 600;
  }

  .no-assignee { color: #334155; font-style: italic; font-size: 0.78rem; }

  /* ── Footer ── */
  footer {
    margin-top: 48px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  footer .left  { font-size: 11px; color: #334155; }
  footer .right { font-size: 11px; color: #334155; }

  @media print {
    body { background: #0f1623 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
`