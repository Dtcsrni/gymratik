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
  const historyRecordKey = (session, record) => `${String(session?.sessionId || dateOf(session))}:${String(session?.routineId || '')}:${String(record?.exerciseId || normalizeName(record?.exerciseName))}:${String(record?.setKey || record?.setNumber || '')}`;
  const LOAD_PROFILES = [
    [/^jalon al pecho$/,40,2.5],[/^remo alto unilateral$/,25,2.5],[/^remo horizontal en maquina$/,40,2.5],[/^apertura inversa en maquina$/,25,2.5],
    [/^curl de biceps sentado en maquina$/,25,5],[/^curl de biceps en maquina$/,15,2.5],[/^hack squat$/,100,5],[/^hip thrust$/,80,5],
    [/^prensa de piernas$/,120,5],[/^prensa unilateral alterna$/,50,5],[/^curl femoral/,30,2.5],[/^extension de piernas$/,40,2.5],
    [/^pantorrillas de pie$/,60,2.5],[/^press de pecho sentado/,40,2.5],[/^press inclinado convergente/,35,2.5],[/^pec deck/,30,2.5],
    [/^press de hombro/,25,2.5],[/^elevacion lateral/,10,2.5],[/^jalon de triceps/,20,2.5],[/^extension de triceps sobre cabeza/,15,2.5],
    [/^peso muerto rumano en smith$/,40,2.5],[/^peso muerto rumano con barra$/,50,2.5],[/^abduccion de cadera/,40,2.5],
    [/^aduccion de cadera/,40,2.5],[/^elevacion de pantorrilla sentada$/,40,2.5],[/^crunch con elevacion de piernas sentada$/,30,2.5],
  ].map(([pattern, referenceKg, stepKg]) => ({ pattern, referenceKg, stepKg }));
  const normalizeName = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim().replace(/\s+/g, ' ');
  const loadProfile = name => LOAD_PROFILES.find(profile => profile.pattern.test(normalizeName(name)));
  const loadKgOf = record => {
    const load = Number(record.load);
    const hasStoredKg = record.loadKg !== null && record.loadKg !== undefined && record.loadKg !== '';
    const kg = hasStoredKg && Number.isFinite(Number(record.loadKg)) ? Number(record.loadKg) : record.loadUnit === 'lb' ? load * 0.45359237 : record.loadUnit === 'kg' ? load : NaN;
    return record.loadSelected !== false && ['kg','lb'].includes(record.loadUnit) && record.load !== null && record.load !== undefined && Number.isFinite(load) && Number.isFinite(kg) ? kg : NaN;
  };
  const formatNumber = value => new Intl.NumberFormat('es-MX', {maximumFractionDigits:1}).format(value);
  const formatPreferredLoad = (kg, units = 'metric') => units === 'imperial' ? `${formatNumber(kg / 0.45359237)} lb` : `${formatNumber(kg)} kg`;
  const formatAlternateLoad = (kg, units = 'metric') => units === 'imperial' ? `${formatNumber(kg)} kg` : `${formatNumber(kg / 0.45359237)} lb`;
  const formatLoad = (kg, units = 'metric') => `${formatPreferredLoad(kg, units)} · ${formatAlternateLoad(kg, units)}`;
  const formatDelta = (kg, units = 'metric') => `${kg > 0 ? '+' : '−'}${formatPreferredLoad(Math.abs(kg), units)}`;
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };
  const svgElement = (tag, attrs = {}) => {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, String(value));
    return node;
  };
  function milestoneSparkline(records, name, units) {
    const values = records.map(record => record.kg);
    const width = 180;
    const height = 52;
    const pad = 7;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const spread = max - min || 1;
    const points = values.map((value, index) => ({
      x: values.length === 1 ? width / 2 : pad + index * (width - 2 * pad) / (values.length - 1),
      y: height - pad - (value - min) / spread * (height - 2 * pad),
      value,
      record: records[index],
    }));
    const svg = svgElement('svg', { class:'milestone-sparkline', viewBox:`0 0 ${width} ${height}`, role:'img', 'aria-label':`${name}: evolución de ${values.length} máximos de sesión validados` });
    const title = svgElement('title');
    title.textContent = `${name}: ${points.map(point => `${dateLabel(point.record.date)}, ${formatPreferredLoad(point.value, units)}`).join('; ')}`;
    svg.append(title, svgElement('line', { class:'spark-guide', x1:pad, y1:height - pad, x2:width - pad, y2:height - pad }));
    if (points.length > 1) svg.append(svgElement('polyline', { class:'spark-line', points:points.map(point => `${point.x},${point.y}`).join(' ') }));
    for (const [index, point] of points.entries()) svg.append(svgElement('circle', { class:`spark-point${index === points.length - 1 ? ' spark-point--latest' : ''}`, cx:point.x, cy:point.y, r:index === points.length - 1 ? 4 : 2.7 }));
    return svg;
  }
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
  function setMascotPreference(sex) {
    const art = $('.hero-art');
    if (art) art.dataset.sex = ['female', 'male'].includes(sex) ? sex : 'all';
  }
  function sessionPeakRecords(sessions) {
    const peaks = new Map();
    const review = [];
    for (const session of sessions) {
      if (!number(session.completedSeries)) continue;
      const date = dateOf(session);
      if (!date) continue;
      const sessionExercises = new Map();
      for (const record of safeRecords(session)) {
        const kg = loadKgOf(record);
        if (!Number.isFinite(kg) || kg === 0) continue;
        const exerciseName = String(record.exerciseName || record.exerciseId || 'Ejercicio').slice(0,100);
        const profile = loadProfile(exerciseName);
        const exerciseId = String(record.exerciseId || normalizeName(exerciseName)).slice(0,100);
        const key = `${String(session.routineId || '')}:${exerciseId}`;
        const item = { key, exerciseName, profile, kg, reps:number(record.reps), session, date, record };
        if (profile && (kg < profile.referenceKg * .25 || kg > profile.referenceKg * 2.5)) {
          const lower = new Intl.NumberFormat('es-MX',{maximumFractionDigits:1}).format(profile.referenceKg * .25);
          const upper = new Intl.NumberFormat('es-MX',{maximumFractionDigits:1}).format(profile.referenceKg * 2.5);
          review.push({ ...item, reason:`Fuera de la banda orientativa (${lower}–${upper} kg).` });
          continue;
        }
        const current = sessionExercises.get(key);
        if (!current || kg > current.kg) sessionExercises.set(key, { ...item, sets:1 });
        else if (kg === current.kg) current.sets += 1;
      }
      for (const [key, item] of sessionExercises) {
        const items = peaks.get(key) || [];
        items.push(item);
        peaks.set(key, items);
      }
    }
    return { peaks, review };
  }
  function validateMilestones(sessions) {
    const validExercises = [];
    const review = [];
    let personalRecords = 0;
    const { peaks:groups, review:rangeReview } = sessionPeakRecords(sessions);
    review.push(...rangeReview);
    for (const items of groups.values()) {
      items.sort((a,b) => a.date - b.date);
      const accepted = [];
      for (const item of items) {
        const profile = item.profile;
        let reason = '';
        if (!profile) reason = 'No hay referencia orientativa para validar este ejercicio.';
        else if (accepted.length) {
          const previous = accepted[accepted.length - 1];
          const allowedChange = Math.max(profile.stepKg, previous.kg * .10);
          if (Math.abs(item.kg - previous.kg) > allowedChange + .001) {
            reason = `Cambio de ${formatDelta(item.kg - previous.kg)} frente a la última sesión válida; el límite orientativo era ${formatLoad(allowedChange)}.`;
          }
        }
        if (reason) { review.push({ ...item, reason }); continue; }
        const previousBest = accepted.reduce((best, candidate) => !best || candidate.kg > best.kg ? candidate : best, null);
        const isNewRecord = Boolean(previousBest && item.kg > previousBest.kg + .001);
        if (isNewRecord) personalRecords += 1;
        accepted.push({ ...item, isNewRecord });
      }
      if (!accepted.length) continue;
      const best = accepted.reduce((current, item) => !current || item.kg > current.kg || (item.kg === current.kg && item.date > current.date) ? item : current, null);
      validExercises.push({
        name:best.exerciseName,
        best,
        baseline:accepted[0],
        validRecords:accepted,
        validSessions:accepted.length,
        personalRecords:accepted.filter(item => item.isNewRecord).length,
        gainKg:best.kg - accepted[0].kg,
      });
    }
    validExercises.sort((a,b) => b.best.kg - a.best.kg || a.name.localeCompare(b.name, 'es'));
    return { validExercises, review, personalRecords };
  }
  function renderMilestones(sessions, units = 'metric') {
    const { validExercises, review, personalRecords } = validateMilestones(sessions);
    const highest = validExercises[0];
    $('#heroLoad').textContent = highest ? formatLoad(highest.best.kg, units) : '—';
    $('#heroLoadContext').textContent = highest ? `${highest.name} · ${dateLabel(highest.best.date)}` : 'Aún no hay cargas verificables.';
    $('#milestoneStatus').textContent = `Validación orientativa sobre ${sessions.length} sesiones disponibles (hasta 50). Los datos originales no se modifican.`;
    $('#milestoneExercises').textContent = String(validExercises.length);
    $('#milestonePrs').textContent = String(personalRecords);
    $('#milestoneCorrections').textContent = String(review.length);

    const root = $('#milestoneList');
    root.replaceChildren();
    if (!validExercises.length) setEmpty(root, 'Todavía no hay cargas validadas. Completa series y registra la carga con el nombre de ejercicio de tu rutina.');
    for (const [index, item] of validExercises.entries()) {
      const card = make('article', 'milestone-card');
      const rank = make('span', 'milestone-rank', `#${index + 1}`);
      rank.setAttribute('aria-label', `Puesto ${index + 1}`);
      const copy = make('span', 'milestone-copy');
      copy.append(make('strong', 'milestone-name', item.name));
      const best = item.best;
      const repLabel = best.reps ? ` · ${best.reps} rep.` : '';
      copy.append(make('small', 'milestone-meta', `${item.validSessions} sesiones válidas · ${best.sets} series en el máximo${repLabel} · ${dateLabel(best.date)}`));
      const load = make('strong', 'milestone-load', formatPreferredLoad(best.kg, units));
      load.append(make('small', '', `${formatAlternateLoad(best.kg, units)} · máximo personal`));
      const gain = make('div', `milestone-gain${item.gainKg <= .001 ? ' is-flat' : ''}`);
      const netPercent = item.baseline.kg > 0 ? item.gainKg / item.baseline.kg * 100 : 0;
      const latest = item.validRecords[item.validRecords.length - 1];
      const previous = item.validRecords.length > 1 ? item.validRecords[item.validRecords.length - 2] : null;
      const lastDelta = previous ? latest.kg - previous.kg : 0;
      const lastPercent = previous?.kg > 0 ? lastDelta / previous.kg * 100 : 0;
      const lastDeltaLabel = previous ? `Δ última captura ${formatDelta(lastDelta, units)} (${lastPercent > 0 ? '+' : ''}${formatNumber(lastPercent)} %)` : 'Una captura válida';
      gain.append(make('span', '', item.gainKg > .001 ? `↗ ${formatDelta(item.gainKg, units)} netos · +${formatNumber(netPercent)} % desde tu primera sesión válida` : '• Sin cambio neto desde tu primera sesión válida'));
      gain.append(make('span', '', `${item.personalRecords} ${item.personalRecords === 1 ? 'nuevo máximo' : 'nuevos máximos'}`));
      const trend = make('div', `milestone-trend${lastDelta < -.001 ? ' is-down' : lastDelta <= .001 ? ' is-flat' : ''}`);
      trend.append(milestoneSparkline(item.validRecords, item.name, units), make('span', 'milestone-delta', lastDeltaLabel));
      card.append(rank, copy, load, gain, trend);
      root.append(card);
    }
    const reviewDetails = $('#reviewDetails');
    const reviewList = $('#reviewList');
    reviewList.replaceChildren();
    reviewDetails.hidden = review.length === 0;
    $('#reviewCount').textContent = String(review.length);
    for (const item of review.slice().reverse()) {
      const row = make('div', 'review-item');
      row.append(make('span', '', `${item.exerciseName} · ${dateLabel(item.date)}`), make('strong', '', `${formatLoad(item.kg)} — ${item.reason}`));
      reviewList.append(row);
    }
  }
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
  const sessionTimestamp = session => Number(session?.endedAt) || dateOf(session);
  const countDeltaLabel = (current, previous) => {
    const delta = current - previous;
    if (!delta) return 'Sin cambio';
    const sign = delta > 0 ? '+' : '−';
    const percent = previous > 0 ? ` · ${delta > 0 ? '+' : '−'}${formatNumber(Math.abs(delta) / previous * 100)} %` : '';
    return `${sign}${formatNumber(Math.abs(delta))}${percent}`;
  };
  const countDeltaClass = (current, previous) => current > previous ? 'delta-up' : current < previous ? 'delta-down' : 'delta-flat';
  function sessionStats(session) {
    const records = safeRecords(session);
    return {
      sets: number(session?.completedSeries),
      reps: records.reduce((sum, record) => sum + number(record.reps), 0),
      exercises: new Set(records.map(record => String(record.exerciseId || normalizeName(record.exerciseName))).filter(Boolean)).size,
    };
  }
  function comparisonMetrics(current, previous, definitions) {
    const grid = make('div', 'comparison-metrics');
    for (const [key, label] of definitions) {
      const row = make('div', 'comparison-metric');
      const delta = make('strong', `metric-delta ${countDeltaClass(current[key], previous[key])}`, countDeltaLabel(current[key], previous[key]));
      row.append(make('span', 'metric-name', label), make('span', 'metric-current', formatNumber(current[key])), make('span', 'metric-previous', formatNumber(previous[key])), delta);
      grid.append(row);
    }
    return grid;
  }
  function renderSessionComparison(sessions) {
    const root = $('#sessionComparison');
    const hint = $('#sessionComparisonHint');
    root.replaceChildren();
    const recent = sessions.filter(session => number(session.completedSeries) > 0).slice().sort((a,b) => sessionTimestamp(b) - sessionTimestamp(a));
    if (!recent.length) {
      hint.textContent = 'Se necesitan sesiones con series registradas';
      return setEmpty(root, 'Aún no hay sesiones con actividad para comparar.');
    }
    const current = recent[0];
    const previous = recent[1];
    if (!previous) {
      hint.textContent = 'La comparación aparecerá al guardar otra sesión';
      const card = make('article', 'session-latest-card');
      card.append(make('span', 'comparison-kicker', 'TU SESIÓN MÁS RECIENTE'), make('strong', 'session-latest-name', sessionTitle(current)), make('span', 'session-latest-date', dateLabel(dateOf(current))));
      const metrics = sessionStats(current);
      const summary = make('div','latest-metric-grid');
      for (const [key,label] of [['sets','Series'],['reps','Repeticiones'],['exercises','Ejercicios con datos']]) {
        const metric = make('div','latest-metric');
        metric.append(make('span','',label),make('strong','',formatNumber(metrics[key])));
        summary.append(metric);
      }
      card.append(summary);
      root.append(card);
      return;
    }
    hint.textContent = `${sessionTitle(current)} · comparación descriptiva, incluso si cambió la rutina`;
    const currentStats = sessionStats(current);
    const previousStats = sessionStats(previous);
    const comparison = make('article', 'session-pair-card');
    const headings = make('div', 'session-pair-headings');
    const currentHead = make('div', 'session-period session-period--current');
    currentHead.append(make('span', 'comparison-kicker', 'MÁS RECIENTE'), make('strong', '', sessionTitle(current)), make('small', '', dateLabel(dateOf(current))));
    const previousHead = make('div', 'session-period');
    previousHead.append(make('span', 'comparison-kicker', 'ANTERIOR'), make('strong', '', sessionTitle(previous)), make('small', '', dateLabel(dateOf(previous))));
    headings.append(currentHead, make('span', 'comparison-arrow', '→'), previousHead);
    const labels = make('div', 'comparison-column-labels');
    labels.append(make('span', '', 'Indicador'), make('span', '', 'Última'), make('span', '', 'Anterior'), make('span', '', 'Delta'));
    comparison.append(headings, labels, comparisonMetrics(currentStats, previousStats, [['sets','Series'],['reps','Repeticiones'],['exercises','Ejercicios con datos']]));
    root.append(comparison);
  }
  const startOfDay = date => new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const daysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
  function statsInRange(sessions, from, through) {
    const items = sessions.filter(session => {
      const timestamp = dateOf(session);
      return timestamp >= from.getTime() && timestamp <= through.getTime() && number(session.completedSeries) > 0;
    });
    const days = new Set(items.map(session => {
      const date = new Date(dateOf(session));
      return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
    }));
    return {
      sessions:items.length,
      sets:items.reduce((sum, session) => sum + number(session.completedSeries), 0),
      reps:items.reduce((sum, session) => sum + safeRecords(session).reduce((total, record) => total + number(record.reps), 0), 0),
      days:days.size,
    };
  }
  const shortDateLabel = value => new Intl.DateTimeFormat('es-MX', {day:'numeric',month:'short'}).format(value);
  function renderPeriodCard(root, title, currentRange, previousRange, sessions) {
    const card = make('article', 'period-compare-card');
    const head = make('div', 'period-compare-head');
    head.append(make('span', 'comparison-kicker', title), make('span', 'period-current-range', `${shortDateLabel(currentRange.from)}–${shortDateLabel(currentRange.through)}`));
    card.append(head);
    const labels = make('div', 'comparison-column-labels');
    labels.append(make('span', '', 'Indicador'), make('span', '', 'Actual'), make('span', '', 'Anterior'), make('span', '', 'Delta'));
    const currentStats = statsInRange(sessions,currentRange.from,currentRange.through);
    const previousStats = statsInRange(sessions,previousRange.from,previousRange.through);
    if (!currentStats.sessions && !previousStats.sessions) {
      card.append(make('p','empty-note','Aún no hay actividad en estos tramos.'));
    } else {
      card.append(labels,comparisonMetrics(currentStats,previousStats,[['sessions','Sesiones'],['sets','Series'],['reps','Repeticiones'],['days','Días activos']]));
    }
    const foot = make('p', 'period-compare-foot', `vs ${shortDateLabel(previousRange.from)}–${shortDateLabel(previousRange.through)} del periodo anterior`);
    card.append(foot);
    root.append(card);
  }
  function renderPeriodComparisons(sessions) {
    const root = $('#periodComparison');
    root.replaceChildren();
    const now = new Date();
    const currentWeek = mondayStart(now);
    const previousWeek = new Date(currentWeek);
    previousWeek.setDate(previousWeek.getDate() - 7);
    const previousWeekThrough = new Date(now);
    previousWeekThrough.setDate(previousWeekThrough.getDate() - 7);
    const currentMonth = new Date(now.getFullYear(),now.getMonth(),1);
    const previousMonth = new Date(now.getFullYear(),now.getMonth()-1,1);
    const comparisonDay = Math.min(now.getDate(),daysInMonth(previousMonth.getFullYear(),previousMonth.getMonth()));
    const currentMonthThrough = new Date(now);
    currentMonthThrough.setDate(comparisonDay);
    currentMonthThrough.setHours(now.getHours(),now.getMinutes(),now.getSeconds(),now.getMilliseconds());
    const previousMonthThrough = new Date(previousMonth);
    previousMonthThrough.setDate(comparisonDay);
    previousMonthThrough.setHours(now.getHours(),now.getMinutes(),now.getSeconds(),now.getMilliseconds());
    renderPeriodCard(root,'Semana en curso · mismo tramo',
      {from:currentWeek,through:now}, {from:previousWeek,through:previousWeekThrough}, sessions);
    renderPeriodCard(root,'Mes en curso · mismo tramo',
      {from:currentMonth,through:currentMonthThrough}, {from:previousMonth,through:previousMonthThrough}, sessions);
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
    const weeks = Array.from({length:12}, (_, index) => {
      const start = new Date(currentMonday);
      start.setDate(start.getDate() - (11 - index) * 7);
      return { start, series:0 };
    });
    for (const session of sessions) {
      if (!number(session.completedSeries)) continue;
      const start = mondayStart(new Date(dateOf(session)));
      const week = weeks.find(item => item.start.getTime() === start.getTime());
      if (week) week.series += number(session.completedSeries);
    }
    const max = Math.max(1, ...weeks.map(week => week.series));
    root.setAttribute('aria-label',`Series completadas por semana, últimas 12 semanas: ${weeks.map(week=>`${shortDateLabel(week.start)}, ${week.series}`).join('; ')}`);
    for (const week of weeks) {
      const isCurrent = week.start.getTime() === currentMonday.getTime();
      const column = make('div', `week-column${isCurrent ? ' is-current' : ''}`);
      const weekEnd = new Date(week.start); weekEnd.setDate(weekEnd.getDate() + 6);
      column.setAttribute('aria-label', `${isCurrent ? 'Semana actual, ' : ''}${shortDateLabel(week.start)} al ${shortDateLabel(weekEnd)}: ${week.series} series`);
      column.append(make('span', 'week-value', week.series));
      const track = make('div', 'week-track');
      track.setAttribute('aria-hidden', 'true');
      const bar = make('div', 'week-bar');
      bar.style.height = `${week.series ? Math.max(5, week.series / max * 100) : 0}%`;
      bar.style.animationDelay = `${(weeks.indexOf(week) % 8) * 35}ms`;
      track.append(bar);
      column.append(track, make('span', 'week-label', new Intl.DateTimeFormat('es-MX', {day:'numeric', month:'short'}).format(week.start)));
      root.append(column);
    }
  }
  function renderDaily(sessions) {
    const root = $('#dailyChart');
    root.replaceChildren();
    const today = startOfDay(new Date());
    const days = Array.from({length:14},(_,index) => {
      const date = new Date(today);
      date.setDate(today.getDate() - (13 - index));
      return {date,series:0};
    });
    for (const session of sessions) {
      if (!number(session.completedSeries)) continue;
      const date = startOfDay(new Date(dateOf(session)));
      const day = days.find(item => item.date.getTime() === date.getTime());
      if (day) day.series += number(session.completedSeries);
    }
    const max = Math.max(1,...days.map(day=>day.series));
    for (const [index,day] of days.entries()) {
      const column = make('div',`daily-column${day.series ? ' has-training' : ''}${index === days.length - 1 ? ' is-today' : ''}`);
      column.title = `${dateLabel(day.date.getTime())}: ${day.series} series`;
      column.setAttribute('aria-label',`${dateLabel(day.date.getTime())}: ${day.series} series`);
      const track = make('div','daily-track');
      const bar = make('div','daily-bar');
      bar.style.height = `${day.series ? Math.max(5,day.series/max*100) : 0}%`;
      bar.style.animationDelay = `${index*24}ms`;
      track.append(bar);
      const dayName = new Intl.DateTimeFormat('es-MX',{weekday:'narrow'}).format(day.date);
      column.append(track,make('span','daily-day',dayName),make('span','daily-date',String(day.date.getDate())));
      root.append(column);
    }
    const activeDays = days.filter(day=>day.series>0).length;
    const total = days.reduce((sum,day)=>sum+day.series,0);
    root.setAttribute('aria-label',`Actividad diaria de los últimos 14 días: ${days.map(day=>`${shortDateLabel(day.date)}, ${day.series} series`).join('; ')}`);
    $('#dailyTrendSummary').textContent = `${formatNumber(total)} series en ${activeDays} ${activeDays === 1 ? 'día activo' : 'días activos'} de los últimos 14.`;
  }
  function renderMonthly(sessions) {
    const root = $('#monthlyChart');
    root.replaceChildren();
    const now = new Date();
    const months = Array.from({length:6},(_,index) => {
      const start = new Date(now.getFullYear(),now.getMonth() - (5 - index),1);
      return {start,sessions:0,series:0};
    });
    for (const session of sessions) {
      if (!number(session.completedSeries)) continue;
      const date = new Date(dateOf(session));
      const month = months.find(item => item.start.getFullYear() === date.getFullYear() && item.start.getMonth() === date.getMonth());
      if (month) { month.sessions += 1; month.series += number(session.completedSeries); }
    }
    const max = Math.max(1,...months.map(month=>month.sessions));
    for (const [index,month] of months.entries()) {
      const current = index === months.length - 1;
      const column = make('div',`month-column${current ? ' is-current' : ''}${month.sessions ? ' has-training' : ''}`);
      const monthLabel = new Intl.DateTimeFormat('es-MX',{month:'short'}).format(month.start).replace('.','');
      column.title = `${new Intl.DateTimeFormat('es-MX',{month:'long',year:'numeric'}).format(month.start)}: ${month.sessions} sesiones, ${month.series} series${current ? ' (mes en curso)' : ''}`;
      column.setAttribute('aria-label',column.title);
      const track = make('div','month-track');
      const bar = make('div','month-bar');
      bar.style.height = `${month.sessions ? Math.max(5,month.sessions/max*100) : 0}%`;
      bar.style.animationDelay = `${index*55}ms`;
      track.append(bar);
      column.append(make('span','month-value',String(month.sessions)),track,make('span','month-label',monthLabel));
      root.append(column);
    }
    const current = months[months.length-1];
    const previous = months[months.length-2];
    root.setAttribute('aria-label',`Sesiones mensuales: ${months.map(month=>`${new Intl.DateTimeFormat('es-MX',{month:'long',year:'numeric'}).format(month.start)}, ${month.sessions} sesiones, ${month.series} series`).join('; ')}`);
    $('#monthlyTrendSummary').textContent = `Mes en curso: ${current.sessions} ${current.sessions === 1 ? 'sesión' : 'sesiones'} · mes anterior completo: ${previous.sessions}. El comparativo principal usa el mismo tramo.`;
  }
  function renderLoads(sessions) {
    const root = $('#exerciseLoads');
    root.replaceChildren();
    const selectedSessionKeys = new Set(sessions.map(session => String(session.sessionId || `${session.routineId || ''}:${dateOf(session)}`)));
    const values = validateMilestones(allSessions).validExercises.map(item => {
      const validRecords = item.validRecords.filter(record => selectedSessionKeys.has(String(record.session.sessionId || `${record.session.routineId || ''}:${dateOf(record.session)}`)));
      if (!validRecords.length) return null;
      const best = validRecords.reduce((current, record) => !current || record.kg > current.kg || (record.kg === current.kg && record.date > current.date) ? record : current, null);
      return { ...item, best, validSessions:validRecords.length };
    }).filter(Boolean);
    if (!values.length) return setEmpty(root, 'Aún no hay cargas guardadas. Las series sin carga registrada no se cuentan como cero.');
    for (const item of values) {
      const row = make('div', 'exercise-item');
      const name = make('span', '', item.name);
      name.append(make('small', '', `${item.validSessions} sesiones válidas · máximo ${dateLabel(item.best.date)}`));
      row.append(name, make('strong', '', formatLoad(item.best.kg, currentProfile?.units || 'metric')));
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
    const reviewKeys = new Set(validateMilestones(allSessions).review.map(item => historyRecordKey(item.session, item.record)));
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
        const value = make('span', '', performanceLabel(record));
        if (reviewKeys.has(historyRecordKey(session, record))) {
          row.classList.add('review-row');
          value.append(make('small', 'record-review-flag', 'Revisar · no cuenta para hitos'));
        }
        row.append(make('span', '', `${exercise}${set}`), value);
        performance.append(row);
      }
      details.append(summary, performance);
      root.append(details);
    }
  }
  function render() {
    const sessions = selectedSessions();
    renderMilestones(allSessions, currentProfile?.units || 'metric');
    renderSummary(sessions);
    renderSessionComparison(allSessions);
    renderPeriodComparisons(allSessions);
    renderWeeks(allSessions);
    renderDaily(allSessions);
    renderMonthly(allSessions);
    renderLoads(sessions);
    renderRoutines(sessions);
    renderHistory(sessions);
    status.textContent = `${sessions.length} de ${allSessions.length} sesiones disponibles · lectura local, sin cambios en tus datos.`;
    content.hidden = false;
  }
  let allSessions = [];
  let currentProfile = null;
  async function refresh() {
    if (!window.GymratikInstallGate?.isInstalled() || !window.TrainingProgressStore?.getHistory) {
      status.textContent = 'Para proteger tu privacidad, los registros solo se consultan desde la PWA instalada en este dispositivo.';
      status.dataset.state = 'error';
      content.hidden = true;
      return;
    }
    try {
      status.dataset.state = '';
      const [history, profile] = await Promise.all([
        window.TrainingProgressStore.getHistory(50),
        window.TrainingProgressStore.getProfile ? window.TrainingProgressStore.getProfile() : Promise.resolve(null),
      ]);
      allSessions = Array.isArray(history) ? history : [];
      currentProfile = profile;
      setMascotPreference(profile?.sex);
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
  document.addEventListener('visibilitychange', () => {
    document.documentElement.dataset.pageHidden = String(document.hidden);
    if (!document.hidden) refresh();
  });
  refresh();
})();
