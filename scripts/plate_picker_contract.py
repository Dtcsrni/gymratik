"""Inyecta el selector visual de discos en las cuatro rutinas autocontenidas."""

from __future__ import annotations


STYLE = r'''<style data-enhancement="plate-picker-v1">
.platePickerToggle{display:flex;align-items:center;justify-content:space-between;gap:.65rem;width:100%;min-height:48px;margin-top:.45rem;padding:.55rem .75rem;border:1px solid rgba(105,215,255,.3);border-radius:.7rem;background:linear-gradient(110deg,rgba(14,43,61,.94),rgba(7,28,42,.9));color:#e8faff;font:inherit;font-size:.84rem;font-weight:850;text-align:left;cursor:pointer}
.platePickerToggle:focus-visible,.platePickerOption:focus-visible,.platePickerRemove:focus-visible,.platePickerAction:focus-visible{outline:3px solid #5ce8c8;outline-offset:2px}
.platePickerToggleLabel{display:flex;align-items:center;gap:.5rem}.platePickerToggleTotal{margin-left:auto;color:#5ce8c8;font-size:.8rem;font-weight:950}
.platePicker{display:grid;gap:.6rem;margin-top:.5rem;padding:.65rem;border:1px solid rgba(105,215,255,.26);border-radius:.8rem;background:linear-gradient(145deg,rgba(10,33,48,.98),rgba(5,22,34,.98))}
.platePicker[hidden]{display:none!important}.platePickerHelp{margin:0;color:#a9c3cd;font-size:.7rem;line-height:1.4}
.platePickerSelection{display:grid;gap:.35rem;padding:.55rem;border-radius:.6rem;background:rgba(7,23,36,.72)}
.platePickerSelectionTitle{color:#9fbac5;font-size:.67rem;font-weight:800}.platePickerComposition{min-height:1.25em;color:#e8faff;font-size:.76rem;font-weight:800;overflow-wrap:anywhere}.platePickerTotal{color:#5ce8c8;font-size:1rem;font-weight:950}.platePickerStatus{min-height:1.1em;margin:0;color:#ffcf85;font-size:.68rem;line-height:1.35}
.platePickerUnit{display:grid;gap:.35rem}.platePickerUnitTitle{margin:0;color:#5ce8c8;font-size:.72rem;font-weight:900;letter-spacing:.035em}
.platePickerGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.35rem}
.platePickerItem{position:relative;display:grid;min-width:0;min-height:88px;grid-template-rows:48px auto;justify-items:center;align-items:center;gap:.15rem;padding:.35rem .2rem;border:1px solid rgba(120,163,183,.2);border-radius:.6rem;background:rgba(7,25,39,.6)}
.platePickerOption{display:grid;justify-items:center;align-content:center;gap:.15rem;width:100%;min-width:0;padding:0;border:0;background:transparent;color:#e7f5fa;font:inherit;font-size:.69rem;font-weight:850;cursor:pointer;touch-action:manipulation}
.platePickerOption img{display:block;width:44px;height:44px;object-fit:contain}.platePickerCount{min-height:.9em;color:#5ce8c8;font-size:.62rem;font-weight:900}
.platePickerRemove{position:absolute;top:.15rem;right:.15rem;display:grid;place-items:center;width:28px;height:28px;padding:0;border:1px solid rgba(105,215,255,.22);border-radius:50%;background:#0b2238;color:#cdebf2;font:inherit;font-size:1rem;font-weight:900;cursor:pointer}.platePickerRemove[hidden]{display:none}
.platePickerActions{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:.45rem}.platePickerAction{min-height:42px;padding:.45rem .55rem;border:1px solid rgba(105,215,255,.32);border-radius:.65rem;background:#0b2238;color:#dff7fb;font:inherit;font-size:.75rem;font-weight:850;cursor:pointer}.platePickerActionPrimary{border-color:transparent;background:linear-gradient(100deg,#5ce8c8,#45d4f1);color:#06222b}.platePickerAction:disabled{opacity:.48;cursor:not-allowed}
@media(max-width:360px){.platePickerGrid{grid-template-columns:repeat(3,minmax(0,1fr))}.platePicker{padding:.5rem}.platePickerItem{min-height:82px}}
</style>'''


MARKUP = r'''
    const platePickerToggle = document.createElement('button'); platePickerToggle.type = 'button'; platePickerToggle.className = 'platePickerToggle'; platePickerToggle.setAttribute('aria-expanded', 'false');
    const platePickerLabel = document.createElement('span'); platePickerLabel.className = 'platePickerToggleLabel'; const platePickerIcon = createPerformanceIcon('weight'); if (platePickerIcon) platePickerLabel.append(platePickerIcon); const platePickerTitle = document.createElement('span'); platePickerTitle.textContent = 'Discos'; platePickerLabel.append(platePickerTitle);
    const platePickerHeaderTotal = document.createElement('span'); platePickerHeaderTotal.className = 'platePickerToggleTotal'; platePickerHeaderTotal.textContent = item.performanceLoadSelected ? loadOutput.textContent : 'Elegir'; platePickerToggle.append(platePickerLabel, platePickerHeaderTotal);
    const platePickerPanel = document.createElement('section'); platePickerPanel.className = 'platePicker'; platePickerPanel.hidden = true; platePickerPanel.setAttribute('aria-label', 'Selector de discos'); platePickerPanel.id = `plate-picker-${item.index + 1}`; platePickerToggle.setAttribute('aria-controls', platePickerPanel.id);
    const platePickerHelp = document.createElement('p'); platePickerHelp.className = 'platePickerHelp'; platePickerHelp.textContent = 'Toca un disco para agregarlo. Puedes combinar libras y kilogramos.';
    const platePickerSelection = document.createElement('div'); platePickerSelection.className = 'platePickerSelection'; const platePickerSelectionTitle = document.createElement('span'); platePickerSelectionTitle.className = 'platePickerSelectionTitle'; platePickerSelectionTitle.textContent = 'Discos seleccionados'; const platePickerComposition = document.createElement('output'); platePickerComposition.className = 'platePickerComposition'; platePickerComposition.setAttribute('aria-live', 'polite'); platePickerComposition.textContent = 'Selecciona discos para ver la suma'; const platePickerTotal = document.createElement('output'); platePickerTotal.className = 'platePickerTotal'; platePickerTotal.textContent = '0.0 kg'; const platePickerStatus = document.createElement('p'); platePickerStatus.className = 'platePickerStatus'; platePickerStatus.setAttribute('role', 'status'); platePickerSelection.append(platePickerSelectionTitle, platePickerComposition, platePickerTotal, platePickerStatus);
    const platePickerGrid = document.createElement('div'); platePickerGrid.className = 'platePickerGrid'; const platePickerCounts = new Map();
    const platePickerOptions = [['lb',[45,35,25,20,15,10,5,2.5]],['kg',[25,20,15,10,5,2.5,1.25,0.5,0.25]]];
    platePickerOptions.forEach(([unit,values]) => { const group = document.createElement('section'); group.className = 'platePickerUnit'; const heading = document.createElement('h4'); heading.className = 'platePickerUnitTitle'; heading.textContent = unit === 'lb' ? 'Discos en lb' : 'Discos en kg'; const grid = document.createElement('div'); grid.className = 'platePickerGrid'; values.forEach(weight => { const key = `${unit}:${weight}`; const tile = document.createElement('div'); tile.className = 'platePickerItem'; const add = document.createElement('button'); add.type = 'button'; add.className = 'platePickerOption'; add.setAttribute('aria-label', `Agregar disco de ${weight} ${unit}`); const plateImage = document.createElement('img'); plateImage.src = '../../../assets/branding/gymratik-plate-dark.webp'; plateImage.alt = ''; plateImage.loading = 'lazy'; plateImage.decoding = 'async'; const label = document.createElement('span'); label.textContent = `${weight} ${unit}`; const count = document.createElement('span'); count.className = 'platePickerCount'; add.append(plateImage,label,count); const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'platePickerRemove'; remove.textContent = '−'; remove.hidden = true; remove.setAttribute('aria-label', `Quitar un disco de ${weight} ${unit}`); const renderCount = () => { const amount = platePickerCounts.get(key) || 0; count.textContent = amount ? `×${amount}` : ''; remove.hidden = !amount; add.setAttribute('aria-label', `${amount ? 'Agregar otro' : 'Agregar'} disco de ${weight} ${unit}${amount ? `; seleccionados ${amount}` : ''}`); }; add.addEventListener('click', () => { platePickerCounts.set(key,(platePickerCounts.get(key)||0)+1); renderCount(); renderPlatePicker(); }); remove.addEventListener('click', () => { const amount = (platePickerCounts.get(key)||0)-1; if (amount > 0) platePickerCounts.set(key,amount); else platePickerCounts.delete(key); renderCount(); renderPlatePicker(); }); tile.append(add,remove); grid.append(tile); }); group.append(heading,grid); platePickerGrid.append(group); });
    const platePickerActions = document.createElement('div'); platePickerActions.className = 'platePickerActions'; const platePickerApply = document.createElement('button'); platePickerApply.type = 'button'; platePickerApply.className = 'platePickerAction platePickerActionPrimary'; platePickerApply.textContent = 'Aplicar carga'; platePickerApply.disabled = true; const platePickerClear = document.createElement('button'); platePickerClear.type = 'button'; platePickerClear.className = 'platePickerAction'; platePickerClear.textContent = 'Limpiar selección'; platePickerActions.append(platePickerApply,platePickerClear);
    platePickerPanel.append(platePickerHelp,platePickerSelection,platePickerGrid,platePickerActions); loadLabel.append(platePickerToggle,platePickerPanel);
'''


HANDLERS = r'''
    const renderPlatePicker = () => {
      let totalKg = 0; const parts = [];
      for (const [key,count] of platePickerCounts) { const [unit,raw] = key.split(':'); const weight = Number(raw); totalKg += loadMath.toKg(weight * count, unit); parts.push(`${weight} ${unit} × ${count}`); }
      const displayKg = loadMath.normalizeKg(totalKg, item.performanceLoadProfile); const valid = totalKg > 0 && Number.isFinite(displayKg) && totalKg >= item.performanceLoadProfile.minKg && totalKg <= item.performanceLoadProfile.maxKg;
      platePickerComposition.textContent = parts.length ? parts.join(' + ') : 'Selecciona discos para ver la suma'; platePickerTotal.textContent = `${totalKg.toFixed(1)} kg`; platePickerApply.textContent = `Aplicar ${totalKg.toFixed(1)} kg`; platePickerApply.disabled = !valid;
      platePickerStatus.textContent = totalKg > 0 && !valid ? `La suma debe estar entre ${item.performanceLoadProfile.minKg} y ${item.performanceLoadProfile.maxKg} kg.` : 'El total suma los discos seleccionados; no incluye barra o máquina.';
      platePickerHeaderTotal.textContent = parts.length ? `${totalKg.toFixed(1)} kg` : item.performanceLoadSelected ? loadOutput.textContent : 'Elegir';
    };
    platePickerToggle.addEventListener('click', () => { const open = platePickerPanel.hidden; platePickerPanel.hidden = !open; platePickerToggle.setAttribute('aria-expanded', String(open)); if (open) renderPlatePicker(); });
    platePickerClear.addEventListener('click', () => { platePickerCounts.clear(); platePickerPanel.querySelectorAll('.platePickerCount').forEach(count => { count.textContent = ''; }); platePickerPanel.querySelectorAll('.platePickerRemove').forEach(remove => { remove.hidden = true; }); renderPlatePicker(); });
    const resetPlatePickerDraft = () => { platePickerCounts.clear(); platePickerPanel.querySelectorAll('.platePickerCount').forEach(count => { count.textContent = ''; }); platePickerPanel.querySelectorAll('.platePickerRemove').forEach(remove => { remove.hidden = true; }); renderPlatePicker(); };
    const syncPlatePickerHeader = () => { if (!platePickerCounts.size) platePickerHeaderTotal.textContent = item.performanceLoadSelected ? loadOutput.textContent : 'Elegir'; };
    item.performanceLoad.addEventListener('input', () => { resetPlatePickerDraft(); queueMicrotask(syncPlatePickerHeader); });
    loadUnitSelect.addEventListener('change', () => { resetPlatePickerDraft(); queueMicrotask(syncPlatePickerHeader); });
    loadOutput.addEventListener('click', resetPlatePickerDraft);
    loadLabel.addEventListener('focusout', () => queueMicrotask(syncPlatePickerHeader));
    platePickerApply.addEventListener('click', () => { let totalKg = 0; for (const [key,count] of platePickerCounts) { const [unit,raw] = key.split(':'); totalKg += loadMath.toKg(Number(raw) * count, unit); } if (!Number.isFinite(totalKg) || totalKg <= 0 || totalKg < item.performanceLoadProfile.minKg || totalKg > item.performanceLoadProfile.maxKg) return; const normalizedKg = loadMath.normalizeKg(totalKg, item.performanceLoadProfile); item.performanceLoadExact = loadMath.toDisplay(normalizedKg, item.performanceLoadUnit); item.performanceLoadSelected = true; loadInput.value = String(item.performanceLoadExact); updateLoadControl(); savePerformanceDraft(); platePickerHeaderTotal.textContent = `${normalizedKg.toFixed(1)} kg`; platePickerPanel.hidden = true; platePickerToggle.setAttribute('aria-expanded','false'); });
    item.performanceLoadClear.addEventListener('click', () => { platePickerCounts.clear(); platePickerPanel.querySelectorAll('.platePickerCount').forEach(count => { count.textContent = ''; }); platePickerPanel.querySelectorAll('.platePickerRemove').forEach(remove => { remove.hidden = true; }); renderPlatePicker(); platePickerHeaderTotal.textContent = 'Elegir'; });
'''


def apply_plate_picker_contract(source: str) -> str:
    """Instala estilos y la UI; conserva la carga confirmada en el contrato actual."""
    if 'data-enhancement="plate-picker-v1"' not in source:
        source = source.replace("</head>", STYLE + "\n</head>", 1)
    if "const platePickerCounts = new Map();" not in source:
        anchor = "loadLabel.append(loadHead, loadOutputRow, loadInput);"
        if anchor not in source:
            raise ValueError("No se encontró el selector base de carga para agregar discos")
        source = source.replace(anchor, anchor + MARKUP, 1)
    if "const renderPlatePicker = () => {" not in source:
        anchor = "    const savedReps = Number(savedDraft?.reps);"
        if anchor not in source:
            raise ValueError("No se encontró el guardado del borrador para enlazar el selector de discos")
        source = source.replace(anchor, HANDLERS + "\n" + anchor, 1)
    return source
