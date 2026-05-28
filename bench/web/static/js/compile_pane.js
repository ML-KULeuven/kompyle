// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
//  * cactus, log scale
//  * cactus, linear
//  * circuit-nodes per backend
//  * sparsity per backend

import {
    COLORS, CFG, layout, layoutNoLegend,
    axisTicks, baseXAxis, baseYAxis,
} from './plotly_config.js';

function compileCactusTraces(d) {
    const backends = Object.keys(d.series);
    return backends.map((b, i) => {
        const s = d.series[b];
        if (!s.cumsum.length) return null;
        const label = s.n_failed > 0 ? `${b} (${s.n_failed} t/o)` : b;
        return {
            type: 'scatter',
            mode: 'lines',
            name: label,
            x:    s.cumsum.map((_, j) => j + 1),
            y:    s.cumsum,
            line: { color: COLORS[i % COLORS.length], width: 2.2 },
        };
    }).filter(Boolean);
}

function renderCompileCactus(d) {
    const traces = compileCactusTraces(d);
    const maxN = Math.max(1, ...Object.values(d.series).map(s => s.n_solved));
    const ticks = axisTicks(maxN);
    const xax = { ...baseXAxis(), title: 'Instances', tickvals: ticks, ticktext: ticks.map(String) };

    Plotly.react('chart-compile-log', traces, layout({
        title: { text: 'Compile time cactus (log scale)', font: { size: 13 } },
        xaxis: xax,
        yaxis: { ...baseYAxis(), title: 'Cumulative time (s)', type: 'log' },
    }), CFG);

    Plotly.react('chart-compile-lin',
        traces.map(t => ({ ...t, showlegend: false })),
        layoutNoLegend({
            title: { text: 'Compile time cactus (linear scale)', font: { size: 13 } },
            xaxis: xax,
            yaxis: { ...baseYAxis(), title: 'Cumulative time (s)' },
        }), CFG);
}

function renderInstanceProfile(p) {
    const lineTrace = (name, values, i, opts = {}) => ({
        type: 'scatter',
        mode: 'lines',
        name,
        x:    values.map((_, j) => j + 1),
        y:    values,
        line: { color: COLORS[i % COLORS.length], width: 2 },
        ...opts,
    });

    const nodeTraces = p.backends
        .filter(b => p.nodes_by_backend[b]?.length)
        .map((b, i) => lineTrace(b, p.nodes_by_backend[b], i));
    Plotly.react('chart-nodes', nodeTraces, layout({
        title: { text: 'Nb of nodes (sorted)', font: { size: 13 } },
        margin: { t: 36, r: 130, b: 48, l: 64 },
        xaxis: { ...baseXAxis(), title: 'Instances' },
        yaxis: { ...baseYAxis(), title: 'Nb of nodes', type: 'log' },
    }), CFG);

    const spTraces = p.backends
        .filter(b => p.sparsity_by_backend[b]?.length)
        .map((b, i) => lineTrace(b, p.sparsity_by_backend[b], i, { showlegend: false }));
    Plotly.react('chart-sparsity', spTraces, layoutNoLegend({
        title: { text: 'Sparsity (sorted descending)', font: { size: 13 } },
        margin: { t: 36, r: 16, b: 48, l: 64 },
        xaxis: { ...baseXAxis(), title: 'Instances' },
        yaxis: { ...baseYAxis(), title: 'Sparsity', type: 'log' },
    }), CFG);
}

export function renderCompile(data) {
    if (!data) return;
    if (data.combined_cactus) {
        renderCompileCactus({
            series:   data.combined_cactus.compile_series,
            backends: data.combined_cactus.compile_backends,
        });
    }
    if (data.instance_profile) renderInstanceProfile(data.instance_profile);
}
