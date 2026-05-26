// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Thin wrappers around the /api endpoints so that the rest of the
// frontend never deals with raw fetch calls or URL construction.

async function getJSON(url) {
    const r = await fetch(url);
    if (!r.ok) {
        throw new Error(`${url} -> ${r.status}: ${await r.text()}`);
    }
    return r.json();
}

export async function listExperiments() {
    return getJSON('/api/experiments');
}

export async function fetchResults(expId) {
    return getJSON(`/api/results?exp_id=${encodeURIComponent(expId)}`);
}
