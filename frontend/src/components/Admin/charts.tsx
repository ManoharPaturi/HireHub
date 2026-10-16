/*
 * SVG chart components for already-aggregated admin data. Values arrive from
 * backend count/group queries. The functions convert values to coordinates,
 * arc angles or bar widths; they do not query MySQL or calculate hiring outcomes.
 */

import React from 'react';

// ── Lightweight SVG charts for the admin console (no chart lib needed) ────────

// Map day indexes to x-coordinates and counts to y-coordinates. SVG y
// increases downward, so larger counts subtract more from the baseline.
export const AreaChart: React.FC<{ data: { date: string; count: number }[]; height?: number }> = ({ data, height = 190 }) => {
  const w = 640, h = height, pad = { t: 14, r: 10, b: 26, l: 34 };
  // Use at least 1 as the scale denominator so an empty/all-zero dataset
  // does not divide by zero when computing chart positions.
  const max = Math.max(1, ...data.map((d) => d.count));
  const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
  const x = (i: number) => pad.l + (data.length <= 1 ? iw / 2 : (i / (data.length - 1)) * iw);
  const y = (v: number) => pad.t + ih - (v / max) * ih;
  const line = data.map((d, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(d.count).toFixed(1)}`).join(' ');
  const area = `${line} L${x(data.length - 1).toFixed(1)},${pad.t + ih} L${x(0).toFixed(1)},${pad.t + ih} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img">
      <defs>
        <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#4f7cff" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#4f7cff" stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {[0, 0.25, 0.5, 0.75, 1].map((f) => (
        <line key={f} x1={pad.l} x2={w - pad.r} y1={pad.t + ih * f} y2={pad.t + ih * f} stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
      ))}
      {[0, 0.5, 1].map((f) => (
        <text key={f} x={pad.l - 6} y={pad.t + ih * f + 3} textAnchor="end" fontSize="9" fill="#5a6284">
          {Math.round(max * (1 - f))}
        </text>
      ))}
      <path d={area} fill="url(#areaFill)" />
      <path d={line} fill="none" stroke="#4f7cff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {data.map((d, i) => (
        <circle key={d.date} cx={x(i)} cy={y(d.count)} r="3" fill="#1d2135" stroke="#4f7cff" strokeWidth="2" />
      ))}
      {data.map((d, i) => (
        i % 3 === 0 && (
          <text key={`l${d.date}`} x={x(i)} y={h - 8} textAnchor="middle" fontSize="9" fill="#5a6284">
            {d.date.slice(5).replace('-', '/')}
          </text>
        )
      ))}
    </svg>
  );
};

// Convert each count into a fraction of the total and then an arc angle.
// The running accumulator positions segments after the previous segment.
export const DonutChart: React.FC<{ data: { label: string; value: number; color: string }[]; centerLabel: string }> = ({ data, centerLabel }) => {  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const r = 62, cx = 80, cy = 80, sw = 22;
  let acc = 0;
  const segs = data.map((d) => {
    const frac = d.value / total;
    const seg = { ...d, start: acc, frac };
    acc += frac;
    return seg;
  });

  return (
    <div className="flex items-center gap-5">
      <svg viewBox="0 0 160 160" className="w-[160px] h-[160px] flex-shrink-0">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={sw} />
        {segs.map((s) => {
          const a0 = s.start * 2 * Math.PI - Math.PI / 2;
          const a1 = (s.start + s.frac) * 2 * Math.PI - Math.PI / 2;
          const large = s.frac > 0.5 ? 1 : 0;
          const x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0);
          const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
          if (s.frac <= 0) return null;
          return (
            <path key={s.label} d={`M${x0},${y0} A${r},${r} 0 ${large} 1 ${x1},${y1}`} fill="none" stroke={s.color} strokeWidth={sw} strokeLinecap="butt" />
          );
        })}
        <text x={cx} y={cy - 2} textAnchor="middle" fontSize="22" fontWeight="800" fill="#fff">{total}</text>
        <text x={cx} y={cy + 16} textAnchor="middle" fontSize="9" fill="#8b93b0">{centerLabel}</text>
      </svg>
      <div className="flex-1 min-w-0 space-y-2">
        {data.map((d) => (
          <div key={d.label} className="flex items-start gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0 mt-1" style={{ background: d.color }} />
            <span className="text-xs flex-1 leading-snug break-words" style={{ color: '#aab2cf' }}>{d.label}</span>
            <span className="text-xs font-bold text-white flex-shrink-0">{d.value}</span>
            <span className="text-[10px] w-9 text-right flex-shrink-0" style={{ color: '#5a6284' }}>{Math.round((d.value / total) * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Scale each bar against the largest value in the supplied dataset.
export const BarList: React.FC<{ data: { label: string; value: number; color?: string }[]; unit?: string }> = ({ data, unit = '' }) => {
  const max = Math.max(1, ...data.map((d) => d.value));
  const palette = ['#4f7cff', '#8b5cf6', '#06b6d4', '#f59e0b', '#ec4899'];
  return (
    <div className="space-y-3.5">
      {data.length === 0 && <p className="text-xs" style={{ color: '#5a6284' }}>No data yet</p>}
      {data.map((d, i) => (
        <div key={d.label}>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs truncate pr-2" style={{ color: '#aab2cf' }}>{d.label}</span>
            <span className="text-xs font-bold text-white flex-shrink-0">{d.value}{unit}</span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
            <div className="h-full rounded-full" style={{ width: `${(d.value / max) * 100}%`, background: d.color || palette[i % palette.length] }} />
          </div>
        </div>
      ))}
    </div>
  );
};

/* Daily-count bars — clearer than an area line when the data is sparse
   (most days are zero, a few spike). */
// Give each day a horizontal slot and scale bar height by the maximum
// count. Zero-count days use dots instead of a misleading positive bar.
export const DailyBars: React.FC<{ data: { date: string; count: number }[]; height?: number }> = ({ data, height = 190 }) => {
  const w = 640, h = height, pad = { t: 18, r: 10, b: 26, l: 34 };
  const max = Math.max(1, ...data.map((d) => d.count));
  const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
  const slot = iw / Math.max(1, data.length);
  const bw = Math.min(26, slot * 0.55);

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img">
      {[0, 0.5, 1].map((f) => (
        <line key={f} x1={pad.l} x2={w - pad.r} y1={pad.t + ih * f} y2={pad.t + ih * f} stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
      ))}
      {[0, 0.5, 1].map((f) => (
        <text key={f} x={pad.l - 6} y={pad.t + ih * f + 3} textAnchor="end" fontSize="9" fill="#5a6284">
          {Math.round(max * (1 - f))}
        </text>
      ))}
      {data.map((d, i) => {
        const bh = (d.count / max) * ih;
        const x = pad.l + slot * i + (slot - bw) / 2;
        const y = pad.t + ih - bh;
        return (
          <g key={d.date}>
            <title>{`${d.date} · ${d.count} application${d.count === 1 ? '' : 's'}`}</title>
            {d.count > 0 && <rect x={x} y={y} width={bw} height={Math.max(bh, 2)} rx="3" fill="#4f7cff" opacity="0.9" />}
            {d.count === 0 && <circle cx={x + bw / 2} cy={pad.t + ih} r="1.5" fill="#5a6284" />}
            {d.count > 0 && (
              <text x={x + bw / 2} y={y - 4} textAnchor="middle" fontSize="9" fontWeight="700" fill="#aab2cf">{d.count}</text>
            )}
            {i % 3 === 0 && (
              <text x={x + bw / 2} y={h - 8} textAnchor="middle" fontSize="9" fill="#5a6284">
                {d.date.slice(5).replace('-', '/')}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
};
