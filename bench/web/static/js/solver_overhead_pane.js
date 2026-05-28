// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Solver-overhead pane.
//
// For each compile backend X and its count-only partner X_count we have
// a joined set of instances both solved. Three views:
//   * cactus:    cumsum of count_s vs compile_s (sorted within each)
//   * overhead:  per-instance (compile − count) in seconds, sorted asc
//   * ratio:     per-instance (compile / count), sorted asc

import {
    COLORS, CFG, layout, baseXAxis, baseYAxis,
} from './plotly_config.js';

const COMPILE_COLOR = COLORS[0];
const COUNT_COLOR   = COLORS[1];

// ---------------------------------------------------
// Renderers, one per view mode.
// ---------------------------------------------------

function renderCactus(pair) {
    const xCompile = pair.compile_cumsum.map((_, i) => i + 1);
    const xCount   = pair.count_cumsum.map((_, i) => i + 1);

    Plotly.react('chart-solver-main', [
        {
            type: 'scatter', mode: 'lines',
            name: `${pair.compile_backend} (compile)`,
            x: xCompile, y: pair.compile_cumsum,
            line: { color: COMPILE_COLOR, width: 2.2 },
        },
        {
            type: 'scatter', mode: 'lines',
            name: `${pair.count_backend} (count)`,
            x: xCount, y: pair.count_cumsum,
            line: { color: COUNT_COLOR, width: 2.2 },
        },
    ], layout({
        title: { text: `Compile vs count cactus: ${pair.compile_backend}  (n=${pair.n_pairs})`, font: { size: 13 } },
        xaxis: { ...baseXAxis(), title: 'Instances' },
        yaxis: { ...baseYAxis(), title: 'Cumulative time (s)', type: 'log' },
    }), CFG);
}


function renderOverhead(pair) {
    const x = pair.overhead_s.map((_, i) => i + 1);
    Plotly.react('chart-solver-main', [{
        type: 'scatter', mode: 'lines',
        name: `${pair.compile_backend} − ${pair.count_backend}`,
        x, y: pair.overhead_s,
        line: { color: COMPILE_COLOR, width: 2.2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(50,102,173,0.10)',
    }], layout({
        title: { text: `Per-instance circuit-construction overhead: ${pair.compile_backend}  (n=${pair.n_pairs})`, font: { size: 13 } },
        xaxis: { ...baseXAxis(), title: 'Instances (sorted)' },
        yaxis: { ...baseYAxis(), title: 'compile - count  (s)' },
    }), CFG);
}


function renderRatio(pair) {
    const x = pair.ratios.map((_, i) => i + 1);
    Plotly.react('chart-solver-main', [
        {
            type: 'scatter', mode: 'lines',
            name: `${pair.compile_backend} / ${pair.count_backend}`,
            x, y: pair.ratios,
            line: { color: COMPILE_COLOR, width: 2.2 },
        },
        // y=1 reference line: compile time equals count time
        {
            type: 'scatter', mode: 'lines',
            name: 'no overhead (y=1)',
            x, y: x.map(() => 1),
            line: { color: '#bbb', width: 1, dash: 'dot' },
            showlegend: true,
        },
    ], layout({
        title: { text: `Compile / count ratio: ${pair.compile_backend}  (n=${pair.n_pairs})`, font: { size: 13 } },
        xaxis: { ...baseXAxis(), title: 'Instances (sorted)' },
        yaxis: { ...baseYAxis(), title: 'compile_s / count_s', type: 'log' },
    }), CFG);
}


// ---------------------------------------------------
// Cross-backend summary table
// ---------------------------------------------------

function median(xs) {
    if (!xs.length) return null;
    const sorted = [...xs].sort((a, b) => a - b);
    const m = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2;
}

function mean(xs) {
    return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
}

function renderSummary(pairs) {
    const rows = Object.values(pairs).map(p => ({
        backend:     p.compile_backend,
        n:           p.n_pairs,
        ovh_med_s:   median(p.overhead_s),
        ovh_mean_s:  mean(p.overhead_s),
        ratio_med:   median(p.ratios),
        ratio_mean:  mean(p.ratios),
    }));
    rows.sort((a, b) => (b.ratio_med ?? 0) - (a.ratio_med ?? 0));

    const fmtS = v => v == null ? ':' : v.toFixed(3);
    const fmtR = v => v == null ? ':' : v.toFixed(2) + '×';

    const tableHtml = `
        <table class="summary-table">
            <thead>
                <tr>
                    <th>backend</th>
                    <th>n</th>
                    <th>overhead (s)<br>median</th>
                    <th>overhead (s)<br>mean</th>
                    <th>ratio<br>median</th>
                    <th>ratio<br>mean</th>
                </tr>
            </thead>
            <tbody>
                ${rows.map(r => `
                    <tr>
                        <td>${r.backend}</td>
                        <td>${r.n}</td>
                        <td>${fmtS(r.ovh_med_s)}</td>
                        <td>${fmtS(r.ovh_mean_s)}</td>
                        <td>${fmtR(r.ratio_med)}</td>
                        <td>${fmtR(r.ratio_mean)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    document.getElementById('chart-solver-table').innerHTML = tableHtml;
}

// ---------------------------------------------------
// Entry point.
// ---------------------------------------------------

const VIEWS = {
    cactus:   renderCactus,
    overhead: renderOverhead,
    ratio:    renderRatio,
};


/** Populate the backend select with the count backends available. */
function populateBackendSelect(pairs) {
    const sel = document.getElementById('sel-solver-backend');
    const keys = Object.keys(pairs);
    const prev = sel.value;
    sel.innerHTML = keys
        .map(k => `<option value="${k}">${pairs[k].compile_backend}</option>`)
        .join('');
    sel.value = keys.includes(prev) ? prev : (keys[0] || '');
}


export function renderSolverOverhead(data) {
    if (!data || !data.solver_overhead) return;
    const pairs = data.solver_overhead.pairs;

    populateBackendSelect(pairs);
    renderSummary(pairs);

    const backendKey = document.getElementById('sel-solver-backend').value;
    const view       = document.getElementById('sel-solver-view').value;
    const pair       = pairs[backendKey];

    if (!pair) {
        Plotly.react('chart-solver-main', [], layout({
            title: { text: 'No compile / count overlap yet, run both stages on the same instances.', font: { size: 13 } },
        }), CFG);
        return;
    }
    (VIEWS[view] || renderCactus)(pair);
}
