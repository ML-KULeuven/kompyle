// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Overhead pane 
// A single bar chart of relay-layer fraction per backend,
// filtered by the (semiring, device).

import { CFG, layout, baseYAxis } from './plotly_config.js';

const RELAY_COLOR = '#3266ad';

/** Convert a list of 0..1 fractions into rounded percent values. */
function toPercent(arr, indices) {
    return indices.map(idx => {
        const v = arr[idx];
        return v != null ? +(v * 100).toFixed(1) : null;
    });
}

export function renderOverhead(data) {
    if (!data) return;
    const d = data.exp_chart;
    const semiring = document.getElementById('sel-oh-semiring').value;
    const device   = document.getElementById('sel-oh-device').value;
    const suffix   = `<br>${semiring}/${device}`;

    const matched = d.keys
        .map((k, i) => ({ k, i }))
        .filter(({ k }) => k.endsWith(suffix));
    const labels  = matched.map(({ k }) => k.replace(suffix, ''));
    const indices = matched.map(({ i }) => i);

    Plotly.react('chart-oh-fractions', [{
        type:   'bar',
        name:   'relay layer %',
        x:      labels,
        y:      toPercent(d.relay_fraction, indices),
        marker: { color: RELAY_COLOR },
    }], layout({
        barmode: 'group',
        margin:  { t: 36, r: 170, b: 48, l: 56 },
        title:   { text: `Overhead fractions:  ${semiring}, ${device}`, font: { size: 13 } },
        yaxis:   { ...baseYAxis(), title: '%', rangemode: 'tozero', ticksuffix: '%' },
    }), CFG);
}
