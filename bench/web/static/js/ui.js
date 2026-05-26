// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Generic DOM glue (tab switching, select population, status text).

/** Wire up the tab nav: clicking a `.tab` shows its `#pane-<name>`. */
export function setupTabs(root = document) {
    const tabs  = root.querySelectorAll('#tabs .tab');
    const panes = root.querySelectorAll('.pane');
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            const name = btn.dataset.pane;
            tabs.forEach(b => b.classList.toggle('active', b === btn));
            panes.forEach(p => p.classList.toggle('active', p.id === `pane-${name}`));
        });
    });
}

/**
 * Replace the options of `<select id=...>` with `options`, preserving
 * the previous value if it's still present.
 */
export function populateSelect(id, options) {
    const sel = document.getElementById(id);
    if (!sel) return;
    const prev = sel.value;
    sel.innerHTML = '';
    for (const opt of options) {
        const e = document.createElement('option');
        e.value = opt;
        e.textContent = opt;
        sel.appendChild(e);
    }
    if (options.includes(prev)) sel.value = prev;
}

/** Set the small status string in the header. */
export function setMeta(text) {
    const el = document.getElementById('meta');
    if (el) el.textContent = text;
}

/** Hook up an `onchange` listener on a `<select>` by id. */
export function onSelectChange(id, handler) {
    const sel = document.getElementById(id);
    if (sel) sel.addEventListener('change', handler);
}
