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
        for marker in ('value="7"', 'value="30"', 'value="all"', 'id="sessionComparison"', 'id="periodComparison"', 'id="weeklyChart"', 'id="dailyChart"', 'id="monthlyChart"', 'id="exerciseLoads"', 'id="routineBreakdown"', 'id="sessionHistory"'):
            self.assertIn(marker, self.page)
        for marker in ('statSessions', 'statSets', 'statReps', 'statDays'):
            self.assertIn(f'id="{marker}"', self.page)

    def test_milestones_use_local_mascots_and_explain_validation_bounds(self):
        for marker in ('id="heroLoad"', 'id="milestoneExercises"', 'id="milestonePrs"', 'id="milestoneCorrections"', 'id="milestoneList"', 'id="reviewList"'):
            self.assertIn(marker, self.page)
        self.assertIn('states-v1/female-strength.png', self.page)
        self.assertIn('states-v1/male-strength.png', self.page)
        self.assertIn('25&nbsp;%–250&nbsp;%', self.page)
        self.assertIn('prefers-reduced-motion:reduce', self.style)
        self.assertIn('transform:translateY', self.style)
        self.assertIn('opacity:', self.style)

    def test_analytics_explain_period_cutoffs_and_use_accessible_animations(self):
        self.assertIn('mismo día y hora de la semana anterior', self.page)
        self.assertIn('role="img" aria-label="Gráfica diaria', self.page)
        self.assertIn('role="img" aria-label="Gráfica mensual', self.page)
        self.assertIn('prefers-reduced-motion:reduce', self.style)
        self.assertIn('@keyframes bar-rise', self.style)
        self.assertIn('Semana en curso · mismo tramo', self.script)
        self.assertIn('Mes en curso · mismo tramo', self.script)
        self.assertIn('Última sesión frente a la anterior', self.page)

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
const ids = ['dataStatus','recordsContent','periodFilter','statSessions','statSets','statReps','statDays','sessionComparisonHint','sessionComparison','periodComparison','weeklyChart','dailyChart','dailyTrendSummary','monthlyChart','monthlyTrendSummary','exerciseLoads','routineBreakdown','sessionHistory','historyCount','heroLoad','heroLoadContext','milestoneStatus','milestoneExercises','milestonePrs','milestoneCorrections','milestoneList','reviewDetails','reviewList','reviewCount'];
class Element {
  constructor(id='') { this.id=id; this.children=[]; this.dataset={}; this.style={}; this.classList={items:[],add(value){this.items.push(value);}}; this.hidden=false; this.value='30'; this.textContent=''; this.listeners={}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children=[...items]; }
  setAttribute(name,value) { this[name]=value; }
  addEventListener(name,fn) { this.listeners[name]=fn; }
}
const elements = Object.fromEntries(ids.map(id => [id,new Element(id)]));
elements.heroArt = new Element('hero-art');
global.document = { querySelector:s=>s === '.hero-art' ? elements.heroArt : elements[s.slice(1)], createElement:()=>new Element(), createElementNS:()=>new Element(), addEventListener(){} };
const now = Date.now();
const session = (sessionId, offset, load, reps=8, otherRecords=[]) => ({sessionId,routineId:'day1',label:'Día 1 · Tirón',startedAt:now-offset,updatedAt:now-offset,status:'completed',completedSeries:2,totalSeries:3,performance:[{exerciseId:'row',exerciseName:'Remo horizontal en máquina',setNumber:1,reps,load,loadUnit:'kg',loadKg:load},...otherRecords]});
global.window = { addEventListener(){}, GymratikInstallGate:{isInstalled:()=>true}, TrainingProgressStore:{getHistory:async limit=>{
  assert.equal(limit,50);
  return [
    session('fixture-1',5000,20,8,[{exerciseId:'row',exerciseName:'Remo horizontal en máquina',setNumber:2,reps:10,load:2,loadUnit:'kg',loadKg:2}]),
    session('fixture-2',4000,22.5,7),
    session('fixture-3',3000,80),
    session('fixture-4',2000,20),
    session('fixture-5',1000,12.5),
  ];
},getProfile:async()=>({units:'metric',sex:'female'}),capture(){throw new Error('la vista no debe escribir');},clearAll(){throw new Error('la vista no debe borrar');}} };
require(__SCRIPT__);
setTimeout(()=>{
  assert.equal(elements.statSessions.textContent,'5');
  assert.equal(elements.statSets.textContent,'10');
  assert.equal(elements.statReps.textContent,'49');
  assert.equal(elements.statDays.textContent,'1');
  assert.equal(elements.historyCount.textContent,'5');
  assert.equal(elements.exerciseLoads.children[0].children[1].textContent,'22.5 kg · 49.6 lb');
  assert.equal(elements.routineBreakdown.children.length,1);
  assert.equal(elements.sessionComparison.children.length,1);
  assert.equal(elements.sessionComparison.children[0].className,'session-pair-card');
  assert.equal(elements.periodComparison.children.length,2);
  assert.equal(elements.weeklyChart.children.length,12);
  assert.equal(elements.dailyChart.children.length,14);
  assert.equal(elements.monthlyChart.children.length,6);
  assert.match(elements.dailyTrendSummary.textContent,/series en \d+ día(?:s)? activ(?:o|os)/);
  assert.match(elements.monthlyTrendSummary.textContent,/mes anterior completo/);
  assert.equal(elements.heroLoad.textContent,'22.5 kg · 49.6 lb');
  assert.equal(elements.milestoneExercises.textContent,'1');
  assert.equal(elements.milestonePrs.textContent,'1');
  assert.equal(elements.milestoneCorrections.textContent,'3');
  assert.equal(elements.milestoneList.children.length,1);
  assert.equal(elements.milestoneList.children[0].children[4].children[0].role, 'img');
  assert.match(elements.milestoneList.children[0].children[4].children[1].textContent, /Δ última captura −2.5 kg/);
  assert.match(elements.milestoneList.children[0].children[3].children[0].textContent, /\+12.5 %/);
  assert.equal(elements.reviewList.children.length,3);
  const flaggedLowSet = elements.sessionHistory.children[0].children[1].children[1];
  assert.equal(flaggedLowSet.classList.items.includes('review-row'),true);
  assert.equal(elements.sessionHistory.children[0].children[1].children[0].classList.items.includes('review-row'),false);
  const flaggedHistoryRow = elements.sessionHistory.children[2].children[1].children[0];
  assert.equal(flaggedHistoryRow.classList.items.includes('review-row'),true);
  assert.equal(flaggedHistoryRow.children[1].children[0].textContent,'Revisar · no cuenta para hitos');
  assert.equal(elements.heroArt.dataset.sex,'female');
  assert.equal(elements.recordsContent.hidden,false);
},20);
""".replace("__SCRIPT__", json.dumps(str(ROOT / "records.js")))
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
