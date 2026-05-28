// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

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
    const meta = DATA.meta;
    const metaParts = [
        `${DATA.n_compile} compile   ${DATA.n_count ?? 0} count`
        + `   ${DATA.n_infer} infer   ${DATA.n_experiment} experiment`,
    ];
    if (meta) {
        const desc = Object.entries(meta)
            .map(([k, v]) => `${k}: ${v}`)
            .join('   ');
        if (desc) metaParts.push(desc);
    }
    setMeta(metaParts.join('   |   '));
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
    setMeta('loading...');
    const expName = document.getElementById('exp-select').value;
    try {
        DATA = await fetchResults(expName);
        renderAll();
    } catch (e) {
        setMeta('error, see console');
        console.error(e);
    }
}

async function refreshExps() {
    try {
        const names = await listExperiments();
        const sel = document.getElementById('exp-select');
        const prev = sel.value;
        sel.innerHTML = names
            .map(name => `<option value="${name}">${name}</option>`)
            .join('');
        sel.value = names.includes(prev) ? prev : (names[names.length - 1] ?? '');
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
