// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Combined pane: every compile backend AND every count backend on one cactus.
// Compile = solid line, count = dotted line. Backends from the same family
// (X compile and X_count) share a colour so it's immediately obvious which
// pairs go together. Counters without a matching compile backend (e.g.
// isymganak_count) get their own colour.
//
// Two charts as elsewhere in this dashboard: log scale on top (with the
// legend on the right), linear scale below (no legend, shares axes).

import {
    COLORS, CFG, layout, layoutNoLegend,
    axisTicks, baseXAxis, baseYAxis,
} from './plotly_config.js';

// Backends are grouped into "families" so a compile backend and its
// matching counters share a colour on the cactus. Two suffixes get
// stripped, in order:
//   _count   library/binary counter naming convention (X -> X_count)
//   _bin     binary variant (X_count -> X_bin_count -> X)
// After stripping, what remains is the family key (e.g. "ganak",
// "d4v2"). isymganak_count has no _bin suffix, so it remains its own
// family ("isymganak") with its own colour.

const SUFFIXES = ['_count', '_bin'];

/** Reduce a backend name to its family key. */
function familyOf(name) {
    let f = name;
    let changed = true;
    while (changed) {
        changed = false;
        for (const s of SUFFIXES) {
            if (f.endsWith(s)) { f = f.slice(0, -s.length); changed = true; }
        }
    }
    return f;
}

/**
 * Build a stable family -> colour map. Walk compile series first (so
 * `ganak` claims its colour before `ganak_count` is considered), then
 * count series (which mostly reuse colours, but `isymganak_count` claims
 * a fresh one).
 */
function colorMap(d) {
    const fams = [];
    const seen = new Set();
    const visit = (name) => {
        const fam = familyOf(name);
        if (!seen.has(fam)) { seen.add(fam); fams.push(fam); }
    };
    Object.keys(d.compile_series).sort().forEach(visit);
    Object.keys(d.count_series).sort().forEach(visit);
    const m = {};
    fams.forEach((f, i) => { m[f] = COLORS[i % COLORS.length]; });
    return m;
}

function buildTraces(d, colors) {
    const traces = [];

    // Compile: solid lines.
    Object.entries(d.compile_series).forEach(([b, s]) => {
        if (!s.cumsum.length) return;
        const fam = familyOf(b);
        const label = s.n_timeout > 0
            ? `${b} compile (${s.n_timeout} t/o)`
            : `${b} compile`;
        traces.push({
            type: 'scatter', mode: 'lines',
            name: label,
            x: s.cumsum.map((_, j) => j + 1),
            y: s.cumsum,
            line: { color: colors[fam], width: 2.2, dash: 'solid' },
            legendgroup: fam,
        });
    });

    // Count: library counter (no `_bin` suffix)    -> dotted
    //        binary counter   (`_bin_count` name)  -> dash-dot
    // This makes the three baselines per family (compile, lib-count,
    // bin-count) visually distinct while still sharing a colour.
    Object.entries(d.count_series).forEach(([b, s]) => {
        if (!s.cumsum.length) return;
        const fam     = familyOf(b);
        const isBin   = b.includes('_bin');
        const dash    = isBin ? 'dashdot' : 'dot';
        const label   = s.n_timeout > 0 ? `${b} (${s.n_timeout} t/o)` : b;
        traces.push({
            type: 'scatter', mode: 'lines',
            name: label,
            x: s.cumsum.map((_, j) => j + 1),
            y: s.cumsum,
            line: { color: colors[fam], width: 2.2, dash },
            legendgroup: fam,
        });
    });

    return traces;
}

export function renderCombined(data) {
    if (!data || !data.combined_cactus) return;
    const d = data.combined_cactus;
    const colors = colorMap(d);
    const traces = buildTraces(d, colors);

    const maxN = Math.max(
        1,
        ...Object.values(d.compile_series).map(s => s.n_solved),
        ...Object.values(d.count_series).map(s => s.n_solved),
    );
    const ticks = axisTicks(maxN);
    const xax = {
        ...baseXAxis(),
        title: 'Instances',
        tickvals: ticks,
        ticktext: ticks.map(String),
    };

    Plotly.react('chart-combined-log', traces, layout({
        title: {
            text: 'All solvers cactus (log).',
            font: { size: 13 },
        },
        xaxis: xax,
        yaxis: { ...baseYAxis(), title: 'Cumulative time (ms)', type: 'log' },
    }), CFG);

    Plotly.react('chart-combined-lin',
        traces.map(t => ({ ...t, showlegend: false })),
        layoutNoLegend({
            title: {
                text: 'All solvers cactus (linear)',
                font: { size: 13 },
            },
            xaxis: xax,
            yaxis: { ...baseYAxis(), title: 'Cumulative time (ms)' },
        }), CFG);
}
