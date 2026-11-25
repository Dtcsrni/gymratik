"""Inyecta el selector visual de discos en las cuatro rutinas autocontenidas."""

from __future__ import annotations

import re


STYLE = r'''<style data-enhancement="plate-picker-v1">
.platePickerToggle{display:flex;align-items:center;justify-content:space-between;gap:.65rem;width:100%;min-height:50px;margin-top:.45rem;padding:.62rem .75rem;border:1px solid rgba(105,215,255,.42);border-radius:.8rem;background:linear-gradient(110deg,rgba(14,50,68,.98),rgba(7,28,42,.98));color:#e8faff;font:inherit;font-size:.88rem;font-weight:900;text-align:left;cursor:pointer;box-shadow:inset 0 1px rgba(255,255,255,.05)}
.platePickerToggle:focus-visible,.platePickerOption:focus-visible,.platePickerRemove:focus-visible,.platePickerAction:focus-visible{outline:3px solid #5ce8c8;outline-offset:2px}
.platePickerToggleLabel{display:flex;align-items:center;gap:.5rem}.platePickerToggleTotal{margin-left:auto;color:#70f1d7;font-size:.86rem;font-weight:950;font-variant-numeric:tabular-nums}
.platePicker,.platePicker *{box-sizing:border-box}.platePicker{display:grid;gap:.65rem;margin-top:.55rem;padding:.72rem;border:1px solid rgba(105,215,255,.34);border-radius:.9rem;background:radial-gradient(ellipse at 100% 0,rgba(30,120,145,.16),transparent 44%),linear-gradient(145deg,rgba(10,33,48,.99),rgba(5,22,34,.99));box-shadow:0 12px 28px rgba(0,0,0,.24),inset 0 1px rgba(255,255,255,.035)}
.platePicker[hidden]{display:none!important}.platePickerHelp{margin:0;color:#c1d9e3;font-size:.76rem;font-weight:700;line-height:1.38}
.platePickerSelection{display:grid;grid-template-columns:minmax(0,1fr);gap:.38rem;padding:.72rem;border:1px solid rgba(101,242,221,.35);border-radius:.78rem;background:linear-gradient(125deg,rgba(9,46,57,.98),rgba(7,27,41,.98));box-shadow:inset 0 1px rgba(255,255,255,.045)}
.platePickerSelectionTitle{color:#a6c7d2;font-size:.68rem;font-weight:950;letter-spacing:.1em;text-transform:uppercase}.platePickerComposition{min-height:1.3em;color:#f1fcff;font-size:.84rem;font-weight:850;line-height:1.35;overflow-wrap:anywhere}.platePickerTotal{color:#77f4dc;font-size:1.05rem;font-weight:1000;font-variant-numeric:tabular-nums;line-height:1.2}.platePickerTransfer{color:#d5eef3;font-size:.77rem;font-weight:850;line-height:1.35}.platePickerStatus{min-height:1.1em;margin:0;color:#ffda91;font-size:.72rem;font-weight:750;line-height:1.35}
.platePicker .platePickerUnits{display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:.7rem;width:100%!important;min-width:0;min-height:0}.platePicker .platePickerUnit{display:grid!important;grid-template-columns:minmax(0,1fr)!important;gap:.4rem;width:100%!important;min-width:0}.platePickerUnitTitle{margin:0;color:#5ce8c8;font-size:.78rem;font-weight:950;letter-spacing:.035em}
.platePicker .platePickerGrid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:.42rem;width:100%!important;min-width:0}
.platePicker .platePickerItem{position:relative;display:grid;min-width:0;min-height:100px;grid-template-rows:1fr;justify-items:stretch;align-items:stretch;gap:0;padding:.18rem;border:1px solid rgba(120,163,183,.34);border-radius:.8rem;background:linear-gradient(155deg,rgba(16,51,68,.98),rgba(6,24,38,.99));box-shadow:inset 0 1px rgba(255,255,255,.05);transition:border-color .16s ease,background .16s ease,transform .16s ease}
.platePicker .platePickerItem[data-selected="true"]{border-color:rgba(101,242,221,.76);background:linear-gradient(155deg,rgba(13,74,77,.98),rgba(7,34,45,.99));box-shadow:0 0 0 1px rgba(101,242,221,.13),inset 0 1px rgba(255,255,255,.08)}
.platePicker .platePickerOption{position:relative;display:grid!important;grid-template-rows:64px auto;justify-items:center;align-content:center;align-items:center;gap:.25rem;width:100%;min-width:0;min-height:94px;padding:.16rem .08rem;border:0;border-radius:.65rem;background:transparent;color:#fff;font:inherit;cursor:pointer;touch-action:manipulation}
.platePicker .platePickerOption:active{transform:scale(.96)}.platePicker .platePickerOption::after{content:"+";position:absolute;top:0;right:0;display:grid;place-items:center;width:24px;height:24px;border:1px solid rgba(112,241,215,.55);border-radius:50%;background:#103749;color:#afffee;font-size:1rem;font-weight:950;line-height:1}
.platePickerDiscFace{display:flex;flex-direction:column;align-items:center;justify-content:center;width:var(--plate-size,50px);height:var(--plate-size,50px);flex:none;border:3px solid #72e5ed;border-radius:50%;background:radial-gradient(circle at 50% 50%,#d7fff4 0 8%,#1a5668 10% 17%,#10384c 19% 58%,#39b7c4 61% 69%,#0a293a 72% 100%);box-shadow:inset 0 0 0 2px rgba(4,18,30,.74),0 2px 8px rgba(0,0,0,.35),0 0 12px rgba(80,218,226,.18);color:#fff;transition:width .18s ease,height .18s ease,transform .18s ease}
.platePickerDiscValue{font-size:.75rem;font-weight:1000;line-height:1;text-shadow:0 1px 3px #061b29;white-space:nowrap}.platePickerDiscUnit{margin-top:2px;color:#bafff1;font-size:.52rem;font-weight:950;letter-spacing:.04em;line-height:1;text-transform:uppercase;white-space:nowrap}
.platePickerDiscFace[data-unit="lb"]{border-color:#8cc6ff;background:radial-gradient(circle at 50% 50%,#e6f4ff 0 8%,#326c9d 10% 17%,#153e60 19% 58%,#579bdb 61% 69%,#0a293a 72% 100%)}.platePickerDiscFace[data-unit="lb"] .platePickerDiscUnit{color:#d8edff}
.platePicker .platePickerCount{min-height:1em;padding:.08rem .2rem;border-radius:999px;background:rgba(101,242,221,.1);color:#8ff8e3;font-size:.66rem;font-weight:950;line-height:1;white-space:nowrap}.platePickerRemove{position:absolute;z-index:2;top:.2rem;left:.2rem;display:grid;place-items:center;width:26px;height:26px;padding:0;border:1px solid rgba(255,214,145,.52);border-radius:50%;background:rgba(63,43,18,.96);color:#ffe3aa;font:inherit;font-size:1rem;font-weight:950;cursor:pointer}.platePickerRemove[hidden]{display:none}
.platePickerActions{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,.8fr);gap:.48rem}.platePickerAction{min-height:48px;padding:.48rem .55rem;border:1px solid rgba(105,215,255,.4);border-radius:.72rem;background:linear-gradient(145deg,#0e2c40,#0a2133);color:#e2f7fd;font:inherit;font-size:.78rem;font-weight:900;line-height:1.18;cursor:pointer}.platePickerActionPrimary{border-color:transparent;background:linear-gradient(105deg,#63edd2,#58d8f0);color:#06222b;box-shadow:0 5px 16px rgba(51,215,194,.14)}.platePickerAction:disabled{opacity:.48;cursor:not-allowed}.platePickerAction:not(:disabled):active{transform:translateY(1px) scale(.99)}
@media(max-width:680px){.platePicker{max-height:min(62vh,560px);max-height:min(62svh,560px);grid-template-rows:auto auto minmax(0,1fr) auto;overflow:hidden}.platePickerUnits{min-height:0;overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin;scrollbar-color:rgba(105,215,255,.4) transparent}}
@media(min-width:390px) and (min-height:800px) and (max-width:680px){.platePicker{max-height:min(52vh,480px);max-height:min(52svh,480px)}}
@media(max-width:360px){.platePicker .platePickerGrid{grid-template-columns:repeat(3,minmax(0,1fr))!important}.platePicker{padding:.55rem}.platePicker .platePickerItem{min-height:96px}.platePicker .platePickerOption{grid-template-rows:64px auto;min-height:90px}.platePickerActions{grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr)}}
</style>'''


MARKUP = r'''
    const platePickerToggle = document.createElement('button'); platePickerToggle.type = 'button'; platePickerToggle.className = 'platePickerToggle'; platePickerToggle.setAttribute('aria-expanded', 'false');
    const platePickerLabel = document.createElement('span'); platePickerLabel.className = 'platePickerToggleLabel'; const platePickerIcon = createPerformanceIcon('weight'); if (platePickerIcon) platePickerLabel.append(platePickerIcon); const platePickerTitle = document.createElement('span'); platePickerTitle.textContent = 'Discos'; platePickerLabel.append(platePickerTitle);
    const platePickerHeaderTotal = document.createElement('span'); platePickerHeaderTotal.className = 'platePickerToggleTotal'; platePickerHeaderTotal.textContent = item.performanceLoadSelected ? loadOutput.textContent : 'Elegir'; platePickerToggle.append(platePickerLabel, platePickerHeaderTotal);
    const platePickerPanel = document.createElement('section'); platePickerPanel.className = 'platePicker'; platePickerPanel.hidden = true; platePickerPanel.setAttribute('aria-label', 'Selector de discos'); platePickerPanel.id = `plate-picker-${item.index + 1}`; platePickerToggle.setAttribute('aria-controls', platePickerPanel.id);
    const platePickerHelp = document.createElement('p'); platePickerHelp.className = 'platePickerHelp'; platePickerHelp.textContent = 'Toca + para añadir una pieza; usa − para quitarla. Puedes mezclar kg y lb.';
    const platePickerSelection = document.createElement('div'); platePickerSelection.className = 'platePickerSelection'; const platePickerSelectionTitle = document.createElement('span'); platePickerSelectionTitle.className = 'platePickerSelectionTitle'; platePickerSelectionTitle.textContent = 'Suma de discos'; const platePickerTotal = document.createElement('output'); platePickerTotal.className = 'platePickerTotal'; platePickerTotal.setAttribute('aria-live', 'polite'); platePickerTotal.textContent = '0 kg · 0 lb'; const platePickerComposition = document.createElement('output'); platePickerComposition.className = 'platePickerComposition'; platePickerComposition.textContent = 'Aún no hay discos añadidos.'; const platePickerTransfer = document.createElement('span'); platePickerTransfer.className = 'platePickerTransfer'; platePickerTransfer.textContent = 'La suma se transferirá al selector Carga.'; const platePickerStatus = document.createElement('p'); platePickerStatus.className = 'platePickerStatus'; platePickerStatus.setAttribute('role', 'status'); platePickerSelection.append(platePickerSelectionTitle, platePickerTotal, platePickerComposition, platePickerTransfer, platePickerStatus);
    const platePickerGroups = document.createElement('div'); platePickerGroups.className = 'platePickerUnits'; const platePickerCounts = new Map();
    const platePickerOptions = [['lb',[45,35,25,20,15,10,5,2.5]],['kg',[25,20,15,10,5,2.5,1.25,0.5,0.25]]];
    platePickerOptions.forEach(([unit,values]) => { const group = document.createElement('section'); group.className = 'platePickerUnit'; const heading = document.createElement('h4'); heading.className = 'platePickerUnitTitle'; heading.textContent = unit === 'lb' ? 'Discos · libras (lb)' : 'Discos · kilogramos (kg)'; const grid = document.createElement('div'); grid.className = 'platePickerGrid'; values.forEach(weight => { const key = `${unit}:${weight}`; const tile = document.createElement('div'); tile.className = 'platePickerItem'; tile.dataset.weight = String(weight); tile.dataset.unit = unit; tile.dataset.selected = 'false'; const plateKg = loadMath.toKg(weight, unit); const minRoot = Math.sqrt(0.25); const maxRoot = Math.sqrt(25); const plateSize = 34 + 28 * Math.max(0,Math.min(1,(Math.sqrt(plateKg)-minRoot)/(maxRoot-minRoot))); tile.style.setProperty('--plate-size',`${plateSize.toFixed(1)}px`); const add = document.createElement('button'); add.type = 'button'; add.className = 'platePickerOption'; add.setAttribute('aria-label', `Agregar disco de ${weight} ${unit}`); const face = document.createElement('span'); face.className = 'platePickerDiscFace'; face.dataset.unit = unit; face.setAttribute('aria-hidden','true'); const faceValue = document.createElement('strong'); faceValue.className = 'platePickerDiscValue'; faceValue.textContent = String(weight); const faceUnit = document.createElement('span'); faceUnit.className = 'platePickerDiscUnit'; faceUnit.textContent = unit; face.append(faceValue,faceUnit); const count = document.createElement('span'); count.className = 'platePickerCount'; count.textContent = 'Añadir'; add.append(face,count); const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'platePickerRemove'; remove.textContent = '−'; remove.hidden = true; remove.setAttribute('aria-label', `Quitar un disco de ${weight} ${unit}`); const renderCount = () => { const amount = platePickerCounts.get(key) || 0; tile.dataset.selected = String(amount > 0); count.textContent = amount ? `×${amount} · añadir` : 'Añadir'; remove.hidden = !amount; add.setAttribute('aria-label', `${amount ? 'Agregar otro' : 'Agregar'} disco de ${weight} ${unit}${amount ? `; seleccionados ${amount}` : ''}`); }; add.addEventListener('click', () => { platePickerCounts.set(key,(platePickerCounts.get(key)||0)+1); renderCount(); renderPlatePicker(); }); remove.addEventListener('click', () => { const amount = (platePickerCounts.get(key)||0)-1; if (amount > 0) platePickerCounts.set(key,amount); else platePickerCounts.delete(key); renderCount(); renderPlatePicker(); }); tile.append(add,remove); grid.append(tile); }); group.append(heading,grid); platePickerGroups.append(group); });
    const platePickerActions = document.createElement('div'); platePickerActions.className = 'platePickerActions'; const platePickerApply = document.createElement('button'); platePickerApply.type = 'button'; platePickerApply.className = 'platePickerAction platePickerActionPrimary'; platePickerApply.textContent = 'Añade discos para aplicar'; platePickerApply.disabled = true; const platePickerClear = document.createElement('button'); platePickerClear.type = 'button'; platePickerClear.className = 'platePickerAction'; platePickerClear.textContent = 'Vaciar discos'; platePickerActions.append(platePickerApply,platePickerClear);
    platePickerPanel.append(platePickerHelp,platePickerSelection,platePickerGroups,platePickerActions); loadLabel.append(platePickerToggle,platePickerPanel);
'''


HANDLERS = r'''
    const formatPlateValue = value => {
      const rounded = Math.round((Number(value) + Number.EPSILON) * 100) / 100;
      return String(rounded);
    };
    const renderPlatePicker = () => {
      let totalKg = 0; const pieces = [];
      for (const [key,count] of platePickerCounts) { const [unit,raw] = key.split(':'); const weight = Number(raw); totalKg += loadMath.toKg(weight * count, unit); pieces.push(`${count} × ${weight} ${unit}`); }
      totalKg = Math.round(totalKg * 1000000) / 1000000;
      const totalLb = loadMath.toDisplay(totalKg, 'lb');
      const valid = totalKg > 0 && Number.isFinite(totalKg) && totalKg >= item.performanceLoadProfile.minKg && totalKg <= item.performanceLoadProfile.maxKg;
      const targetUnit = item.performanceLoadUnit === 'lb' ? 'lb' : 'kg';
      const appliedValue = valid ? loadMath.toDisplay(totalKg, targetUnit) : NaN;
      const transferText = Number.isFinite(appliedValue) ? `${formatPlateValue(appliedValue)} ${targetUnit}` : '—';
      platePickerComposition.textContent = pieces.length ? pieces.join('  ·  ') : 'Aún no hay discos añadidos.';
      platePickerTotal.textContent = `${formatPlateValue(totalKg)} kg · ${formatPlateValue(totalLb)} lb`;
      platePickerTransfer.textContent = pieces.length ? `Carga recibirá ${transferText}.` : 'La suma se transferirá al selector Carga.';
      platePickerApply.textContent = valid ? `Usar ${transferText} en Carga` : pieces.length ? 'Revisa el rango de carga' : 'Añade discos para aplicar';
      platePickerApply.disabled = !valid;
      platePickerStatus.textContent = !pieces.length ? 'Agrega una o más piezas para habilitar el traspaso.' : !valid ? `Fuera del rango de este ejercicio (${item.performanceLoadProfile.minKg}–${item.performanceLoadProfile.maxKg} kg).` : 'Cuenta las piezas elegidas; no incluye barra ni máquina.';
      platePickerHeaderTotal.textContent = pieces.length && Number.isFinite(appliedValue) ? transferText : item.performanceLoadSelected ? loadOutput.textContent : 'Elegir';
    };
    const fitPlatePickerAboveSessionBar = () => requestAnimationFrame(() => { const bar = document.getElementById('floatingSessionSummary'); if (!bar || getComputedStyle(bar).position !== 'fixed') return; const panelBox = platePickerPanel.getBoundingClientRect(); const safeBottom = bar.getBoundingClientRect().top - 10; const overflow = panelBox.bottom - safeBottom; const scrollRoom = Math.max(0, panelBox.top - 12); if (overflow > 0 && scrollRoom > 0) window.scrollBy({top: Math.min(overflow, scrollRoom), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'}); });
    platePickerToggle.addEventListener('click', () => { const open = platePickerPanel.hidden; platePickerPanel.hidden = !open; platePickerToggle.setAttribute('aria-expanded', String(open)); if (open) { renderPlatePicker(); fitPlatePickerAboveSessionBar(); } });
    const clearPlatePickerCounts = () => { platePickerCounts.clear(); platePickerPanel.querySelectorAll('.platePickerItem').forEach(tile => { tile.dataset.selected = 'false'; }); platePickerPanel.querySelectorAll('.platePickerCount').forEach(count => { count.textContent = 'Añadir'; }); platePickerPanel.querySelectorAll('.platePickerRemove').forEach(remove => { remove.hidden = true; }); renderPlatePicker(); };
    platePickerClear.addEventListener('click', clearPlatePickerCounts);
    const resetPlatePickerDraft = clearPlatePickerCounts;
    const syncPlatePickerHeader = () => { if (!platePickerCounts.size) platePickerHeaderTotal.textContent = item.performanceLoadSelected ? loadOutput.textContent : 'Elegir'; };
    item.performanceLoad.addEventListener('input', () => { resetPlatePickerDraft(); queueMicrotask(syncPlatePickerHeader); });
    loadUnitSelect.addEventListener('change', () => queueMicrotask(() => { renderPlatePicker(); syncPlatePickerHeader(); }));
    loadOutput.addEventListener('click', resetPlatePickerDraft);
    loadLabel.addEventListener('focusout', () => queueMicrotask(syncPlatePickerHeader));
    platePickerApply.addEventListener('click', () => { let totalKg = 0; for (const [key,count] of platePickerCounts) { const [unit,raw] = key.split(':'); totalKg += loadMath.toKg(Number(raw) * count, unit); } totalKg = Math.round(totalKg * 1000000) / 1000000; if (!Number.isFinite(totalKg) || totalKg <= 0 || totalKg < item.performanceLoadProfile.minKg || totalKg > item.performanceLoadProfile.maxKg) return; item.platePickerExactLoadKg = totalKg; item.performanceLoadExact = loadMath.toDisplay(totalKg, item.performanceLoadUnit); item.performanceLoadSelected = true; loadInput.value = String(item.performanceLoadExact); updateLoadControl(); savePerformanceDraft(); platePickerHeaderTotal.textContent = loadOutput.textContent; platePickerPanel.hidden = true; platePickerToggle.setAttribute('aria-expanded','false'); });
    item.performanceLoadClear.addEventListener('click', () => { clearPlatePickerCounts(); platePickerHeaderTotal.textContent = 'Elegir'; });
'''


def apply_plate_picker_contract(source: str) -> str:
    """Instala estilos y la UI; conserva la carga confirmada en el contrato actual."""
    style_pattern = re.compile(r'<style\s+data-enhancement="plate-picker-v1">.*?</style>', re.S)
    if style_pattern.search(source):
        source = style_pattern.sub(lambda _match: STYLE, source, count=1)
    else:
        source = source.replace("</head>", STYLE + "\n</head>", 1)
    markup_pattern = re.compile(r"    const platePickerToggle = document\.createElement\('button'\);.*?loadLabel\.append\(platePickerToggle,\s*platePickerPanel\);", re.S)
    markup_matches = list(markup_pattern.finditer(source))
    if markup_matches:
        pieces = []
        cursor = 0
        for index, match in enumerate(markup_matches):
            pieces.append(source[cursor:match.start()])
            if index == 0:
                pieces.append(MARKUP.lstrip("\n").rstrip())
            cursor = match.end()
        pieces.append(source[cursor:])
        source = "".join(pieces)
    else:
        anchor = "loadLabel.append(loadHead, loadOutputRow, loadInput);"
        if anchor not in source:
            raise ValueError("No se encontró el selector base de carga para agregar discos")
        source = source.replace(anchor, anchor + MARKUP.lstrip("\n"), 1)
    anchor = "    const savedReps = Number(savedDraft?.reps);"
    if anchor not in source:
        raise ValueError("No se encontró el guardado del borrador para enlazar el selector de discos")
    handler_pattern = re.compile(r"    const (?:formatPlateValue = value => \{|renderPlatePicker = \(\) => \{).*?(?=\n    const savedReps = Number\(savedDraft\?\.reps\);)", re.S)
    if handler_pattern.search(source):
        source = handler_pattern.sub(lambda _match: HANDLERS.lstrip("\n").rstrip(), source, count=1)
    else:
        source = source.replace(anchor, HANDLERS.lstrip("\n").rstrip() + "\n" + anchor, 1)
    source = source.replace("Toca un disco para agregarlo. Puedes combinar libras y kilogramos.", "Toca para sumar; desplázate para ver kg y mezclar unidades.")
    source = source.replace("Selecciona discos para ver la suma", "Sin discos seleccionados")
    source = source.replace("El total suma los discos seleccionados; no incluye barra o máquina.", "No incluye barra ni máquina.")
    source = re.sub(
        r'const selectedValue = Number\(item\.performanceLoadExact\);\s*const displayedValue = item\.performanceLoadSelected && Number\.isFinite\(selectedValue\)\s*\? loadMath\.toDisplay\(loadMath\.normalizeKg\(loadMath\.toKg\(selectedValue, unit\), item\.performanceLoadProfile\), unit\)\s*: profileMin;',
        "const selectedValue = Number(item.performanceLoadExact);\n      const exactPlateKg = Number(item.platePickerExactLoadKg);\n      const hasExactPlateLoad = item.platePickerExactLoadKg != null && Number.isFinite(exactPlateKg) && exactPlateKg >= item.performanceLoadProfile.minKg && exactPlateKg <= item.performanceLoadProfile.maxKg;\n      const displayedValue = item.performanceLoadSelected && Number.isFinite(selectedValue)\n        ? hasExactPlateLoad ? loadMath.toDisplay(exactPlateKg, unit) : loadMath.toDisplay(loadMath.normalizeKg(loadMath.toKg(selectedValue, unit), item.performanceLoadProfile), unit)\n        : profileMin;",
        source,
        count=1,
    )
    source = source.replace(
        "loadInput.min = String(profileMin); loadInput.max = String(profileMax); loadInput.step = String(unitStep);",
        "loadInput.min = String(profileMin); loadInput.max = String(profileMax); loadInput.step = hasExactPlateLoad ? 'any' : String(unitStep);",
    )
    source = source.replace(
        "const displayValue = unit === 'lb' ? String(Math.round(value)) : Number.isInteger(value) ? String(value) : value.toFixed(1);",
        "const displayValue = item.platePickerExactLoadKg != null ? String(Math.round(value * 100) / 100) : unit === 'lb' ? String(Math.round(value)) : Number.isInteger(value) ? String(value) : value.toFixed(1);",
    )
    source = source.replace(
        "item.performanceLoad.addEventListener('input', () => { const enteredKg = loadMath.toKg(item.performanceLoad.value, item.performanceLoadUnit);",
        "item.performanceLoad.addEventListener('input', () => { item.platePickerExactLoadKg = null; const enteredKg = loadMath.toKg(item.performanceLoad.value, item.performanceLoadUnit);",
    )
    source = source.replace(
        "loadClear.addEventListener('click', () => { item.performanceLoadSelected = false;",
        "loadClear.addEventListener('click', () => { item.platePickerExactLoadKg = null; item.performanceLoadSelected = false;",
    )
    source = source.replace(
        "editor.value = item.performanceLoadSelected ? (item.performanceLoadUnit === 'lb' ? String(Math.round(item.performanceLoadExact)) : String(item.performanceLoadExact)) : '';",
        "editor.value = item.performanceLoadSelected ? String(item.performanceLoadExact) : '';",
    )
    source = source.replace(
        "if (Number.isFinite(entered) && entered >= Number(loadInput.min) && entered <= Number(loadInput.max)) { item.performanceLoadExact =",
        "if (Number.isFinite(entered) && entered >= Number(loadInput.min) && entered <= Number(loadInput.max)) { item.platePickerExactLoadKg = null; item.performanceLoadExact =",
    )
    source = source.replace(
        "const kilograms = loadMath.toKg(currentLoad, previousUnit);",
        "const kilograms = item.platePickerExactLoadKg != null ? Number(item.platePickerExactLoadKg) : loadMath.toKg(currentLoad, previousUnit);",
    )
    source = source.replace(
        "const rounded = loadMath.toDisplay(loadMath.normalizeKg(kilograms, item.performanceLoadProfile), nextUnit);",
        "const rounded = item.platePickerExactLoadKg != null ? loadMath.toDisplay(kilograms, nextUnit) : loadMath.toDisplay(loadMath.normalizeKg(kilograms, item.performanceLoadProfile), nextUnit);",
    )
    source = source.replace(
        "const savedLoadIsValid = savedLoadWasSelected && Number.isFinite(savedLoadKg) && savedLoadKg >= item.performanceLoadProfile.minKg && savedLoadKg <= item.performanceLoadProfile.maxKg;",
        "const savedPlateKg = Number(savedDraft?.platePickerExactLoadKg);\n    const savedLoadIsValid = savedLoadWasSelected && Number.isFinite(savedLoadKg) && savedLoadKg >= item.performanceLoadProfile.minKg && savedLoadKg <= item.performanceLoadProfile.maxKg;\n    item.platePickerExactLoadKg = savedDraft?.platePickerExactLoadKg != null && Number.isFinite(savedPlateKg) && savedPlateKg >= item.performanceLoadProfile.minKg && savedPlateKg <= item.performanceLoadProfile.maxKg ? savedPlateKg : null;",
    )
    source = source.replace(
        "load: item.performanceLoadSelected ? String(item.performanceLoadExact) : '', loadSelected: item.performanceLoadSelected, loadUnit: item.performanceLoadUnit",
        "load: item.performanceLoadSelected ? String(item.performanceLoadExact) : '', loadSelected: item.performanceLoadSelected, loadUnit: item.performanceLoadUnit, platePickerExactLoadKg: item.platePickerExactLoadKg",
    )
    source = source.replace(
        "load: item.performanceLoadExact,\n          loadSelected: item.performanceLoadSelected,",
        "load: item.performanceLoadExact,\n          loadSelected: item.performanceLoadSelected,\n          platePickerExactLoadKg: item.platePickerExactLoadKg,",
    )
    source = source.replace(
        "loadKg: loadSelected ? loadKg : null,\n          loadSelected",
        "loadKg: loadSelected ? loadKg : null,\n          platePickerExactLoadKg: item.platePickerExactLoadKg,\n          loadSelected",
    )
    source = source.replace(
        "item.performanceLoadExact = loadMath.toDisplay(loadMath.normalizeKg(savedKg, item.performanceLoadProfile), savedUnit);",
        "const savedPlateKg = Number(saved?.platePickerExactLoadKg);\n          const exactPlate = saved?.platePickerExactLoadKg != null && Number.isFinite(savedPlateKg) && savedPlateKg >= item.performanceLoadProfile.minKg && savedPlateKg <= item.performanceLoadProfile.maxKg;\n          item.platePickerExactLoadKg = exactPlate ? savedPlateKg : null;\n          item.performanceLoadExact = loadMath.toDisplay(exactPlate ? savedPlateKg : loadMath.normalizeKg(savedKg, item.performanceLoadProfile), savedUnit);",
    )
    source = source.replace(
        "} else {\n          item.performanceLoadExact = 0;\n          item.performanceLoadSelected = false;",
        "} else {\n          item.platePickerExactLoadKg = null;\n          item.performanceLoadExact = 0;\n          item.performanceLoadSelected = false;",
    )
    source = source.replace(
        "if (commit && editor.value === '') { item.performanceLoadSelected = false;",
        "if (commit && editor.value === '') { item.platePickerExactLoadKg = null; item.performanceLoadSelected = false;",
    )
    source = source.replace(
        "item.performanceLoadExact = normal.load;\n          item.performanceLoadSelected = normal.loadSelected;",
        "item.performanceLoadExact = normal.load;\n          item.performanceLoadSelected = normal.loadSelected;\n          item.platePickerExactLoadKg = normal.platePickerExactLoadKg ?? null;",
    )
    # Repeated application must not redeclare consts inside the same routine
    # initializer. Older generated pages accumulated these lines on every run,
    # which stopped the whole script at parse time and left progress at 0/total.
    source = re.sub(
        r"(?m)^([ \t]*(?:const savedPlateKg = Number\(savedDraft\?\.platePickerExactLoadKg\);|const savedPlateKg = Number\(saved\?\.platePickerExactLoadKg\);|const exactPlate = saved\?\.platePickerExactLoadKg != null && Number\.isFinite\(savedPlateKg\) && savedPlateKg >= item\.performanceLoadProfile\.minKg && savedPlateKg <= item\.performanceLoadProfile\.maxKg;|item\.platePickerExactLoadKg = savedDraft\?\.platePickerExactLoadKg != null && Number\.isFinite\(savedPlateKg\) && savedPlateKg >= item\.performanceLoadProfile\.minKg && savedPlateKg <= item\.performanceLoadProfile\.maxKg \? savedPlateKg : null;|item\.platePickerExactLoadKg = exactPlate \? savedPlateKg : null;)[ \t]*\n)(?:\1)+",
        r"\1",
        source,
    )
    source = re.sub(
        r"(, platePickerExactLoadKg: item\.platePickerExactLoadKg)(?:\1)+",
        r"\1",
        source,
    )
    return source
