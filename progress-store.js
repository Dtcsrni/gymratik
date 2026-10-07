(() => {
  'use strict';

  const DB_NAME = 'entrenamiento-progress';
  const DB_VERSION = 3;
  const PROGRESS_STORE = 'routineProgress';
  const SESSION_STORE = 'sessions';
  const ACTIVITY_STORE = 'activity';
  const PROFILE_STORE = 'profiles';
  const META_STORE = 'meta';
  const DEFAULT_PROFILE_ID = 'local-default';
  const PROFILE_SCHEMA_VERSION = 3;
  const FALLBACK_KEY = 'entrenamiento-progress-fallback-v3';
  const ROUTINES = {
    day1: { label: 'Día 1 · Espalda + Bíceps', totalExercises: 6, totalSeries: 20 },
    day2: { label: 'Día 2 · Pierna + Glúteo', totalExercises: 6, totalSeries: 20 },
    day3: { label: 'Día 3 · Pecho + Hombro + Tríceps', totalExercises: 7, totalSeries: 22 },
    day4: { label: 'Día 4 · Pierna equilibrada', totalExercises: 7, totalSeries: 20 },
  };
  const pad = value => String(value).padStart(2, '0');
  const numberOrZero = value => {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : 0;
  };
  const nonNegativeNumber = value => Math.max(0, numberOrZero(value));

  function requireInstalledApp() {
    if (!window.GymratikInstallGate?.isInstalled()) {
      throw new Error('Instala Gymratik para guardar y consultar tu perfil y avance.');
    }
  }

  function defaultProfile(timestamp = Date.now()) {
    return {
      profileId: DEFAULT_PROFILE_ID,
      displayName: '',
      birthDate: '',
      sex: '',
      heightCm: null,
      goal: 'general-fitness',
      units: 'metric',
      reminderDays: [],
      remindersEnabled: false,
      createdAt: timestamp,
      updatedAt: timestamp,
      schemaVersion: PROFILE_SCHEMA_VERSION,
    };
  }

  function normalizeProfile(input = {}) {
    const value = input && typeof input === 'object' ? input : {};
    const base = defaultProfile(Number(value.createdAt) || Date.now());
    const displayName = String(value.displayName || '').trim().slice(0, 80);
    const birthDate = String(value.birthDate || '').trim();
    if (birthDate && !/^\d{4}-\d{2}-\d{2}$/.test(birthDate)) throw new Error('La fecha de nacimiento no es válida');
    if (birthDate) {
      const parsed = new Date(`${birthDate}T00:00:00`);
      if (Number.isNaN(parsed.getTime()) || parsed > new Date()) throw new Error('La fecha de nacimiento no puede estar en el futuro');
    }
    const sex = ['', 'female', 'male', 'nonbinary', 'prefer-not-to-say'].includes(value.sex) ? value.sex : '';
    const height = value.heightCm === '' || value.heightCm === null || value.heightCm === undefined ? null : Number(value.heightCm);
    if (height !== null && (!Number.isFinite(height) || height < 100 || height > 250)) throw new Error('La altura debe estar entre 100 y 250 cm');
    const goal = ['strength', 'hypertrophy', 'general-fitness', 'mobility', 'health'].includes(value.goal) ? value.goal : base.goal;
    const units = value.units === 'imperial' ? 'imperial' : 'metric';
    const reminderDays = [...new Set((Array.isArray(value.reminderDays) ? value.reminderDays : [])
      .map(Number).filter(day => Number.isInteger(day) && day >= 0 && day <= 6))].sort();
    return {
      ...base,
      profileId: DEFAULT_PROFILE_ID,
      displayName,
      birthDate,
      sex,
      heightCm: height === null ? null : Math.round(height * 10) / 10,
      goal,
      units,
      reminderDays,
      remindersEnabled: value.remindersEnabled === true && reminderDays.length > 0,
      createdAt: Number(value.createdAt) || base.createdAt,
      updatedAt: Number(value.updatedAt) || Date.now(),
      schemaVersion: PROFILE_SCHEMA_VERSION,
    };
  }

  function timeKeys(timestamp = Date.now()) {
    const date = new Date(timestamp);
    const dayKey = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
    const hourKey = `${dayKey}T${pad(date.getHours())}`;
    const minuteKey = `${hourKey}:${pad(date.getMinutes())}`;
    return { dayKey, hourKey, minuteKey };
  }

  function trainingWeekKey(timestamp = Date.now()) {
    const date = new Date(timestamp);
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - ((date.getDay() + 6) % 7));
    return timeKeys(date.getTime()).dayKey;
  }

  function temporalRelation(timestamp, referenceTimestamp = Date.now()) {
    if (!timestamp) return 'none';
    const source = timeKeys(timestamp);
    const reference = timeKeys(referenceTimestamp);
    if (source.minuteKey === reference.minuteKey) return 'same-minute';
    if (source.hourKey === reference.hourKey) return 'same-hour';
    if (source.dayKey === reference.dayKey) return 'same-day';
    return 'other-day';
  }

  let databasePromise;
  const writeQueues = new Map();

  const emit = (name, detail = {}) => {
    window.dispatchEvent(new CustomEvent(name, { detail }));
  };

  function openDatabase() {
    if (databasePromise) return databasePromise;
    if (!('indexedDB' in window)) return Promise.reject(new Error('IndexedDB no está disponible'));
    databasePromise = new Promise((resolve, reject) => {
      let previousDatabaseVersion;
      const request = window.indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = (event) => {
        previousDatabaseVersion = event.oldVersion;
        const db = request.result;
        if (!db.objectStoreNames.contains(PROGRESS_STORE)) {
          const store = db.createObjectStore(PROGRESS_STORE, { keyPath: 'routineId' });
          store.createIndex('updatedAt', 'updatedAt');
        }
        if (!db.objectStoreNames.contains(SESSION_STORE)) {
          const store = db.createObjectStore(SESSION_STORE, { keyPath: 'sessionId' });
          store.createIndex('routineId', 'routineId');
          store.createIndex('status', 'status');
          store.createIndex('endedAt', 'endedAt');
        }
        if (!db.objectStoreNames.contains(ACTIVITY_STORE)) {
          const store = db.createObjectStore(ACTIVITY_STORE, { keyPath: 'activityKey' });
          store.createIndex('routineId', 'routineId');
          store.createIndex('dayKey', 'dayKey');
          store.createIndex('hourKey', 'hourKey');
          store.createIndex('minuteKey', 'minuteKey');
          store.createIndex('updatedAt', 'updatedAt');
        }
        if (!db.objectStoreNames.contains(PROFILE_STORE)) {
          db.createObjectStore(PROFILE_STORE, { keyPath: 'profileId' });
        }
        if (!db.objectStoreNames.contains(META_STORE)) {
          db.createObjectStore(META_STORE, { keyPath: 'key' });
        }
        const stores = [PROGRESS_STORE, SESSION_STORE, ACTIVITY_STORE];
        stores.forEach((storeName) => {
          const store = request.transaction.objectStore(storeName);
          if (!store.indexNames.contains('profileId')) store.createIndex('profileId', 'profileId');
          const cursorRequest = store.openCursor();
          cursorRequest.onsuccess = () => {
            const cursor = cursorRequest.result;
            if (!cursor) return;
            const value = cursor.value;
            if (!value.profileId) {
              value.profileId = DEFAULT_PROFILE_ID;
              cursor.update(value);
            }
            cursor.continue();
          };
        });
        const profileStore = request.transaction.objectStore(PROFILE_STORE);
        const profileRequest = profileStore.get(DEFAULT_PROFILE_ID);
        profileRequest.onsuccess = () => {
          if (!profileRequest.result) profileStore.put(defaultProfile());
        };
        request.transaction.objectStore(META_STORE).put({ key: 'schemaVersion', value: DB_VERSION, updatedAt: Date.now() });
      };
      request.onsuccess = () => {
        const db = request.result;
        db.onversionchange = () => db.close();
        if (previousDatabaseVersion > 0 && previousDatabaseVersion < DB_VERSION) {
          emit('training-database-upgraded', { version: DB_VERSION, previousVersion: previousDatabaseVersion, preservedExistingStores: true });
        }
        resolve(db);
      };
      request.onerror = () => {
        databasePromise = undefined;
        reject(request.error || new Error('No se pudo abrir IndexedDB'));
      };
      request.onblocked = () => {
        databasePromise = undefined;
        reject(new Error('IndexedDB está bloqueada por otra pestaña'));
      };
    });
    return databasePromise;
  }

  function transaction(db, stores, mode, operation) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(stores, mode);
      let result;
      try {
        result = operation(tx);
      } catch (error) {
        tx.abort();
        reject(error);
        return;
      }
      tx.oncomplete = () => resolve(result);
      tx.onerror = () => reject(tx.error || new Error('Transacción de almacenamiento fallida'));
      tx.onabort = () => reject(tx.error || new Error('Transacción de almacenamiento cancelada'));
    });
  }

  function enqueueWrite(routineId, operation) {
    const previous = writeQueues.get(routineId) || Promise.resolve();
    const next = previous.catch(() => {}).then(operation);
    writeQueues.set(routineId, next.finally(() => {
      if (writeQueues.get(routineId) === next) writeQueues.delete(routineId);
    }));
    return next;
  }

  function readFallback() {
    try {
      const value = JSON.parse(window.localStorage.getItem(FALLBACK_KEY) || '{}');
      return {
        progress: value.progress && typeof value.progress === 'object' ? value.progress : {},
        sessions: value.sessions && typeof value.sessions === 'object' ? value.sessions : {},
        activity: value.activity && typeof value.activity === 'object' ? value.activity : {},
        profiles: value.profiles && typeof value.profiles === 'object' ? value.profiles : {},
      };
    } catch (_) {
      return { progress: {}, sessions: {}, activity: {}, profiles: {} };
    }
  }

  function writeFallback(record) {
    try {
      const fallback = readFallback();
      fallback.progress[record.routineId] = record;
      if (record.sessionId) {
        fallback.sessions[record.sessionId] = toSession(record);
      }
      if (record.warmupCompleted && record.doneSeries > 0) fallback.activity[record.activityKey] = toActivity(record);
      window.localStorage.setItem(FALLBACK_KEY, JSON.stringify(fallback));
    } catch (error) {
      emit('training-storage-error', { error });
    }
  }

  function writeFallbackProfile(profile) {
    const fallback = readFallback();
    fallback.profiles[DEFAULT_PROFILE_ID] = profile;
    window.localStorage.setItem(FALLBACK_KEY, JSON.stringify(fallback));
  }

  function fallbackData() {
    const fallback = readFallback();
    return {
      progress: Object.values(fallback.progress).map((record) => ({ ...record, profileId: record.profileId || DEFAULT_PROFILE_ID })),
      sessions: Object.values(fallback.sessions).map((session) => ({ ...session, profileId: session.profileId || DEFAULT_PROFILE_ID })),
      activity: Object.values(fallback.activity).map((item) => ({ ...item, profileId: item.profileId || DEFAULT_PROFILE_ID })),
    };
  }

  function stateMetrics(state, routine) {
    const seriesKeys = Object.keys(state || {}).filter((key) => /^e\d+s\d+$/.test(key));
    const byExercise = new Map();
    seriesKeys.forEach((key) => {
      const exercise = key.match(/^e(\d+)s\d+$/)?.[1];
      if (!exercise) return;
      if (!byExercise.has(exercise)) byExercise.set(exercise, []);
      byExercise.get(exercise).push(state[key] === true);
    });
    const doneSeries = seriesKeys.reduce((sum, key) => sum + Number(state[key] === true), 0);
    const skippedExercises = state?.__skippedExercises && typeof state.__skippedExercises === 'object' ? state.__skippedExercises : {};
    const completedExerciseIds = new Set([...byExercise.entries()]
      .filter(([, series]) => series.length > 0 && series.every(Boolean))
      .map(([exerciseId]) => exerciseId));
    Object.entries(skippedExercises).forEach(([exerciseId, skipped]) => {
      const numericId = Number(exerciseId);
      if (skipped === true && Number.isInteger(numericId) && numericId >= 1 && numericId <= routine.totalExercises) completedExerciseIds.add(exerciseId);
    });
    const completedExercises = completedExerciseIds.size;
    const skippedExerciseCount = Object.entries(skippedExercises).filter(([exerciseId, skipped]) => skipped === true && Number.isInteger(Number(exerciseId)) && Number(exerciseId) >= 1 && Number(exerciseId) <= routine.totalExercises).length;
    const timing = state && state.__timing && typeof state.__timing === 'object' ? state.__timing : {};
    const warmupCompleted = timing.warmup?.phase === 'done';
    const sessionStartedAt = Number.isFinite(Number(timing.sessionStartedAt)) ? Number(timing.sessionStartedAt) : 0;
    const sessionEndedAt = Number.isFinite(Number(timing.sessionEndedAt)) ? Number(timing.sessionEndedAt) : 0;
    return {
      totalExercises: routine.totalExercises,
      totalSeries: routine.totalSeries,
      doneSeries,
      warmupCompleted,
      completedExercises,
      skippedExerciseCount,
      sessionStartedAt,
      sessionEndedAt,
      sessionId: sessionStartedAt ? `${routine.id}:${sessionStartedAt}` : null,
    };
  }

  function normalizeSnapshot({ routineId, state, totalExercises, totalSeries }) {
    const base = ROUTINES[routineId];
    if (!base) throw new Error(`Rutina no reconocida: ${routineId}`);
    const routine = { ...base, id: routineId, totalExercises: totalExercises || base.totalExercises, totalSeries: totalSeries || base.totalSeries };
    const metrics = stateMetrics(state || {}, routine);
    const capturedAt = Date.now();
    const temporal = timeKeys(capturedAt);
    const sessionId = metrics.sessionId;
    return {
      profileId: DEFAULT_PROFILE_ID,
      routineId,
      label: routine.label,
      totalExercises: metrics.totalExercises,
      totalSeries: metrics.totalSeries,
      doneSeries: metrics.doneSeries,
      warmupCompleted: metrics.warmupCompleted,
      completedExercises: metrics.completedExercises,
      skippedExercises: metrics.skippedExerciseCount,
      sessionStartedAt: metrics.sessionStartedAt,
      sessionEndedAt: metrics.sessionEndedAt,
      sessionId,
      weekKey: trainingWeekKey(metrics.sessionStartedAt || capturedAt),
      performance: Object.entries(state?.__performance || {}).flatMap(([exerciseId, sets]) =>
        Object.entries(sets || {}).filter(([setKey, value]) => /^e\d+s\d+$/.test(setKey) && state[setKey] === true && value && Number.isFinite(Number(value.reps)) && Number(value.reps) >= 1)
          .map(([setKey, value]) => {
            const load = value.load === '' || value.load == null || !Number.isFinite(Number(value.load)) ? null : Math.min(2000, Math.max(0, Number(value.load)));
            const loadUnit = value.loadUnit === 'lb' ? 'lb' : 'kg';
            const durationMs = Number.isFinite(Number(value.durationMs)) ? Math.min(24 * 60 * 60 * 1000, Math.max(0, Math.round(Number(value.durationMs)))) : null;
            return { exerciseId: String(exerciseId).slice(0, 80), exerciseName: String(value.title || '').slice(0, 100), setKey, setNumber: Number(setKey.match(/s(\d+)$/)?.[1]) || 0, reps: Math.min(100, Math.round(Number(value.reps))), load, loadUnit, loadKg: load === null ? null : loadUnit === 'lb' ? load * 0.45359237 : load, ...(durationMs === null ? {} : { durationMs }), updatedAt: Number(value.updatedAt) || capturedAt };
          })
      ),
      capturedAt,
      ...temporal,
      activityKey: `${routineId}:${sessionId || 'unscheduled'}:${temporal.minuteKey}`,
      updatedAt: capturedAt,
    };
  }

  function toSession(record) {
    return {
      profileId: record.profileId || DEFAULT_PROFILE_ID,
      sessionId: record.sessionId,
      routineId: record.routineId,
      label: record.label,
      startedAt: record.sessionStartedAt,
      endedAt: record.sessionEndedAt || 0,
      status: record.sessionEndedAt ? 'completed' : 'active',
      completedSeries: nonNegativeNumber(record.doneSeries ?? record.completedSeries),
      warmupCompleted: record.warmupCompleted === true,
      completedExercises: nonNegativeNumber(record.completedExercises),
      skippedExercises: nonNegativeNumber(record.skippedExercises),
      totalSeries: nonNegativeNumber(record.totalSeries),
      updatedAt: record.updatedAt,
      performance: Array.isArray(record.performance) ? record.performance : [],
    };
  }

  function toActivity(record) {
    const capturedAt = record.capturedAt || record.updatedAt || Date.now();
    const startedAt = Number(record.startedAt || record.sessionStartedAt) || 0;
    // Attribution to "today" must follow the workout start, not a later
    // persistence/backfill timestamp that can refresh an older session.
    const temporal = timeKeys(startedAt || capturedAt);
    const sessionId = record.sessionId || null;
    const activityKey = record.activityKey || `${record.routineId}:${sessionId || 'unscheduled'}:${temporal.minuteKey}`;
    return {
      profileId: record.profileId || DEFAULT_PROFILE_ID,
      activityKey,
      routineId: record.routineId,
      sessionId,
      label: record.label,
      dayKey: startedAt ? temporal.dayKey : record.dayKey || temporal.dayKey,
      hourKey: startedAt ? temporal.hourKey : record.hourKey || temporal.hourKey,
      minuteKey: startedAt ? temporal.minuteKey : record.minuteKey || temporal.minuteKey,
      capturedAt,
      completedSeries: nonNegativeNumber(record.doneSeries ?? record.completedSeries),
      warmupCompleted: record.warmupCompleted === true,
      totalSeries: nonNegativeNumber(record.totalSeries),
      startedAt: startedAt || 0,
      endedAt: Number(record.endedAt || record.sessionEndedAt) || 0,
      updatedAt: record.updatedAt,
      performance: Array.isArray(record.performance) ? record.performance : [],
    };
  }

  async function capture(payload) {
    requireInstalledApp();
    const record = normalizeSnapshot(payload);
    return enqueueWrite(record.routineId, async () => {
      try {
        const db = await openDatabase();
        await transaction(db, [PROGRESS_STORE, SESSION_STORE, ACTIVITY_STORE], 'readwrite', (tx) => {
          tx.objectStore(PROGRESS_STORE).put(record);
          if (record.sessionId) tx.objectStore(SESSION_STORE).put(toSession(record));
          if (record.warmupCompleted && record.doneSeries > 0) tx.objectStore(ACTIVITY_STORE).put(toActivity(record));
        });
        emit('training-progress-updated', { source: 'indexeddb', record });
        return { source: 'indexeddb', record };
      } catch (error) {
        writeFallback(record);
        emit('training-storage-error', { error, fallback: true });
        emit('training-progress-updated', { source: 'localstorage', record });
        return { source: 'localstorage', record };
      }
    });
  }

  async function getProfile() {
    requireInstalledApp();
    const fallbackProfile = readFallback().profiles[DEFAULT_PROFILE_ID];
    let databaseProfile;
    try {
      const db = await openDatabase();
      databaseProfile = await transaction(db, [PROFILE_STORE], 'readonly', (tx) => {
        const request = tx.objectStore(PROFILE_STORE).get(DEFAULT_PROFILE_ID);
        return request;
      }).then((request) => request.result);
    } catch (_) {
      databaseProfile = undefined;
    }
    const selected = [fallbackProfile, databaseProfile]
      .filter(Boolean)
      .sort((left, right) => Number(right.updatedAt || 0) - Number(left.updatedAt || 0))[0];
    return normalizeProfile(selected || defaultProfile());
  }

  async function saveProfile(input) {
    requireInstalledApp();
    const profile = normalizeProfile(input);
    return enqueueWrite('__profile__', async () => {
      try {
        const db = await openDatabase();
        await transaction(db, [PROFILE_STORE, META_STORE], 'readwrite', (tx) => {
          tx.objectStore(PROFILE_STORE).put(profile);
          tx.objectStore(META_STORE).put({ key: 'activeProfileId', value: DEFAULT_PROFILE_ID, updatedAt: profile.updatedAt });
        });
        try { writeFallbackProfile(profile); } catch (fallbackError) { emit('training-storage-error', { error: fallbackError, source: 'fallback-mirror' }); }
        emit('training-profile-updated', { source: 'indexeddb', profile });
        return { source: 'indexeddb', profile };
      } catch (error) {
        try { writeFallbackProfile(profile); } catch (fallbackError) { emit('training-storage-error', { error: fallbackError }); throw fallbackError; }
        emit('training-storage-error', { error, fallback: true });
        emit('training-profile-updated', { source: 'localstorage', profile });
        return { source: 'localstorage', profile };
      }
    });
  }

  async function getHistory(limit = 12) {
    requireInstalledApp();
    const data = await readDatabase();
    return data.sessions
      .filter((session) => session && session.sessionId)
      .sort((left, right) => Number(right.updatedAt || right.endedAt || right.startedAt || 0) - Number(left.updatedAt || left.endedAt || left.startedAt || 0))
      .slice(0, Math.max(1, Math.min(50, Number(limit) || 12)));
  }

  function exportFallbackData(profile, data) {
    const fallback = readFallback();
    fallback.profiles[DEFAULT_PROFILE_ID] = profile;
    fallback.progress = Object.fromEntries(data.progress.map((record) => [record.routineId, record]));
    fallback.sessions = Object.fromEntries(data.sessions.map((session) => [session.sessionId, session]));
    fallback.activity = Object.fromEntries(data.activity.map((item) => [item.activityKey, item]));
    window.localStorage.setItem(FALLBACK_KEY, JSON.stringify(fallback));
  }

  async function exportData() {
    requireInstalledApp();
    const profile = await getProfile();
    const data = await readDatabase();
    return {
      format: 'gymratik-backup',
      schemaVersion: 3,
      exportedAt: Date.now(),
      profile,
      data,
    };
  }

  function normalizeImport(payload) {
    if (!payload || payload.format !== 'gymratik-backup' || payload.schemaVersion !== 3 || payload.profile?.schemaVersion !== 3) throw new Error('El archivo no es un respaldo Gymratik compatible con el esquema 3');
    const data = payload.data && typeof payload.data === 'object' ? payload.data : {};
    const arrays = ['progress', 'sessions', 'activity'];
    arrays.forEach((name) => { if (!Array.isArray(data[name]) || data[name].length > 10000) throw new Error(`El respaldo tiene una colección inválida: ${name}`); });
    const progress = data.progress.filter((record) => record && ROUTINES[record.routineId]).map((record) => ({ ...record, profileId: DEFAULT_PROFILE_ID }));
    const sessions = data.sessions.filter((session) => session && typeof session.sessionId === 'string' && ROUTINES[session.routineId]).map((session) => {
      const performance = session.performance === undefined ? [] : session.performance;
      if (!Array.isArray(performance) || performance.length > 100) throw new Error('El respaldo contiene un registro de series inválido');
      const cleanPerformance = performance.filter(record => record && typeof record === 'object').map(record => {
        const reps = Number(record.reps);
        const load = record.load === null || record.load === '' || record.load === undefined ? null : Number(record.load);
        const durationMs = record.durationMs === null || record.durationMs === undefined ? null : Number(record.durationMs);
        if (!Number.isInteger(reps) || reps < 1 || reps > 100 || (load !== null && (!Number.isFinite(load) || load < 0 || load > 2000)) || (durationMs !== null && (!Number.isFinite(durationMs) || durationMs < 0 || durationMs > 24 * 60 * 60 * 1000))) throw new Error('El respaldo contiene repeticiones, carga o duración fuera de rango');
        const loadUnit = record.loadUnit === 'lb' ? 'lb' : 'kg';
        return { exerciseId: String(record.exerciseId || '').slice(0, 80), exerciseName: String(record.exerciseName || '').slice(0, 100), setKey: String(record.setKey || '').slice(0, 16), setNumber: Math.max(0, Math.min(100, Math.round(Number(record.setNumber) || 0))), reps, load, loadUnit, loadKg: load === null ? null : loadUnit === 'lb' ? load * 0.45359237 : load, ...(durationMs === null ? {} : { durationMs: Math.round(durationMs) }), updatedAt: Number(record.updatedAt) || Number(session.updatedAt) || Date.now() };
      });
      return { ...session, performance: cleanPerformance, profileId: DEFAULT_PROFILE_ID };
    });
    const activity = data.activity.filter((item) => item && typeof item.activityKey === 'string' && ROUTINES[item.routineId]).map((item) => ({ ...item, profileId: DEFAULT_PROFILE_ID }));
    return { profile: normalizeProfile(payload.profile), data: { progress, sessions, activity } };
  }

  async function importData(payload) {
    requireInstalledApp();
    const imported = normalizeImport(payload);
    await Promise.all([...writeQueues.values()].map((queue) => queue.catch(() => {})));
    try {
      const db = await openDatabase();
      await transaction(db, [PROGRESS_STORE, SESSION_STORE, ACTIVITY_STORE, PROFILE_STORE, META_STORE], 'readwrite', (tx) => {
        tx.objectStore(PROGRESS_STORE).clear();
        tx.objectStore(SESSION_STORE).clear();
        tx.objectStore(ACTIVITY_STORE).clear();
        imported.data.progress.forEach((record) => tx.objectStore(PROGRESS_STORE).put(record));
        imported.data.sessions.forEach((session) => tx.objectStore(SESSION_STORE).put(session));
        imported.data.activity.forEach((item) => tx.objectStore(ACTIVITY_STORE).put(item));
        tx.objectStore(PROFILE_STORE).put(imported.profile);
        tx.objectStore(META_STORE).put({ key: 'activeProfileId', value: DEFAULT_PROFILE_ID, updatedAt: Date.now() });
      });
      try { exportFallbackData(imported.profile, imported.data); } catch (fallbackError) { emit('training-storage-error', { error: fallbackError, source: 'fallback-mirror' }); }
      emit('training-progress-updated', { source: 'indexeddb', imported: true });
      emit('training-profile-updated', { source: 'indexeddb', profile: imported.profile });
      return { source: 'indexeddb', imported: true, profile: imported.profile, counts: { progress: imported.data.progress.length, sessions: imported.data.sessions.length, activity: imported.data.activity.length } };
    } catch (error) {
      exportFallbackData(imported.profile, imported.data);
      emit('training-storage-error', { error, fallback: true });
      emit('training-progress-updated', { source: 'localstorage', imported: true });
      emit('training-profile-updated', { source: 'localstorage', profile: imported.profile });
      return { source: 'localstorage', imported: true, profile: imported.profile, counts: { progress: imported.data.progress.length, sessions: imported.data.sessions.length, activity: imported.data.activity.length } };
    }
  }

  async function clearAll() {
    requireInstalledApp();
    await Promise.all([...writeQueues.values()].map((queue) => queue.catch(() => {})));
    let source = 'indexeddb';
    let databaseError;
    if ('indexedDB' in window) {
      try {
        const db = await openDatabase();
        await transaction(db, [PROGRESS_STORE, SESSION_STORE, ACTIVITY_STORE], 'readwrite', (tx) => {
          tx.objectStore(PROGRESS_STORE).clear();
          tx.objectStore(SESSION_STORE).clear();
          tx.objectStore(ACTIVITY_STORE).clear();
        });
      } catch (error) {
        databaseError = error;
        source = 'localstorage';
        emit('training-storage-error', { error, fallback: true });
      }
    }
    try {
      window.localStorage.removeItem(FALLBACK_KEY);
      Object.keys(ROUTINES).forEach((routineId) => window.localStorage.removeItem(`fitlovers-${routineId}-series-v1`));
    } catch (error) {
      emit('training-storage-error', { error });
      throw error;
    }
    if (databaseError) throw databaseError;
    emit('training-progress-updated', { source, cleared: true });
    return { source, cleared: true };
  }

  function deleteByRoutine(tx, storeName, routineId) {
    const store = tx.objectStore(storeName);
    const request = store.index('routineId').openCursor(window.IDBKeyRange.only(routineId));
    request.onsuccess = () => {
      const cursor = request.result;
      if (!cursor) return;
      cursor.delete();
      cursor.continue();
    };
  }

  async function clearRoutine(routineId) {
    requireInstalledApp();
    if (!ROUTINES[routineId]) throw new Error(`Rutina no reconocida: ${routineId}`);
    await (writeQueues.get(routineId) || Promise.resolve()).catch(() => {});
    let databaseError;
    if ('indexedDB' in window) {
      try {
        const db = await openDatabase();
        await transaction(db, [PROGRESS_STORE, SESSION_STORE, ACTIVITY_STORE], 'readwrite', (tx) => {
          tx.objectStore(PROGRESS_STORE).delete(routineId);
          deleteByRoutine(tx, SESSION_STORE, routineId);
          deleteByRoutine(tx, ACTIVITY_STORE, routineId);
        });
      } catch (error) {
        databaseError = error;
        emit('training-storage-error', { error, fallback: true });
      }
    }
    try {
      const fallback = readFallback();
      delete fallback.progress[routineId];
      Object.keys(fallback.sessions).forEach((key) => { if (fallback.sessions[key]?.routineId === routineId) delete fallback.sessions[key]; });
      Object.keys(fallback.activity).forEach((key) => { if (fallback.activity[key]?.routineId === routineId) delete fallback.activity[key]; });
      window.localStorage.setItem(FALLBACK_KEY, JSON.stringify(fallback));
      window.localStorage.removeItem(`fitlovers-${routineId}-series-v1`);
    } catch (error) {
      emit('training-storage-error', { error });
      throw error;
    }
    if (databaseError) throw databaseError;
    emit('training-progress-updated', { routineId, cleared: true });
    return { routineId, cleared: true };
  }

  async function readDatabase() {
    try {
      const db = await openDatabase();
      const databaseData = await transaction(db, [PROGRESS_STORE, SESSION_STORE, ACTIVITY_STORE], 'readonly', (tx) => {
        const progressRequest = tx.objectStore(PROGRESS_STORE).getAll();
        const sessionsRequest = tx.objectStore(SESSION_STORE).getAll();
        const activityRequest = tx.objectStore(ACTIVITY_STORE).getAll();
        return { progressRequest, sessionsRequest, activityRequest };
      }).then(({ progressRequest, sessionsRequest, activityRequest }) => ({
        progress: progressRequest.result || [],
        sessions: sessionsRequest.result || [],
        activity: activityRequest.result || [],
      }));
      const fallback = readFallback();
      const progress = new Map();
      [...Object.values(fallback.progress), ...databaseData.progress].forEach((record) => {
        const current = progress.get(record.routineId);
        if (!current || (record.updatedAt || 0) >= (current.updatedAt || 0)) progress.set(record.routineId, record);
      });
      const sessions = new Map();
      [...Object.values(fallback.sessions), ...databaseData.sessions].forEach((session) => {
        const current = sessions.get(session.sessionId);
        if (!current || (session.updatedAt || 0) >= (current.updatedAt || 0)) sessions.set(session.sessionId, session);
      });
      const activity = new Map();
      [...Object.values(fallback.activity), ...databaseData.activity].forEach((item) => {
        const current = activity.get(item.activityKey);
        if (!current || (item.updatedAt || 0) >= (current.updatedAt || 0)) activity.set(item.activityKey, item);
      });
      return { progress: [...progress.values()], sessions: [...sessions.values()], activity: [...activity.values()] };
    } catch (_) {
      return fallbackData();
    }
  }

  async function backfillActivity(data) {
    const known = new Set(data.activity.map((item) => item.activityKey));
    const missing = data.progress
      .filter((record) => record.warmupCompleted === true && nonNegativeNumber(record.doneSeries) > 0)
      .map(toActivity)
      .filter((item) => !known.has(item.activityKey));
    if (!missing.length) return data;
    try {
      const db = await openDatabase();
      await transaction(db, [ACTIVITY_STORE], 'readwrite', (tx) => {
        missing.forEach((item) => tx.objectStore(ACTIVITY_STORE).put(item));
      });
    } catch (error) {
      missing.forEach((item) => {
        const fallback = readFallback();
        fallback.activity[item.activityKey] = item;
        try { window.localStorage.setItem(FALLBACK_KEY, JSON.stringify(fallback)); } catch (error) { emit('training-storage-error', { error }); }
      });
    }
    data.activity.push(...missing);
    return data;
  }

  function dashboardFrom(data) {
    const currentWeek = trainingWeekKey();
    const currentWeekProgress = data.progress.filter((record) => (record.weekKey || trainingWeekKey(record.sessionStartedAt || record.updatedAt)) === currentWeek);
    const progressByRoutine = new Map(currentWeekProgress.map((record) => [record.routineId, record]));
    const sessionsById = new Map(data.sessions.map((session) => [session.sessionId, session]));
    const progressBySessionId = new Map(data.progress.filter((record) => record.sessionId).map((record) => [record.sessionId, record]));
    const sessions = data.sessions.filter((session) => session.status === 'completed');
    const completedSeries = sessions.reduce((sum, session) => sum + nonNegativeNumber(session.completedSeries), 0);
    const activeSeries = currentWeekProgress.reduce((sum, record) => sum + (record.sessionEndedAt ? 0 : nonNegativeNumber(record.doneSeries)), 0);
    const currentSeries = currentWeekProgress.reduce((sum, record) => sum + nonNegativeNumber(record.doneSeries), 0);
    const plannedSeries = Object.values(ROUTINES).reduce((sum, routine) => sum + routine.totalSeries, 0);
    const now = Date.now();
    const nowKeys = timeKeys(now);
    const activity = (data.activity || []).map((record) => {
      const session = record.sessionId ? sessionsById.get(record.sessionId) : null;
      const progress = record.sessionId ? progressBySessionId.get(record.sessionId) : null;
      if ((!session || session.routineId !== record.routineId) && (!progress || progress.routineId !== record.routineId)) return toActivity(record);
      // Older activity rows can lack timestamps or carry a recapture day. Only
      // inherit dates from the exact linked session, never from routine alone.
      return toActivity({
        ...record,
        startedAt: record.startedAt || record.sessionStartedAt || session?.startedAt || progress?.sessionStartedAt,
        endedAt: record.endedAt || record.sessionEndedAt || session?.endedAt || progress?.sessionEndedAt,
        completedSeries: record.completedSeries ?? record.doneSeries ?? session?.completedSeries ?? progress?.doneSeries,
      });
    })
      .filter((item) => item.warmupCompleted === true && nonNegativeNumber(item.completedSeries) > 0);
    const activityTime = (item) => Number(item?.endedAt || item?.startedAt || item?.capturedAt || item?.updatedAt) || 0;
    const latestActivity = activity.reduce((latest, item) => activityTime(item) > activityTime(latest) ? item : latest, null);
    const lastActivity = activityTime(latestActivity);
    const relation = temporalRelation(lastActivity, now);
    const todayBySession = new Map();
    activity.filter((item) => item.dayKey === nowKeys.dayKey).forEach((item) => {
      const key = `${item.routineId}:${item.sessionId || item.activityKey}`;
      const current = todayBySession.get(key);
      const completedSeriesForDay = nonNegativeNumber(item.completedSeries);
      if (!current || completedSeriesForDay > current) todayBySession.set(key, completedSeriesForDay);
    });
    return {
      plannedSeries,
      recordedSeries: completedSeries + activeSeries,
      currentSeries,
      todaySeries: [...todayBySession.values()].reduce((sum, value) => sum + value, 0),
      activityDays: new Set(activity.map((item) => item.dayKey).filter(Boolean)).size,
      currentPlanPercent: plannedSeries ? Math.min(100, Math.round((currentSeries / plannedSeries) * 100)) : 0,
      sessionsStarted: new Set(data.sessions.map((session) => session.sessionId)).size,
      sessionsCompleted: sessions.length,
      lastActivity,
      temporal: {
        relation,
        sameMinute: relation === 'same-minute',
        sameHour: relation === 'same-minute' || relation === 'same-hour',
        sameDay: relation === 'same-minute' || relation === 'same-hour' || relation === 'same-day',
        otherDay: relation === 'other-day',
        dayKey: nowKeys.dayKey,
      },
      routines: Object.entries(ROUTINES).map(([routineId, routine]) => {
        const record = progressByRoutine.get(routineId);
        return {
          routineId,
          label: routine.label,
          totalExercises: routine.totalExercises,
          totalSeries: routine.totalSeries,
          doneSeries: nonNegativeNumber(record?.doneSeries),
          completedExercises: nonNegativeNumber(record?.completedExercises),
          updatedAt: nonNegativeNumber(record?.updatedAt),
          sessionStartedAt: nonNegativeNumber(record?.sessionStartedAt),
          sessionEndedAt: nonNegativeNumber(record?.sessionEndedAt),
          percent: record ? Math.min(100, Math.round((nonNegativeNumber(record.doneSeries) / routine.totalSeries) * 100)) : 0,
        };
      }),
    };
  }

  async function restoreMissingRoutineProgress() {
    requireInstalledApp();
    const existing = await readDatabase();
    const knownRoutines = new Set(existing.progress.map((record) => record?.routineId));
    let restored = 0;
    for (const routineId of Object.keys(ROUTINES)) {
      if (knownRoutines.has(routineId)) continue;
      let state;
      try {
        state = JSON.parse(window.localStorage.getItem(`fitlovers-${routineId}-series-v1`) || 'null');
      } catch (_) {
        state = null;
      }
      if (!state || typeof state !== 'object' || Array.isArray(state)) continue;
      const hasSavedProgress = Object.entries(state).some(([key, value]) => /^e\d+s\d+$/.test(key) && value === true)
        || Number(state.__timing?.sessionStartedAt) > 0
        || Number(state.__timing?.warmup?.preparationEndsAt) > 0;
      if (!hasSavedProgress) continue;
      await capture({ routineId, state });
      restored += 1;
    }
    return restored;
  }

  async function getDashboard() {
    requireInstalledApp();
    await restoreMissingRoutineProgress();
    const data = await backfillActivity(await readDatabase());
    return dashboardFrom(data);
  }

  async function requestPersistence() {
    requireInstalledApp();
    if (!navigator.storage?.persist) return false;
    try {
      return await navigator.storage.persist();
    } catch (_) {
      return false;
    }
  }

  async function storageStatus() {
    const persistent = navigator.storage?.persisted ? await navigator.storage.persisted().catch(() => false) : false;
    return { indexedDB: 'indexedDB' in window, persistent };
  }

  window.TrainingProgressStore = Object.freeze({ capture, clearAll, clearRoutine, getDashboard, getProfile, saveProfile, getHistory, exportData, importData, requestPersistence, storageStatus, classifyTemporalRelation: temporalRelation });
})();
