// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Plotly defaults shared by every pane.

export const COLORS = [
    '#3266ad', '#1d9e75', '#d85a30',
    '#d4537e', '#7f77dd', '#ba7517',
];

export const CFG = { responsive: true, displayModeBar: false };

// Base layout for charts that show a legend on the right.
const BASE = {
    margin:        { t: 36, r: 170, b: 52, l: 64 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor:  'rgba(0,0,0,0)',
    font: {
        family: "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",
        size:   12,
        color:  '#444',
    },
    xaxis:  { gridcolor: '#efefed', linecolor: '#ddd', zeroline: false },
    yaxis:  { gridcolor: '#efefed', linecolor: '#ddd', zeroline: false },
    legend: {
        x: 1.02, y: 1,
        xanchor: 'left', yanchor: 'top',
        bgcolor: 'rgba(0,0,0,0)',
        borderwidth: 0,
        font: { size: 12 },
        groupclick: 'toggleitem',
    },
};

/** Merge `overrides` into the legend-on-right base layout. */
export function layout(overrides = {}) {
    return Object.assign({}, BASE, overrides);
}

/** Same, but no legend (used for the linear-scale companion charts). */
export function layoutNoLegend(overrides = {}) {
    return Object.assign(
        {}, BASE,
        { margin: { t: 36, r: 16, b: 52, l: 64 }, showlegend: false },
        overrides,
    );
}

/** Build sane tick values for an x-axis that goes 1..maxN. */
export function axisTicks(maxN) {
    const step = Math.max(1, Math.ceil(maxN / 12));
    const v = [];
    for (let i = step; i <= maxN; i += step) v.push(i);
    return v;
}

/** Convenience: pull the xaxis config from BASE without mutating it. */
export function baseXAxis() { return Object.assign({}, BASE.xaxis); }
export function baseYAxis() { return Object.assign({}, BASE.yaxis); }
