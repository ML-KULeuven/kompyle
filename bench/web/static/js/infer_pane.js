// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Inference pane
// Cactus of forward (or forward+backward) latency,
// one trace per (backend x device).

import {
    COLORS, CFG, layout, layoutNoLegend,
    axisTicks, baseXAxis, baseYAxis,
} from './plotly_config.js';

/** Pick the right cumsum array for the current pass selection. */
function passSeries(s, pass) {
    return pass === 'forward' ? s.forward_cumsum : s.backward_cumsum;
}

/**
 * Build the (series, color, name, dash) tuples for the current
 * filter combo. Backends get assigned a color index by sort order;
 * CUDA traces share the backend color but with dashed stroke.
 */
function buildItems(d, semiring) {
    const backends = [...new Set(Object.values(d.series).map(s => s.backend))].sort();
    const items = [];
    backends.forEach((b, bi) => {
        ['cpu', 'cuda'].forEach(dev => {
            const s = d.series[`${b}/${semiring}/${dev}`];
            if (!s) return;
            items.push({
                s,
                color: COLORS[bi % COLORS.length],
                name:  `${b} (${dev})`,
                dash:  dev === 'cuda' ? 'dash' : 'solid',
            });
        });
    });
    return items;
}

function buildTraces(items, pass, showlegend) {
    return items.map(({ s, color, name, dash }) => {
        const vals = passSeries(s, pass);
        if (!vals?.length) return null;
        return {
            type: 'scatter',
            mode: 'lines',
            name,
            showlegend,
            x:    vals.map((_, i) => i + 1),
            y:    vals,
            line: { color, dash, width: 2.2 },
        };
    }).filter(Boolean);
}

export function renderInfer(data) {
    if (!data) return;
    const semiring = document.getElementById('sel-semiring').value;
    const pass     = document.getElementById('sel-pass').value;

    const items = buildItems(data.infer_cactus, semiring);
    const maxN  = Math.max(1, ...items.map(({ s }) => passSeries(s, pass)?.length || 0));
    const ticks = axisTicks(maxN);
    const xax   = { ...baseXAxis(), title: 'Instances', tickvals: ticks, ticktext: ticks.map(String) };

    Plotly.react('chart-infer-log', buildTraces(items, pass, true), layout({
        title: { text: 'Inference cactus (log scale)', font: { size: 13 } },
        xaxis: xax,
        yaxis: { ...baseYAxis(), title: 'Cumulative time (s)', type: 'log' },
    }), CFG);

    Plotly.react('chart-infer-lin', buildTraces(items, pass, false), layoutNoLegend({
        title: { text: 'Inference cactus (linear scale)', font: { size: 13 } },
        xaxis: xax,
        yaxis: { ...baseYAxis(), title: 'Cumulative time (s)' },
    }), CFG);
}
