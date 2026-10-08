import unittest
import subprocess
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


class RecordsScreenContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "records.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "records.js").read_text(encoding="utf-8")
        cls.style = (ROOT / "records.css").read_text(encoding="utf-8")
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_homepage_links_to_full_read_only_records_view(self):
        self.assertIn('href="./records.html"', self.home)
        self.assertIn('id="progressWeekSessions"', self.home)
        self.assertIn('series de hoy', self.home)
        self.assertIn('sesiones esta semana', self.home)
        self.assertIn('startedAt >= weekStart && startedAt < weekEnd', self.home)
        self.assertIn('Number(session.completedSeries) > 0', self.home)

    def test_records_screen_offers_periods_and_useful_metrics(self):
        for marker in ('value="7"', 'value="30"', 'value="all"', 'id="weeklyChart"', 'id="exerciseLoads"', 'id="routineBreakdown"', 'id="sessionHistory"'):
            self.assertIn(marker, self.page)
        for marker in ('statSessions', 'statSets', 'statReps', 'statDays'):
            self.assertIn(f'id="{marker}"', self.page)

    def test_records_are_read_from_local_store_without_mutation_or_html_injection(self):
        self.assertIn('TrainingProgressStore.getHistory(50)', self.script)
        self.assertIn('GymratikInstallGate?.isInstalled()', self.script)
        self.assertIn('node.textContent = String(text)', self.script)
        self.assertNotIn('.innerHTML', self.script)
        self.assertNotIn('TrainingProgressStore.clear', self.script)
        self.assertNotIn('TrainingProgressStore.capture', self.script)
        self.assertNotIn('TrainingProgressStore.save', self.script)

    def test_records_screen_is_mobile_responsive_and_respects_reduced_motion(self):
        self.assertIn('@media(max-width:460px)', self.style)
        self.assertIn('@media(prefers-reduced-motion:reduce)', self.style)
        self.assertIn('min-width:320px', self.style)

    def test_records_render_correctly_from_synthetic_local_history(self):
        script = r"""
const assert = require('node:assert/strict');
const ids = ['dataStatus','recordsContent','periodFilter','statSessions','statSets','statReps','statDays','weeklyChart','exerciseLoads','routineBreakdown','sessionHistory','historyCount'];
class Element {
  constructor(id='') { this.id=id; this.children=[]; this.dataset={}; this.style={}; this.hidden=false; this.value='30'; this.textContent=''; this.listeners={}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children=[...items]; }
  setAttribute(name,value) { this[name]=value; }
  addEventListener(name,fn) { this.listeners[name]=fn; }
}
const elements = Object.fromEntries(ids.map(id => [id,new Element(id)]));
global.document = { querySelector:s=>elements[s.slice(1)], createElement:()=>new Element(), addEventListener(){} };
const now = Date.now();
global.window = { addEventListener(){}, GymratikInstallGate:{isInstalled:()=>true}, TrainingProgressStore:{getHistory:async limit=>{
  assert.equal(limit,50);
  return [{sessionId:'fixture-1',routineId:'day1',label:'Día 1 · Tirón',startedAt:now-1000,updatedAt:now,status:'completed',completedSeries:2,totalSeries:3,performance:[{exerciseId:'row',exerciseName:'Remo',setNumber:1,reps:8,load:20,loadUnit:'kg',loadKg:20},{exerciseId:'row',exerciseName:'Remo',setNumber:2,reps:7,load:20,loadUnit:'kg',loadKg:20}]}];
},capture(){throw new Error('la vista no debe escribir');},clearAll(){throw new Error('la vista no debe borrar');}} };
require(__SCRIPT__);
setTimeout(()=>{
  assert.equal(elements.statSessions.textContent,'1');
  assert.equal(elements.statSets.textContent,'2');
  assert.equal(elements.statReps.textContent,'15');
  assert.equal(elements.statDays.textContent,'1');
  assert.equal(elements.historyCount.textContent,'1');
  assert.equal(elements.exerciseLoads.children[0].children[1].textContent,'20 kg');
  assert.equal(elements.routineBreakdown.children.length,1);
  assert.equal(elements.recordsContent.hidden,false);
},20);
""".replace("__SCRIPT__", json.dumps(str(ROOT / "records.js")))
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
