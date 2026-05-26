// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Frontend entry point. Wires together:
//   * the API client (api.js)
//   * generic DOM helpers (ui.js)
//   * the four pane modules:
//       compile_pane, infer_pane, solver_overhead_pane, overhead_pane
//
// Lifecycle:
//   1. on load -> refreshExps() -> fetch /api/experiments, populate the
//      exp picker, then loadData().
//   2. loadData() fetches /api/results?exp_id=... and renders all panes.
//   3. Each pane re-renders on its own when its filter selects change.

import { fetchResults, listExperiments } from './api.js';
import { onSelectChange, populateSelect, setMeta, setupTabs } from './ui.js';
import { renderCompile         } from './compile_pane.js';
import { renderInfer           } from './infer_pane.js';
import { renderSolverOverhead  } from './solver_overhead_pane.js';
import { renderOverhead        } from './overhead_pane.js';
import { renderCombined        } from './combined_pane.js';

let DATA = null;

function renderAll() {
    if (!DATA) return;
    setMeta(
        `${DATA.n_compile} compile · ${DATA.n_count ?? 0} count`
        + ` · ${DATA.n_infer} infer · ${DATA.n_experiment} experiment`
    );
    populateSelect('sel-semiring',    DATA.infer_cactus.semirings);
    populateSelect('sel-oh-semiring', DATA.infer_cactus.semirings);
    populateSelect('sel-oh-device',   DATA.infer_cactus.devices);
    renderCompile(DATA);
    renderInfer(DATA);
    renderSolverOverhead(DATA);
    renderOverhead(DATA);
    renderCombined(DATA);
}

async function loadData() {
    setMeta('loading\u2026');
    const expId = document.getElementById('exp-select').value;
    try {
        DATA = await fetchResults(expId);
        renderAll();
    } catch (e) {
        setMeta('error, see console');
        console.error(e);
    }
}

async function refreshExps() {
    try {
        const ids = await listExperiments();
        const sel = document.getElementById('exp-select');
        const prev = sel.value;
        sel.innerHTML = ids
            .map(id => `<option value="${id}">exp${String(id).padStart(4, '0')}</option>`)
            .join('');
        sel.value = ids.map(String).includes(prev) ? prev : ids[ids.length - 1];
        await loadData();
    } catch (e) {
        console.error(e);
    }
}

setupTabs();

document.getElementById('exp-select').addEventListener('change', loadData);
document.getElementById('refresh-btn').addEventListener('click', refreshExps);

onSelectChange('sel-semiring',        () => renderInfer(DATA));
onSelectChange('sel-pass',            () => renderInfer(DATA));
onSelectChange('sel-solver-backend',  () => renderSolverOverhead(DATA));
onSelectChange('sel-solver-view',     () => renderSolverOverhead(DATA));
onSelectChange('sel-oh-semiring',     () => renderOverhead(DATA));
onSelectChange('sel-oh-device',       () => renderOverhead(DATA));

refreshExps();
