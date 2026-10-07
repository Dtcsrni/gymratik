import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
STORE = ROOT / "progress-store.js"


class ProgressStoreRuntimeTests(unittest.TestCase):
    def test_previous_week_progress_is_excluded_from_current_plan_without_deleting_history(self):
        script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const startedAt = Date.now() - 8 * 24 * 60 * 60 * 1000;
const currentStartedAt = Date.now() - 60 * 1000;
const endedAt = startedAt + 60 * 60 * 1000;
const oldSession = `day1:${startedAt}`;
const currentWeek = new Date(); currentWeek.setHours(0,0,0,0); currentWeek.setDate(currentWeek.getDate() - ((currentWeek.getDay()+6)%7));
const weekKey = `${currentWeek.getFullYear()}-${String(currentWeek.getMonth()+1).padStart(2,'0')}-${String(currentWeek.getDate()).padStart(2,'0')}`;
const fallback = JSON.stringify({
  progress: {
    day1: { routineId: 'day1', sessionId: oldSession, doneSeries: 20, totalSeries: 20, sessionStartedAt: startedAt, sessionEndedAt: endedAt, updatedAt: Date.now() },
    day2: { routineId: 'day2', weekKey, doneSeries: 2, totalSeries: 20, sessionStartedAt: currentStartedAt, sessionEndedAt: 0, updatedAt: Date.now() }
  },
  sessions: { [oldSession]: { sessionId: oldSession, routineId: 'day1', startedAt, endedAt, status: 'completed', completedSeries: 20, totalSeries: 20, updatedAt: endedAt } },
  activity: {}
});
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } }, dispatchEvent() {},
  localStorage: { getItem() { return fallback; }, setItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
window.TrainingProgressStore.getDashboard().then(dashboard => {
  assert.strictEqual(dashboard.routines.find(row => row.routineId === 'day1').doneSeries, 0);
  assert.strictEqual(dashboard.routines.find(row => row.routineId === 'day2').doneSeries, 2);
  assert.strictEqual(dashboard.currentSeries, 2);
  assert.strictEqual(dashboard.sessionsCompleted, 1);
  assert.strictEqual(dashboard.recordedSeries, 22, 'last-week workout remains in history alongside current-week activity');
  console.log(JSON.stringify({ ok: true }));
}).catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_legacy_activity_without_start_uses_linked_session_date(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const startedAt = Date.now() - 48 * 60 * 60 * 1000;
const today = new Date();
const todayKey = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
const sessionId = `day1:${startedAt}`;
const fallback = JSON.stringify({
  progress: { day1: { routineId: 'day1', sessionId, doneSeries: 22, warmupCompleted: true, sessionStartedAt: startedAt, sessionEndedAt: startedAt + 3600000, updatedAt: Date.now() } },
  sessions: { [sessionId]: { sessionId, routineId: 'day1', startedAt, endedAt: startedAt + 3600000, completedSeries: 22, warmupCompleted: true, status: 'completed', updatedAt: Date.now() } },
  activity: { legacy: { activityKey: 'day1:legacy', routineId: 'day1', sessionId, dayKey: todayKey, capturedAt: Date.now(), completedSeries: 22, warmupCompleted: true, updatedAt: Date.now() } }
});
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {}, localStorage: { getItem() { return fallback; }, setItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
window.TrainingProgressStore.getDashboard().then((dashboard) => {
  assert.strictEqual(dashboard.todaySeries, 0, 'legacy activity must inherit the linked historical session date');
  assert.strictEqual(dashboard.routines[0].doneSeries, 0, 'last-week progress must not appear in this-week routine status');
  assert.strictEqual(dashboard.temporal.otherDay, true, 'latest activity must use its linked session timestamp');
  assert.strictEqual(dashboard.lastActivity, startedAt + 3600000, 'legacy rows must retain the linked session end timestamp');
  console.log(JSON.stringify({ ok: true }));
}).catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_old_session_recaptured_today_does_not_count_as_training_today(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const startedAt = Date.now() - 48 * 60 * 60 * 1000;
const today = new Date();
const todayKey = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
const fallback = JSON.stringify({
  progress: { day1: { routineId: 'day1', doneSeries: 22, warmupCompleted: true, sessionStartedAt: startedAt, sessionEndedAt: startedAt + 3600000, updatedAt: Date.now() } },
  sessions: {},
  activity: { old: { activityKey: 'day1:old', routineId: 'day1', sessionId: `day1:${startedAt}`, dayKey: todayKey, startedAt, capturedAt: Date.now(), completedSeries: 22, warmupCompleted: true, updatedAt: Date.now() } }
});
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {}, localStorage: { getItem() { return fallback; }, setItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
window.TrainingProgressStore.getDashboard().then((dashboard) => {
  assert.strictEqual(dashboard.todaySeries, 0, 'a session started two days ago must not be attributed to today');
  assert.strictEqual(dashboard.routines[0].doneSeries, 0, 'last-week progress must not appear in this-week routine status');
  assert.strictEqual(dashboard.temporal.otherDay, true, 'the last-session label must use the workout date, not its recapture date');
  assert.strictEqual(dashboard.lastActivity, startedAt + 3600000, 'recapturing old progress must retain the original session end timestamp');
  console.log(JSON.stringify({ ok: true }));
}).catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_capture_of_historical_session_keeps_its_original_activity_day(self):
        script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
let persisted = null;
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {}, localStorage: { getItem() { return persisted; }, setItem(_key, value) { persisted = value; } }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
(async () => {
  const startedAt = Date.now() - 48 * 60 * 60 * 1000;
  const day = new Date(startedAt);
  const expectedDay = `${day.getFullYear()}-${String(day.getMonth()+1).padStart(2,'0')}-${String(day.getDate()).padStart(2,'0')}`;
  await window.TrainingProgressStore.capture({ routineId: 'day2', state: { e1s1: true, __timing: { sessionStartedAt: startedAt, warmup: { phase: 'done' } } } });
  const backup = await window.TrainingProgressStore.exportData();
  assert.strictEqual(backup.data.activity[0].dayKey, expectedDay);
  assert.strictEqual((await window.TrainingProgressStore.getDashboard()).todaySeries, 0);
  console.log(JSON.stringify({ ok: true }));
})().catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_activity_requires_completed_warmup_and_at_least_one_work_set_for_all_routines(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
let persisted = null;
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return persisted; }, setItem(_key, value) { persisted = value; } }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
const store = window.TrainingProgressStore;
(async () => {
  for (const routineId of ['day1', 'day2', 'day3', 'day4']) {
    const start = Date.now();
    const activityCountBefore = (await store.exportData()).data.activity.length;
    await store.capture({ routineId, state: { __timing: { sessionStartedAt: start, warmup: { phase: 'idle' } }, e1s1: true } });
    assert.strictEqual((await store.exportData()).data.activity.length, activityCountBefore, `${routineId}: no activity before warm-up`);
    await store.capture({ routineId, state: { __timing: { sessionStartedAt: start, warmup: { phase: 'done' } } } });
    assert.strictEqual((await store.exportData()).data.activity.length, activityCountBefore, `${routineId}: warm-up alone is not activity`);
    await store.capture({ routineId, state: { __timing: { sessionStartedAt: start, warmup: { phase: 'done' } }, e1s1: true } });
  }
  const backup = await store.exportData();
  assert.strictEqual(backup.data.activity.length, 4);
  assert.ok(backup.data.activity.every((item) => item.warmupCompleted === true && item.completedSeries >= 1));
  assert.strictEqual((await store.getDashboard()).activityDays, 1);
  console.log(JSON.stringify({ ok: true }));
})().catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_temporal_boundaries_are_classified_without_duplicate_contexts(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return null; }, setItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
const classify = window.TrainingProgressStore.classifyTemporalRelation;
const base = new Date(2026, 8, 19, 12, 34, 0).getTime();
assert.strictEqual(classify(base, base + 30 * 1000), 'same-minute');
assert.strictEqual(classify(base, base + 2 * 60 * 1000), 'same-hour');
assert.strictEqual(classify(base, base + 2 * 60 * 60 * 1000), 'same-day');
assert.strictEqual(classify(base, base + 24 * 60 * 60 * 1000), 'other-day');
console.log(JSON.stringify({ ok: true }));
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_malformed_persisted_numbers_do_not_produce_nan_or_undefined_dashboard_values(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const fallback = JSON.stringify({
  progress: {
    day1: { routineId: 'day1', doneSeries: 'invalid', completedExercises: undefined, sessionEndedAt: 0, updatedAt: 'invalid' }
  },
  sessions: {
    'day1:bad': { sessionId: 'day1:bad', status: 'completed', completedSeries: 'invalid', updatedAt: 'invalid' }
  },
  activity: {
    bad: { activityKey: 'bad', routineId: 'day1', dayKey: '2026-09-19', completedSeries: 'invalid', updatedAt: 'invalid' }
  }
});
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return fallback; }, setItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
window.TrainingProgressStore.getDashboard().then((dashboard) => {
  assert.strictEqual(dashboard.recordedSeries, 0);
  assert.strictEqual(dashboard.todaySeries, 0);
  assert.strictEqual(dashboard.routines.length, 4);
  assert.strictEqual(dashboard.routines.find((routine) => routine.routineId === 'day4').totalSeries, 20);
  assert.ok(dashboard.routines.every((routine) => Number.isFinite(routine.doneSeries)));
  assert.ok(dashboard.routines.every((routine) => !Object.values(routine).includes(undefined)));
  console.log(JSON.stringify({ ok: true }));
}).catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_store_exposes_explicit_reset_operations(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
assert.strictEqual(typeof window.TrainingProgressStore.clearAll, 'function');
assert.strictEqual(typeof window.TrainingProgressStore.clearRoutine, 'function');
console.log(JSON.stringify({ ok: true }));
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_profile_is_saved_and_normalized_in_local_fallback(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
let persisted = null;
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: {
    getItem() { return persisted; },
    setItem(_key, value) { persisted = value; },
    removeItem() {}
  }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
window.TrainingProgressStore.saveProfile({ displayName: 'Eva', birthDate: '1990-05-12', sex: 'female', heightCm: '171.5', goal: 'hypertrophy', units: 'metric' }).then(() => window.TrainingProgressStore.getProfile()).then(async (profile) => {
  assert.strictEqual(profile.profileId, 'local-default');
  assert.strictEqual(profile.displayName, 'Eva');
  assert.strictEqual(profile.birthDate, '1990-05-12');
  assert.strictEqual(profile.heightCm, 171.5);
  assert.strictEqual(profile.goal, 'hypertrophy');
  await window.TrainingProgressStore.saveProfile({ displayName: 'Eva', reminderDays: [1, 1, 8, 5], remindersEnabled: true });
  const reminderProfile = await window.TrainingProgressStore.getProfile();
  assert.deepStrictEqual(Array.from(reminderProfile.reminderDays), [1, 5]);
  assert.strictEqual(reminderProfile.remindersEnabled, true);
  await window.TrainingProgressStore.saveProfile({ reminderDays: [], remindersEnabled: true });
  assert.strictEqual((await window.TrainingProgressStore.getProfile()).remindersEnabled, false);
  console.log(JSON.stringify({ ok: true }));
}).catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_backup_import_round_trip_preserves_profile_and_session_summary(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
let persisted = null;
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return persisted; }, setItem(_key, value) { persisted = value; }, removeItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
const payload = {
  format: 'gymratik-backup', schemaVersion: 3,
  profile: { schemaVersion: 3, displayName: 'Respaldo', birthDate: '1988-01-02', sex: 'male', heightCm: 180, goal: 'strength', units: 'metric' },
  data: {
    progress: [{ routineId: 'day1', doneSeries: 3, totalSeries: 20, updatedAt: 10 }],
    sessions: [{ sessionId: 'day1:10', routineId: 'day1', label: 'Día 1', status: 'completed', completedSeries: 3, totalSeries: 20, updatedAt: 10, performance: [{ exerciseId: '1', exerciseName: 'Jalón', setNumber: 1, reps: 12, load: 100, loadUnit: 'lb' }] }],
    activity: [{ activityKey: 'day1:day1:10:2026-09-21T10:00', routineId: 'day1', completedSeries: 3, dayKey: '2026-09-21', updatedAt: 10 }]
  }
};
window.TrainingProgressStore.importData(payload).then(() => Promise.all([window.TrainingProgressStore.getProfile(), window.TrainingProgressStore.getHistory(), window.TrainingProgressStore.exportData()])).then(([profile, history, backup]) => {
  assert.strictEqual(profile.displayName, 'Respaldo');
  assert.strictEqual(profile.schemaVersion, 3);
  assert.strictEqual(history.length, 1);
  assert.strictEqual(history[0].completedSeries, 3);
  assert.strictEqual(history[0].performance[0].reps, 12);
  assert.strictEqual(history[0].performance[0].load, 100);
  assert.strictEqual(history[0].performance[0].loadUnit, 'lb');
  assert.ok(Math.abs(history[0].performance[0].loadKg - 45.359237) < 1e-9);
  assert.strictEqual(backup.data.progress.length, 1);
  assert.strictEqual(backup.data.activity.length, 1);
  assert.strictEqual(backup.schemaVersion, 3);
  console.log(JSON.stringify({ ok: true }));
}).catch((error) => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_backup_import_rejects_older_schemas(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} }
};
vm.runInNewContext(source, { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout });
const payload = { format: 'gymratik-backup', schemaVersion: 2, profile: {}, data: { progress: [], sessions: [], activity: [] } };
window.TrainingProgressStore.importData(payload).then(() => { throw new Error('Se aceptó un respaldo anterior a v3'); }).catch(error => {
  assert.match(error.message, /esquema 3/);
  console.log(JSON.stringify({ ok: true }));
}).catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_existing_indexeddb_v1_or_v2_is_upgraded_without_deleting_stores_or_local_routine_state(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
async function verify(oldVersion) {
  let request;
  const storage = new Map([
    ['entrenamiento-progress-fallback-v1', JSON.stringify({ progress: { day1: { doneSeries: 9 } } })],
    ['fitlovers-day1-series-v1', '{"e1s1":true}'],
    ['fitlovers-day2-series-v1', '{"e2s1":true}'],
    ['fitlovers-day3-series-v1', '{"e3s1":true}'],
    ['fitlovers-day4-series-v1', '{"e4s1":true}']
  ]);
  const deletedStores = [];
  const events = [];
  const stores = new Map();
  function makeStore(name) {
    return {
      indexNames: { contains() { return false; } },
      createIndex() {},
      openCursor() { const cursor = { result: null }; setTimeout(() => cursor.onsuccess?.(), 0); return cursor; },
      get() { const getRequest = { result: undefined }; setTimeout(() => getRequest.onsuccess?.(), 0); return getRequest; },
      getAll() { return { result: [] }; },
      put() {}, clear() {}, delete() {}, index() { return { openCursor() { return { result: null }; } }; }
    };
  }
  const db = {
    get objectStoreNames() { return { contains: name => stores.has(name), [Symbol.iterator]: function* () { yield* stores.keys(); } }; },
    deleteObjectStore(name) { deletedStores.push(name); stores.delete(name); },
    createObjectStore(name) { stores.set(name, makeStore(name)); return stores.get(name); },
    transaction() {
      const tx = { objectStore(name) { if (!stores.has(name)) throw new Error(`Store inexistente: ${name}`); return stores.get(name); } };
      setTimeout(() => tx.oncomplete?.(), 0);
      return tx;
    }, close() {}
  };
  const window = { GymratikInstallGate: { isInstalled() { return true; } },
    CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
    dispatchEvent(event) { events.push(event); },
    localStorage: { getItem(key) { return storage.get(key) || null; }, setItem(key, value) { storage.set(key, value); }, removeItem(key) { storage.delete(key); } },
    indexedDB: { open() {
      for (const name of ['oldProgress', 'oldProfile']) stores.set(name, makeStore(name));
      request = { result: db, transaction: { objectStore(name) { return stores.get(name); } } };
      setTimeout(() => {
        request.onupgradeneeded({ oldVersion });
        setTimeout(() => request.onsuccess(), 0);
      }, 0);
      return request;
    } }
  };
  vm.runInNewContext(source, { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout });
  const dashboard = await window.TrainingProgressStore.getDashboard();
  assert.strictEqual(dashboard.routines.every(routine => routine.doneSeries === 0), true);
  assert.deepStrictEqual(deletedStores, []);
  assert.deepStrictEqual([...stores.keys()].sort(), ['activity', 'meta', 'oldProfile', 'oldProgress', 'profiles', 'routineProgress', 'sessions']);
  assert.strictEqual(storage.has('entrenamiento-progress-fallback-v1'), true);
  for (let day = 1; day <= 4; day += 1) {
    assert.strictEqual(storage.get(`fitlovers-day${day}-series-v1`), `{"e${day}s1":true}`);
  }
  assert.strictEqual(events.some(event => event.name === 'training-database-upgraded' && event.detail.previousVersion === oldVersion && event.detail.preservedExistingStores === true), true);
}
(async () => { await verify(1); await verify(2); console.log(JSON.stringify({ ok: true })); })().catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_missing_central_progress_is_recovered_from_local_routine_snapshot(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const storage = new Map([['fitlovers-day1-series-v1', JSON.stringify({ e1s1: true, __timing: { sessionStartedAt: Date.now() - 120000, sessionEndedAt: 0, warmup: { phase: 'done' } } })]]);
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {}, localStorage: { getItem(key) { return storage.get(key) ?? null; }, setItem(key, value) { storage.set(key, value); }, removeItem(key) { storage.delete(key); } } };
vm.runInNewContext(source, { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout });
(async () => {
  const dashboard = await window.TrainingProgressStore.getDashboard();
  assert.strictEqual(dashboard.routines.find(row => row.routineId === 'day1').doneSeries, 1);
  const sessions = await window.TrainingProgressStore.getHistory(10);
  assert.strictEqual(sessions.filter(session => session.routineId === 'day1').length, 1);
  assert.strictEqual(JSON.parse(storage.get('fitlovers-day1-series-v1')).e1s1, true);
  console.log(JSON.stringify({ ok: true }));
})().catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_skipped_exercise_advances_completion_without_fabricating_sets(self):
        script = r"""
const fs = require('fs'); const vm = require('vm'); const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8'); const storage = new Map();
const window = { GymratikInstallGate: { isInstalled() { return true; } }, CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } }, dispatchEvent() {}, localStorage: { getItem(key) { return storage.get(key) ?? null; }, setItem(key, value) { storage.set(key, value); }, removeItem(key) { storage.delete(key); } } };
vm.runInNewContext(source, { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout });
(async () => { const started = Date.now() - 10000; await window.TrainingProgressStore.capture({ routineId: 'day1', state: { e1s1: false, __skippedExercises: { '1': true, '999': true }, __timing: { sessionStartedAt: started, warmup: { phase: 'done' } }, __performance: { '1': { e1s1: { reps: 10, load: 40 } } } } }); const data = await window.TrainingProgressStore.exportData(); const record = data.data.progress.find(item => item.routineId === 'day1'); const session = data.data.sessions.find(item => item.routineId === 'day1'); assert.strictEqual(record.doneSeries, 0); assert.strictEqual(record.completedExercises, 1); assert.strictEqual(record.skippedExercises, 1); assert.strictEqual(record.performance.length, 0); assert.strictEqual(session.completedSeries, 0); assert.strictEqual(session.skippedExercises, 1); console.log(JSON.stringify({ ok: true })); })().catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_capture_persists_only_completed_sets_with_valid_repetitions(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
let persisted = null;
const window = { GymratikInstallGate: { isInstalled() { return true; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return persisted; }, setItem(_key, value) { persisted = value; }, removeItem() {} }
};
const context = { window, CustomEvent: window.CustomEvent, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
const state = {
  e1s1: true, e1s2: true, e1s3: true,
  __timing: { sessionStartedAt: 123, sessionEndedAt: 0 },
  __performance: { '1': {
    e1s1: { title: 'Jalón al pecho', reps: 12, load: '88.1849049', loadUnit: 'lb', durationMs: 24000, updatedAt: 124 },
    e1s2: { title: 'Jalón al pecho', reps: 9, load: null, loadUnit: 'kg', updatedAt: 125 },
    e1s3: { title: 'Jalón al pecho', reps: 10, load: 0, loadUnit: 'kg', updatedAt: 126 }
  } }
};
window.TrainingProgressStore.capture({ routineId: 'day1', state }).then(() => window.TrainingProgressStore.getHistory()).then(history => {
  assert.strictEqual(history.length, 1);
  assert.strictEqual(history[0].performance.length, 3);
  assert.strictEqual(history[0].performance[0].exerciseName, 'Jalón al pecho');
  assert.strictEqual(history[0].performance[0].reps, 12);
  assert.strictEqual(history[0].performance[0].load, 88.1849049);
  assert.strictEqual(history[0].performance[0].loadUnit, 'lb');
  assert.strictEqual(history[0].performance[0].durationMs, 24000);
  assert.ok(Math.abs(history[0].performance[0].loadKg - 40) < 1e-7);
  assert.strictEqual(history[0].performance.find(row => row.setKey === 'e1s2').load, null);
  assert.strictEqual(history[0].performance.find(row => row.setKey === 'e1s3').load, 0);
  console.log(JSON.stringify({ ok: true }));
}).catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_uninstalled_browser_cannot_read_or_write_profile_or_progress(self):
        script = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
let writes = 0;
const window = {
  GymratikInstallGate: { isInstalled() { return false; } },
  CustomEvent: class CustomEvent { constructor(name, init) { this.name = name; this.detail = init?.detail; } },
  dispatchEvent() {},
  localStorage: { getItem() { return null; }, setItem() { writes += 1; }, removeItem() {} }
};
const context = { window, localStorage: window.localStorage, navigator: {}, console, Date, setTimeout, clearTimeout };
vm.runInNewContext(source, context);
const store = window.TrainingProgressStore;
const checks = [
  store.capture({ routineId: 'day1', state: {} }),
  store.getProfile(),
  store.saveProfile({ displayName: 'No guardar' }),
  store.getHistory(),
  store.getDashboard(),
  store.exportData(),
  store.importData({}),
  store.clearAll(),
  store.clearRoutine('day1'),
  store.requestPersistence()
];
Promise.all(checks.map(operation => assert.rejects(operation, /Instala Gymratik/))).then(() => {
  assert.strictEqual(writes, 0);
  console.log(JSON.stringify({ ok: true }));
}).catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(
            ["node", "-e", script, str(STORE)], cwd=ROOT, check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})


if __name__ == "__main__":
    unittest.main()
