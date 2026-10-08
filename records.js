(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const status = $('#dataStatus');
  const content = $('#recordsContent');
  const filter = $('#periodFilter');
  const number = value => Math.max(0, Math.round(Number(value) || 0));
  const dateOf = session => Number(session?.startedAt) || Number(session?.updatedAt) || Number(session?.endedAt) || 0;
  const dateLabel = value => value ? new Intl.DateTimeFormat('es-MX', { day:'numeric', month:'short', year:'numeric' }).format(new Date(value)) : 'Fecha no disponible';
  const sessionTitle = session => String(session?.label || session?.routineId || 'Sesión de entrenamiento');
  const safeRecords = session => Array.isArray(session?.performance) ? session.performance.filter(item => item && typeof item === 'object') : [];
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };
  const startedWithin = (session, days, now) => {
    const startedAt = dateOf(session);
    return startedAt > 0 && startedAt <= now && startedAt >= now - days * 86400000;
  };
  function selectedSessions() {
    const value = filter.value;
    if (value === 'all') return allSessions.slice();
    const days = Number(value);
    const now = Date.now();
    return allSessions.filter(session => startedWithin(session, days, now));
  }
  function setEmpty(container, message) { container.replaceChildren(make('p', 'empty-note', message)); }
  function renderSummary(sessions) {
    const activeSessions = sessions.filter(session => number(session.completedSeries) > 0);
    const records = activeSessions.flatMap(safeRecords);
    const trainedDays = new Set(activeSessions.map(session => {
      const date = new Date(dateOf(session));
      return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
    }));
    $('#statSessions').textContent = String(activeSessions.length);
    $('#statSets').textContent = String(activeSessions.reduce((sum, session) => sum + number(session.completedSeries), 0));
    $('#statReps').textContent = String(records.reduce((sum, record) => sum + number(record.reps), 0));
    $('#statDays').textContent = String(trainedDays.size);
  }
  function mondayStart(date) {
    const copy = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    copy.setDate(copy.getDate() - ((copy.getDay() + 6) % 7));
    return copy;
  }
  function renderWeeks(sessions) {
    const root = $('#weeklyChart');
    root.replaceChildren();
    const now = new Date();
    const currentMonday = mondayStart(now);
    const weeks = Array.from({length:6}, (_, index) => {
      const start = new Date(currentMonday);
      start.setDate(start.getDate() - (5 - index) * 7);
      return { start, series:0 };
    });
    for (const session of sessions) {
      if (!number(session.completedSeries)) continue;
      const start = mondayStart(new Date(dateOf(session)));
      const week = weeks.find(item => item.start.getTime() === start.getTime());
      if (week) week.series += number(session.completedSeries);
    }
    const max = Math.max(1, ...weeks.map(week => week.series));
    for (const week of weeks) {
      const column = make('div', 'week-column');
      column.setAttribute('aria-label', `${dateLabel(week.start.getTime())}: ${week.series} series`);
      column.append(make('span', 'week-value', week.series));
      const track = make('div', 'week-track');
      track.setAttribute('aria-hidden', 'true');
      const bar = make('div', 'week-bar');
      bar.style.height = `${week.series ? Math.max(5, week.series / max * 100) : 0}%`;
      track.append(bar);
      column.append(track, make('span', 'week-label', new Intl.DateTimeFormat('es-MX', {day:'numeric', month:'short'}).format(week.start)));
      root.append(column);
    }
  }
  function renderLoads(sessions) {
    const root = $('#exerciseLoads');
    root.replaceChildren();
    const byExercise = new Map();
    for (const session of sessions) for (const record of safeRecords(session)) {
      const kg = Number(record.loadKg);
      const load = Number(record.load);
      if (!Number.isFinite(kg) || !Number.isFinite(load) || !record.loadUnit) continue;
      const key = String(record.exerciseId || record.exerciseName || 'exercise').slice(0,100);
      const existing = byExercise.get(key) || { name:String(record.exerciseName || record.exerciseId || 'Ejercicio'), kg:-1, load, unit:String(record.loadUnit), count:0 };
      existing.count += 1;
      if (kg > existing.kg) Object.assign(existing, { kg, load, unit:String(record.loadUnit) });
      byExercise.set(key, existing);
    }
    const values = [...byExercise.values()].sort((a,b) => a.name.localeCompare(b.name, 'es'));
    if (!values.length) return setEmpty(root, 'Aún no hay cargas guardadas. Las series sin carga registrada no se cuentan como cero.');
    for (const item of values) {
      const row = make('div', 'exercise-item');
      const name = make('span', '', item.name);
      name.append(make('small', '', `${item.count} registros de carga`));
      row.append(name, make('strong', '', `${new Intl.NumberFormat('es-MX', {maximumFractionDigits:2}).format(item.load)} ${item.unit}`));
      root.append(row);
    }
  }
  function renderRoutines(sessions) {
    const root = $('#routineBreakdown');
    root.replaceChildren();
    const totals = new Map();
    for (const session of sessions) {
      if (!number(session.completedSeries)) continue;
      const key = String(session.routineId || session.label || 'Rutina');
      const item = totals.get(key) || { label:sessionTitle(session), sessions:0, series:0 };
      item.sessions += 1;
      item.series += number(session.completedSeries);
      totals.set(key, item);
    }
    if (!totals.size) return setEmpty(root, 'No hay sesiones con series completadas en este periodo.');
    for (const item of [...totals.values()].sort((a,b) => b.series - a.series)) {
      const row = make('div', 'routine-item');
      row.append(make('span', '', item.label), make('strong', '', `${item.sessions} ses. · ${item.series} series`));
      root.append(row);
    }
  }
  function performanceLabel(record) {
    const parts = [];
    if (number(record.reps)) parts.push(`${number(record.reps)} rep.`);
    const load = Number(record.load);
    if (Number.isFinite(load) && record.loadUnit) parts.push(`${new Intl.NumberFormat('es-MX', {maximumFractionDigits:2}).format(load)} ${record.loadUnit}`);
    if (Number(record.durationMs) > 0) parts.push(`${Math.round(Number(record.durationMs) / 1000)} s`);
    return parts.length ? parts.join(' · ') : 'Sin reps ni carga registrada';
  }
  function renderHistory(sessions) {
    const root = $('#sessionHistory');
    root.replaceChildren();
    $('#historyCount').textContent = String(sessions.length);
    if (!sessions.length) return setEmpty(root, 'No hay sesiones en el periodo seleccionado.');
    for (const session of sessions) {
      const details = make('details');
      const summary = make('summary');
      summary.append(make('span', 'session-title', sessionTitle(session)));
      summary.append(make('span', 'session-meta', `${dateLabel(dateOf(session))} · ${session.status === 'completed' ? 'Completada' : 'En curso'}`));
      summary.append(make('span', 'session-badge', `${number(session.completedSeries)}/${number(session.totalSeries)} series`));
      const performance = make('div', 'session-performance');
      const rows = safeRecords(session).sort((a,b) => number(a.setNumber) - number(b.setNumber));
      if (!rows.length) performance.append(make('p', 'empty-note', 'Esta sesión no tiene datos de reps o carga por serie guardados.'));
      for (const record of rows) {
        const row = make('div', 'performance-row');
        const exercise = String(record.exerciseName || record.exerciseId || 'Ejercicio');
        const set = number(record.setNumber) ? ` · Serie ${number(record.setNumber)}` : '';
        row.append(make('span', '', `${exercise}${set}`), make('span', '', performanceLabel(record)));
        performance.append(row);
      }
      details.append(summary, performance);
      root.append(details);
    }
  }
  function render() {
    const sessions = selectedSessions();
    renderSummary(sessions);
    renderWeeks(allSessions);
    renderLoads(sessions);
    renderRoutines(sessions);
    renderHistory(sessions);
    status.textContent = `${sessions.length} de ${allSessions.length} sesiones disponibles · lectura local, sin cambios en tus datos.`;
    content.hidden = false;
  }
  let allSessions = [];
  async function refresh() {
    if (!window.GymratikInstallGate?.isInstalled() || !window.TrainingProgressStore?.getHistory) {
      status.textContent = 'Para proteger tu privacidad, los registros solo se consultan desde la PWA instalada en este dispositivo.';
      status.dataset.state = 'error';
      content.hidden = true;
      return;
    }
    try {
      status.dataset.state = '';
      allSessions = await window.TrainingProgressStore.getHistory(50);
      render();
    } catch (error) {
      console.error('No fue posible leer el historial local.', error);
      status.textContent = 'No se pudieron leer los registros locales. Tu información no se modificó; vuelve a intentarlo desde la portada.';
      status.dataset.state = 'error';
      content.hidden = true;
    }
  }
  filter.addEventListener('change', render);
  window.addEventListener('training-progress-updated', refresh);
  window.addEventListener('pageshow', refresh);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  refresh();
})();
