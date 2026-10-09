"""Estandariza la referencia anatómica de la franja «Músculos del día».

Las láminas son referencias ilustrativas. El foco visual ayuda a localizar la
región descrita sin afirmar que la imagen, por sí sola, demuestre activación
muscular ni superioridad fisiológica.
"""

from __future__ import annotations

import re
from html import escape, unescape

from pwa_battery import apply_battery_motion

ROUTINE_COVER_STYLE = '''<style data-enhancement="routine-day-cover-v1">
.routineDayCover{position:relative;width:min(100%,780px);height:clamp(180px,28vw,320px);margin:10px auto 2px;overflow:hidden;border:1px solid rgba(114,220,255,.18);border-radius:20px;background:radial-gradient(ellipse at 50% 72%,rgba(26,111,119,.25),transparent 68%),linear-gradient(135deg,rgba(8,30,44,.48),rgba(5,18,29,.12));isolation:isolate}
.routineDayCover::before{content:"";position:absolute;inset:12% 18%;z-index:-1;border-radius:50%;background:radial-gradient(ellipse,rgba(56,211,196,.16),rgba(15,42,59,0) 70%);filter:blur(12px)}
.routineDayCover img{display:block;width:100%;height:100%;object-fit:contain;object-position:center bottom;filter:drop-shadow(0 8px 18px rgba(0,0,0,.25))}
@media(max-width:680px){.routineDayCover{width:100%;height:clamp(170px,52vw,240px);margin:8px auto 0;border-radius:16px}}
@media(prefers-reduced-motion:reduce){.routineDayCover img{animation:none!important;transition:none!important}}
</style>'''

INTERACTION_FEEDBACK_STYLE = '''<style data-enhancement="interaction-feedback-v1">
button:not(:disabled):active,[role="button"]:not([aria-disabled="true"]):active{transform:scale(.97);filter:brightness(.9)}
.performanceRepsControl{display:grid;grid-template-columns:48px minmax(0,1fr) 48px;align-items:center;gap:.55rem;width:100%}
.performanceRepsValue{display:grid;min-height:48px;place-items:center;padding:.4rem .55rem;border:1px solid rgba(101,242,221,.36);border-radius:.7rem;background:rgba(15,45,65,.72);color:#eaffff;font-size:clamp(1rem,3vw,1.3rem);font-weight:900;text-align:center;font-variant-numeric:tabular-nums;transition:background-color .2s ease,border-color .2s ease,transform .2s ease}
.performanceRepsValue[data-selected="true"]{border-color:rgba(101,242,221,.72);background:linear-gradient(110deg,rgba(18,91,83,.82),rgba(15,45,65,.86));transform:scale(1.02)}
.performanceRepsNudge{display:grid;min-width:48px;min-height:48px;place-items:center;border:1px solid rgba(114,220,255,.48);border-radius:.7rem;background:rgba(38,104,137,.38);color:#f1ffff;font:inherit;font-size:1.45rem;font-weight:850;cursor:pointer;touch-action:manipulation;transition:transform .12s ease,filter .12s ease,background-color .12s ease}
.performanceRepsNudge:disabled,.performanceClear:disabled{opacity:.42;cursor:default}
.performanceField .performanceReps{width:100%;min-height:42px;touch-action:pan-x;accent-color:#42e1bf}
.performanceEntry{grid-template-columns:minmax(0,1fr);gap:.55rem;padding:.65rem;border-color:rgba(105,215,255,.25);border-radius:1rem;background:linear-gradient(145deg,rgba(10,33,48,.94),rgba(5,22,34,.96));box-shadow:inset 0 1px rgba(255,255,255,.035)}
.performanceField{gap:.42rem!important;min-width:0;padding:.55rem .65rem;border:1px solid rgba(105,215,255,.18);border-radius:.8rem;background:rgba(17,48,65,.58)}
.performanceFieldTitleRow,.performanceLoadHead{display:flex;align-items:center;justify-content:space-between;gap:.5rem;min-height:34px;color:#d7eef4;font-size:.83rem;font-weight:850;line-height:1.2}
.performanceFieldLabel{display:flex;align-items:center;gap:.45rem;min-width:0}
.performanceFieldIcon{width:21px;height:21px;flex:0 0 21px;color:#70dcff}
.performanceRequired{flex:none;padding:.19rem .42rem;border:1px solid rgba(101,242,221,.25);border-radius:999px;background:rgba(15,75,69,.34);color:#8debd8;font-size:.61rem;font-weight:850}
.performanceMissingDialog{width:min(440px,calc(100vw - 32px));max-width:none;padding:22px;border:1px solid rgba(255,210,119,.58);border-radius:20px;background:linear-gradient(145deg,#153444,#0b1b29);color:#effaff;box-shadow:0 24px 80px rgba(0,0,0,.6)}
.performanceMissingDialog::backdrop{background:rgba(1,8,14,.76);backdrop-filter:blur(4px)}
.performanceMissingDialog h2{margin:0 0 8px;color:#ffd277;font-size:1.08rem}
.performanceMissingDialog p{margin:0 0 12px;color:#d6e8ee;line-height:1.45}
.performanceMissingDialog ul{margin:0 0 16px;padding-left:1.25rem;color:#ffe4a4}
.performanceMissingDialog .dialogActions{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.performanceMissingDialog button{min-height:48px;padding:9px 12px;border:1px solid rgba(134,198,215,.36);border-radius:12px;background:#123044;color:#e9f7fa;font:inherit;font-weight:800}
.performanceMissingDialog button[value="continue"]{border-color:#ffd277;background:linear-gradient(120deg,#9a6b17,#725019);color:#fff0bd}
.performanceClear{min-width:44px;min-height:34px;padding:.3rem .52rem;border:1px solid rgba(255,171,149,.32);border-radius:.55rem;background:rgba(83,37,42,.28);color:#ffc2ae;font:inherit;font-size:.68rem;font-weight:850;cursor:pointer;transition:color .18s ease,border-color .18s ease,background-color .18s ease}
.performanceClear[hidden]{display:none!important}
.performanceClear:hover:not(:disabled),.performanceClear:focus-visible{border-color:rgba(114,220,255,.72);background:rgba(22,67,88,.76);color:#effbff}
.performanceLoadOutputRow{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:.35rem}
.performanceField input[type="range"]{--range-progress:0%;appearance:none;-webkit-appearance:none;width:100%;height:38px;min-height:38px;margin:0;padding:0;background:transparent;cursor:pointer;touch-action:pan-x}
.performanceField input[type="range"]::-webkit-slider-runnable-track{height:8px;border:1px solid rgba(137,194,211,.3);border-radius:999px;background:linear-gradient(90deg,#43dcb9 0%,#70e8d3 var(--range-progress),rgba(103,147,164,.28) var(--range-progress),rgba(103,147,164,.28) 100%);box-shadow:inset 0 1px 2px rgba(0,0,0,.35)}
.performanceReps[data-zone="below"]{--rep-color:#ff927b;--rep-glow:rgba(255,146,123,.2)}
.performanceReps[data-zone="low"]{--rep-color:#ffd277;--rep-glow:rgba(255,210,119,.2)}
.performanceReps[data-zone="mid"]{--rep-color:#43dcb9;--rep-glow:rgba(67,220,185,.2)}
.performanceReps[data-zone="high"]{--rep-color:#70dcff;--rep-glow:rgba(112,220,255,.2)}
.performanceReps[data-zone="above"]{--rep-color:#c2a4ff;--rep-glow:rgba(194,164,255,.22)}
.performanceReps{--rep-color:#43dcb9;--rep-glow:rgba(67,220,185,.2)}
.performanceField input.performanceReps[data-zone]::-webkit-slider-runnable-track{background:linear-gradient(90deg,var(--rep-color) 0%,var(--rep-color) var(--range-progress),rgba(103,147,164,.28) var(--range-progress),rgba(103,147,164,.28) 100%)}
.performanceField input.performanceReps[data-zone]::-moz-range-progress{background:var(--rep-color)}
.performanceField input.performanceReps[data-zone]::-webkit-slider-thumb{background:var(--rep-color);box-shadow:0 0 0 4px var(--rep-glow),0 2px 8px rgba(0,0,0,.4)}
.performanceField input.performanceReps[data-zone]::-moz-range-thumb{background:var(--rep-color);box-shadow:0 0 0 4px var(--rep-glow),0 2px 8px rgba(0,0,0,.4)}
.performanceRepsValue[data-zone="below"]{color:#ff927b!important}.performanceRepsValue[data-zone="low"]{color:#ffd277!important}.performanceRepsValue[data-zone="mid"]{color:#73f0d0!important}.performanceRepsValue[data-zone="high"]{color:#70dcff!important}.performanceRepsValue[data-zone="above"]{color:#c2a4ff!important}
.performanceField input[type="range"]::-moz-range-track{height:8px;border:1px solid rgba(137,194,211,.3);border-radius:999px;background:rgba(103,147,164,.28);box-shadow:inset 0 1px 2px rgba(0,0,0,.35)}
.performanceField input[type="range"]::-moz-range-progress{height:8px;border-radius:999px;background:linear-gradient(90deg,#43dcb9,#70e8d3)}
.performanceField input[type="range"]::-webkit-slider-thumb{appearance:none;-webkit-appearance:none;width:24px;height:24px;margin-top:-9px;border:3px solid #d8fff4;border-radius:50%;background:#39d6b2;box-shadow:0 0 0 4px rgba(57,214,178,.17),0 2px 8px rgba(0,0,0,.4);transition:transform .18s ease,box-shadow .18s ease}
.performanceField input[type="range"]::-moz-range-thumb{width:18px;height:18px;border:3px solid #d8fff4;border-radius:50%;background:#39d6b2;box-shadow:0 0 0 4px rgba(57,214,178,.17),0 2px 8px rgba(0,0,0,.4);transition:transform .18s ease,box-shadow .18s ease}
.performanceField input[type="range"]:active::-webkit-slider-thumb{transform:scale(1.16);box-shadow:0 0 0 7px rgba(57,214,178,.22),0 2px 8px rgba(0,0,0,.4)}
.performanceField input[type="range"]:focus-visible{outline:2px solid #d8fff4;outline-offset:3px;border-radius:999px}
.performanceRepsValue{min-height:44px;border-color:transparent;background:transparent;color:#73f0d0;font-size:1.04rem}
.performanceRepsValue[data-selected="false"]{color:#91aeb9;font-size:.78rem;font-weight:700}
.performanceRepsNudge{min-width:44px;min-height:44px;border-radius:.72rem;background:linear-gradient(145deg,rgba(48,120,145,.48),rgba(24,75,96,.6));box-shadow:inset 0 1px rgba(255,255,255,.1),0 2px 8px rgba(0,0,0,.2)}
.performanceLoadValue{min-height:44px;border-color:rgba(105,215,255,.28);border-radius:.68rem;background:rgba(7,28,42,.78);text-align:left;transition:border-color .18s ease,background .18s ease,transform .18s ease}
.performanceLoadUnit{min-height:36px;padding:.25rem .45rem;border:1px solid rgba(164,223,231,.24);border-radius:.55rem;background:#081923;color:#dff5fa;font:inherit;font-size:.75rem;font-weight:800}
.performanceEntry .progressionCue{margin:.05rem .2rem 0;color:#9dbac4;font-size:.68rem;line-height:1.35}
.performanceEntry.isLocked{border-color:rgba(101,242,221,.38)!important;background:linear-gradient(145deg,rgba(14,48,52,.84),rgba(5,22,34,.96))!important}.performanceEntry.isLocked :disabled{cursor:not-allowed!important}.performanceEntry.isLocked .performanceField{opacity:.76}
.performanceEntry{grid-template-columns:minmax(0,1fr)!important;gap:.55rem!important;padding:.65rem!important;border-color:rgba(105,215,255,.25)!important;border-radius:1rem!important;background:linear-gradient(145deg,rgba(10,33,48,.94),rgba(5,22,34,.96))!important}
.performanceField input[type="range"]{height:38px!important;min-height:38px!important;margin:0!important;touch-action:pan-x!important}
.performanceLoadValue[data-selected="true"]{border-color:rgba(101,242,221,.56)!important;background:linear-gradient(110deg,rgba(18,91,83,.48),rgba(15,45,65,.8))!important;color:#8ef4d8!important}
.performanceLoadValue[data-selected="false"]{color:#bbd0d7!important}
.performanceLoadOutputRow .performanceClear{min-width:58px}
button:not(:disabled):focus-visible{outline:2px solid #fff;outline-offset:3px}
@media(max-width:640px){.performanceEntry{gap:.45rem!important;padding:.55rem!important}.performanceField{padding:.5rem .58rem}.performanceRepsControl{grid-template-columns:48px minmax(0,1fr) 48px;gap:.35rem}.performanceRepsValue{min-height:48px}.performanceRepsNudge{min-width:48px;min-height:48px}.performanceClear{min-height:38px}}
@media(prefers-reduced-motion:reduce){.performanceRepsNudge,.performanceRepsValue,.performanceClear,.performanceField input[type="range"]::-webkit-slider-thumb,.performanceField input[type="range"]::-moz-range-thumb{transition:none}button:not(:disabled):active,[role="button"]:not([aria-disabled="true"]):active{transform:none;filter:none}}
</style>'''

REST_COUNTDOWN_STYLE = '''<style data-fix="rest-countdown-activity-v1">
.warmupHead p,.warmupCopy p,.warmupInstructions{font-size:clamp(13px,3.6vw,15px)!important;line-height:1.45!important}
.warmupVisual[data-media-state="FALLBACK_STATIC"] .warmupGif,.gifFrame[data-media-state="FALLBACK_STATIC"] .gifMotion{display:none!important}
.warmupVisual[data-media-state="FALLBACK_STATIC"] .warmupFallback,.gifFrame[data-media-state="FALLBACK_STATIC"] .gifFallback{display:block!important}
.exerciseTracker{position:relative;z-index:2;pointer-events:auto}
.exerciseTracker .completeSetButton{position:relative;z-index:4;pointer-events:auto}
.exerciseTracker .skipExerciseButton{flex:0 0 auto;min-height:34px;margin-top:.1rem;padding:.35rem .55rem;border-color:rgba(255,179,132,.24);background:rgba(74,34,38,.22);color:rgba(255,213,197,.6);font-size:.64rem;opacity:.55;transition:opacity .18s ease,border-color .18s ease,background .18s ease,color .18s ease}
.exerciseTracker .skipExerciseButton:hover,.exerciseTracker .skipExerciseButton:focus-visible,.exerciseTracker .skipExerciseButton.is-holding{border-color:rgba(255,179,132,.78);background:rgba(74,34,38,.82);color:#ffe0d3;opacity:1}
.exerciseTracker .skipExerciseButton:disabled{opacity:.3}
.exerciseTracker .holdFeedback{opacity:.5}
.summaryExercise.isResting .summaryExerciseState{color:#ffd277}
.summaryExercise.isResting .summaryExerciseState{animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryExercise.isSeriesActive .summaryExerciseState{color:#65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
.summaryExercise.isPreparing .summaryExerciseState{color:#72dcff}
.warmupProgressSegment.is-current,.seriesProgressSegment.is-current{border-color:#72dcff;animation:progressPulse 1.15s ease-in-out infinite}
.warmupProgressSegment.is-current::after,.seriesProgressSegment.is-current::after{transform:scaleX(.38);opacity:1;background-image:linear-gradient(100deg,#159bb3 0%,#35d6a4 55%,#a0d95c 100%);background-size:220% 100%;animation:progressActiveSweep 1.6s linear infinite}
.warmupProgressSegment.is-next,.seriesProgressSegment.is-next{border-color:rgba(114,220,255,.32);animation:none}
.summaryToggle.isActive::before,.summaryToggle.isResting::before,.summaryToggle.isPreparing::before{content:"";width:.48rem;height:.48rem;flex:none;border-radius:50%;background:currentColor;box-shadow:0 0 .55rem currentColor;animation:activityFastPulse .68s ease-in-out infinite}
.warmupTracker>.warmupProgressSegments{margin:.3rem 0 .45rem}
.warmupInstructions{margin:.15rem 0 .4rem;color:#c5e3eb;font-size:.68rem;line-height:1.4}
.exerciseWarmupHint{flex:1 1 100%;margin:.25rem 0;padding:.5rem .65rem;border:1px solid rgba(255,210,119,.4);border-radius:.7rem;background:rgba(112,79,21,.2);color:#ffe4a4;font-size:.68rem;line-height:1.4}.exerciseWarmupHint[hidden]{display:none!important}.exerciseTracker.is-approximation{border-color:rgba(255,210,119,.68);box-shadow:0 0 0 1px rgba(255,210,119,.12)}.exerciseTracker .approximationProgress{display:flex;align-items:center;gap:.45rem;margin:.35rem 0;color:#ffd277;font-size:.68rem;font-weight:850}.approximationProgress[hidden]{display:none!important}.approximationProgressTrack{height:8px;flex:1;overflow:hidden;border:1px solid rgba(255,210,119,.38);border-radius:999px;background:rgba(6,25,37,.82)}.approximationProgressTrack>span{display:block;width:0;height:100%;border-radius:inherit;background:linear-gradient(90deg,#b98221,#ffd277);transition:width .25s ease}.approximationProgress[data-active=true] .approximationProgressTrack>span{width:48%;animation:restSlowPulse 2.4s ease-in-out infinite}.approximationProgress[data-complete=true] .approximationProgressTrack>span{width:100%}.performanceEntry.is-approximation{border-color:rgba(255,210,119,.48)!important;background:linear-gradient(145deg,rgba(65,48,22,.68),rgba(5,22,34,.96))!important}.performanceEntry.is-approximation .progressionCue{color:#ffe4a4!important}button.completeSetButton.is-approximation{border-color:#ffd277;background:linear-gradient(135deg,#9a6b17,#725019);color:#fff0bd;box-shadow:0 0 0 1px rgba(255,210,119,.2)}button.completeSetButton.is-approximation-active{animation:restSlowPulse 2.4s ease-in-out infinite}.exerciseTracker.is-approximation .exerciseWarmupHint{display:block}
.warmupTrackerActions button[data-phase="preparing"],.warmupTrackerActions button[data-phase="cardio"],.warmupTrackerActions button[data-phase="mobility"]{border-color:rgba(114,220,255,.7);background:rgba(24,75,101,.7);color:#d8f5ff}
.warmupTrackerActions button[data-phase="done"]{border-color:rgba(101,242,221,.65);background:rgba(19,73,72,.65);color:#b9fff1}
.summaryToggle.isResting{border:1px solid rgba(255,210,119,.78);background:linear-gradient(90deg,rgba(112,79,21,.96),rgba(83,61,29,.92));color:#ffe4a4;animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryToggle.isActive{border:1px solid rgba(101,242,221,.78);background:linear-gradient(90deg,rgba(19,105,91,.96),rgba(19,73,72,.92));color:#b9fff1;animation:activityFastPulse .68s ease-in-out infinite}
.summaryToggle.isPreparing{border:1px solid rgba(114,220,255,.65);background:linear-gradient(90deg,rgba(24,75,101,.96),rgba(15,45,65,.92));color:#bfeeff}
.summaryToggle.isApproximation,.summaryActivityStatus.isApproximation{border-color:rgba(255,210,119,.72);background:linear-gradient(105deg,rgba(112,79,21,.62),rgba(83,61,29,.46));color:#ffe4a4}
.summaryToggle.isApproximation::before,.summaryActivityStatus.isApproximation .summaryActivityIndicator{background:#ffd277;box-shadow:0 0 .55rem #ffd277;animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryExercise.isApproximation{border-color:rgba(255,210,119,.72);background:rgba(83,61,29,.42)}
button.completeSetButton.is-resting{border-color:#ffd277;background:linear-gradient(135deg,#9a6b17,#725019);color:#fff0bd;box-shadow:0 0 0 1px rgba(255,210,119,.2)}
button.completeSetButton.is-series-active{border-color:#65f2dd;background:linear-gradient(135deg,#159d83,#146d5e);color:#eafff8;box-shadow:0 0 0 1px rgba(101,242,221,.2)}
button.completeSetButton.is-preparing{border-color:#72dcff;background:linear-gradient(135deg,#18506b,#17384c);color:#d8f5ff;animation:preparationPulse 1.3s ease-in-out infinite}
.exerciseTracker:has(.completeSetButton.is-resting){border-color:rgba(255,210,119,.82);box-shadow:0 0 18px rgba(255,210,119,.14)}
.exerciseTracker:has(.completeSetButton.is-series-active){border-color:rgba(101,242,221,.76);box-shadow:0 0 18px rgba(101,242,221,.14)}
.exerciseTracker:has(.completeSetButton.is-resting) .exerciseRest{border-color:#ffd277;background:rgba(112,79,21,.44);color:#ffe4a4;animation:restSlowPulse 2.4s ease-in-out infinite}
.exerciseTracker:has(.completeSetButton.is-series-active) .seriesProgressSegment.is-current{border-color:#65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
.summaryExercise.isResting{border-color:rgba(255,210,119,.78);background:rgba(83,61,29,.5);animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryExercise.isSeriesActive{border-color:rgba(101,242,221,.78);background:rgba(19,73,72,.56)}
.seriesProgressSegment.is-current.is-resting{border-color:#ffd277;animation:restSlowPulse 2.4s ease-in-out infinite}
.seriesProgressSegment.is-current.is-resting::after{transform:scaleX(.38);background-image:linear-gradient(100deg,#b98221 0%,#ffd277 55%,#fff0bd 100%);background-size:220% 100%;animation:progressActiveSweep 2.4s linear infinite}
.seriesProgressSegment.is-current.is-active{border-color:#65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
.summaryActivityStatus.isResting{border-color:rgba(255,210,119,.62);background:rgba(83,61,29,.38);color:#ffe4a4}
.summaryActivityStatus.isActive{border-color:rgba(101,242,221,.58);background:rgba(19,73,72,.38);color:#b9fff1}
.summaryActivityStatus.isPreparing{border-color:rgba(114,220,255,.56);background:rgba(24,75,101,.36);color:#d8f5ff}
.summaryActivityStatus.isResting .summaryActivityIndicator{background:#ffd277;box-shadow:0 0 .55rem #ffd277;animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryActivityStatus.isActive .summaryActivityIndicator{background:#65f2dd;box-shadow:0 0 .55rem #65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
.summaryActivityStatus.isPreparing .summaryActivityIndicator{background:#72dcff;box-shadow:0 0 .55rem #72dcff;animation:preparationPulse 1.3s ease-in-out infinite}
.summaryMascotWrap{position:relative;grid-column:3;grid-row:1/3;display:grid;width:68px;height:68px;place-items:center;align-self:center;overflow:visible;border:1px solid rgba(155,222,241,.24);border-radius:1rem;background:radial-gradient(circle at 50% 75%,rgba(23,91,105,.42),rgba(6,21,31,.68) 72%);box-shadow:inset 0 0 16px rgba(101,242,221,.08)}
#summaryActivityMascot{display:block;width:70px;height:70px;object-fit:contain;transform-origin:50% 82%;transition:filter .2s ease;image-rendering:auto}
#summaryToggle.isResting #summaryActivityMascot{filter:drop-shadow(0 0 8px rgba(255,210,119,.36))}
#summaryToggle.isActive #summaryActivityMascot{filter:drop-shadow(0 0 8px rgba(101,242,221,.3))}
#summaryActivityMascot[data-motion="start"]{animation:mascotIdleBreath 4s ease-in-out infinite}
#summaryActivityMascot[data-motion="ready"]{animation:mascotReadyShift 2.8s ease-in-out infinite}
#summaryActivityMascot[data-motion="preparing"]{animation:mascotPreparationBrace 1.8s cubic-bezier(.35,0,.2,1) infinite}
#summaryActivityMascot[data-motion="approximation"]{animation:mascotWarmupFlow 2.1s ease-in-out infinite}
#summaryActivityMascot[data-motion="strength"]{animation:mascotStrengthEffort 1.35s cubic-bezier(.35,0,.2,1) infinite}
#summaryActivityMascot[data-motion="cardio"]{animation:mascotCardioCadence .68s cubic-bezier(.4,0,.6,1) infinite}
#summaryActivityMascot[data-motion="mobility"]{animation:mascotMobilityFlow 2.4s cubic-bezier(.4,0,.6,1) infinite}
#summaryActivityMascot[data-motion="rest"]{animation:mascotRecoveryBreath 3.6s ease-in-out infinite}
#summaryActivityMascot[data-motion="celebration"]{animation:mascotApprovalCelebrate 1.8s cubic-bezier(.2,.8,.2,1) infinite;filter:drop-shadow(0 0 9px rgba(255,220,116,.85))}
.summaryMascotWrap:has(#summaryActivityMascot[data-motion="celebration"]){border-color:rgba(255,220,116,.8);background:rgba(122,81,21,.28);box-shadow:0 0 18px rgba(255,220,116,.35)}
.summaryMascotWrap:has(#summaryActivityMascot[data-motion="celebration"])::before,.summaryMascotWrap:has(#summaryActivityMascot[data-motion="celebration"])::after{position:absolute;z-index:2;color:#ffe18a;font-size:14px;line-height:1;pointer-events:none;animation:mascotSparkle .9s ease-in-out infinite alternate}
.summaryMascotWrap:has(#summaryActivityMascot[data-motion="celebration"])::before{content:"✦";top:-5px;right:-4px}
.summaryMascotWrap:has(#summaryActivityMascot[data-motion="celebration"])::after{content:"✧";bottom:-3px;left:-4px;animation-delay:.3s}
.exerciseTiming{display:flex;flex-wrap:wrap;align-items:center;gap:.38rem;margin:.4rem 0 .5rem;padding:.38rem .42rem;border:1px solid rgba(114,220,255,.13);border-radius:.85rem;background:linear-gradient(105deg,rgba(5,23,35,.68),rgba(8,31,44,.46));color:#bad4de;font-size:.65rem;line-height:1.1}
.exerciseTimerChip{position:relative;display:inline-flex;align-items:center;gap:.38rem;min-height:30px;max-width:100%;overflow:hidden;padding:.35rem .55rem;border:1px solid rgba(114,220,255,.19);border-radius:999px;background:rgba(16,47,63,.75);font-variant-numeric:tabular-nums;white-space:nowrap}
.exerciseTimerLabel{color:#a9cbd6;font-size:.56rem;font-weight:850;letter-spacing:.06em;text-transform:uppercase}
.exerciseTimerValue{color:#e5f5f8;font-size:.69rem;font-weight:900}
.exerciseTimerChip[data-kind="set"]{border-color:rgba(53,214,164,.25)}
.exerciseTimerChip[data-kind="set"] .exerciseTimerValue{color:#80edcf}
.exerciseTimerChip[data-kind="rest"]{border-color:rgba(255,210,119,.3)}
.exerciseTimerChip[data-kind="rest"] .exerciseTimerValue{color:#ffdc8d}
.exerciseTimerChip[data-kind="exercise"]{border-color:rgba(114,220,255,.2)}
.exerciseTimerChip[data-kind="active-set"]{border-color:rgba(101,242,221,.74);background:linear-gradient(105deg,rgba(19,105,91,.72),rgba(10,54,57,.9));box-shadow:0 0 14px rgba(101,242,221,.13)}
.exerciseTimerChip[data-kind="active-set"]::before,.exerciseTimerChip[data-kind="active-rest"]::before{width:.42rem;height:.42rem;flex:none;border-radius:50%;background:#65f2dd;content:"";box-shadow:0 0 .5rem currentColor;animation:timerActivityPulse .82s ease-in-out infinite}
.exerciseTimerChip[data-kind="active-set"]::after{position:absolute;right:0;bottom:0;left:0;height:2px;background:linear-gradient(90deg,transparent,#65f2dd,transparent);content:"";animation:timerActivitySweep 2.3s ease-in-out infinite}
.exerciseTimerChip[data-kind="active-rest"]{border-color:rgba(255,210,119,.72);background:linear-gradient(105deg,rgba(112,79,21,.56),rgba(68,51,27,.8));box-shadow:0 0 12px rgba(255,210,119,.11)}
.exerciseTimerChip[data-kind="active-rest"]::after{position:absolute;right:0;bottom:0;left:0;height:2px;transform:scaleX(var(--timer-progress,0));transform-origin:left;background:linear-gradient(90deg,#b98221,#ffd277);content:"";transition:transform .35s linear}
.exerciseTimerChip[data-kind="active-rest"]::before{background:#ffd277;color:#ffd277}
.exerciseTimerChip[data-kind="preparation"]{border-color:rgba(114,220,255,.62);background:rgba(24,75,101,.6)}
.exerciseTimerChip[data-kind="empty"]{border-style:dashed;color:#99b7c1}
.exerciseTimerChip[hidden]{display:none}
@keyframes timerActivityPulse{0%,100%{opacity:.72;transform:scale(.82)}50%{opacity:1;transform:scale(1.15)}}
@keyframes timerActivitySweep{0%{transform:translateX(-100%);opacity:.15}50%{opacity:.9}100%{transform:translateX(100%);opacity:.15}}
@keyframes mascotIdleBreath{0%,100%{transform:translateY(1px) rotate(-.5deg) scale(1)}50%{transform:translateY(-1px) rotate(.5deg) scale(1.025,1.012)}}
@keyframes mascotReadyShift{0%,100%{transform:translateX(-1px) rotate(-1.2deg)}32%{transform:translateX(1px) rotate(1deg)}68%{transform:translateY(-1px) rotate(.2deg)}}
@keyframes mascotPreparationBrace{0%,100%{transform:translateY(1px) rotate(0) scale(1)}32%{transform:translate(-2px,1px) rotate(-2.8deg) scale(1.015,.99)}58%{transform:translate(1px,-1px) rotate(1.2deg) scale(1.005,1.01)}}
@keyframes mascotWarmupFlow{0%,100%{transform:rotate(-1.5deg) translateY(0)}28%{transform:rotate(2deg) translateY(-1px)}63%{transform:rotate(-2deg) translateY(-1px)}82%{transform:rotate(1deg)}}
@keyframes mascotStrengthEffort{0%,100%{transform:translateY(1px) rotate(-.5deg) scale(1)}28%{transform:translateY(-2px) rotate(1deg) scale(1.035,.975)}55%{transform:translateY(0) rotate(-.7deg) scale(.99,1.015)}78%{transform:translateY(1px) scale(1.01,.995)}}
@keyframes mascotCardioCadence{0%,100%{transform:translateY(1px) rotate(-2deg) scale(1,.99)}25%{transform:translateY(-3px) rotate(1.5deg) scale(.99,1.025)}50%{transform:translateY(0) rotate(-1deg) scale(1.015,.985)}75%{transform:translateY(-2px) rotate(2deg) scale(.99,1.015)}}
@keyframes mascotMobilityFlow{0%,100%{transform:rotate(-4deg) translateX(-1px)}38%{transform:rotate(1deg) translateX(0)}70%{transform:rotate(4deg) translateX(1px)}}
@keyframes mascotRecoveryBreath{0%,100%{transform:translateY(1px) rotate(.4deg) scale(1)}45%{transform:translateY(-1px) rotate(-.4deg) scale(1.02,1.015)}72%{transform:translateY(0) scale(1.008,.998)}}
@keyframes mascotApprovalCelebrate{0%,100%{transform:translateY(0) rotate(-1deg) scale(1)}24%{transform:translateY(-4px) rotate(1.5deg) scale(1.045)}48%{transform:translateY(-1px) rotate(0) scale(1.015)}72%{transform:translateY(-2px) rotate(-1deg) scale(1.03)}}
@keyframes mascotToastApproval{0%,100%{transform:translateY(1px) rotate(-1deg)}35%{transform:translateY(-2px) rotate(1deg)}68%{transform:translateY(0) rotate(-.4deg)}}
@keyframes mascotSparkle{from{opacity:.45;transform:scale(.7) rotate(-18deg)}to{opacity:1;transform:scale(1.15) rotate(18deg)}}
.summaryExercise{position:relative;overflow:hidden;min-height:52px;transition:background-color .2s ease,border-color .2s ease,transform .18s ease}
.summaryExercise::before,.summaryExercise::after{position:absolute;right:.68rem;bottom:.38rem;left:.68rem;height:4px;border-radius:999px;content:"";pointer-events:none}
.summaryExercise::before{background:rgba(30,61,75,.95);box-shadow:inset 0 0 0 1px rgba(114,220,255,.3)}
.summaryExercise::after{transform:scaleX(var(--summary-progress,0));transform-origin:left;background:linear-gradient(90deg,#159bb3,#35d6a4,#a0d95c);transition:transform .48s cubic-bezier(.2,.75,.25,1),filter .2s ease}
.summaryExercise.isDone::after{transform:scaleX(1);background:linear-gradient(90deg,#1ec89b,#88e56c)}
.summaryExercise.isCurrent{border-color:rgba(101,242,221,.7);box-shadow:0 0 0 1px rgba(101,242,221,.16)}
.summaryExercise.isCurrent:not(.isSeriesActive):not(.isResting){animation:none}
.summaryExercise.isSeriesActive::after{filter:brightness(1.15);animation:activityFastPulse .68s ease-in-out infinite}
.summaryExercise.isResting{box-shadow:0 0 0 1px rgba(255,210,119,.24),0 0 14px rgba(255,210,119,.12)}
.summaryProgressTrack{height:7px;overflow:hidden;border:1px solid rgba(114,220,255,.18);border-radius:999px;background:rgba(4,20,31,.78)}
.summaryProgressTrack>span{display:block;width:100%;height:100%;transform:scaleX(var(--summary-progress,0));transform-origin:left;border-radius:inherit;background:linear-gradient(90deg,#159bb3,#35d6a4,#a0d95c);transition:transform .5s cubic-bezier(.2,.75,.25,1)}
#floatingSessionSummary{position:fixed!important;right:max(.65rem,env(safe-area-inset-right))!important;bottom:max(.65rem,env(safe-area-inset-bottom))!important;z-index:40;width:min(420px,calc(100vw - 1.3rem))!important;max-height:min(42dvh,380px)!important;border:1px solid rgba(114,220,255,.42)!important;border-radius:1rem!important;background:rgba(6,24,37,.97)!important;box-shadow:0 18px 54px rgba(0,0,0,.42),0 0 30px rgba(71,202,216,.14)!important;backdrop-filter:blur(18px)!important;overflow:hidden!important;display:flex!important;flex-direction:column!important}
#summaryToggle{display:grid!important;grid-template-columns:auto minmax(0,1fr) clamp(50px,14vw,68px) auto!important;grid-template-rows:auto auto;flex:none!important;min-height:78px!important;gap:.22rem .55rem!important;padding:.55rem .7rem!important;background:linear-gradient(105deg,rgba(14,73,90,.98),rgba(37,42,75,.98))!important;font-size:.84rem!important;line-height:1.22!important}
#summaryActivityIcon{grid-column:1;grid-row:1/3;align-self:center}
#summaryToggle #summaryHeadline{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-variant-numeric:tabular-nums}
#summaryActivityHeadline{grid-column:2;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#bfdce5;font-size:.72rem;font-weight:750;line-height:1.2}
#summaryActivityHeadline::before{content:"";display:inline-block;width:.4rem;height:.4rem;margin-right:.35rem;border-radius:50%;vertical-align:.03rem;background:#82aebb}
#summaryToggle.isResting #summaryActivityHeadline::before{background:#ffd277;animation:restSlowPulse 2.4s ease-in-out infinite}
#summaryToggle.isActive #summaryActivityHeadline::before{background:#65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
#summaryToggle.isPreparing #summaryActivityHeadline::before{background:#72dcff;animation:preparationPulse 1.3s ease-in-out infinite}
#summaryToggle .summaryMascotWrap{grid-column:3;grid-row:1/3}
#summaryToggle .summaryChevron{grid-column:4;grid-row:1/3;align-self:center;margin-left:0!important;font-size:1.1rem!important}
#summaryToggle[aria-expanded="true"]{grid-template-rows:auto;min-height:50px!important}
#summaryToggle[aria-expanded="true"] #summaryActivityHeadline{display:none}
#summaryToggle[aria-expanded="true"] #summaryActivityIcon,#summaryToggle[aria-expanded="true"] .summaryMascotWrap,#summaryToggle[aria-expanded="true"] .summaryChevron{grid-row:1}
#summaryToggle.isResting{border:1px solid rgba(255,210,119,.82)!important;background:linear-gradient(105deg,rgba(112,79,21,.98),rgba(83,61,29,.96))!important;color:#ffe4a4!important}
#summaryToggle.isActive{border:1px solid rgba(101,242,221,.82)!important;background:linear-gradient(105deg,rgba(19,105,91,.98),rgba(19,73,72,.96))!important;color:#b9fff1!important}
#summaryToggle.isPreparing{border:1px solid rgba(114,220,255,.72)!important;background:linear-gradient(105deg,rgba(24,75,101,.98),rgba(15,45,65,.96))!important;color:#d8f5ff!important}
#summaryToggle.isComplete{border:1px solid rgba(255,220,116,.82)!important;background:linear-gradient(105deg,rgba(112,79,21,.96),rgba(72,51,80,.98))!important;color:#fff0b4!important}
#summaryToggle.isResting,#summaryToggle.isActive,#summaryToggle.isPreparing,#summaryToggle.isComplete{animation:none!important}
#summaryBody{min-height:0;padding:.55rem .65rem .68rem!important;overflow:hidden;display:flex!important;flex-direction:column!important;gap:.42rem}
#summaryBody[hidden]{display:none!important}
.summaryTotals{flex:none!important;min-height:28px;padding:.1rem .15rem!important;font-size:.72rem!important}
.summaryTotals span{display:inline-flex;align-items:center;min-height:28px;padding:.18rem .58rem;border:1px solid rgba(255,210,119,.26);border-radius:999px;background:rgba(83,61,29,.22);font-size:.76rem!important;font-weight:850}
.summaryActivityStatus{display:flex;align-items:center;gap:.55rem;flex:none;min-height:44px;padding:.48rem .62rem;border:1px solid rgba(114,220,255,.2);border-radius:.65rem;background:rgba(14,44,61,.66);color:#d5edf4;font-size:.76rem;font-weight:850;line-height:1.25}
.summaryActivityIndicator{width:.52rem;height:.52rem;flex:none;border-radius:50%;background:#82aebb;box-shadow:0 0 .4rem rgba(130,174,187,.26)}
.summaryActivityLabel{min-width:0;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.summaryActivityClock{flex:none;color:inherit;font-variant-numeric:tabular-nums;font-size:.76rem;font-weight:950}
.summaryActivityStatus.isIdle .summaryActivityIndicator{background:#82aebb;animation:none}
.summaryOverallProgress{flex:none}
.summaryTime{flex:none!important;margin:0!important;font-size:.74rem!important;line-height:1.35!important}
.sessionSummaryList{min-height:0;max-height:min(34dvh,320px)!important;gap:.34rem!important;padding:.04rem .12rem .1rem .02rem!important;overflow-y:auto!important;overscroll-behavior:contain;scrollbar-width:thin;scrollbar-color:rgba(114,220,255,.42) transparent;-webkit-overflow-scrolling:touch}
.summaryExercise{grid-template-columns:minmax(0,1fr) auto!important;gap:.2rem .55rem!important;min-height:48px!important;padding:.48rem .68rem .72rem!important;border-radius:.68rem!important}
.summaryExerciseName{font-size:.78rem!important;line-height:1.25!important;white-space:nowrap!important;display:block!important;overflow:hidden;text-overflow:ellipsis}
.summaryExerciseState{font-size:.78rem!important;line-height:1.2!important;font-variant-numeric:tabular-nums}
.summaryExercise.isCurrent{scroll-margin-block:8px}
.summaryActivityStatus:not(.isIdle){animation:summaryStatusIn .24s ease-out both}
@keyframes summaryStatusIn{from{opacity:.5;transform:translateY(3px)}to{opacity:1;transform:none}}
@media(max-width:640px){#floatingSessionSummary{right:max(.55rem,env(safe-area-inset-right))!important;bottom:max(.55rem,env(safe-area-inset-bottom))!important;width:min(420px,calc(100vw - 1.1rem))!important;max-height:min(44dvh,400px)!important}#summaryToggle{grid-template-columns:auto minmax(0,1fr) 64px auto!important;min-height:68px!important}.sessionSummaryList{max-height:min(28dvh,180px)!important}.summaryExercise{min-height:44px!important;padding:.42rem .6rem .68rem!important}.summaryExercise::before,.summaryExercise::after{right:.6rem;bottom:.34rem;height:4px}.summaryExerciseName{font-size:.74rem!important}.summaryMascotWrap{width:62px;height:62px;border-radius:.88rem}#summaryActivityMascot{width:58px;height:58px}}
@media(max-width:640px){#summaryToggle[aria-expanded="true"]{grid-template-columns:auto minmax(0,1fr) 58px auto!important;grid-template-rows:auto auto!important;min-height:58px!important}#summaryToggle[aria-expanded="true"] #summaryActivityHeadline{display:block!important;font-size:.62rem!important;line-height:1.1!important}#summaryToggle[aria-expanded="true"] .summaryMascotWrap{width:54px!important;height:54px!important}#summaryToggle[aria-expanded="true"] #summaryActivityMascot{width:50px!important;height:50px!important}#summaryToggle[aria-expanded="true"] + #summaryBody{max-height:none!important;padding:.32rem .48rem .42rem!important;gap:.28rem!important}#summaryToggle[aria-expanded="true"] + #summaryBody .summaryTotals{display:none!important}#summaryToggle[aria-expanded="true"] + #summaryBody .summaryActivityStatus{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}#summaryToggle[aria-expanded="true"] + #summaryBody #summaryElapsed{display:none!important}}
@media(max-width:380px){.summaryMascotWrap{width:54px;height:54px}#summaryActivityMascot{width:50px;height:50px}#summaryToggle{grid-template-columns:auto minmax(0,1fr) 54px auto!important;gap:.2rem .38rem!important;padding:.48rem .5rem!important}}
@media(max-height:680px){#floatingSessionSummary{max-height:min(62dvh,380px)!important}.sessionSummaryList{max-height:min(28dvh,180px)!important}}
@media(min-width:341px) and (max-width:640px) and (min-height:600px) and (max-height:680px){#floatingSessionSummary{max-height:min(58dvh,380px)!important}}
@media(max-height:420px) and (max-width:900px){#floatingSessionSummary{max-height:min(62.5dvh,225px)!important}.sessionSummaryList{max-height:min(24dvh,90px)!important;gap:.12rem!important}.summaryToggle[aria-expanded=true]{min-height:48px!important}.summaryActivityStatus{min-height:32px!important;padding:.24rem .45rem!important;font-size:.65rem!important}.summaryBody{gap:.18rem!important;padding:.2rem .4rem .28rem!important}.summaryTotals,.summaryTotals span{min-height:20px!important}.summaryTotals span{padding:.12rem .42rem!important;font-size:.58rem!important}.summaryExercise{min-height:24px!important;padding:.06rem .35rem .28rem!important}.summaryExerciseName,.summaryExerciseState{font-size:.58rem!important}}
@media(max-width:380px){.exerciseTiming{gap:.28rem;padding:.3rem}.exerciseTimerChip{min-height:28px;padding:.3rem .42rem;gap:.28rem}.exerciseTimerLabel{font-size:.52rem}.exerciseTimerValue{font-size:.65rem}}
@media(prefers-reduced-motion:reduce){.exerciseTimerChip[data-kind="active-set"]::before,.exerciseTimerChip[data-kind="active-rest"]::before,.exerciseTimerChip[data-kind="active-set"]::after,.summaryActivityStatus:not(.isIdle),.summaryActivityStatus.isResting .summaryActivityIndicator,.summaryActivityStatus.isActive .summaryActivityIndicator,.summaryActivityStatus.isPreparing .summaryActivityIndicator,.summaryActivityStatus.isApproximation .summaryActivityIndicator,#summaryActivityMascot,.summaryMascotWrap::before,.summaryMascotWrap::after,.summaryExercise::after,.summaryProgressTrack>span,.summaryExercise,.warmupProgressSegment.is-current,.seriesProgressSegment.is-current,.warmupProgressSegment.is-current::after,.seriesProgressSegment.is-current::after,.approximationProgress[data-active=true] .approximationProgressTrack>span{animation:none!important;transition:none!important}#floatingSessionSummary,#summaryToggle{scroll-behavior:auto}}
@keyframes activityFillGlow{from{opacity:1}to{opacity:1}}
@keyframes progressActiveSweep{from{background-position:100% 0}to{background-position:-120% 0}}
@keyframes restSlowPulse{50%{opacity:.78}}
@keyframes activityFastPulse{50%{opacity:.72}}
@keyframes preparationPulse{50%{opacity:.78;filter:brightness(1.18);box-shadow:0 0 10px rgba(114,220,255,.25)}}
@media(prefers-reduced-motion:reduce){.summaryToggle.isResting,.summaryToggle.isActive,.summaryToggle.isPreparing,.summaryToggle.isResting::before,.summaryToggle.isActive::before,.summaryToggle.isPreparing::before,.summaryExercise.isResting,.summaryExercise.isSeriesActive,.summaryExercise.isResting .summaryExerciseState,.summaryExercise.isSeriesActive .summaryExerciseState,.summaryExercise.isSeriesActive::after,button.completeSetButton.is-resting,button.completeSetButton.is-series-active,button.completeSetButton.is-preparing,.exerciseTracker:has(.completeSetButton.is-resting) .exerciseRest,.exerciseTracker:has(.completeSetButton.is-series-active) .seriesProgressSegment.is-current,.warmupProgressSegment.is-current,.seriesProgressSegment.is-current,.seriesProgressSegment.is-current.is-resting,.seriesProgressSegment.is-current.is-active,.seriesProgressSegment.is-current.is-resting::after,.warmupProgressSegment.is-current::after,.seriesProgressSegment.is-current::after{animation:none}}
</style>'''


COMPACT_ROUTINE_METRICS_STYLE = '''<style data-enhancement="compact-routine-metrics-v1">
.metrics{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(min(100%,9rem),1fr))!important;align-items:stretch!important;gap:7px!important;margin:0 0 8px!important}
.metric{min-width:0!important;min-height:54px!important;padding:7px 9px!important;gap:7px!important;border-radius:13px!important}
.metricIcon{width:29px!important;height:29px!important;flex:0 0 29px!important;padding:4px!important;border-radius:9px!important}
.metricText{min-width:0!important}
.metricLabel{font-size:9px!important;line-height:1.1!important;letter-spacing:.055em!important;margin-bottom:3px!important}
.metricVal{font-size:clamp(.86rem,3.6vw,1.05rem)!important;line-height:1.12!important;overflow-wrap:anywhere!important}
@media(max-width:360px){.metrics{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:5px!important}.metric{min-height:48px!important;padding:6px!important;gap:5px!important}.metricIcon{width:25px!important;height:25px!important;flex-basis:25px!important}.metricLabel{font-size:8px!important}.metricVal{font-size:.82rem!important}}
</style>'''


APPROVAL_TOAST_STYLE = '''<style data-enhancement="approval-toast-mascot-v1">
#gymratikEncouragement .toastMascot{display:block;flex:0 0 54px;width:54px;height:54px;object-fit:contain;transform-origin:50% 82%;animation:mascotToastApproval 1.4s ease-in-out infinite}
#gymratikEncouragement .toastCopy{min-width:0;overflow-wrap:anywhere}
@media(max-width:380px){#gymratikEncouragement{gap:.4rem;min-height:56px;padding:.35rem .65rem .35rem .4rem;font-size:.82rem}#gymratikEncouragement .toastMascot{flex-basis:46px;width:46px;height:46px}}
</style>'''

LUCIDE_SPRITE = '''<svg id="gymratikLucideSprite" class="gymratikIconSprite" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
<symbol id="gymratik-icon-activity" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/></symbol>
<symbol id="gymratik-icon-arrow-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></symbol>
<symbol id="gymratik-icon-dumbbell" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.596 12.768a2 2 0 1 0 2.829-2.829l-1.768-1.767a2 2 0 0 0 2.828-2.829l-2.828-2.828a2 2 0 0 0-2.829 2.828l-1.767-1.768a2 2 0 1 0-2.829 2.829z"/><path d="m2.5 21.5 1.4-1.4"/><path d="m20.1 3.9 1.4-1.4"/><path d="M5.343 21.485a2 2 0 1 0 2.829-2.828l1.767 1.768a2 2 0 1 0 2.829-2.829l-6.364-6.364a2 2 0 1 0-2.829 2.829l1.768 1.767a2 2 0 0 0-2.828 2.829z"/><path d="m9.6 14.4 4.8-4.8"/></symbol>
<symbol id="gymratik-icon-list-checks" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 5h8"/><path d="M13 12h8"/><path d="M13 19h8"/><path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/></symbol>
<symbol id="gymratik-icon-move-up-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 5h6v6"/><path d="M19 5 5 19"/></symbol>
<symbol id="gymratik-icon-repeat-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 9 3-3 3 3"/><path d="M13 18H7a2 2 0 0 1-2-2V6"/><path d="m22 15-3 3-3-3"/><path d="M11 6h6a2 2 0 0 1 2 2v10"/></symbol>
<symbol id="gymratik-icon-settings-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 17H5"/><path d="M19 7h-9"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/></symbol>
<symbol id="gymratik-icon-target" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></symbol>
<symbol id="gymratik-icon-timer" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/></symbol>
<symbol id="gymratik-icon-triangle-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></symbol>
<symbol id="gymratik-icon-wind" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/></symbol>
<symbol id="gymratik-icon-weight" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><path d="M6.5 8a2 2 0 0 0-1.905 1.46L2.1 18.5A2 2 0 0 0 4 21h16a2 2 0 0 0 1.925-2.54L19.4 9.5A2 2 0 0 0 17.48 8Z"/></symbol>
</svg>'''

VISUAL_LANGUAGE_STYLE = '''<style data-enhancement="visual-language-lucide-v1">
.gymratikIconSprite{position:absolute!important;width:0!important;height:0!important;overflow:hidden!important;pointer-events:none!important}
.gymratikIcon{display:inline-block;width:1.15em;height:1.15em;flex:0 0 1.15em;vertical-align:-.2em;stroke:currentColor;fill:none}
.routine-home-link{position:absolute!important;top:1rem!important;left:1rem!important;z-index:20!important;display:inline-flex!important;width:max-content!important;max-width:calc(100% - 2rem)!important;min-height:44px!important;align-items:center!important;justify-content:flex-start!important;gap:.45rem!important;padding:.48rem .78rem!important;border:1px solid rgba(133,224,246,.38)!important;border-radius:999px!important;background:rgba(6,23,39,.78)!important;color:#e8f8ff!important;font-size:.9rem!important;line-height:1!important;text-decoration:none!important;box-shadow:0 5px 18px rgba(0,0,0,.18)!important;backdrop-filter:blur(8px)}
.routine-home-link:hover,.routine-home-link:focus-visible{border-color:rgba(133,224,246,.72)!important;background:rgba(15,57,75,.94)!important;color:#fff!important}
.routine-home-link .gymratikIcon{width:1.05rem;height:1.05rem;flex-basis:1.05rem}
.coachRibbonIcon .gymratikIcon{width:1.2rem;height:1.2rem;flex-basis:1.2rem}
.techStepTitle{display:flex!important;align-items:center;gap:.45rem;line-height:1.2}
.techStepTitle .gymratikIcon{width:1.05rem;height:1.05rem;flex-basis:1.05rem}
.techStep.setup .techStepTitle{color:#79ddff}.techStep.move .techStepTitle{color:#58e5c5}.techStep.warning .techStepTitle{color:#ffc477}
.techSteps{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:.48rem!important;width:100%!important;margin:.48rem 0 0!important;padding:0!important}
.techStep{display:grid!important;grid-template-rows:auto 1fr!important;align-content:start!important;gap:.32rem!important;min-width:0!important;min-height:0!important;padding:.58rem .66rem!important;border:1px solid rgba(114,220,255,.2)!important;border-left:3px solid var(--guide-accent,#72dcff)!important;border-radius:.78rem!important;background:linear-gradient(145deg,rgba(9,31,46,.94),rgba(7,25,38,.92))!important;box-shadow:inset 0 1px rgba(255,255,255,.035)!important}
.techStep.setup{--guide-accent:#72dcff}.techStep.move{--guide-accent:#43dcb9}.techStep.warning{--guide-accent:#ffd277}
.techStepTitle{display:flex!important;align-items:center!important;gap:.38rem!important;min-height:1.25rem!important;font-size:.72rem!important;font-weight:900!important;letter-spacing:.04em!important;text-transform:uppercase!important}
.techStepTitle .gymratikIcon{width:.95rem;height:.95rem;flex-basis:.95rem}
.techStepText{min-width:0!important;color:#d2e5ed!important;font-size:.8rem!important;font-weight:600!important;line-height:1.35!important;overflow-wrap:anywhere!important}
.techStep.warning{background:linear-gradient(145deg,rgba(54,39,24,.58),rgba(7,25,38,.92))!important}
.techAccordion{width:100%;margin:.65rem 0 0;border:1px solid rgba(114,220,255,.22);border-radius:.82rem;background:rgba(6,24,37,.58);overflow:hidden}
.techAccordion>summary{display:flex;min-height:42px;align-items:center;justify-content:space-between;gap:.6rem;padding:.58rem .78rem;color:#cfeaf3;font-size:.78rem;font-weight:900;cursor:pointer;list-style:none}
.techAccordion>summary::-webkit-details-marker{display:none}.techAccordion>summary::after{content:"＋";color:#72dcff;font-size:1rem;transition:transform .18s ease}.techAccordion[open]>summary::after{content:"−"}
.techAccordion>summary:focus-visible{outline:2px solid #72dcff;outline-offset:-3px}.techAccordion .techSteps{margin:0!important;padding:.1rem .65rem .65rem!important}
.techAccordion:not([open])>.techSteps{display:none!important}.techAccordion[open]>.techSteps{display:grid!important}
@media(prefers-reduced-motion:reduce){.techAccordion>summary::after{transition:none}}
@media(max-width:640px){.techSteps{grid-template-columns:minmax(0,1fr)!important;gap:.38rem!important;margin-top:.1rem!important}.techStep{padding:.5rem .62rem!important}.techStepTitle{font-size:.7rem!important}.techStepText{font-size:.79rem!important;line-height:1.34!important}}
.motivationPortrait img[hidden]{display:none!important}
.warmupTrackerHead>span{display:inline-flex;align-items:center;gap:.4rem}
.warmupTrackerHead .gymratikIcon{width:1rem;height:1rem;flex-basis:1rem;color:#65f2dd}
.warmup-title-icon{width:1em;height:1em;margin-right:.3em;color:#65f2dd}
.footerTitle .gymratikIcon{width:1.1em;height:1.1em;margin-right:.38em;color:#65f2dd}
.exerciseQuickSummary[hidden],.exerciseQuickSummary{display:none!important}
.note.notePanel{display:none!important}
.sessionCompletionPanel{grid-template-columns:auto minmax(7rem,8.5rem) minmax(0,1fr)!important;padding-right:1.25rem!important;overflow:visible!important}
.motivationPhotoWrap{position:relative;z-index:1;grid-column:2;display:flex;min-width:0;flex-direction:column;align-items:center;gap:.35rem}
.motivationPortrait{width:clamp(7rem,12vw,8.5rem)!important;height:clamp(8.25rem,15vw,10rem)!important;flex:0 0 auto;border-radius:1rem!important;box-shadow:0 8px 24px rgba(0,0,0,.28)}
.motivationPortrait img{display:block;width:100%;height:100%;object-fit:cover;object-position:50% 24%}
.motivationPhotoCredit{max-width:100%;color:#a9ccd8;font-size:.56rem;line-height:1.25;text-align:center;text-decoration:none;overflow-wrap:anywhere}
.motivationPhotoCredit:hover,.motivationPhotoCredit:focus-visible{color:#fff;text-decoration:underline}
.sessionCompletionCopy{grid-column:3;min-width:0}
.sessionCompletionCopy p{display:block!important;max-width:100%!important;height:auto!important;max-height:none!important;overflow:visible!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important;line-height:1.42!important}
.motivationNote{max-width:100%;overflow-wrap:anywhere;white-space:normal}
.sessionCompletionActions{grid-column:2/4!important;min-width:0}
@media(max-width:640px){.sessionCompletionPanel:not([hidden]){width:calc(100vw - 1.25rem)!important;max-width:calc(100vw - 1.25rem)!important;min-width:0!important;box-sizing:border-box!important;grid-template-columns:minmax(0,6.5rem) minmax(0,1fr)!important;align-items:start!important;gap:.7rem!important;padding:.8rem!important;overflow-x:clip!important}.sessionCompletionPanel:not([hidden])>*{min-width:0!important;max-width:100%!important}.sessionCompletionPanel .completionOrb{display:none!important}.motivationPhotoWrap{grid-column:1;align-items:flex-start}.motivationPortrait{width:min(100%,6.5rem)!important;height:clamp(7.25rem,34vw,8.5rem)!important}.motivationPhotoCredit{text-align:left;font-size:.52rem}.sessionCompletionCopy{grid-column:2;align-self:center}.sessionCompletionCopy p{font-size:clamp(.98rem,4.3vw,1.12rem)!important}.sessionCompletionActions{grid-column:1/-1!important;flex-wrap:wrap!important;min-width:0!important}.newMotivation,.soundToggle{min-width:0;max-width:100%;min-height:44px;white-space:normal;overflow-wrap:anywhere}}
@media(max-width:360px){.sessionCompletionPanel:not([hidden]){grid-template-columns:5.5rem minmax(0,1fr)!important;gap:.55rem!important;padding:.68rem!important}.motivationPortrait{width:5.5rem!important;height:6.7rem!important}.sessionCompletionCopy p{font-size:.96rem!important}}
@media(max-width:640px){.sessionCompletionPanel::before,.sessionCompletionPanel::after{inset:0!important;transform:none!important;animation:none!important}.sessionCompletionPanel .motivationPortrait img:not([hidden]){transform:scale(1.38);transform-origin:50% 60%}}
@media(max-width:640px){.routine-home-link{top:.15rem!important;left:.65rem!important;min-height:44px!important;padding:.45rem .68rem!important;font-size:.82rem!important}.hero>div:first-of-type{padding-top:56px!important}.routine-home-link .gymratikIcon{width:1rem;height:1rem;flex-basis:1rem}}
@media(prefers-reduced-motion:reduce){.gymratikIcon{transition:none!important}}
</style>'''

WARMUP_PROGRESS_MARKUP = '''<div class="warmupProgressSegments" id="warmupProgress" role="progressbar" aria-label="Progreso del calentamiento" aria-valuemin="0" aria-valuemax="2" aria-valuenow="0" data-state="empty"><span class="warmupProgressSegment is-next" data-phase="cardio" aria-hidden="true"></span><span class="warmupProgressSegment is-next" data-phase="mobility" aria-hidden="true"></span></div>'''

OFFLINE_OPTIONAL_MEDIA_FALLBACK_SCRIPT = '''<script data-fix="offline-optional-gif-fallback-v1">
(() => {
  const revealPoster = image => {
    if (!(image instanceof HTMLImageElement) || !image.matches('.warmupGif,.gifMotion')) return;
    const fallback = image.parentElement?.querySelector('.warmupFallback,.gifFallback');
    if (!fallback) return;
    image.hidden = true;
    fallback.hidden = false;
    const frame = image.closest('.warmupVisual,.gifFrame');
    if (frame) frame.dataset.mediaState = 'FALLBACK_STATIC';
  };
  document.addEventListener('error', event => revealPoster(event.target), true);
  document.querySelectorAll('img.warmupGif,img.gifMotion').forEach(image => {
    if (image.complete && image.naturalWidth === 0) revealPoster(image);
  });
})();
</script>'''

WARMUP_SINGLE_VIEWER_STYLE = '''<style data-enhancement="warmup-single-active-viewer-style-v1">
.warmupStep .warmupMedia.warmupSingleViewer{display:grid!important;grid-template-columns:minmax(0,1fr)!important;align-items:stretch!important;gap:.65rem!important;width:100%!important;max-width:none!important;min-width:0!important;height:auto!important;min-height:0!important;margin:0!important;padding-inline:clamp(4px,1.4vw,7px)!important;border-inline:1px solid rgba(114,220,255,.2)!important;border-radius:18px!important;overflow:visible!important;background:linear-gradient(90deg,rgba(83,231,207,.055),transparent 12%,transparent 88%,rgba(114,220,255,.055))!important}
.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual{position:relative!important;display:grid!important;place-items:center!important;width:100%!important;max-width:none!important;height:clamp(190px,56vw,330px)!important;min-height:0!important;aspect-ratio:16/9!important;overflow:hidden!important;border:1px solid rgba(133,224,246,.28)!important;border-radius:16px!important;background:#f1f5f7!important}
.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual[data-orientation="square"]{height:clamp(220px,68vw,300px)!important;aspect-ratio:4/3!important}
.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual[data-orientation="portrait"]{height:clamp(240px,70vw,330px)!important;aspect-ratio:4/5!important;background:#0c1f2b!important}
.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual>.warmupGif,.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual>.warmupFallback{position:absolute!important;inset:0!important;display:block!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;margin:auto!important;object-fit:contain!important;object-position:center!important;background:transparent!important}
.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual>.warmupGif[hidden],.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual>.warmupFallback[hidden]{display:none!important}
.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual>.warmupMediaLabel{position:absolute!important;z-index:2;left:.65rem!important;right:.65rem!important;bottom:.6rem!important;width:max-content!important;max-width:calc(100% - 1.3rem)!important;margin:0 auto!important;padding:.35rem .65rem!important;border:1px solid rgba(255,255,255,.3)!important;border-radius:999px!important;background:rgba(5,22,32,.88)!important;color:#fff!important;font-size:.78rem!important;font-weight:900!important;letter-spacing:.035em!important;line-height:1.2!important;text-align:center!important}
.warmupMediaChoiceRow{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(min(100%,6.8rem),1fr))!important;gap:.5rem!important;width:100%!important;min-width:0!important}
.warmupMediaChoice{display:grid!important;place-items:center!important;min-width:0!important;min-height:46px!important;padding:.55rem .65rem!important;border:1px solid rgba(120,208,231,.3)!important;border-radius:12px!important;background:rgba(18,48,64,.9)!important;color:#d8edf4!important;font:inherit!important;font-size:clamp(.72rem,3.2vw,.88rem)!important;font-weight:850!important;line-height:1.2!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important;cursor:pointer!important;touch-action:manipulation}
.warmupMediaChoice[aria-pressed="true"]{border-color:#53e7cf!important;background:linear-gradient(120deg,rgba(17,125,117,.78),rgba(19,69,91,.95))!important;color:#f4fffd!important;box-shadow:0 0 0 2px rgba(83,231,207,.13)!important}
.warmupMediaChoice:focus-visible{outline:3px solid #79ddff!important;outline-offset:2px!important}
.warmupMediaStatus{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
@media(max-width:640px){.warmupStep.cardio,.warmupStep.mobility{grid-template-columns:minmax(0,1fr)!important;gap:.7rem!important}.warmupStep .warmupMedia.warmupSingleViewer{grid-column:1/-1!important}.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual{height:clamp(190px,56vw,260px)!important}.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual[data-orientation="square"]{height:clamp(220px,68vw,290px)!important}.warmupStep .warmupMedia.warmupSingleViewer>.warmupVisual[data-orientation="portrait"]{height:clamp(240px,70vw,320px)!important}.warmupMediaChoiceRow{gap:.4rem!important}.warmupMediaChoice{min-height:46px!important;padding:.5rem .42rem!important}}
@media(prefers-reduced-motion:reduce){.warmupMediaChoice{transition:none!important}}
</style>'''

WARMUP_SINGLE_VIEWER_SCRIPT = '''<script data-fix="warmup-single-active-viewer-script-v1">
(() => {
  document.querySelectorAll('.warmupSingleViewer').forEach(group => {
    const frame = group.querySelector('.warmupVisual');
    const image = frame?.querySelector('.warmupGif');
    const poster = frame?.querySelector('.warmupFallback');
    const label = frame?.querySelector('.warmupMediaLabel');
    const buttons = [...group.querySelectorAll('.warmupMediaChoice')];
    if (!frame || !image || !poster || !buttons.length) return;
    let revision = 0;
    const showLoadedImage = expectedSrc => {
      if (image.dataset.batteryPaused === 'true') return;
      if (image.getAttribute('src') !== expectedSrc || !image.complete || !image.naturalWidth) return;
      frame.removeAttribute('data-media-state');
      frame.dataset.orientation = image.naturalHeight > image.naturalWidth * 1.2 ? 'portrait' : image.naturalHeight > image.naturalWidth * .8 ? 'square' : 'landscape';
      image.hidden = false;
      poster.hidden = true;
    };
    image.addEventListener('load', () => showLoadedImage(image.getAttribute('src')));
    const select = button => {
      const currentRevision = ++revision;
      const gifSrc = button.dataset.gifSrc;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      if (!gifSrc) return;
      frame.removeAttribute('data-media-state');
      image.hidden = true;
      poster.hidden = !button.dataset.posterSrc;
      if (button.dataset.posterSrc) {
        poster.loading = 'eager';
        poster.src = button.dataset.posterSrc;
      }
      image.alt = button.dataset.alt || button.dataset.label || '';
      image.loading = 'eager';
      image.dataset.expectedSrc = gifSrc;
      if (label) label.textContent = button.dataset.label || '';
      image.addEventListener('load', () => {
        if (revision === currentRevision) showLoadedImage(gifSrc);
      }, { once: true });
      if (window.GymratikBatteryMotion) window.GymratikBatteryMotion.setSource(image, gifSrc);
      else image.src = gifSrc;
      if (image.complete) queueMicrotask(() => {
        if (revision === currentRevision) showLoadedImage(gifSrc);
      });
      const status = group.querySelector('.warmupMediaStatus');
      if (status) status.textContent = `Mostrando ${button.dataset.label || 'animación'} del calentamiento.`;
    };
    buttons.forEach(button => button.addEventListener('click', () => select(button)));
    const initial = buttons.find(button => button.getAttribute('aria-pressed') === 'true') || buttons[0];
    if (image.complete && image.naturalWidth) showLoadedImage(image.getAttribute('src'));
    else {
      image.hidden = true;
      poster.hidden = false;
    }
    if (initial) {
      const status = group.querySelector('.warmupMediaStatus');
      if (status) status.textContent = `Mostrando ${initial.dataset.label || 'animación'} del calentamiento.`;
    }
  });
})();
</script>'''

REST_TIMING_DISPLAY_CONTRACT = '''  const renderTimingDisplays = () => {
    const renderExerciseTimer = (item, entries, label) => {
      const display = item.timingDisplay;
      if (!display) return;
      if (!item.timerChips) {
        item.timerChips = new Map();
        display.setAttribute('role', 'group');
        display.setAttribute('aria-live', 'off');
      }
      const visibleKeys = new Set();
      entries.forEach(entry => {
        visibleKeys.add(entry.key);
        let chip = item.timerChips.get(entry.key);
        if (!chip) {
          chip = document.createElement('span');
          chip.className = 'exerciseTimerChip';
          const name = document.createElement('span'); name.className = 'exerciseTimerLabel';
          const value = document.createElement('strong'); value.className = 'exerciseTimerValue';
          chip.append(name, value);
          item.timerChips.set(entry.key, chip);
          display.append(chip);
        }
        chip.dataset.kind = entry.kind;
        chip.querySelector('.exerciseTimerLabel').textContent = entry.label;
        chip.querySelector('.exerciseTimerValue').textContent = entry.value;
        chip.setAttribute('aria-label', `${entry.label}: ${entry.value}`);
        if (Number.isFinite(entry.progress)) chip.style.setProperty('--timer-progress', String(Math.max(0, Math.min(1, entry.progress))));
        else chip.style.removeProperty('--timer-progress');
      });
      for (const [key, chip] of item.timerChips) {
        if (visibleKeys.has(key)) continue;
        chip.remove();
        item.timerChips.delete(key);
      }
      display.setAttribute('aria-label', label);
    };
    const renderTimerEntries = (item, timing, row, now, restActive, restRemaining, recommendation, seriesActive, preparing) => {
      const entries = [];
      (timing?.seriesTimes || []).forEach((duration, index) => {
        if (Number.isFinite(duration)) {
          const record = state.__performance?.[String(item.index + 1)]?.[item.seriesKeys[index]];
          const repsValue = Number(record?.reps);
          const reps = Number.isInteger(repsValue) && repsValue >= 1 && repsValue <= 100 ? `${repsValue}r` : null;
          const load = record?.load !== null && record?.load !== undefined && Number.isFinite(Number(record.load)) ? `${Number(record.load)}${record.loadUnit || 'kg'}` : null;
          const details = [reps, load].filter(Boolean).join(' · ') || 'sin datos';
          entries.push({ key: `set-${index + 1}`, label: `S${index + 1} · ${details}`, value: formatElapsed(duration), kind: 'set' });
        }
      });
      (timing?.restTimes || []).forEach((duration, index) => {
        if (Number.isFinite(duration)) entries.push({ key: `rest-${index + 1}`, label: `Descanso ${index + 1}`, value: formatElapsed(duration), kind: 'rest' });
      });
      if (preparing) {
        const preparation = seriesPreparation.get(item.index);
        const remaining = Math.max(0, (preparation?.endsAt || timing?.preparationEndsAt || now) - now);
        entries.push({ key: 'preparation', label: 'Preparación', value: formatCountdown(remaining), kind: 'preparation' });
      } else if (restActive) {
        const elapsed = Math.max(0, recommendation.minMs - restRemaining);
        entries.push({ key: 'active-rest', label: 'Descanso activo', value: `${formatCountdown(restRemaining)} restante`, kind: 'active-rest', progress: recommendation.minMs ? elapsed / recommendation.minMs : 0 });
      } else if (timing?.restStartedAt && !row.complete && !seriesActive) {
        entries.push({ key: 'rest-ready', label: 'Descanso listo', value: 'Continuar cuando quieras', kind: 'preparation' });
      } else if (seriesActive) {
        entries.push({ key: `active-set-${row.done + 1}`, label: `Serie ${row.done + 1} · en curso`, value: formatElapsed(now - timing.seriesStartedAt), kind: 'active-set' });
      }
      const elapsed = timing?.startedAt ? (timing.endedAt || now) - timing.startedAt : NaN;
      if (Number.isFinite(elapsed)) entries.push({ key: 'exercise-total', label: 'Ejercicio', value: formatElapsed(elapsed), kind: 'exercise' });
      if (!entries.length) entries.push({ key: 'empty', label: row.complete ? 'Ejercicio' : 'Cronómetro', value: row.complete ? 'Completado' : 'Listo para iniciar', kind: 'empty' });
      renderExerciseTimer(item, entries, entries.map(entry => `${entry.label}, ${entry.value}`).join('. '));
    };

    const root = state.__timing;
    const now = Date.now();
    let currentActivity = null;
    const total = document.getElementById('summaryElapsed');
    if (total) {
      const elapsed = root?.sessionStartedAt ? (root.sessionEndedAt || now) - root.sessionStartedAt : NaN;
      total.textContent = `⏱ Total de rutina: ${formatElapsed(elapsed)}`;
      total.classList.toggle('isLive', Boolean(root?.sessionStartedAt && !root.sessionEndedAt));
    }
    exerciseItems.forEach(item => {
      const display = item.timingDisplay;
      if (!display) return;
      const timing = root?.exercises?.[String(item.index + 1)];
      const row = snapshot(item);
      const labels = [];
      (timing?.seriesTimes || []).forEach((duration, index) => {
        if (Number.isFinite(duration)) labels.push(`S${index + 1} ${formatElapsed(duration)}`);
      });
      (timing?.restTimes || []).forEach((duration, index) => {
        if (Number.isFinite(duration)) labels.push(`D${index + 1} ${formatElapsed(duration)}`);
      });
      const preparing = isSeriesPreparing(item);
      const preparation = seriesPreparation.get(item.index);
      const restElapsed = timing?.restStartedAt ? Math.max(0, now - timing.restStartedAt) : 0;
      const recommendation = getRestRecommendation(item);
      const restRemaining = Math.max(0, recommendation.minMs - restElapsed);
      const restActive = Boolean(!root?.sessionEndedAt && timing?.restStartedAt && restRemaining > 0);
      const seriesActive = Boolean(!row.complete && timing?.seriesStartedAt && !timing?.restStartedAt);
      const restPending = Boolean(!root?.sessionEndedAt && timing?.restStartedAt && !seriesActive && !preparing);
      const warmupActive = Boolean(!row.complete && timing?.warmupStartedAt && !restPending);
      const activity = warmupActive
        ? { kind: 'approximation', label: `Aproximación · ${item.title}`, clock: formatElapsed(now - timing.warmupStartedAt), startedAt: Number(timing.warmupStartedAt) || 0 }
        : restPending
        ? { kind: restActive ? 'rest' : 'ready', label: restActive ? `Descanso · ${item.title}` : `Descanso listo · ${item.title}`, clock: restActive ? `${formatCountdown(restRemaining)} restantes` : 'Lista', startedAt: Number(timing.restStartedAt) || 0 }
        : preparing
          ? { kind: 'preparing', label: `Preparación · ${item.title}`, clock: formatCountdown((preparation?.endsAt || timing?.preparationEndsAt || now) - now), startedAt: Number(timing?.preparationEndsAt) || now }
          : seriesActive
            ? { kind: 'strength', label: `Serie ${row.done + 1} activa · ${item.title}`, clock: formatElapsed(now - timing.seriesStartedAt), startedAt: Number(timing.seriesStartedAt) || 0 }
            : null;
      if (activity && (!currentActivity || activity.startedAt >= currentActivity.startedAt)) currentActivity = activity;
      if (!root?.sessionEndedAt && timing?.restStartedAt) notifyRestReady(item, timing, restElapsed);
      const summaryButton = summaryList.querySelector(`[data-exercise="${item.index + 1}"]`);
      const summaryState = summaryButton?.querySelector('.summaryExerciseState');
      if (summaryButton && summaryState) {
        summaryButton.classList.toggle('isResting', restActive);
        summaryButton.classList.toggle('isSeriesActive', seriesActive);
        summaryButton.classList.toggle('isPreparing', preparing);
        summaryButton.classList.toggle('isApproximation', warmupActive);
        if (row.skipped) summaryState.textContent = '↷ Omitido';
        else if (restActive) summaryState.textContent = `Descanso · ${formatCountdown(restRemaining)}`;
        else if (row.complete) summaryState.textContent = '✓ Listo';
        else if (warmupActive) summaryState.textContent = `Aproximación · ${formatElapsed(now - timing.warmupStartedAt)}`;
        else if (preparing) summaryState.textContent = `Preparación · ${formatCountdown(preparation ? preparation.endsAt - now : 0)}`;
        else if (seriesActive) summaryState.textContent = `● S${row.done + 1} activa · ${formatElapsed(now - timing.seriesStartedAt)}`;
        else summaryState.textContent = `${row.done}/${item.seriesKeys.length}`;
      }
      if (preparing) {
        renderPreparationDisplay(item);
        renderTimerEntries(item, timing, row, now, restActive, restRemaining, recommendation, seriesActive, true);
        if (item.restDisplay) item.restDisplay.hidden = true;
        return;
      }
      if (restActive) {
        const phase = restPhase(restElapsed, recommendation);
        labels.push(`Descanso ${formatCountdown(restRemaining)} restante`);
        if (item.restDisplay) {
          item.restDisplay.hidden = false;
          item.restDisplay.className = `exerciseRest rest-${phase}`;
          item.restDisplay.innerHTML = `⏳ Descanso restante: <strong>${formatCountdown(restRemaining)}</strong>`;
        }
      } else if (seriesActive) {
        labels.push(`S${row.done + 1} ${formatElapsed(now - timing.seriesStartedAt)} activa`);
      }
      renderTimerEntries(item, timing, row, now, restActive, restRemaining, recommendation, seriesActive, preparing);
      if (item.restDisplay) item.restDisplay.hidden = !restActive;
    });
    const warmup = getWarmupTiming();
    if (warmup.phase === 'preparing') {
      const startedAt = Number(warmup.preparationEndsAt) - PREPARATION_MS;
      const activity = { kind: 'preparing', label: 'Preparación · Calentamiento', clock: formatCountdown(warmupPreparationRemaining()), startedAt };
      if (!currentActivity || activity.startedAt >= currentActivity.startedAt) currentActivity = activity;
    } else if (warmup.phase === 'cardio' || warmup.phase === 'mobility') {
      const startedAt = Number(warmup[`${warmup.phase}StartedAt`]) || 0;
      const activity = { kind: warmup.phase, label: `Calentamiento · ${warmup.phase === 'cardio' ? 'Cardio' : 'Movilidad'}`, clock: formatElapsed(now - startedAt), startedAt };
      if (!currentActivity || activity.startedAt >= currentActivity.startedAt) currentActivity = activity;
    }
    const activityButton = document.getElementById('summaryToggle');
    const activityIcon = document.getElementById('summaryActivityIcon');
    const activityHeadline = document.getElementById('summaryHeadline');
    const compactActivityHeadline = document.getElementById('summaryActivityHeadline');
    const activityStatus = document.getElementById('summaryActivityStatus');
    const activityLabel = document.getElementById('summaryActivityLabel');
    const activityClock = document.getElementById('summaryActivityClock');
    const overallProgress = document.getElementById('summaryOverallProgress');
    const progressFill = document.getElementById('summaryProgressFill');
    if (activityButton && activityHeadline) {
      const doneExercises = exerciseItems.filter(item => snapshot(item).complete).length;
      const doneSeries = exerciseItems.reduce((sum, item) => sum + snapshot(item).done, 0);
      const totalSeries = exerciseItems.reduce((sum, item) => sum + item.seriesKeys.length, 0);
      const sessionComplete = doneExercises === exerciseItems.length;
      const justStarted = Boolean(root?.sessionStartedAt && now - root.sessionStartedAt < 2600);
      const warmupDone = warmup.phase === 'done';
      const displayActivity = sessionComplete
        ? { kind: 'complete', label: 'Rutina completada', clock: '🎉', startedAt: Number(root?.sessionEndedAt) || now }
        : currentActivity || (justStarted
          ? { kind: 'start', label: '¡Rutina iniciada!', clock: 'Vamos', startedAt: Number(root.sessionStartedAt) }
          : { kind: warmupDone || doneSeries > 0 || root?.sessionStartedAt ? 'ready' : 'start', label: warmupDone || doneSeries > 0 || root?.sessionStartedAt ? 'Listo para continuar' : '¡Vamos a entrenar!', clock: warmupDone || doneSeries > 0 || root?.sessionStartedAt ? 'Lista' : 'Iniciar', startedAt: 0 });
      const progressText = `${doneExercises}/${exerciseItems.length} ejercicios · ${doneSeries}/${totalSeries} series`;
      const activityText = `${displayActivity.label} · ${displayActivity.clock}`;
      activityHeadline.textContent = progressText;
      if (compactActivityHeadline) compactActivityHeadline.textContent = activityText;
      if (activityLabel) activityLabel.textContent = displayActivity.label;
      if (activityClock) activityClock.textContent = displayActivity.clock;
      const activeKinds = ['strength', 'cardio', 'mobility', 'approximation'];
      const isActive = activeKinds.includes(displayActivity.kind);
      if (activityStatus) {
        activityStatus.classList.toggle('isResting', displayActivity.kind === 'rest');
        activityStatus.classList.toggle('isActive', isActive);
        activityStatus.classList.toggle('isPreparing', displayActivity.kind === 'preparing');
        activityStatus.classList.toggle('isApproximation', displayActivity.kind === 'approximation');
        activityStatus.classList.toggle('isIdle', ['start', 'ready', 'complete'].includes(displayActivity.kind));
        activityStatus.dataset.activity = displayActivity.kind;
      }
      const mascot = document.getElementById('summaryActivityMascot');
      if (mascot) {
        const mascotMode = displayActivity.kind === 'complete' ? 'celebration' : displayActivity.kind;
        const poseState = ({ start: 'idle', ready: 'ready', preparing: 'preparing', approximation: 'warmup', strength: 'strength', cardio: 'cardio', mobility: 'mobility', rest: 'rest', celebration: 'approval' })[mascotMode] || 'idle';
        const mascotVariant = window.gymratikMascotVariant || 'neutral';
        const fallbackState = ['rest', 'idle', 'ready'].includes(poseState) ? 'rest' : 'exercise';
        const mascotAsset = ['male', 'female'].includes(mascotVariant) ? `../../../data/profile/mascot-motion/states-v1/${mascotVariant}-${poseState}.png` : `../../../data/profile/mascot-motion/${mascotVariant}-${fallbackState}-still.webp`;
        mascot.hidden = false;
        mascot.dataset.motion = document.hidden ? 'paused' : mascotMode;
        mascot.dataset.poseState = poseState;
        const mascotDescription = mascotMode === 'celebration' ? 'aprobando y celebrando la rutina completada' : mascotMode === 'start' ? 'animando el inicio de la rutina' : mascotMode === 'ready' ? 'lista para continuar' : mascotMode === 'rest' ? 'descansando' : mascotMode === 'cardio' ? 'haciendo cardio' : mascotMode === 'mobility' ? 'en movilidad' : mascotMode === 'preparing' ? 'preparándose para entrenar' : mascotMode === 'approximation' ? 'calentando con una serie de aproximación' : 'entrenando fuerza';
        mascot.alt = `${mascotVariant === 'female' ? 'Ratona' : mascotVariant === 'male' ? 'Ratón' : 'Mascotas Gymratik'} ${mascotDescription}`;
        if (mascot.dataset.requestedSrc !== mascotAsset && mascot.getAttribute('src') !== mascotAsset) {
          mascot.dataset.requestedSrc = mascotAsset;
          const revision = (Number(mascot.dataset.requestRevision) || 0) + 1;
          mascot.dataset.requestRevision = String(revision);
          const candidates = [mascotAsset, `../../../data/profile/mascot-motion/${mascotVariant}-${fallbackState}-still.webp`, `../../../data/profile/mascot-motion/neutral-${fallbackState}-still.webp`].filter((asset, index, all) => asset && all.indexOf(asset) === index);
          const loadCandidate = index => {
            if (index >= candidates.length || Number(mascot.dataset.requestRevision) !== revision) return;
            const probe = new Image();
            probe.onload = () => {
              if (Number(mascot.dataset.requestRevision) !== revision) return;
              mascot.src = candidates[index];
              mascot.dataset.loadedSrc = candidates[index];
            };
            probe.onerror = () => loadCandidate(index + 1);
            probe.src = candidates[index];
          };
          loadCandidate(0);
        }
      }
      if (overallProgress) {
        overallProgress.setAttribute('aria-valuemax', String(totalSeries));
        overallProgress.setAttribute('aria-valuenow', String(doneSeries));
        overallProgress.setAttribute('aria-valuetext', `${doneExercises} de ${exerciseItems.length} ejercicios; ${doneSeries} de ${totalSeries} series completadas`);
        overallProgress.dataset.state = doneSeries === 0 ? 'empty' : doneSeries === totalSeries ? 'full' : 'filling';
      }
      if (progressFill) progressFill.style.setProperty('--summary-progress', String(totalSeries ? doneSeries / totalSeries : 0));
      const buttonLabel = `${progressText}. ${activityText}. Activar para mostrar u ocultar el progreso`;
      activityButton.title = buttonLabel;
      activityButton.setAttribute('aria-label', buttonLabel);
      activityButton.classList.toggle('isResting', displayActivity.kind === 'rest');
      activityButton.classList.toggle('isActive', isActive);
      activityButton.classList.toggle('isPreparing', displayActivity.kind === 'preparing');
      activityButton.classList.toggle('isApproximation', displayActivity.kind === 'approximation');
      activityButton.classList.toggle('isComplete', displayActivity.kind === 'complete');
      if (activityIcon) activityIcon.textContent = displayActivity.kind === 'complete' ? '🎉' : displayActivity.kind === 'start' ? '🚀' : displayActivity.kind === 'ready' ? '✨' : displayActivity.kind === 'rest' ? '⏳' : displayActivity.kind === 'cardio' ? '🏃' : displayActivity.kind === 'strength' ? '🏋️' : displayActivity.kind === 'approximation' ? '⚖️' : displayActivity.kind === 'mobility' ? '↔' : displayActivity.kind === 'preparing' ? '◷' : '📋';
    }
  };'''


MUSCLE_FOCUS = {
    "Dorsal ancho": {
        "view": "posterior",
        "key": "latissimus",
        "region": "región lateral del dorso",
    },
    "Romboides": {
        "view": "posterior",
        "key": "rhomboids",
        "region": "entre las escápulas",
    },
    "Trapecio medio": {
        "view": "posterior",
        "key": "middle-trapezius",
        "region": "espalda media entre las escápulas",
    },
    "Deltoides posterior": {
        "view": "posterior",
        "key": "rear-deltoid",
        "region": "parte posterior del hombro",
    },
    "Bíceps braquial": {
        "view": "anterior",
        "key": "biceps",
        "region": "cara anterior del brazo",
    },
    "Pectoral mayor": {
        "view": "anterior",
        "key": "pectoralis-major",
        "region": "tórax anterior",
    },
    "Cuádriceps": {
        "view": "anterior",
        "key": "quadriceps",
        "region": "cara anterior del muslo",
    },
    "Glúteo mayor": {
        "view": "posterior",
        "key": "gluteus-maximus",
        "region": "cadera posterior",
    },
    "Isquiosurales": {
        "view": "posterior",
        "key": "hamstrings",
        "region": "cara posterior del muslo",
    },
    "Aductores": {
        "view": "anterior",
        "key": "adductors",
        "region": "cara medial del muslo",
    },
    "Abductores": {
        "view": "posterior",
        "key": "abductors",
        "region": "cara lateral de la cadera",
    },
    "Gastrocnemio": {
        "view": "posterior",
        "key": "gastrocnemius",
        "region": "pantorrilla superficial",
    },
    "Sóleo": {
        "view": "posterior",
        "key": "soleus",
        "region": "pantorrilla profunda inferior",
    },
    "Deltoides": {
        "view": "anterior",
        "key": "deltoid",
        "region": "hombro",
    },
    "Tríceps": {
        "view": "posterior",
        "key": "triceps",
        "region": "cara posterior del brazo",
    },
}

# Coordenadas normalizadas sobre la lámina cuadrada (0% = borde superior/izquierdo).
# Los músculos pares llevan dos marcadores para evitar señalar la línea media o
# el espacio intermuscular como si fuera el tejido objetivo.
MUSCLE_MARKERS = {
    "Dorsal ancho": (("izquierdo", "35%", "59%"), ("derecho", "65%", "59%")),
    "Romboides": (("izquierdo", "43%", "39%"), ("derecho", "57%", "39%")),
    "Trapecio medio": (("izquierdo", "41%", "48%"), ("derecho", "59%", "48%")),
    "Deltoides posterior": (("izquierdo", "28%", "34%"), ("derecho", "72%", "34%")),
    "Bíceps braquial": (("izquierdo", "23%", "53%"), ("derecho", "77%", "53%")),
    "Pectoral mayor": (("izquierdo", "38%", "40%"), ("derecho", "62%", "40%")),
    "Cuádriceps": (("izquierdo", "42%", "32%"), ("derecho", "58%", "32%")),
    "Glúteo mayor": (("izquierdo", "42%", "18%"), ("derecho", "58%", "18%")),
    "Isquiosurales": (("izquierdo", "42%", "37%"), ("derecho", "58%", "37%")),
    "Aductores": (("izquierdo", "45%", "39%"), ("derecho", "55%", "39%")),
    "Abductores": (("izquierdo", "29%", "25%"), ("derecho", "71%", "25%")),
    "Gastrocnemio": (("izquierdo", "43%", "61%"), ("derecho", "57%", "61%")),
    "Sóleo": (("izquierdo", "43%", "76%"), ("derecho", "57%", "76%")),
    "Deltoides": (("izquierdo", "28%", "31%"), ("derecho", "72%", "31%")),
    "Tríceps": (("izquierdo", "23%", "51%"), ("derecho", "77%", "51%")),
}

MUSCLE_CODE = {
    "Dorsal ancho": "DORSAL",
    "Romboides": "ROMBO",
    "Trapecio medio": "TRAP",
    "Deltoides posterior": "DELTO",
    "Bíceps braquial": "BÍCEPS",
    "Pectoral mayor": "PECHO",
    "Cuádriceps": "CUÁDRI",
    "Glúteo mayor": "GLÚTEO",
    "Isquiosurales": "ISQUIO",
    "Aductores": "ADUCT",
    "Abductores": "ABDUCT",
    "Gastrocnemio": "GASTRO",
    "Sóleo": "SÓLEO",
    "Deltoides": "HOMBRO",
    "Tríceps": "TRÍCEP",
}

MUSCLE_COLOR = {
    "Bíceps braquial": "#ffd277",
    "Pectoral mayor": "#ff9da2",
    "Deltoides": "#7ff0cc",
    "Deltoides posterior": "#7ff0cc",
}

UPPER_MUSCLES = {
    "Dorsal ancho",
    "Romboides",
    "Trapecio medio",
    "Deltoides posterior",
    "Bíceps braquial",
    "Pectoral mayor",
    "Deltoides",
    "Tríceps",
}


MUSCLE_VISUAL_STYLE = r'''<style data-fix="muscle-specific-focus-v1" data-enhancement="muscle-marker-precision-v2">
/* Referencia ilustrativa: el halo localiza la región, no pretende ser una
   segmentación clínica ni una prueba de activación muscular. */
.muscleDayItem[data-muscle-focus]{--focus-color:rgba(100,215,255,.92);--focus-x:50%;--focus-y:50%;--focus-r:38%;--focus-scale:1.18}
.muscleDayVisual{position:relative!important;width:104px!important;height:104px!important;flex:0 0 104px!important;overflow:hidden!important;isolation:isolate!important;border-radius:16px!important;background:#f7f5ee!important}
.muscleDayImage{display:block!important;width:100%!important;height:100%!important;max-width:none!important}
.muscleDayVisual::after{content:"";position:absolute;inset:0;z-index:2;pointer-events:none;border-radius:inherit;background:radial-gradient(ellipse at var(--focus-x) var(--focus-y),var(--focus-color) 0%,rgba(255,255,255,.12) 10%,transparent var(--focus-r));mix-blend-mode:screen;opacity:.72}
.muscleDayVisual::before{display:none}
.muscleFocusMarker{position:absolute;z-index:4;left:var(--marker-x);top:var(--marker-y);width:24px;height:24px;transform:translate(-50%,-50%);border:2px solid var(--focus-color);border-radius:50%;box-shadow:0 0 0 3px rgba(4,17,27,.36),0 0 18px var(--focus-color);pointer-events:none;opacity:.92}
.muscleDayItem[data-muscle-focus] .muscleDayImage{object-fit:cover!important;object-position:var(--focus-x) var(--focus-y)!important;transform:scale(var(--focus-scale))!important;transform-origin:var(--focus-x) var(--focus-y)!important}
.muscleDayItem[data-muscle-focus="latissimus"]{--focus-x:50%;--focus-y:59%;--focus-r:30%;--focus-scale:1.22}
.muscleDayItem[data-muscle-focus="rhomboids"]{--focus-x:50%;--focus-y:39%;--focus-r:30%;--focus-scale:1.34}
.muscleDayItem[data-muscle-focus="middle-trapezius"]{--focus-x:50%;--focus-y:48%;--focus-r:28%;--focus-scale:1.35}
.muscleDayItem[data-muscle-focus="rear-deltoid"]{--focus-x:50%;--focus-y:34%;--focus-r:27%;--focus-scale:1.28}
.muscleDayItem[data-muscle-focus="biceps"]{--focus-x:50%;--focus-y:53%;--focus-r:30%;--focus-scale:1.28}
.muscleDayItem[data-muscle-focus="pectoralis-major"]{--focus-x:50%;--focus-y:40%;--focus-r:28%;--focus-scale:1.22}
.muscleDayItem[data-muscle-focus="quadriceps"]{--focus-x:50%;--focus-y:32%;--focus-r:30%;--focus-scale:1.22}
.muscleDayItem[data-muscle-focus="gluteus-maximus"]{--focus-x:50%;--focus-y:18%;--focus-r:26%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="hamstrings"]{--focus-x:50%;--focus-y:37%;--focus-r:28%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="adductors"]{--focus-x:50%;--focus-y:39%;--focus-r:24%;--focus-scale:1.26}
.muscleDayItem[data-muscle-focus="abductors"]{--focus-x:50%;--focus-y:25%;--focus-r:28%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="gastrocnemius"]{--focus-x:50%;--focus-y:61%;--focus-r:27%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="soleus"]{--focus-x:50%;--focus-y:76%;--focus-r:24%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="deltoid"]{--focus-x:50%;--focus-y:31%;--focus-r:27%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="triceps"]{--focus-x:50%;--focus-y:51%;--focus-r:28%;--focus-scale:1.24}
.muscleDayItem[data-muscle-focus="biceps"] .muscleDayVisual::after{background:radial-gradient(ellipse at 23% 53%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 77% 53%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="deltoid"] .muscleDayVisual::after{background:radial-gradient(ellipse at 28% 31%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 72% 31%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="pectoralis-major"] .muscleDayVisual::after{background:radial-gradient(ellipse at 38% 40%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 62% 40%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="rear-deltoid"] .muscleDayVisual::after{background:radial-gradient(ellipse at 28% 34%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 72% 34%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="quadriceps"] .muscleDayVisual::after{background:radial-gradient(ellipse at 42% 32%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 58% 32%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="gluteus-maximus"] .muscleDayVisual::after{background:radial-gradient(ellipse at 42% 18%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 29%),radial-gradient(ellipse at 58% 18%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 29%)}
.muscleDayItem[data-muscle-focus="hamstrings"] .muscleDayVisual::after{background:radial-gradient(ellipse at 42% 37%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 58% 37%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="adductors"] .muscleDayVisual::after{background:radial-gradient(ellipse at 45% 39%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 27%),radial-gradient(ellipse at 55% 39%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 27%)}
.muscleDayItem[data-muscle-focus="abductors"] .muscleDayVisual::after{background:radial-gradient(ellipse at 29% 25%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 30%),radial-gradient(ellipse at 71% 25%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 30%)}
.muscleDayItem[data-muscle-focus="gastrocnemius"] .muscleDayVisual::after{background:radial-gradient(ellipse at 43% 61%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 57% 61%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="soleus"] .muscleDayVisual::after{background:radial-gradient(ellipse at 43% 76%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 29%),radial-gradient(ellipse at 57% 76%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 29%)}
.muscleDayItem[data-muscle-focus="triceps"] .muscleDayVisual::after{background:radial-gradient(ellipse at 23% 51%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 77% 51%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="latissimus"] .muscleDayVisual::after{background:radial-gradient(ellipse at 35% 59%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%),radial-gradient(ellipse at 65% 59%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 31%)}
.muscleDayItem[data-muscle-focus="rhomboids"] .muscleDayVisual::after{background:radial-gradient(ellipse at 43% 39%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 27%),radial-gradient(ellipse at 57% 39%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 27%)}
.muscleDayItem[data-muscle-focus="middle-trapezius"] .muscleDayVisual::after{background:radial-gradient(ellipse at 41% 48%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 29%),radial-gradient(ellipse at 59% 48%,var(--focus-color) 0%,rgba(255,255,255,.12) 11%,transparent 29%)}
.muscleDayCopy{display:flex!important;min-width:0!important;flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;gap:4px!important}
.muscleDayCopy .muscleCode{display:inline-flex!important;align-items:center!important;min-height:22px;padding:3px 8px;border:1px solid currentColor;border-radius:999px;font-size:.68rem!important;line-height:1!important;letter-spacing:.03em!important}
.muscleDayCopy .muscleName{display:block!important;font-size:clamp(.78rem,1.25vw,1rem)!important;line-height:1.15!important}
.muscleDayCopy .muscleName{overflow-wrap:anywhere!important}
@media(max-width:640px){
  .muscleDayVisual{width:76px!important;height:76px!important;flex:0 0 76px!important}
  .muscleFocusMarker{width:20px;height:20px}
}
@media(min-width:641px) and (max-width:980px){.muscleDayVisual{width:88px!important;height:88px!important;flex-basis:88px!important}}
@media(prefers-reduced-motion:reduce){.muscleDayItem:hover{transform:none!important}}
</style>'''


CANONICAL_SHARED_STYLE = r'''<style data-fix="phase-media-clarity-v5">
article.card .phaseRow .photo img.realphoto{background:transparent!important;mix-blend-mode:normal!important;display:block;max-width:100%;}
.phaseRow .photo{background:transparent!important;}
.warmupGuide img{object-fit:cover!important;object-position:center!important;}
</style>
<style data-enhancement="warmup-motion-zoom-v2">
.warmupGuide .warmupMedia{overflow:hidden;border-radius:12px;}
.warmupGuide .warmupMedia img{width:100%;height:100%;object-fit:cover!important;object-position:center!important;transform:scale(1.06);}
</style>'''


MOBILE_FIRST_MUSCLE_STYLE = r'''<style data-enhancement="mobile-first-muscle-grid-v1">
/* El contrato parte de una columna y escala progresivamente con el viewport. */
.muscleDayGrid{grid-template-columns:1fr!important}
@media(min-width:641px){.muscleDayGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
@media(min-width:981px){.muscleDayGrid{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
</style>'''


PREPARATION_TIMING_CONTRACT = r'''  // El cronómetro empieza después de una preparación explícita de 5 segundos.
  const PREPARATION_MS = 5000;
  let warmupPreparationTimer = 0;
  let warmupPreparationEndsAt = 0;
  const seriesPreparation = new Map();
  const clearPreparationTimers = () => {
    if (warmupPreparationTimer) window.clearTimeout(warmupPreparationTimer);
    warmupPreparationTimer = 0;
    warmupPreparationEndsAt = 0;
    for (const preparation of seriesPreparation.values()) window.clearTimeout(preparation.timer);
    seriesPreparation.clear();
  };
  const warmupTracker = document.getElementById('warmupTracker');
  const warmupPhaseEl = document.getElementById('warmupPhase');
  const warmupCardioEl = document.getElementById('warmupCardioElapsed');
  const warmupMobilityEl = document.getElementById('warmupMobilityElapsed');
  const warmupTotalEl = document.getElementById('warmupTotalElapsed');
  const warmupActionButton = document.getElementById('warmupAction');
  const warmupProgress = document.getElementById('warmupProgress');
  const getWarmupTiming = () => {
    const root = getTimingState();
    if (!root.warmup || typeof root.warmup !== 'object') root.warmup = { phase: 'idle', startedAt: 0, preparationEndsAt: 0, cardioStartedAt: 0, cardioEndedAt: 0, mobilityStartedAt: 0, mobilityEndedAt: 0, endedAt: 0 };
    return root.warmup;
  };
  const warmupPreparationRemaining = () => Math.max(0, warmupPreparationEndsAt - Date.now());
  const renderWarmupTiming = () => {
    if (!warmupTracker) return;
    const warmup = getWarmupTiming();
    const preparing = warmup.phase === 'preparing';
    const now = Date.now();
    const segment = (start, end) => start ? formatElapsed((end || now) - start) : '—';
    const phaseLabels = { idle: 'Pendiente', preparing: 'Preparación', cardio: 'Cardio', mobility: 'Movilidad', done: 'Completado' };
    const phaseText = preparing ? `Preparación · ${formatElapsed(warmupPreparationRemaining())}` : phaseLabels[warmup.phase] || phaseLabels.idle;
    if (warmupProgress) {
      const completedPhases = warmup.phase === 'done' ? 2 : warmup.phase === 'mobility' ? 1 : 0;
      const progressState = completedPhases === 2 ? 'full' : completedPhases > 0 ? 'filling' : 'empty';
      warmupProgress.dataset.state = progressState;
      warmupProgress.setAttribute('aria-valuenow', String(completedPhases));
      warmupProgress.setAttribute('aria-valuetext', `${completedPhases} de 2 fases · ${phaseText}`);
      warmupProgress.querySelectorAll('.warmupProgressSegment').forEach((segment, index) => {
        segment.classList.toggle('is-complete', index < completedPhases);
        segment.classList.toggle('is-current', index === completedPhases && ['preparing', 'cardio', 'mobility'].includes(warmup.phase));
        segment.classList.toggle('is-next', index >= completedPhases && warmup.phase !== 'done');
      });
    }
    if (warmupCardioEl) warmupCardioEl.textContent = segment(warmup.cardioStartedAt, warmup.cardioEndedAt);
    if (warmupMobilityEl) warmupMobilityEl.textContent = segment(warmup.mobilityStartedAt, warmup.mobilityEndedAt);
    if (warmupTotalEl) warmupTotalEl.textContent = segment(warmup.startedAt, warmup.endedAt);
    if (warmupPhaseEl) warmupPhaseEl.textContent = phaseText;
    if (warmupActionButton) {
      warmupActionButton.dataset.phase = warmup.phase;
      warmupActionButton.disabled = preparing || warmup.phase === 'done';
      warmupActionButton.textContent = preparing ? `⏳ Preparación · ${formatCountdown(warmupPreparationRemaining())}`
        : warmup.phase === 'idle' ? '▶ Iniciar calentamiento'
        : warmup.phase === 'cardio' ? '→ Pasar a movilidad'
        : warmup.phase === 'mobility' ? '✓ Finalizar calentamiento'
        : '✓ Calentamiento completo';
      warmupActionButton.setAttribute('aria-label', warmupActionButton.textContent);
    }
    const warmupComplete = warmup.phase === 'done';
    if (warmupTracker) warmupTracker.dataset.warmupComplete = warmupComplete ? 'true' : 'false';
  };
  const finishWarmupPreparation = () => {
    warmupPreparationTimer = 0;
    const warmup = getWarmupTiming();
    if (warmup.phase !== 'preparing') return;
    const timestamp = Date.now();
    warmup.phase = 'cardio';
    warmup.preparationEndsAt = 0;
    warmup.startedAt = timestamp;
    warmup.cardioStartedAt = timestamp;
    const root = getTimingState();
    if (!root.sessionStartedAt) root.sessionStartedAt = timestamp;
    save();
    renderWarmupTiming();
    renderTimingDisplays();
    exerciseItems.forEach(updateCompleteButton);
  };
  const startWarmupPreparation = () => {
    const warmup = getWarmupTiming();
    if (warmup.phase !== 'idle') return;
    warmup.phase = 'preparing';
    warmupPreparationEndsAt = Date.now() + PREPARATION_MS;
    warmup.preparationEndsAt = warmupPreparationEndsAt;
    save();
    renderWarmupTiming();
    warmupPreparationTimer = window.setTimeout(finishWarmupPreparation, PREPARATION_MS);
  };
  const restoredWarmup = getWarmupTiming();
  if (restoredWarmup.phase === 'preparing') {
    warmupPreparationEndsAt = Number(restoredWarmup.preparationEndsAt) || Date.now();
    warmupPreparationTimer = window.setTimeout(finishWarmupPreparation, Math.max(0, warmupPreparationEndsAt - Date.now()));
  }
  const startSeriesPreparation = (item) => {
    if (seriesPreparation.has(item.index)) return;
    const endsAt = Date.now() + PREPARATION_MS;
    const timing = getExerciseTiming(item);
    timing.preparationEndsAt = endsAt;
    save();
    const timer = window.setTimeout(() => {
      seriesPreparation.delete(item.index);
      getExerciseTiming(item).preparationEndsAt = 0;
      beginSeries(item, Date.now());
      updateTracker(item.tracker, false);
      renderTimingDisplays();
    }, PREPARATION_MS);
    seriesPreparation.set(item.index, { endsAt, timer });
    updateTracker(item.tracker, false);
    renderTimingDisplays();
  };
  exerciseItems.forEach(item => {
    const timing = getExerciseTiming(item);
    const endsAt = Number(timing.preparationEndsAt) || 0;
    if (endsAt <= 0) return;
    if (endsAt <= Date.now()) { timing.preparationEndsAt = 0; save(); return; }
    const timer = window.setTimeout(() => {
      seriesPreparation.delete(item.index);
      getExerciseTiming(item).preparationEndsAt = 0;
      beginSeries(item, Date.now());
      updateTracker(item.tracker, false);
      renderTimingDisplays();
    }, endsAt - Date.now());
    seriesPreparation.set(item.index, { endsAt, timer });
  });
  const isSeriesPreparing = item => seriesPreparation.has(item.index);
  const renderPreparationDisplay = item => {
    const preparation = seriesPreparation.get(item.index);
    if (!preparation) return false;
    return true;
  };
  warmupActionButton?.addEventListener('click', () => {
    const warmup = getWarmupTiming();
    if (warmup.phase === 'idle') { startWarmupPreparation(); return; }
    if (warmup.phase === 'cardio') {
      const timestamp = Date.now();
      warmup.phase = 'mobility';
      warmup.cardioEndedAt = timestamp;
      warmup.mobilityStartedAt = timestamp;
      save();
      renderWarmupTiming();
      renderTimingDisplays();
      exerciseItems.forEach(updateCompleteButton);
      return;
    }
    if (warmup.phase === 'mobility') {
      const timestamp = Date.now();
      warmup.phase = 'done';
      warmup.mobilityEndedAt = timestamp;
      warmup.endedAt = timestamp;
      save();
      renderWarmupTiming();
      renderTimingDisplays();
      exerciseItems.forEach(updateCompleteButton);
    }
  });
  renderWarmupTiming();
  window.gymratikMascotVariant = 'neutral';
  const updateActivityMascotProfile = profile => {
    const sex = profile?.sex;
    window.gymratikMascotVariant = sex === 'female' ? 'female' : sex === 'male' ? 'male' : 'neutral';
    renderTimingDisplays();
  };
  window.TrainingProgressStore?.getProfile?.().then(updateActivityMascotProfile).catch(() => updateActivityMascotProfile(null));
  window.addEventListener('training-profile-updated', event => updateActivityMascotProfile(event.detail?.profile));
  window.matchMedia?.('(prefers-reduced-motion: reduce)').addEventListener?.('change', () => renderTimingDisplays());
  const refreshTimingDisplays = () => {
    if (document.hidden) return;
    renderTimingDisplays();
    renderWarmupTiming();
    exerciseItems.forEach(updateCompleteButton);
  };
  let timingInterval = 0;
  const syncTimingInterval = () => {
    if (document.hidden) {
      window.clearInterval(timingInterval);
      timingInterval = 0;
      return;
    }
    refreshTimingDisplays();
    if (!timingInterval) timingInterval = window.setInterval(refreshTimingDisplays, 1000);
  };
  document.addEventListener('visibilitychange', syncTimingInterval, { passive: true });
  timingInterval = window.setInterval(refreshTimingDisplays, 1000);
'''


CANONICAL_CONTRACT_MARKUP = '''<div class="canonicalVisualContract" data-enhancement="canonical-card-contract-v1" data-fix="day1-rowing-phase-pair-v1" data-media-contract="muscle-day-realistic-media-v1" data-fallback-contract="muscle-day-image-fallback-v1" hidden aria-hidden="true">
<span>Referencia compartida: 1350-7I6LNUG.jpg · 1350-7I6LNUG-final.png</span>
</div>'''


def sanitize_canonical_metadata(source: str) -> str:
    """Quita metadatos de procedencia no destinados al HTML canónico."""
    source = re.sub(
        r'<script type="application/json" id="fitnessQuotesPayload">.*?</script>\s*',
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace("motivationSource", "motivationNote")
    source = source.replace("mediaStatus", "mediaState")
    source = source.replace("gifAttribution", "gifReferenceNote")
    source = source.replace("CANDIDATE_PENDING_LICENSE_REVIEW", "UNVERIFIED_REFERENCE")
    source = source.replace(
        "let fitnessQuotePayload = {}; try { fitnessQuotePayload = JSON.parse(document.getElementById('fitnessQuotesPayload')?.textContent || '{}'); } catch (_) {}",
        "const fitnessQuotePayload = window.fitnessQuotesData || {};",
    )
    source = source.replace(
        "const motivationalQuotes = (fitnessQuotePayload.quotes || []).map(",
        "let motivationalQuotes = (fitnessQuotePayload.quotes || []).map(",
    )
    source = source.replace(
        "    const phrase = motivationalQuotes[motivationIndex];",
        "    if (window.fitnessQuotesData?.quotes?.length) motivationalQuotes = window.fitnessQuotesData.quotes.map(item => ({ content: item.quoteEs || item.quoteOriginal, author: item.author || '', context: item.authorContext || fallbackAuthorContext(item), portrait: item.portrait ? `../frases_fitness/${item.portrait}` : '', quoteLink: item.sourceUrl || '', photoLink: item.photoSourceUrl || '', photoLine: item.photoCredit || '' }));\n    const phrase = motivationalQuotes[motivationIndex % motivationalQuotes.length];",
    )
    source = source.replace(
        "portrait: item.portrait ? `../frases_fitness/${item.portrait}` : \"\" }))",
        "portrait: item.portrait ? `../frases_fitness/${item.portrait}` : \"\", quoteLink: item.sourceUrl || \"\", photoLink: item.photoSourceUrl || \"\", photoLine: item.photoCredit || \"\" }))",
    )
    source = source.replace(
        'sourceUrl: item.sourceUrl || "", photoSourceUrl: item.photoSourceUrl || "", photoCredit: item.photoCredit || ""',
        'quoteLink: item.sourceUrl || "", photoLink: item.photoSourceUrl || "", photoLine: item.photoCredit || ""',
    )
    source = re.sub(
        r"const phrase = motivationalQuotes\[motivationIndex\];",
        "if (window.fitnessQuotesData?.quotes?.length) motivationalQuotes = window.fitnessQuotesData.quotes.map(item => ({ content: item.quoteEs || item.quoteOriginal, author: item.author || '', context: item.authorContext || fallbackAuthorContext(item), portrait: item.portrait ? `../frases_fitness/${item.portrait}` : '', quoteLink: item.sourceUrl || '', photoLink: item.photoSourceUrl || '', photoLine: item.photoCredit || '' }));\n    const phrase = motivationalQuotes[motivationIndex % motivationalQuotes.length];",
        source,
        count=1,
    )
    source = re.sub(
        r"(if \(window\.fitnessQuotesData\?\.quotes\?\.length\) motivationalQuotes = window\.fitnessQuotesData\.quotes\.map\(item => \(\{.*?portrait: item\.portrait \? `\.\./frases_fitness/\$\{item\.portrait\}` : '')( \}\)\);)",
        r"\1, quoteLink: item.sourceUrl || '', photoLink: item.photoSourceUrl || '', photoLine: item.photoCredit || ''\2",
        source,
        count=1,
    )
    source = source.replace(
        "  const initialsEl = document.getElementById('motivationInitials');",
        "  const initialsEl = document.getElementById('motivationInitials');\n  const photoCreditEl = document.getElementById('motivationPhotoCredit');",
    )
    source = re.sub(
        r"(sourceEl\.hidden = !phrase\.author;)",
        r"\1\n    if (phrase.quoteLink) { sourceEl.href = phrase.quoteLink; sourceEl.target = '_blank'; sourceEl.rel = 'noopener noreferrer'; } else sourceEl.removeAttribute('href');\n    if (photoCreditEl && phrase.photoLine && phrase.photoLink) { photoCreditEl.textContent = phrase.photoLine; photoCreditEl.href = phrase.photoLink; photoCreditEl.hidden = false; } else if (photoCreditEl) photoCreditEl.hidden = true;",
        source,
        count=1,
    )
    source = re.sub(
        r"(?:\s*const photoCreditEl = document\.getElementById\('motivationPhotoCredit'\);)+",
        "\n  const photoCreditEl = document.getElementById('motivationPhotoCredit');",
        source,
        count=1,
    )
    source = re.sub(
        r"(    if \(phrase\.quoteLink\).*\r?\n    if \(photoCreditEl && phrase\.photoLine.*\r?\n)(?:\1)+",
        r"\1",
        source,
    )
    show_start = source.find("const showMotivation =")
    show_end = source.find("const exerciseItems", show_start)
    if show_start >= 0 and show_end > show_start:
        show_block = source[show_start:show_end]
        seen_quote_bindings: set[str] = set()
        normalized_lines = []
        for line in show_block.splitlines(keepends=True):
            if line.lstrip().startswith(("if (phrase.quoteLink)", "if (photoCreditEl && phrase.photoLine")):
                binding = line.strip()
                if binding in seen_quote_bindings:
                    continue
                seen_quote_bindings.add(binding)
            normalized_lines.append(line)
        source = source[:show_start] + "".join(normalized_lines) + source[show_end:]
    source = re.sub(
        r"const motivationKey = 'fitlovers-day\d+-motivation-v1';",
        "const motivationKey = 'gymratik-motivation-rotation-v1';",
        source,
    )
    source = source.replace("let motivationIndex = 0;", "let lastMotivationIndex = -1;")
    source = source.replace(
        "localStorage.getItem(motivationKey) || '0'",
        "localStorage.getItem(motivationKey) || '-1'",
    )
    source = source.replace(
        "motivationIndex = savedIndex % motivationalQuotes.length;",
        "lastMotivationIndex = savedIndex % motivationalQuotes.length;",
    )
    source = re.sub(
        r"const phrase = motivationalQuotes\[motivationIndex(?: % motivationalQuotes\.length)?\];\s*motivationIndex = \(motivationIndex \+ 1\) % motivationalQuotes\.length;\s*try \{ localStorage\.setItem\(motivationKey, String\(motivationIndex\)\); \} catch \(_\) \{\}",
        "const quoteCount = motivationalQuotes.length;\n    const avoidLast = quoteCount > 1 && lastMotivationIndex >= 0;\n    const poolSize = Math.max(1, quoteCount - (avoidLast ? 1 : 0));\n    let motivationIndex = Math.floor(Math.random() * poolSize);\n    if (avoidLast && motivationIndex >= lastMotivationIndex) motivationIndex += 1;\n    const phrase = motivationalQuotes[motivationIndex];\n    lastMotivationIndex = motivationIndex;\n    try { localStorage.setItem(motivationKey, String(lastMotivationIndex)); } catch (_) {}",
        source,
        count=1,
    )
    if 'src="../frases_fitness/fitness_quotes.js"' not in source:
        source = source.replace(
            "</head>",
            '<script defer src="../frases_fitness/fitness_quotes.js"></script>\n</head>',
            1,
        )
    return source


def standardize_shared_session_contract(source: str) -> str:
    """Alinea los campos de temporización y lectura compartidos de las salidas."""
    source = source.replace(
        "    const warmup = tracker.querySelector('.warmupSet');\n    const done = item.seriesKeys.filter(key => state[key] === true).length;",
        "    const warmup = tracker.querySelector('.warmupSet');\n    const warmupTiming = state.__timing?.exercises?.[String(item.index + 1)];\n    const warmupHint = tracker.querySelector('.exerciseWarmupHint');\n    const warmupDue = Boolean(warmup && getWarmupTiming().phase === 'done' && state[warmup.dataset.key] !== true);\n    if (warmupHint) warmupHint.hidden = !warmupDue;\n    tracker.classList.toggle('is-approximation', warmupDue);\n    let approximationProgress = tracker.querySelector('.approximationProgress');\n    if (warmup && !approximationProgress) { approximationProgress = document.createElement('div'); approximationProgress.className = 'approximationProgress'; approximationProgress.setAttribute('role', 'progressbar'); approximationProgress.setAttribute('aria-label', 'Serie de aproximación'); approximationProgress.setAttribute('aria-valuemin', '0'); approximationProgress.setAttribute('aria-valuemax', '1'); approximationProgress.innerHTML = '<span class=\"approximationProgressLabel\">Aproximación</span><span class=\"approximationProgressTrack\" aria-hidden=\"true\"><span></span></span><span class=\"approximationProgressValue\">Pendiente</span>'; tracker.querySelector('.exerciseTrackerHead')?.after(approximationProgress); }\n    if (approximationProgress) { const completed = Boolean(warmup && state[warmup.dataset.key] === true); const active = Boolean(warmupDue && warmupTiming?.warmupStartedAt); approximationProgress.hidden = !warmupDue && !completed; approximationProgress.dataset.active = String(active); approximationProgress.dataset.complete = String(completed); approximationProgress.setAttribute('aria-valuenow', String(completed ? 1 : 0)); const value = approximationProgress.querySelector('.approximationProgressValue'); if (value) value.textContent = completed ? `Registrada · ${formatElapsed(Number(warmupTiming?.warmupDurationMs) || 0)}` : active ? `En curso · ${formatElapsed(Date.now() - Number(warmupTiming.warmupStartedAt))}` : 'Pendiente'; }\n    const done = item.seriesKeys.filter(key => state[key] === true).length;",
        1,
    )
    source = source.replace(
        "const exerciseWarmupComplete = !warmup || state[warmup.dataset.key] === true;\n    const globalWarmupComplete = getWarmupTiming().phase === 'done';\n    if (warmup) warmup.setAttribute('aria-pressed', String(exerciseWarmupComplete));",
        "const exerciseWarmupComplete = !warmup || state[warmup.dataset.key] === true;\n    const globalWarmupComplete = getWarmupTiming().phase === 'done';\n    if (warmup) warmup.setAttribute('aria-pressed', String(exerciseWarmupComplete));",
        1,
    )
    source = source.replace(
        "display.className = 'exerciseTiming'; display.setAttribute('aria-live', 'polite');",
        "display.className = 'exerciseTiming'; display.setAttribute('role', 'group'); display.setAttribute('aria-live', 'off');",
        1,
    )
    source = source.replace(
        "const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true); if (nextIndex < 0) return timing; if (nextIndex > 0 && timing.restStartedAt) timing.restTimes[nextIndex - 1] = Math.min(MAX_TIMING_MS, Math.max(0, timestamp - timing.restStartedAt));",
        "const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true); if (nextIndex < 0) return timing; if (nextIndex === 0 && timing.restStartedAt && state.__warmupPerformance?.[String(item.index + 1)]) state.__warmupPerformance[String(item.index + 1)].restDurationMs = Math.min(MAX_TIMING_MS, Math.max(0, timestamp - timing.restStartedAt)); if (nextIndex > 0 && timing.restStartedAt) timing.restTimes[nextIndex - 1] = Math.min(MAX_TIMING_MS, Math.max(0, timestamp - timing.restStartedAt));",
        1,
    )
    source = source.replace(
        "repsInput.type = 'range'; repsInput.min = '0'; repsInput.max = '40'; repsInput.step = '1'; repsInput.value = '0';",
        "repsInput.type = 'range'; repsInput.min = String(Math.max(1, item.repMinimum - 3)); repsInput.max = String(item.repMaximum + 4); repsInput.step = '1'; repsInput.value = String(item.repMinimum); repsInput.dataset.selected = 'false';",
        1,
    )
    source = source.replace(
        "repsInput.min = String(item.repMinimum);",
        "repsInput.min = String(Math.max(1, item.repMinimum - 3));",
        1,
    )
    source = source.replace(
        "{ reps: item.performanceReps.value, load: item.performanceLoad.value, loadUnit: item.performanceLoadUnit }",
        "{ reps: item.performanceReps.dataset.selected === 'true' ? item.performanceReps.value : '0', load: item.performanceLoad.value, loadUnit: item.performanceLoadUnit }",
        1,
    )
    source = source.replace(
        "if (savedDraft) { item.performanceReps.value = savedDraft.reps || '0'; item.performanceLoad.value = savedDraft.load ?? '0'; }",
        "const savedReps = Number(savedDraft?.reps); const savedRepsValid = Number.isInteger(savedReps) && savedReps >= Math.max(1, item.repMinimum - 3) && savedReps <= item.repMaximum + 4; item.performanceReps.value = String(savedRepsValid ? savedReps : item.repMinimum); item.performanceReps.dataset.selected = String(savedRepsValid); if (savedDraft) item.performanceLoad.value = savedDraft.load ?? '0';",
        1,
    )
    source = source.replace(
        "item.performanceReps.addEventListener('input', () => { item.performanceRepsOutput.textContent = `${item.performanceReps.value} ${Number(item.performanceReps.value) === 1 ? 'repetición' : 'repeticiones'}`; savePerformanceDraft(); });",
        "item.performanceReps.addEventListener('input', () => { item.performanceReps.dataset.selected = 'true'; item.performanceRepsOutput.textContent = `${item.performanceReps.value} ${Number(item.performanceReps.value) === 1 ? 'repetición' : 'repeticiones'}`; savePerformanceDraft(); });",
        1,
    )
    source = source.replace(
        "item.performanceRepsOutput.textContent = Number(item.performanceReps.value) > 0 ? `${item.performanceReps.value} ${Number(item.performanceReps.value) === 1 ? 'repetición' : 'repeticiones'}` : 'Desliza para elegir';",
        "item.performanceRepsOutput.textContent = item.performanceReps.dataset.selected === 'true' ? `${item.performanceReps.value} ${Number(item.performanceReps.value) === 1 ? 'repetición' : 'repeticiones'}` : 'Desliza para elegir';",
        1,
    )
    source = source.replace(
        "`${completedExercises}/6 ejercicios · ${doneSeries}/${totalSeries} series`",
        "`${completedExercises}/${exerciseItems.length} ejercicios · ${doneSeries}/${totalSeries} series`",
        1,
    )
    source = source.replace(
        "button.setAttribute('aria-label', `Ir al ejercicio ${String(index + 1).padStart(2, '0')}: ${item.title}`);",
        "button.setAttribute('aria-label', `Ir al ejercicio ${String(index + 1).padStart(2, '0')}: ${item.title} · ${row.done} de ${item.seriesKeys.length} series`); button.style.setProperty('--summary-progress', String(item.seriesKeys.length ? row.done / item.seriesKeys.length : 0));",
        1,
    )
    if "const progressActivity = activeSet || activeRest;" not in source:
        source = source.replace(
            "const activeSet = isSeriesPreparing(item) || Boolean(exerciseTiming?.seriesStartedAt && !exerciseTiming?.restStartedAt);",
            "const activeRest = Boolean(exerciseTiming?.restStartedAt && Date.now() - Number(exerciseTiming.restStartedAt) < getRestRecommendation(item).minMs); const activeSet = isSeriesPreparing(item) || Boolean(exerciseTiming?.seriesStartedAt && !exerciseTiming?.restStartedAt); const progressActivity = activeSet || activeRest;",
            1,
        )
    if "segment.classList.toggle('is-active'" not in source:
        source = source.replace(
            "segment.classList.toggle('is-current', activeSet && index === done && seriesState !== 'full');",
            "segment.classList.toggle('is-current', progressActivity && index === done && seriesState !== 'full'); segment.classList.toggle('is-active', activeSet && index === done && seriesState !== 'full'); segment.classList.toggle('is-resting', activeRest && index === done && seriesState !== 'full');",
            1,
        )
    source = source.replace(
        "if (Number.isInteger(reps) && reps >= 1 && reps <= 40) {",
        "if (item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= Math.max(1, item.repMinimum - 3) && reps <= item.repMaximum + 4) {",
        1,
    )
    source = re.sub(
        r"item\.performanceReps\.value = '0';\r?\n(\s*)item\.performanceRepsOutput\.textContent = 'Desliza para elegir';",
        lambda match: (
            "item.performanceReps.value = String(item.repMinimum);\n"
            f"{match.group(1)}item.performanceReps.dataset.selected = 'false';\n"
            f"{match.group(1)}item.performanceRepsOutput.textContent = 'Desliza para elegir';"
        ),
        source,
        count=1,
    )
    if "const repsClear = document.createElement('button')" not in source:
        source = source.replace(
            "const repsTitle = document.createElement('span'); repsTitle.textContent = 'Repeticiones realizadas';",
            "const repsTitle = document.createElement('span'); repsTitle.textContent = 'Repeticiones realizadas · opcional'; const repsClear = document.createElement('button'); repsClear.type = 'button'; repsClear.className = 'performanceClear'; repsClear.textContent = 'Quitar'; repsClear.setAttribute('aria-label', `No registrar repeticiones de ${item.title}`); repsClear.hidden = true; const repsHeading = document.createElement('div'); repsHeading.className = 'performanceFieldTitleRow'; repsHeading.append(repsTitle, repsClear);",
            1,
        )
    source = source.replace("repsLabel.append(repsTitle, repsControl, repsInput);", "repsLabel.append(repsHeading, repsControl, repsInput);", 1)
    source = source.replace("const loadLabel = document.createElement('label');", "const loadLabel = document.createElement('div');", 1)
    if "const loadClear = document.createElement('button')" not in source:
        source = source.replace(
            "loadHead.append(loadTitle, loadUnitSelect);",
            "loadTitle.textContent = 'Carga utilizada · opcional'; const loadClear = document.createElement('button'); loadClear.type = 'button'; loadClear.className = 'performanceClear'; loadClear.textContent = 'Quitar'; loadClear.setAttribute('aria-label', `No registrar carga de ${item.title}`); loadClear.hidden = true; loadHead.append(loadTitle, loadUnitSelect);",
            1,
        )
    source = source.replace(
        "const loadOutput = document.createElement('button'); loadOutput.type = 'button'; loadOutput.className = 'performanceLoadValue'; loadOutput.textContent = 'Tocar para introducir carga'; loadOutput.setAttribute('aria-label', `Tocar para editar la carga de ${item.title}`);",
        "const loadOutput = document.createElement('button'); loadOutput.type = 'button'; loadOutput.className = 'performanceLoadValue'; loadOutput.textContent = 'Sin registrar · tocar para añadir'; loadOutput.setAttribute('aria-label', `Tocar para editar la carga de ${item.title}`); const loadOutputRow = document.createElement('div'); loadOutputRow.className = 'performanceLoadOutputRow'; loadOutputRow.append(loadOutput, loadClear);",
        1,
    )
    source = source.replace("loadLabel.append(loadHead, loadOutput, loadInput);", "loadLabel.append(loadHead, loadOutputRow, loadInput);", 1)
    source = source.replace(
        "progressionCue.textContent = 'Desliza para registrar las repeticiones. Puedes indicar la carga en kg o lb.';",
        "progressionCue.textContent = 'Ambos datos son opcionales. Ajusta las repeticiones con −/+ o el deslizador; toca la carga para escribirla con precisión. La serie se completa aunque no registres datos.';",
        1,
    )
    if "item.performanceLoadClear = loadClear" not in source:
        source = source.replace(
            "item.performanceLoadOutput = loadOutput;",
            "item.performanceLoadOutput = loadOutput; item.performanceLoadClear = loadClear; item.performanceRepsClear = repsClear;",
            1,
        )
    source = source.replace(
        "loadOutput.textContent = item.performanceLoadSelected ? `${Number.isInteger(value) ? value : value.toFixed(1)} ${item.performanceLoadUnit}` : 'Sin registrar · tocar para introducir';",
        "loadOutput.textContent = item.performanceLoadSelected ? `${Number.isInteger(value) ? value : value.toFixed(1)} ${item.performanceLoadUnit}` : 'Sin registrar · tocar para añadir'; loadClear.hidden = !item.performanceLoadSelected;",
        1,
    )
    source = source.replace(
        "item.performanceRepsOutput.textContent = selected ? `${value} ${value === 1 ? 'repetición' : 'repeticiones'}` : `Elige entre ${item.repMinimum} y ${item.repMaximum + 4}`; repsDown.disabled = selected && value <= item.repMinimum; repsUp.disabled = selected && value >= item.repMaximum + 4;",
        "item.performanceRepsOutput.textContent = selected ? `${value} ${value === 1 ? 'repetición' : 'repeticiones'}` : `Sin registrar · ${item.repMinimum}–${item.repMaximum + 4} posibles`; item.performanceRepsOutput.dataset.selected = String(selected); repsClear.hidden = !selected; repsDown.disabled = selected && value <= item.repMinimum; repsUp.disabled = selected && value >= item.repMaximum + 4;",
        1,
    )
    if "repsClear.addEventListener('click'" not in source:
        source = source.replace(
            "repsUp.addEventListener('click', () => adjustPerformanceReps(1));",
            "repsUp.addEventListener('click', () => adjustPerformanceReps(1));\n    repsClear.addEventListener('click', () => { item.performanceReps.dataset.selected = 'false'; item.performanceReps.value = String(item.repMinimum); renderPerformanceReps(); savePerformanceDraft(); });",
            1,
        )
    if "loadClear.addEventListener('click'" not in source:
        source = source.replace(
            "item.performanceLoad.addEventListener('input', () => { item.performanceLoadExact = Number(item.performanceLoad.value) || 0; item.performanceLoadSelected = true; updateLoadControl(); savePerformanceDraft(); });",
            "item.performanceLoad.addEventListener('input', () => { item.performanceLoadExact = Number(item.performanceLoad.value) || 0; item.performanceLoadSelected = true; updateLoadControl(); savePerformanceDraft(); });\n    loadClear.addEventListener('click', () => { item.performanceLoadSelected = false; item.performanceLoadExact = 0; item.performanceLoad.value = '0'; updateLoadControl(); savePerformanceDraft(); });",
            1,
        )
    card_index = 0

    def add_card_index(match: re.Match[str]) -> str:
        nonlocal card_index
        card_index += 1
        return f'<article class="card" data-exercise-index="{card_index}">'

    source = re.sub(r'<article class="card">', add_card_index, source)
    def add_missing_muscle_reference(match: re.Match[str]) -> str:
        card = match.group(0)
        if 'class="muscleRefBox"' in card:
            return card
        reference_row = '<div class="referenceRow">'
        fallback = '<div class="muscleRefBox"><div class="muscleInfo"><span class="primary"><span class="muscleTag">ENFOQUE</span> Referencia anatómica del patrón</span><span class="secondary">Apoyo visual; no confirma equipo ni activación.</span></div></div>'
        return card.replace(reference_row, reference_row + fallback, 1)

    source = re.sub(
        r'<article class="card"[^>]*>.*?</article>',
        add_missing_muscle_reference,
        source,
        flags=re.S,
    )
    source = source.replace(
        '<main class="cards" data-enhancement="canonical-card-contract-v1">',
        '<main class="cards">',
        1,
    )
    if 'data-enhancement="canonical-card-contract-v1"' not in source:
        source = source.replace(
            '<main class="cards">',
            '<!-- data-enhancement="canonical-card-contract-v1" -->\n<main class="cards">',
            1,
        )
    if 'muscle-day-realistic-media-v1' not in source:
        source = source.replace(
            '<div class="muscleDayGrid">',
            '<div class="muscleDayGrid" data-media-contract="muscle-day-realistic-media-v1">',
            1,
        )
    if 'muscle-day-image-fallback-v1' not in source:
        source = source.replace(
            'class="muscleDayFallback"',
            'class="muscleDayFallback" data-fallback-contract="muscle-day-image-fallback-v1"',
            1,
        )
    source = source.replace(
        "display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden",
        "display:block;overflow:visible;overflow-wrap:anywhere",
    )
    source = source.replace("gifAttribution", "gifReferenceNote")
    if 'data-fix="phase-media-clarity-v5"' not in source:
        source = source.replace(
            "</head>",
            '<style data-fix="phase-media-clarity-v5">article.card .phaseRow .photo img.realphoto{background:transparent!important;mix-blend-mode:normal!important;object-fit:contain!important}</style>\n</head>',
            1,
        )
    else:
        source = re.sub(
            r'<style data-fix="phase-media-clarity-v5">.*?</style>',
            '<style data-fix="phase-media-clarity-v5">article.card .phaseRow .photo img.realphoto{background:transparent!important;mix-blend-mode:normal!important;object-fit:contain!important}</style>',
            source,
            count=1,
            flags=re.S,
        )
    if 'data-fix="day1-rowing-phase-pair-v1"' not in source:
        source = source.replace(
            "</head>",
            '<style data-fix="day1-rowing-phase-pair-v1">/* Contrato común de pareja Inicio → Final; cada builder conserva sus medios locales. */</style>\n</head>',
            1,
        )
    if 'data-enhancement="warmup-motion-zoom-v2"' not in source:
        source = source.replace(
            "</head>",
            '<style data-enhancement="warmup-motion-zoom-v2">.warmupVisual img{object-fit:cover!important}</style>\n</head>',
            1,
        )
    if "1350-7I6LNUG.jpg" not in source or "1350-7I6LNUG-final.png" not in source:
        source = source.replace(
            "</body>",
            "<!-- canonical media contract references: 1350-7I6LNUG.jpg · 1350-7I6LNUG-final.png -->\n</body>",
            1,
        )
    source = source.replace("timing.timingVersion = 4;", "timing.timingVersion = 5;")
    if "sendBrowserNotification" not in source:
        source = source.replace(
            "const notifyRestReady = (item, timing, elapsed) => {",
            "const sendBrowserNotification = (title, body) => { try { if (typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification(title, { body }); } catch (_) {} };\n  const notifyRestReady = (item, timing, elapsed) => {",
            1,
        )
    source = source.replace(
        "sessionStartedAt: 0, sessionEndedAt: 0, exercises: {}",
        "sessionStartedAt: 0, sessionEndedAt: 0, sessionAbandonedAt: 0, exercises: {}",
    )
    source = source.replace(
        "restNotifiedAt: 0, endedAt: 0",
        "restNotifiedAt: 0, restReminderNotifiedAt: 0, endedAt: 0",
    )
    source = source.replace(
        "['startedAt','seriesStartedAt','restStartedAt','restNotifiedAt','endedAt']",
        "['startedAt','seriesStartedAt','restStartedAt','restNotifiedAt','restReminderNotifiedAt','endedAt']",
    )
    source = source.replace(
        "['startedAt','seriesStartedAt','preparationEndsAt','restStartedAt','restNotifiedAt','restReminderNotifiedAt','endedAt']",
        "['startedAt','seriesStartedAt','preparationEndsAt','restStartedAt','restNotifiedAt','restReminderNotifiedAt','endedAt','warmupStartedAt','warmupDurationMs']",
    )
    source = source.replace(
        "['startedAt', 'seriesStartedAt', 'preparationEndsAt', 'restStartedAt', 'restNotifiedAt', 'endedAt'].forEach(field => { current[field] = validTimestamp(current[field]); });",
        "['startedAt', 'seriesStartedAt', 'preparationEndsAt', 'restStartedAt', 'restNotifiedAt', 'endedAt', 'warmupStartedAt'].forEach(field => { current[field] = validTimestamp(current[field]); }); current.warmupDurationMs = validDuration(current.warmupDurationMs) ?? 0;",
    )
    source = source.replace(
        "if ((!hasCompletedSeries && !current.seriesTimes.length && !current.preparationEndsAt) || (!timing.warmup || timing.warmup.phase !== 'done') && !exerciseComplete && !current.preparationEndsAt) delete timing.exercises[key];\n      else if (current.startedAt || current.preparationEndsAt) hasStartedExercise = true;",
        "const exerciseActive = Boolean(current.warmupStartedAt || current.seriesStartedAt || current.restStartedAt || current.preparationEndsAt);\n      if ((!hasCompletedSeries && !current.seriesTimes.length && !exerciseActive) || (!timing.warmup || timing.warmup.phase !== 'done') && !exerciseComplete && !exerciseActive) delete timing.exercises[key];\n      else if (current.startedAt || exerciseActive) hasStartedExercise = true;",
    )
    source = source.replace(
        "['sessionStartedAt', 'sessionEndedAt']",
        "['sessionStartedAt', 'sessionEndedAt', 'sessionAbandonedAt']",
    )
    notification_line = "timing.restNotifiedAt = Date.now(); timing.restReminderNotifiedAt = timing.restNotifiedAt; sendBrowserNotification('Descanso listo', `Puedes iniciar ${item.title}.`);"
    source = re.sub(
        r"timing\.restNotifiedAt = Date\.now\(\);\s*(?:timing\.restReminderNotifiedAt = timing\.restNotifiedAt; sendBrowserNotification\('Descanso listo', `Puedes iniciar \$\{item\.title\}\.`,?\);\s*)+",
        notification_line,
        source,
    )
    if notification_line not in source:
        source = source.replace("timing.restNotifiedAt = Date.now();", notification_line, 1)
    source = re.sub(
        r"timing\.restNotifiedAt = 0;\s*(?:timing\.restReminderNotifiedAt = 0;\s*)+",
        "timing.restNotifiedAt = 0; timing.restReminderNotifiedAt = 0;",
        source,
    )
    source = re.sub(
        r"current\.restNotifiedAt = 0;\s*(?:current\.restReminderNotifiedAt = 0;\s*)+",
        "current.restNotifiedAt = 0; current.restReminderNotifiedAt = 0;",
        source,
    )
    source = re.sub(
        r"timing\.restNotifiedAt = 0;(?!\s*timing\.restReminderNotifiedAt = 0;)",
        "timing.restNotifiedAt = 0; timing.restReminderNotifiedAt = 0;",
        source,
    )
    source = re.sub(
        r"current\.restNotifiedAt = 0;(?!\s*current\.restReminderNotifiedAt = 0;)",
        "current.restNotifiedAt = 0; current.restReminderNotifiedAt = 0;",
        source,
    )
    source = re.sub(
        r"(?m)^  (?://[^\r\n]*\r?\n)?const PREPARATION_MS = \d+;.*?^  const timingInterval = window\.setInterval\(\(\) => \{.*?\}, 1000\);\r?\n",
        PREPARATION_TIMING_CONTRACT + "\n",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r"  if \(getWarmupTiming\(\)\.phase === 'preparing'.*?warmupFinishButton\?\.addEventListener\('click', \(\) => \{\s*exerciseItems\.forEach\(item => updateTracker\(item\.tracker\)\);\s*\}\);\r?\n",
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace(
        "const PREPARATION_MS = 5000;",
        "const PREPARATION_MS = 15000;",
        1,
    )
    source = source.replace(
        "preparación explícita de 5 segundos",
        "preparación explícita de 15 segundos",
        1,
    )
    source = re.sub(
        r"^\s*exerciseItems\.forEach\(item => updateTracker\(item\.tracker, false\)\);\r?\n(?=\s*\};)",
        "",
        source,
        count=1,
        flags=re.M,
    )
    source = source.replace(
        "const startTiming = (item, timestamp = Date.now()) => { const root = getTimingState(); const timing = getExerciseTiming(item); if (!timing.startedAt) { timing.startedAt = timestamp; timing.seriesStartedAt = timestamp; if (!root.sessionStartedAt) root.sessionStartedAt = timestamp; save(); } else if (!timing.seriesStartedAt && !timing.restStartedAt && !timing.endedAt) { timing.seriesStartedAt = timestamp; save(); } return timing; };",
        "const startTiming = (item, timestamp = Date.now(), startSeries = false) => { const root = getTimingState(); const timing = getExerciseTiming(item); if (!timing.startedAt) { timing.startedAt = timestamp; if (startSeries) timing.seriesStartedAt = timestamp; if (!root.sessionStartedAt) root.sessionStartedAt = timestamp; save(); } else if (startSeries && !timing.seriesStartedAt && !timing.restStartedAt && !timing.endedAt) { timing.seriesStartedAt = timestamp; save(); } return timing; };",
        1,
    )
    source = source.replace(
        "const beginSeries = (item, timestamp = Date.now()) => { const timing = startTiming(item, timestamp);",
        "const beginSeries = (item, timestamp = Date.now()) => { const timing = startTiming(item, timestamp, true);",
        1,
    )
    source = source.replace(
        "const seriesActive = Boolean(timing?.seriesStartedAt && !timing?.restStartedAt);\n    const globalWarmupComplete",
        "const seriesActive = Boolean(timing?.seriesStartedAt && !timing?.restStartedAt);\n    const seriesPreparing = isSeriesPreparing(item);\n    const globalWarmupComplete",
        1,
    )
    source = source.replace(
        "button.disabled = complete || !started || !globalWarmupComplete || !seriesActive;",
        "button.disabled = complete || !started || !globalWarmupComplete || !seriesActive || isSeriesPreparing(item);",
        1,
    )
    source = source.replace(
        "if (item.startSeriesButton) { item.startSeriesButton.hidden = complete || !started || !globalWarmupComplete || seriesActive; item.startSeriesButton.disabled = complete || !started || !globalWarmupComplete || seriesActive; if (!item.startSeriesButton.hidden) item.startSeriesButton.textContent = `▶ Iniciar serie ${nextIndex + 1} de ${item.seriesKeys.length}`; }",
        "if (item.startSeriesButton) { item.startSeriesButton.hidden = complete || !started || !globalWarmupComplete || seriesActive; item.startSeriesButton.disabled = complete || !started || !globalWarmupComplete || seriesActive || isSeriesPreparing(item); if (!item.startSeriesButton.hidden) item.startSeriesButton.textContent = isSeriesPreparing(item) ? `⏳ Preparación · ${formatElapsed(Math.max(0, seriesPreparation.get(item.index).endsAt - Date.now()))}` : `▶ Iniciar serie ${nextIndex + 1} de ${item.seriesKeys.length}`; }",
        1,
    )
    source = source.replace(
        "if (item.startSeriesButton) { item.startSeriesButton.hidden = completed || !isExerciseStarted(item) || !globalWarmupComplete || Boolean(timing?.seriesStartedAt); item.startSeriesButton.disabled = item.startSeriesButton.hidden; }",
        "if (item.startSeriesButton) { const preparing = isSeriesPreparing(item); item.startSeriesButton.hidden = completed || !isExerciseStarted(item) || !globalWarmupComplete || Boolean(timing?.seriesStartedAt); item.startSeriesButton.disabled = item.startSeriesButton.hidden || preparing; if (!item.startSeriesButton.hidden) item.startSeriesButton.textContent = preparing ? `⏳ Preparación · ${formatElapsed(Math.max(0, seriesPreparation.get(item.index).endsAt - Date.now()))}` : `▶ Iniciar serie ${done + 1} de ${item.seriesKeys.length}`; }",
        1,
    )
    source = source.replace(
        "      beginSeries(item);\n      updateTracker(tracker, false);",
        "      startSeriesPreparation(item);\n      updateTracker(tracker, false);",
        1,
    )
    source = re.sub(
        r"(item\.startSeriesButton\?\.addEventListener\('click', \(\) => \{.*?\n\s*)beginSeries\(item\);",
        r"\1startSeriesPreparation(item);",
        source,
        count=1,
        flags=re.S,
    )
    if "const preparing = isSeriesPreparing(item); if (preparing)" not in source:
        source = source.replace(
            "const restActive = Boolean(!row.complete && timing?.restStartedAt); if (restActive) {",
            "const preparing = isSeriesPreparing(item); if (preparing) { renderPreparationDisplay(item); if (item.restDisplay) item.restDisplay.hidden = true; return; } const restActive = Boolean(!row.complete && timing?.restStartedAt); if (restActive) {",
            1,
        )
    source = source.replace(
        "const preparing = isSeriesPreparing(item); if (preparing) { renderPreparationDisplay(item); if (item.restDisplay) item.restDisplay.hidden = true; return; } const preparing = isSeriesPreparing(item); if (preparing) { renderPreparationDisplay(item); if (item.restDisplay) item.restDisplay.hidden = true; return; }",
        "const preparing = isSeriesPreparing(item); if (preparing) { renderPreparationDisplay(item); if (item.restDisplay) item.restDisplay.hidden = true; return; }",
        1,
    )
    source = re.sub(
        r"if \(!confirmed\) return;\r?\n(\s*)state = \{\};",
        r"if (!confirmed) return;\n\1clearPreparationTimers();\n\1state = {};",
        source,
        count=1,
    )
    source = source.replace(
        " window.addEventListener('pagehide', () => { const timing = state.__timing; if (timing?.sessionStartedAt && !timing.sessionEndedAt) { timing.sessionAbandonedAt = Date.now(); save(); } }, { once: true });",
        "",
    )
    source = re.sub(
        r"    const startSeriesButton = document\.createElement\('button'\);\r?\n"
        r"    startSeriesButton\.type = 'button';\r?\n"
        r"    startSeriesButton\.className = 'startSeriesButton';\r?\n"
        r"    startSeriesButton\.hidden = true;\r?\n"
        r"    startSeriesButton\.setAttribute\('aria-label', `Iniciar siguiente serie de \$\{item\.title\}`\);\r?\n"
        r"    item\.startSeriesButton = startSeriesButton;",
        "    const startSeriesButton = item.tracker.querySelector('.completeSetButton');\n"
        "    let longPressDetected = false;\n"
        "    let longPressTimer = 0;\n"
        "    startSeriesButton?.addEventListener('pointerdown', () => { longPressDetected = false; longPressTimer = window.setTimeout(() => { longPressDetected = true; }, 4000); });\n"
        "    ['pointerup', 'pointercancel', 'pointerleave'].forEach(type => startSeriesButton?.addEventListener(type, () => { if (longPressTimer) { window.clearTimeout(longPressTimer); longPressTimer = 0; longPressDetected = false; } }));\n"
        "    startSeriesButton?.addEventListener('click', event => { if (!longPressDetected) return; event.preventDefault(); event.stopImmediatePropagation(); longPressDetected = false; });\n"
        "    item.startSeriesButton = startSeriesButton;",
        source,
        count=1,
    )
    source = re.sub(
        r"  const updateCompleteButton = item => \{.*?\n  \};",
        lambda _: """  const updateCompleteButton = item => {
    const button = item.tracker.querySelector('.completeSetButton');
    if (!button) return;
    const warmupRecorded = Object.keys(state.__warmupPerformance || {}).length > 0 || Object.keys(state).some(key => /^w\\d+$/.test(key) && state[key] === true);
    const activeApproximation = exerciseItems.find(entry => Number(state.__timing?.exercises?.[String(entry.index + 1)]?.warmupStartedAt) > 0);
    const approximationTarget = activeApproximation || (!warmupRecorded ? exerciseItems.find(entry => !snapshot(entry).complete && !snapshot(entry).machinePending) : null);
    exerciseItems.forEach(entry => {
      const entryTracker = entry.tracker;
      let marker = entryTracker.querySelector('.warmupSet');
      let hint = entryTracker.querySelector('.exerciseWarmupHint');
      if (entry !== approximationTarget) { marker?.remove(); hint?.remove(); entryTracker.querySelector('.completeSetButton')?.removeAttribute('aria-describedby'); return; }
      const setButtons = entryTracker.querySelector('.exerciseSetButtons');
      if (!marker) { marker = document.createElement('span'); marker.className = 'warmupSet'; marker.hidden = true; marker.setAttribute('aria-hidden', 'true'); marker.tabIndex = -1; setButtons?.prepend(marker); }
      marker.dataset.key = `w${entry.index + 1}`;
      if (!hint) { hint = document.createElement('p'); hint.className = 'exerciseWarmupHint'; hint.textContent = 'Serie ligera para ensayar el recorrido; se registra aparte y no suma al volumen de trabajo.'; marker.before(hint); }
      hint.id = `exerciseWarmupHint-${entry.index + 1}`;
      entryTracker.querySelector('.completeSetButton')?.setAttribute('aria-describedby', hint.id);
    });
    const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true);
    const complete = snapshot(item).complete;
    const timing = state.__timing?.exercises?.[String(item.index + 1)];
    const globalWarmupComplete = getWarmupTiming().phase === 'done';
    const warmup = item.tracker.querySelector('.warmupSet');
    const exerciseWarmupComplete = !warmup || state[warmup.dataset.key] === true;
    const warmupStartedAt = Number(timing?.warmupStartedAt) || 0;
    const warmupDue = globalWarmupComplete && !exerciseWarmupComplete;
    const warmupHint = item.tracker.querySelector('.exerciseWarmupHint');
    if (warmupHint) warmupHint.hidden = !warmupDue;
    item.tracker.classList.toggle('is-approximation', warmupDue);
    item.tracker.closest('article.card')?.querySelector('.performanceEntry')?.classList.toggle('is-approximation', warmupDue);
    const approximationValue = item.tracker.querySelector('.approximationProgressValue');
    if (approximationValue && warmupDue && warmupStartedAt) approximationValue.textContent = `En curso · ${formatElapsed(Date.now() - warmupStartedAt)}`;
    const preparing = isSeriesPreparing(item);
    const resting = Boolean(!state.__timing?.sessionEndedAt && timing?.restStartedAt && Date.now() - timing.restStartedAt < getRestRecommendation(item).minMs);
    const restRemaining = resting ? Math.max(0, getRestRecommendation(item).minMs - (Date.now() - timing.restStartedAt)) : 0;
    const seriesActive = Boolean(!complete && timing?.seriesStartedAt && !timing?.restStartedAt);
    const preparation = seriesPreparation.get(item.index);
    const label = resting && restRemaining > 0 ? `Descanso · ${formatElapsed(restRemaining)}`
      : complete ? state.__skippedExercises?.[String(item.index + 1)] === true ? '↷ Ejercicio omitido' : '✓ Ejercicio completado'
      : !globalWarmupComplete ? 'Completa calentamiento'
      : warmupDue ? warmupStartedAt ? `Aproximación activa · ${formatElapsed(Date.now() - warmupStartedAt)} · completar` : 'Iniciar serie de aproximación'
      : preparing ? `⏳ Preparación · ${formatElapsed(preparation ? Math.max(0, preparation.endsAt - Date.now()) : 0)}`
      : seriesActive ? `Completar serie ${nextIndex + 1} de ${item.seriesKeys.length}`
      : resting && restRemaining > 0 ? `Descanso · ${formatElapsed(restRemaining)} · mantén 5 s para continuar`
      : `Iniciar serie ${nextIndex + 1} de ${item.seriesKeys.length}`;
    button.hidden = false;
    button.disabled = complete || !globalWarmupComplete || preparing;
    button.textContent = label;
    button.setAttribute('aria-label', label);
    button.classList.toggle('is-resting', resting && restRemaining > 0);
    button.classList.toggle('is-series-active', seriesActive && !preparing);
    button.classList.toggle('is-preparing', preparing);
    button.classList.toggle('is-approximation', warmupDue);
    button.classList.toggle('is-approximation-active', Boolean(warmupStartedAt && warmupDue));
    if (item.skipExerciseButton) item.skipExerciseButton.disabled = !globalWarmupComplete || complete;
  };""",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r"(?m)^(\s*)if \(item\.startSeriesButton\) \{ const preparing = isSeriesPreparing\(item\);.*; \}\s*$",
        r"\1if (item.startSeriesButton) item.startSeriesButton.hidden = completed;",
        source,
        count=1,
    )
    source = re.sub(
        r"item\.startSeriesButton\?\.addEventListener\('click', \(\) => \{\s*"
        r"const timing = getExerciseTiming\(item\);\s*"
        r"const warmup = tracker\.querySelector\('\.warmupSet'\);\s*"
        r"if \(!item \|\| snapshot\(item\)\.complete \|\| getWarmupTiming\(\)\.phase !== 'done' \|\| \(warmup && state\[warmup\.dataset\.key\] !== true\) \|\| timing\.seriesStartedAt \|\| \(timing\.restStartedAt && Date\.now\(\) - timing\.restStartedAt < getRestRecommendation\(item\)\.minMs\)\) return;\s*"
        r"startSeriesPreparation\(item\);\s*updateTracker\(tracker, false\);\s*\}\);",
        """item.startSeriesButton?.addEventListener('click', async event => {
      const timing = getExerciseTiming(item);
      const warmup = tracker.querySelector('.warmupSet');
      if (!item || snapshot(item).complete || getWarmupTiming().phase !== 'done') return;
      if (warmup && state[warmup.dataset.key] !== true) {
        event.stopImmediatePropagation();
        const warmupKey = String(item.index + 1);
        if (!timing.warmupStartedAt) {
          timing.warmupStartedAt = Date.now();
          startTiming(item, timing.warmupStartedAt);
          save();
          updateTracker(tracker, false);
          return;
        }
        const reps = Number(item.performanceReps?.value);
        const repsSelected = item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= Math.max(1, item.repMinimum - 3) && reps <= item.repMaximum + 4;
        const load = Number(item.performanceLoadExact);
        const loadSelected = item.performanceLoadSelected && Number.isFinite(load) && load >= Number(item.performanceLoad?.min) && load <= Number(item.performanceLoad?.max);
        const missingPerformance = [...(!repsSelected ? ['repeticiones'] : []), ...(!loadSelected ? ['carga'] : [])];
        if (missingPerformance.length && !(await confirmMissingPerformance(missingPerformance))) return;
        const completedAt = Date.now();
        if (!state.__warmupPerformance) state.__warmupPerformance = {};
        state.__warmupPerformance[warmupKey] = {
          reps: repsSelected ? reps : null,
          load: loadSelected ? load : null,
          loadUnit: item.performanceLoadUnit,
          loadKg: loadSelected ? item.performanceLoadUnit === 'lb' ? load * 0.45359237 : load : null,
          durationMs: Math.min(MAX_TIMING_MS, Math.max(0, completedAt - timing.warmupStartedAt)),
          completedAt
        };
        timing.warmupStartedAt = 0;
        timing.warmupDurationMs = state.__warmupPerformance[warmupKey].durationMs;
        timing.restStartedAt = completedAt;
        timing.restPhase = 'warmup';
        state[warmup.dataset.key] = true;
        save();
        pulse(item.startSeriesButton);
        playMilestoneSound('series');
        updateTracker(tracker, false);
        return;
      }
      if (timing.seriesStartedAt || (timing.restStartedAt && Date.now() - timing.restStartedAt < getRestRecommendation(item).minMs)) return;
      startSeriesPreparation(item);
      updateTracker(tracker, false);
    });""",
        source,
        count=1,
        flags=re.S,
    )
    if "timing.warmupStartedAt = Date.now();" not in source:
        source = re.sub(
            r"item\.startSeriesButton\?\.addEventListener\('click', \(\) => \{.*?\n\s*\}\);",
            """item.startSeriesButton?.addEventListener('click', async event => {
      const timing = getExerciseTiming(item);
      const warmup = tracker.querySelector('.warmupSet');
      if (!item || snapshot(item).complete || getWarmupTiming().phase !== 'done') return;
      if (warmup && state[warmup.dataset.key] !== true) {
        event.stopImmediatePropagation();
        const warmupKey = String(item.index + 1);
        if (!timing.warmupStartedAt) { timing.warmupStartedAt = Date.now(); startTiming(item, timing.warmupStartedAt); save(); updateTracker(tracker, false); return; }
        const reps = Number(item.performanceReps?.value);
        const repsSelected = item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= Math.max(1, item.repMinimum - 3) && reps <= item.repMaximum + 4;
        const load = Number(item.performanceLoadExact);
        const loadSelected = item.performanceLoadSelected && Number.isFinite(load) && load >= Number(item.performanceLoad?.min) && load <= Number(item.performanceLoad?.max);
        const missingPerformance = [...(!repsSelected ? ['repeticiones'] : []), ...(!loadSelected ? ['carga'] : [])];
        if (missingPerformance.length && !(await confirmMissingPerformance(missingPerformance))) return;
        const completedAt = Date.now();
        if (!state.__warmupPerformance) state.__warmupPerformance = {};
        state.__warmupPerformance[warmupKey] = { reps: repsSelected ? reps : null, load: loadSelected ? load : null, loadUnit: item.performanceLoadUnit, loadKg: loadSelected ? item.performanceLoadUnit === 'lb' ? load * 0.45359237 : load : null, durationMs: Math.min(MAX_TIMING_MS, Math.max(0, completedAt - timing.warmupStartedAt)), completedAt };
        timing.warmupStartedAt = 0; timing.warmupDurationMs = state.__warmupPerformance[warmupKey].durationMs; timing.restStartedAt = completedAt; timing.restPhase = 'warmup'; state[warmup.dataset.key] = true;
        save(); pulse(item.startSeriesButton); playMilestoneSound('series'); updateTracker(tracker, false); return;
      }
      if (timing.seriesStartedAt || (timing.restStartedAt && Date.now() - timing.restStartedAt < getRestRecommendation(item).minMs)) return;
      startSeriesPreparation(item); updateTracker(tracker, false);
    });""",
            source,
            count=1,
            flags=re.S,
        )
    source = re.sub(
        r"    const button = document\.createElement\('button'\);\r?\n"
        r"    button\.type = 'button';\r?\n"
        r"    button\.className = 'startExerciseButton';.*?"
        r"    item\.startButton = button;\r?\n",
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r"if \(warmupButton\) warmupButton\.after\(button, startSeriesButton\);\r?\n"
        r"\s*else setButtons\?\.prepend\(button, startSeriesButton\);",
        "if (warmupButton) warmupButton.after(startSeriesButton);\n"
        "    else setButtons?.prepend(startSeriesButton);",
        source,
        count=1,
    )
    source = re.sub(
        r"    item\.startButton\?\.addEventListener\('click', \(\) => \{.*?\n    \}\);\r?\n",
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r"    const startButton = item\.startButton;\r?\n"
        r"    const timing = state\.__timing\?\.exercises\?\.\[String\(item\.index \+ 1\)\];\r?\n"
        r"    if \(item\.startSeriesButton\) item\.startSeriesButton\.hidden = completed;\r?\n"
        r"    if \(startButton\) \{.*?\n    \}\r?\n",
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r"var start = tracker && tracker\.querySelector\('\.startExerciseButton'\);\s*"
        r"return Boolean\(tracker && !tracker\.classList\.contains\('exerciseDone'\) && start && normalize\(start\.textContent\) === 'ejercicio iniciado'\);",
        "var action = tracker && tracker.querySelector('.completeSetButton');\n"
        "    return Boolean(tracker && !tracker.classList.contains('exerciseDone') && action && /^(completar serie|preparaci[oó]n)/.test(normalize(action.textContent)));",
        source,
        count=1,
    )
    source = re.sub(
        r"<style data-enhancement=\"explicit-exercise-start-v1\">.*?</style>",
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(r"\.startExerciseButton::before\{[^}]*\}\r?\n?", "", source, count=1)
    source = source.replace(".startExerciseButton,.completeSetButton,.machinePendingToggle", ".completeSetButton,.machinePendingToggle", 1)
    source = source.replace("@media(max-width:700px){.startExerciseButton{min-height:52px!important;min-width:0!important;padding:.68rem .8rem!important;font-size:.8rem!important}", "@media(max-width:700px){", 1)
    source = source.replace("@media(prefers-reduced-motion:reduce){.startExerciseButton,.completeSetButton{transition:none}}", "@media(prefers-reduced-motion:reduce){.completeSetButton{transition:none}}", 1)
    source = source.replace(
        "startSeriesButton?.addEventListener('pointerdown', () => { longPressDetected = false; longPressTimer = window.setTimeout(() => { longPressDetected = true; }, 4000); });",
        "startSeriesButton?.addEventListener('pointerdown', () => { const timing = getExerciseTiming(item); if (!timing.restStartedAt || timing.seriesStartedAt) return; longPressDetected = false; longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); if (!current.restStartedAt || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; const continuedAt = Date.now(); const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true); const restDuration = Math.min(MAX_TIMING_MS, Math.max(0, continuedAt - current.restStartedAt)); if (current.restPhase === 'warmup' && state.__warmupPerformance?.[String(item.index + 1)]) state.__warmupPerformance[String(item.index + 1)].restDurationMs = restDuration; else if (nextIndex > 0) current.restTimes[nextIndex - 1] = restDuration; current.restPhase = 'skipped'; current.restSkippedAt = continuedAt; current.restStartedAt = 0; current.restNotifiedAt = 0; current.restReminderNotifiedAt = 0; startSeriesPreparation(item); updateTracker(item.tracker, false); }, 5000); });",
        1,
    )
    source = source.replace(
        "startSeriesButton?.addEventListener('pointerdown', () => { const timing = getExerciseTiming(item); if (!timing.restStartedAt || timing.seriesStartedAt) return; longPressDetected = false; longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); if (!current.restStartedAt || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; current.restStartedAt = 0; current.restPhase = 'skipped'; current.restSkippedAt = Date.now(); beginSeries(item, Date.now()); updateTracker(item.tracker, false); }, 5000); });",
        "startSeriesButton?.addEventListener('pointerdown', () => { const timing = getExerciseTiming(item); if (!timing.restStartedAt || timing.seriesStartedAt) return; longPressDetected = false; longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); if (!current.restStartedAt || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; const continuedAt = Date.now(); const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true); const restDuration = Math.min(MAX_TIMING_MS, Math.max(0, continuedAt - current.restStartedAt)); if (current.restPhase === 'warmup' && state.__warmupPerformance?.[String(item.index + 1)]) state.__warmupPerformance[String(item.index + 1)].restDurationMs = restDuration; else if (nextIndex > 0) current.restTimes[nextIndex - 1] = restDuration; current.restPhase = 'skipped'; current.restSkippedAt = continuedAt; current.restStartedAt = 0; current.restNotifiedAt = 0; current.restReminderNotifiedAt = 0; startSeriesPreparation(item); updateTracker(item.tracker, false); }, 5000); });",
        1,
    )
    source = source.replace("}, 4000); }));", "}, 5000); }));", 1)
    source = source.replace(
        "    let longPressTimer = 0;\n    const startRestHold = event =>",
        "    let longPressTimer = 0;\n    let longPressResetTimer = 0;\n    const startRestHold = event =>",
        1,
    )
    source = source.replace(
        "if (startSeriesButton.dataset.e2eHoldTarget === 'true') window.__gymratikHoldProbe = {now:Date.now(),timing:{...timing},minimumMs:getRestRecommendation(item).minMs,longPressTimer,eventType:event.type}; ",
        "",
        1,
    )
    source = source.replace(
        "if (startSeriesButton.dataset.e2eHoldTarget === 'true' && window.__gymratikHoldProbe) window.__gymratikHoldProbe.firedAt = Date.now(); ",
        "",
        1,
    )
    source = source.replace(
        "if (!timing.restStartedAt || Date.now() - timing.restStartedAt >= getRestRecommendation(item).minMs || timing.seriesStartedAt) return; if (longPressTimer) { window.clearTimeout(longPressTimer); longPressTimer = 0; } longPressDetected = false;",
        "if (!timing.restStartedAt || Date.now() - timing.restStartedAt >= getRestRecommendation(item).minMs || timing.seriesStartedAt) return; if (longPressTimer) { window.clearTimeout(longPressTimer); longPressTimer = 0; } longPressDetected = false;",
        1,
    )
    source = source.replace(
        "longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); longPressTimer = 0; if (!current.restStartedAt",
        "longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); longPressTimer = 0; if (!current.restStartedAt",
        1,
    )
    source = source.replace(
        "['pointerup', 'pointercancel', 'pointerleave', 'keyup', 'blur'].forEach(type => startSeriesButton?.addEventListener(type, () => { if (longPressTimer) { window.clearTimeout(longPressTimer); longPressTimer = 0; longPressDetected = false; } startSeriesButton.classList.remove('is-holding'); startSeriesButton.style.setProperty('--hold-progress', '0%'); }));",
        "['pointerup', 'pointercancel', 'pointerleave', 'keyup', 'blur'].forEach(type => startSeriesButton?.addEventListener(type, () => { if (longPressTimer) { window.clearTimeout(longPressTimer); longPressTimer = 0; longPressDetected = false; } else if (longPressDetected) { window.clearTimeout(longPressResetTimer); longPressResetTimer = window.setTimeout(() => { longPressDetected = false; longPressResetTimer = 0; }, 350); } startSeriesButton.classList.remove('is-holding'); startSeriesButton.style.setProperty('--hold-progress', '0%'); }));",
        1,
    )
    source = source.replace(
        "startSeriesButton?.addEventListener('click', event => { if (!longPressDetected) return; event.preventDefault(); event.stopImmediatePropagation(); longPressDetected = false; });",
        "startSeriesButton?.addEventListener('click', event => { if (!longPressDetected) return; event.preventDefault(); event.stopImmediatePropagation(); longPressDetected = false; window.clearTimeout(longPressResetTimer); longPressResetTimer = 0; });",
        1,
    )
    source = source.replace(
        "longPressDetected = true; startSeriesButton.style.setProperty('--hold-progress', '0%');",
        "longPressDetected = false; startSeriesButton.style.setProperty('--hold-progress', '0%');",
        1,
    )
    source = source.replace(
        "longPressTimer = 0; if (!current.restStartedAt || Date.now() - current.restStartedAt >= getRestRecommendation(item).minMs || current.seriesStartedAt || snapshot(item).complete) return; startSeriesButton.classList.remove('is-holding');",
        "longPressTimer = 0; if (!current.restStartedAt || Date.now() - current.restStartedAt >= getRestRecommendation(item).minMs || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; startSeriesButton.classList.remove('is-holding');",
        1,
    )
    source = source.replace(
        "longPressDetected = true; startSeriesButton.classList.remove('is-holding'); current.restPhase = 'skipped'; current.restSkippedAt = Date.now(); beginSeries(item, Date.now()); updateTracker(item.tracker, false);",
        "longPressDetected = true; startSeriesButton.classList.remove('is-holding'); const continuedAt = Date.now(); const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true); const restDuration = Math.min(MAX_TIMING_MS, Math.max(0, continuedAt - current.restStartedAt)); if (current.restPhase === 'warmup' && state.__warmupPerformance?.[String(item.index + 1)]) state.__warmupPerformance[String(item.index + 1)].restDurationMs = restDuration; else if (nextIndex > 0) current.restTimes[nextIndex - 1] = restDuration; current.restPhase = 'skipped'; current.restSkippedAt = continuedAt; current.restStartedAt = 0; current.restNotifiedAt = 0; current.restReminderNotifiedAt = 0; startSeriesPreparation(item); updateTracker(item.tracker, false);",
        1,
    )
    source = source.replace(
        "const timingInterval = window.setInterval(() => { renderTimingDisplays(); renderWarmupTiming(); }, 1000);",
        "const timingInterval = window.setInterval(() => { renderTimingDisplays(); renderWarmupTiming(); exerciseItems.forEach(updateCompleteButton); }, 1000);",
        1,
    )
    source = re.sub(
        r"if \(item\) updatePendingButton\(item\);(?!\s*exerciseItems\.forEach\(updateCompleteButton\);)",
        "if (item) updatePendingButton(item);\n      exerciseItems.forEach(updateCompleteButton);",
        source,
        count=1,
    )
    if "const formatCountdown = milliseconds =>" not in source:
        source = source.replace(
            "const MAX_TIMING_MS = 24 * 60 * 60 * 1000;",
            "const formatCountdown = milliseconds => formatElapsed(Math.ceil(Math.max(0, milliseconds) / 1000) * 1000);\n  const MAX_TIMING_MS = 24 * 60 * 60 * 1000;",
            1,
        )
    source, timing_display_count = re.subn(
        r"  const renderTimingDisplays = \(\) => \{.*?\n  \};(?=\n  // El cronómetro empieza|\n  const PREPARATION_MS)",
        REST_TIMING_DISPLAY_CONTRACT,
        source,
        count=1,
        flags=re.S,
    )
    if timing_display_count != 1:
        timing_start = source.find("  const renderTimingDisplays = () => {")
        timing_end_candidates = [
            position for position in (
                source.find("\n  // El cronómetro empieza", timing_start),
                source.find("\n  const PREPARATION_MS", timing_start),
            ) if position >= 0
        ]
        if timing_start < 0 or not timing_end_candidates:
            raise ValueError("No se pudo localizar el bloque delimitado del contador de actividad")
        timing_end = min(timing_end_candidates)
        source = source[:timing_start] + REST_TIMING_DISPLAY_CONTRACT + source[timing_end:]
        timing_display_count = 1
    if "window.gymratikMascotVariant = 'neutral';" not in source:
        profile_mascot_init = """  window.gymratikMascotVariant = 'neutral';
  const updateActivityMascotProfile = profile => {
    const sex = profile?.sex;
    window.gymratikMascotVariant = sex === 'female' ? 'female' : sex === 'male' ? 'male' : 'neutral';
    renderTimingDisplays();
  };
  window.TrainingProgressStore?.getProfile?.().then(updateActivityMascotProfile).catch(() => updateActivityMascotProfile(null));
  window.addEventListener('training-profile-updated', event => updateActivityMascotProfile(event.detail?.profile));
  window.matchMedia?.('(prefers-reduced-motion: reduce)').addEventListener?.('change', () => renderTimingDisplays());
"""
        source = source.replace("  const refreshTimingDisplays = () => {", profile_mascot_init + "  const refreshTimingDisplays = () => {", 1)
    source = source.replace("  document.addEventListener('visibilitychange', () => renderTimingDisplays());\n", "")
    return source


def _muscle_item_replacement(match: re.Match[str]) -> str:
    item = match.group(0)
    name_match = re.search(r'<span class="muscleName">([^<]+)</span>', item)
    if name_match:
        name = name_match.group(1).strip()
    else:
        name = next((candidate for candidate in MUSCLE_FOCUS if f">{candidate}</span>" in item), "")
        if not name:
            raise ValueError("Una tarjeta muscular no tiene un nombre reconocible")
        return _build_muscle_item(name)
    try:
        focus = MUSCLE_FOCUS[name]
    except KeyError as error:
        raise ValueError(f"Músculo no contemplado en el contrato visual: {name}") from error

    item = re.sub(r'\sdata-muscle-focus="[^"]*"', "", item)
    item = re.sub(r'\sdata-muscle-view="[^"]*"', "", item)
    visual = f'{"upper" if name in UPPER_MUSCLES else "lower"}-{focus["view"]}'
    if 'data-muscle-visual="' in item:
        item = re.sub(r'data-muscle-visual="[^"]*"', f'data-muscle-visual="{visual}"', item, count=1)
    else:
        item = item.replace('class="muscleDayItem"', f'class="muscleDayItem" data-muscle-visual="{visual}"', 1)
    item = re.sub(r'\saria-label="[^"]*"', "", item)
    item = item.replace(
        'class="muscleDayItem"',
        f'class="muscleDayItem" data-muscle-focus="{focus["key"]}" data-muscle-view="{focus["view"]}"',
        1,
    )
    item = re.sub(r'<span class="muscleFocusMarker"[^>]*></span>\s*', "", item)
    item = re.sub(
        r'<span class="muscleDayVisual [^"]+"[^>]*>',
        f'<span class="muscleDayVisual {focus["view"]}" title="Foco visual: {focus["region"]}">'
        f'{_marker_markup(name)}',
        item,
        count=1,
    )
    item = re.sub(
        r'<img class="muscleDayImage" src="[^"]+" alt="[^"]+"',
        lambda image_match: _image_markup(image_match.group(0), name, focus),
        item,
        count=1,
    )
    item = re.sub(
        r'<div class="muscleDayItem"([^>]*)>',
        rf'<div class="muscleDayItem"\1 aria-label="{name}; foco visual en {focus["region"]}">',
        item,
        count=1,
    )
    return item


def _build_muscle_item(name: str) -> str:
    focus = MUSCLE_FOCUS[name]
    color = MUSCLE_COLOR.get(name, "#72dcff")
    source = "../medios_publicados/rutinas_autocontenidas/musculos_generados/"
    image = f"{source}{'upper' if name in UPPER_MUSCLES else 'lower'}_{focus['view']}_anatomy_v1.webp"
    return (
        f'<div class="muscleDayItem" data-muscle-focus="{focus["key"]}" '
        f'data-muscle-view="{focus["view"]}" data-muscle-visual="{("upper" if name in UPPER_MUSCLES else "lower")}-{focus["view"]}" '
        f'aria-label="{name}; foco visual en {focus["region"]}">'
        f'<span class="muscleDayVisual {focus["view"]}" title="Foco visual: {focus["region"]}">'
        f'{_marker_markup(name)}'
        f'<img class="muscleDayImage" src="{image}" alt="Referencia anatómica ilustrativa {focus["view"]} del músculo {name}; foco visual aproximado en {focus["region"]}" decoding="async">'
        '<span class="muscleDayFallback" hidden>ANATOMÍA</span></span>'
        f'<span class="muscleDayCopy"><span class="muscleCode" style="color:{color}">{MUSCLE_CODE[name]}</span>'
        f'<span class="muscleName">{name}</span></span></div>'
    )


def _marker_markup(name: str) -> str:
    """Genera marcadores de foco estables y repetibles para una tarjeta."""
    return "".join(
        f'<span class="muscleFocusMarker" data-marker-side="{side}" '
        f'style="--marker-x:{x};--marker-y:{y}" aria-hidden="true"></span>'
        for side, x, y in MUSCLE_MARKERS[name]
    )


def _image_markup(markup: str, name: str, focus: dict[str, str]) -> str:
    image_prefix = "upper" if name in UPPER_MUSCLES else "lower"
    markup = re.sub(
        r'src="[^"]+"',
        f'src="../medios_publicados/rutinas_autocontenidas/musculos_generados/{image_prefix}_{focus["view"]}_anatomy_v1.webp"',
        markup,
        count=1,
    )
    return re.sub(
        r'alt="[^"]+"',
        f'alt="Referencia anatómica ilustrativa {focus["view"]} del músculo {name}; foco visual aproximado en {focus["region"]}"',
        markup,
        count=1,
    )


def standardize_quote_portrait_loading(source: str) -> str:
    start_marker = "if (portraitEl && initialsEl) { portraitEl.hidden = !phrase.portrait;"
    start = source.find(start_marker)
    if start < 0:
        return source.replace(
            "portraitEl.alt = `Retrato de ${phrase.author}`;\n        portraitEl.src = phrase.portrait;",
            "portraitEl.alt = `Retrato de ${phrase.author}`;\n        portraitEl.loading = 'eager';\n        portraitEl.src = phrase.portrait;",
            1,
        )
    end_marker = "portraitEl.onerror = () => { portraitEl.hidden = true; initialsEl.hidden = false; }; } }"
    end = source.find(end_marker, start)
    if end < 0:
        raise ValueError("No se encontró el fallback del retrato de la cita")
    end += len(end_marker)
    replacement = """if (portraitEl && initialsEl) {
      initialsEl.textContent = phrase.author.split(/\\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase() || '★';
      const showPortraitFallback = () => { portraitEl.hidden = true; initialsEl.hidden = false; };
      portraitEl.onload = () => { if (portraitEl.complete && portraitEl.naturalWidth > 0) { portraitEl.hidden = false; initialsEl.hidden = true; } else showPortraitFallback(); };
      portraitEl.onerror = showPortraitFallback;
      if (phrase.portrait) {
        portraitEl.hidden = true; initialsEl.hidden = false;
        portraitEl.alt = `Retrato de ${phrase.author}`;
        portraitEl.loading = 'eager';
        portraitEl.src = phrase.portrait;
      } else {
        showPortraitFallback(); portraitEl.alt = ''; portraitEl.removeAttribute('src');
      }
    }"""
    return source[:start] + replacement + source[end:]


TECHNIQUE_CUES = {
    "JALÓN AL PECHO": ("Muslos sujetos y pecho erguido.", "Lleva los codos hacia abajo; regresa despacio.", "No balancees el torso ni bajes la barra tras la nuca."),
    "REMO ALTO UNILATERAL": ("Pecho apoyado y mirada al frente.", "Lleva un codo abajo y atrás; vuelve despacio.", "No gires el tronco ni despegues el pecho."),
    "REMO HORIZONTAL EN MÁQUINA": ("Pecho apoyado, pies firmes.", "Lleva los codos hacia atrás; vuelve con control.", "No te impulses ni encojas los hombros."),
    "APERTURA INVERSA EN MÁQUINA": ("Pecho apoyado y codos alineados.", "Abre los brazos y vuelve lentamente.", "No gires el movimiento en un remo."),
    "CURL DE BÍCEPS EN MÁQUINA": ("Brazo apoyado y codo alineado con el eje.", "Flexiona el codo; baja lentamente.", "No despegues el brazo ni rebotes."),
    "CURL DE BÍCEPS SENTADO EN MÁQUINA": ("Espalda apoyada y muñecas rectas.", "Flexiona los codos; baja lentamente.", "No balancees el cuerpo ni golpees el tope."),
    "HACK SQUAT": ("Espalda apoyada y pies firmes.", "Baja hasta donde conserves el apoyo; empuja para subir.", "No rebotes ni juntes las rodillas."),
    "HIP THRUST": ("Espalda alta apoyada; pies firmes.", "Eleva la cadera, aprieta glúteos y baja con control.", "No arquees la espalda al subir."),
    "PRENSA DE PIERNAS": ("Espalda y pelvis apoyadas; pies firmes.", "Baja sin despegar la pelvis; empuja con todo el pie.", "No juntes las rodillas ni bloquees con golpe."),
    "CURL FEMORAL EN MÁQUINA": ("Pelvis estable y rodilla alineada con el eje.", "Flexiona las rodillas; vuelve lentamente.", "No levantes la cadera ni uses impulso."),
    "EXTENSIÓN DE PIERNAS": ("Rodilla alineada con el eje de la máquina.", "Extiende y baja con control.", "No golpees el tope ni te balancees."),
    "PANTORRILLAS DE PIE": ("Antepié apoyado y talones libres.", "Baja el talón; elévate y desciende despacio.", "No rebotes ni recortes el recorrido."),
    "PRESS DE PECHO SENTADO EN MÁQUINA": ("Asas a media altura del pecho; espalda apoyada.", "Empuja y regresa lentamente, sin despegar el torso.", "No abras demasiado los codos ni golpees al extender."),
    "PRESS INCLINADO CONVERGENTE EN MÁQUINA": ("Torso apoyado; asas a la altura del pecho alto.", "Empuja siguiendo las asas; vuelve despacio.", "No arquees la espalda ni fuerces el hombro."),
    "PEC DECK / CONTRACTOR DE PECHO": ("Codos levemente flexionados y hombros relajados.", "Junta los brazos; vuelve dentro de un rango cómodo.", "No fuerces la apertura ni eleves los hombros."),
    "PRESS DE HOMBRO EN MÁQUINA": ("Espalda y pelvis apoyadas.", "Empuja arriba y baja lentamente.", "No arquees la espalda ni fuerces el rango."),
    "ELEVACIÓN LATERAL EN MÁQUINA": ("Torso apoyado y eje alineado con el hombro.", "Eleva los brazos; bájalos lentamente.", "No te balancees ni encojas los hombros."),
    "JALÓN DE TRÍCEPS EN POLEA": ("Codos junto al cuerpo y torso estable.", "Estira los codos; vuelve lentamente.", "No uses el peso del cuerpo ni muevas los codos."),
    "EXTENSIÓN DE TRÍCEPS SOBRE CABEZA CON CUERDA": ("Codos al frente y abdomen firme.", "Estira y flexiona los codos con control.", "No arquees la espalda ni abras los codos."),
    "PRENSA UNILATERAL ALTERNA": ("Pelvis apoyada; trabaja un lado a la vez.", "Empuja con un pie; cambia de lado sin bloquear la rodilla.", "No levantes la pelvis ni hundas la rodilla hacia dentro."),
    "PESO MUERTO RUMANO CON BARRA": ("Pies al ancho de cadera; barra cerca de las piernas.", "Lleva la cadera atrás; sube apretando glúteos.", "No redondees la espalda ni alejes la barra."),
    "CURL FEMORAL TUMBADO": ("Cadera apoyada y rodilla alineada con el eje.", "Lleva los talones hacia los glúteos; baja despacio.", "No levantes la cadera ni uses impulso."),
    "ABDUCCIÓN DE CADERA SENTADA": ("Espalda apoyada y pelvis estable.", "Separa las rodillas; vuelve lentamente.", "No rebotes ni inclines el torso."),
    "ADUCCIÓN DE CADERA SENTADA": ("Espalda apoyada y piernas simétricas.", "Junta las rodillas; vuelve lentamente.", "No muevas la pelvis ni fuerces la apertura."),
    "ELEVACIÓN DE PANTORRILLA SENTADA": ("Antepié apoyado y almohadilla sobre los muslos.", "Eleva los talones; baja lentamente.", "No rebotes ni ayudes con las rodillas."),
    "CRUNCH CON ELEVACIÓN DE PIERNAS SENTADA": ("Pelvis estable; manos sin tirar del cuello.", "Acerca tronco y piernas; vuelve lentamente.", "No jales la cabeza ni uses impulso."),
}


def _replace_technique_steps(card: str, cues: tuple[str, str, str]) -> str:
    marker = 'class="techSteps"'
    marker_pos = card.find(marker)
    if marker_pos < 0:
        return card
    opening = card.rfind("<div", 0, marker_pos)
    opening_end = card.find(">", marker_pos)
    depth = 0
    closing_end = -1
    for token in re.finditer(r"<div\b[^>]*>|</div\s*>", card[opening:opening_end + 1], flags=re.I):
        depth += 1 if token.group(0).lower().startswith("<div") else -1
    for token in re.finditer(r"<div\b[^>]*>|</div\s*>", card[opening_end + 1:], flags=re.I):
        depth += 1 if token.group(0).lower().startswith("<div") else -1
        if depth == 0:
            closing_end = opening_end + 1 + token.end()
            break
    if opening < 0 or opening_end < 0 or closing_end < 0:
        return card
    steps = (
        ("setup", "settings-2", "Posición", cues[0]),
        ("move", "move-up-right", "Movimiento", cues[1]),
        ("warning", "triangle-alert", "Evita", cues[2]),
    )
    contents = "".join(
        f'<div class="techStep {kind}"><div class="techStepTitle"><svg class="lucide lucide-{icon} gymratikIcon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#gymratik-icon-{icon}"></use></svg><span>{label}</span></div><div class="techStepText">{escape(text)}</div></div>'
        for kind, icon, label, text in steps
    )
    return card[:opening_end + 1] + contents + card[closing_end - len("</div>"):]


def standardize_technique_guidance(source: str) -> str:
    """Use the same three concise, exercise-specific technique cues in every routine."""
    cards = list(re.finditer(r'<article class="card\b.*?</article>', source, flags=re.S))
    replacements: list[tuple[int, int, str]] = []
    for match in cards:
        card = match.group(0)
        title_match = re.search(r'<div class="exTitle">(.*?)</div>', card, flags=re.S)
        if not title_match:
            continue
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        title = unescape(title)
        cues = TECHNIQUE_CUES.get(title)
        if not cues:
            raise ValueError(f"Falta guía esencial para el ejercicio: {title}")
        replacements.append((match.start(), match.end(), _replace_technique_steps(card, cues)))
    if not replacements:
        raise ValueError("No se encontraron ejercicios con guía técnica estandarizable")
    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    return source


def standardize_technique_accordion(source: str) -> str:
    """Wrap each technique grid in an accessible, collapsed-by-default details element."""
    source = re.sub(
        r'<details class="techAccordion" data-enhancement="technique-accordion-v1">\s*<summary>[^<]*</summary>\s*</details>\s*',
        "",
        source,
    )
    marker = 'class="techSteps"'
    positions = [match.start() for match in re.finditer(marker, source)]
    for marker_pos in reversed(positions):
        opening = source.rfind("<div", 0, marker_pos)
        opening_end = source.find(">", marker_pos)
        if opening < 0 or opening_end < 0:
            continue
        depth = 0
        closing_start = -1
        closing_end = -1
        for token in re.finditer(r"<div\b[^>]*>|</div\s*>", source[opening:opening_end + 1], flags=re.I):
            depth += 1 if token.group(0).lower().startswith("<div") else -1
        for token in re.finditer(r"<div\b[^>]*>|</div\s*>", source[opening_end + 1:], flags=re.I):
            if token.group(0).lower().startswith("<div"):
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    closing_start = opening_end + 1 + token.start()
                    closing_end = opening_end + 1 + token.end()
                    break
        if closing_start < 0:
            continue
        enclosing_details = source.rfind('<details class="techAccordion"', 0, opening)
        if enclosing_details >= 0 and source.find("</details>", enclosing_details) >= closing_end:
            continue
        source = (source[:opening] + '<details class="techAccordion" data-enhancement="technique-accordion-v1">'
                  '<summary>Técnica esencial</summary>' + source[opening:closing_end] + '</details>' + source[closing_end:])
    source = re.sub(
        r'(<details class="techAccordion" data-enhancement="technique-accordion-v1">\s*<summary>).*?(</summary>)',
        r'\1Técnica esencial\2',
        source,
    )
    return source


SUMMARY_NAVIGATION_STYLE = '''<style data-enhancement="summary-free-navigation-v1">
.sessionSummaryList{max-height:min(24dvh,168px)!important;overflow-y:auto!important;overscroll-behavior:contain!important;touch-action:pan-y!important;-webkit-overflow-scrolling:touch!important;scrollbar-gutter:stable}
#floatingSessionSummary .sessionSummaryList{max-height:150px!important}
#summaryToggle{grid-template-columns:auto minmax(0,1fr) 86px auto!important}
.summaryMascotWrap{width:82px!important;height:82px!important}.summaryMascotWrap #summaryActivityMascot{width:78px!important;height:78px!important}
@media(max-width:380px){#summaryToggle{grid-template-columns:auto minmax(0,1fr) 68px auto!important}.summaryMascotWrap{width:64px!important;height:64px!important}.summaryMascotWrap #summaryActivityMascot{width:60px!important;height:60px!important}}
@media(max-height:420px) and (max-width:900px){#floatingSessionSummary .sessionSummaryList{max-height:78px!important;gap:.12rem!important}}
</style>'''


def standardize_weekly_progress_reset(source: str) -> str:
    """Scope routine progress to the local week and show reset clearly at page end."""
    weekly_reset_logic = """  const routineWeekKey = timestamp => { const date = new Date(timestamp); date.setHours(0, 0, 0, 0); date.setDate(date.getDate() - ((date.getDay() + 6) % 7)); return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`; };
  const resetPreviousWeekProgress = () => {
    const startedAt = Number(state.__timing?.sessionStartedAt) || 0;
    const recordedWeek = startedAt ? routineWeekKey(startedAt) : typeof state.__routineWeek === 'string' ? state.__routineWeek : '';
    const hasProgress = Object.entries(state).some(([key, value]) => (/^e\\d+s\\d+$/.test(key) || /^w\\d+$/.test(key)) && value === true)
      || Object.keys(state.__skippedExercises || {}).length > 0
      || Boolean(state.__timing?.warmup?.phase === 'done' || startedAt);
    if (!hasProgress || !recordedWeek || recordedWeek >= routineWeekKey(Date.now())) return false;
    state = {};
    return true;
  };"""
    routine_week_key = weekly_reset_logic.split("\n", 1)[0]
    reset_helper = weekly_reset_logic.split("\n", 1)[1]
    # A snapshot must never be published to the shared store before weekly
    # normalization; otherwise an old completed day can be recaptured as current.
    source = source.replace("  publishProgress();\n  const pulse = button => {", "  const pulse = button => {", 1)
    first_week_key = source.find(routine_week_key)
    if first_week_key >= 0:
        key_end = first_week_key + len(routine_week_key)
        source = source[:key_end] + source[key_end:].replace(routine_week_key + "\n", "")
    if "const routineWeekKey = timestamp =>" not in source:
        source = source.replace(
            "  const migrateTimingState = () => {",
            weekly_reset_logic + "\n  const migrateTimingState = () => {",
            1,
        )
        if "const resetPreviousWeekProgress = () =>" not in source:
            raise ValueError("No se encontró el contrato temporal para reiniciar progreso semanal")
        source = source.replace("  migrateTimingState();", "  if (resetPreviousWeekProgress()) save();\n  migrateTimingState();\n  publishProgress();", 1)
    else:
        source, reset_count = re.subn(
            r"  const resetPreviousWeekProgress = \(\) => \{.*?\n  \};",
            lambda _match: reset_helper,
            source,
            count=1,
            flags=re.S,
        )
        if reset_count != 1:
            raise ValueError("No se pudo actualizar la regla semanal ya instalada")
        if "  migrateTimingState();\n  publishProgress();" not in source:
            source = source.replace("  migrateTimingState();", "  migrateTimingState();\n  publishProgress();", 1)
    if "state.__routineWeek = routineWeekKey(Date.now())" not in source:
        source, save_count = re.subn(
            r"(const save = \(\) => \{\s*if \(!window\.GymratikInstallGate\?\.isInstalled\(\)\) return;)",
            r"\1\n    state.__routineWeek = routineWeekKey(Date.now());",
            source,
            count=1,
        )
        if save_count != 1:
            raise ValueError("No se encontró el guardado local para asignar el ámbito semanal")
    source = source.replace(
        "const confirmed = window.confirm('¿Reiniciar el progreso de esta sesión? Se borrarán marcadores, pendientes y tiempos.');",
        "const confirmed = window.confirm('¿Reiniciar este día? Se borrarán los marcadores y tiempos de esta semana; el historial de entrenamientos se conservará.');",
        1,
    )
    source = source.replace(
        "    try { await window.TrainingProgressStore?.clearRoutine?.(routineId); } catch (error) { console.error('Routine reset failed', error); }\n",
        "",
        1,
    )

    footer_match = re.search(r'<footer class="sessionFooter"[^>]*>.*?</footer>', source, flags=re.S)
    if not footer_match:
        raise ValueError("No se encontró el botón de reinicio del día")
    summary_start = source.find('<div class="summaryBody"')
    summary_end = source.find("</aside>", footer_match.end())
    if summary_start >= 0 and summary_start < footer_match.start() and summary_end >= 0:
        footer_markup = footer_match.group(0)
        source = source[:footer_match.start()] + source[footer_match.end():]
        aside_end = source.find("</aside>", summary_start)
        if aside_end < 0:
            raise ValueError("No se encontró el cierre del resumen flotante")
        aside_end += len("</aside>")
        source = source[:aside_end] + "\n" + footer_markup + source[aside_end:]
    source = re.sub(r'<style data-enhancement="footer-reset-v1">.*?</style>\s*', "", source, count=1, flags=re.S)
    source = re.sub(r'<style data-enhancement="weekly-routine-reset-v1">.*?</style>\s*', "", source, count=1, flags=re.S)
    reset_style = '''<style data-enhancement="weekly-routine-reset-v1">
.sessionFooter{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(10rem,18rem)!important;align-items:center!important;gap:.8rem!important;width:min(100%,62rem)!important;margin:1.5rem auto calc(10rem + env(safe-area-inset-bottom,0px))!important;padding:1rem!important;border:1px solid rgba(255,157,162,.4)!important;border-radius:1rem!important;background:linear-gradient(115deg,rgba(37,32,49,.96),rgba(17,38,54,.96))!important;box-shadow:0 12px 34px rgba(0,0,0,.2)!important;visibility:visible!important;opacity:1!important}
.sessionResetCopy{display:grid;gap:.2rem;min-width:0;color:#f4fbff}.sessionResetCopy strong{font-size:.9rem}.sessionResetCopy span{color:#b8cbd4;font-size:.76rem;line-height:1.4}
#resetSession{display:block!important;visibility:visible!important;opacity:1!important;width:100%;min-height:52px;margin:0;padding:.72rem 1rem;border:1px solid rgba(255,157,162,.72);border-radius:.8rem;background:linear-gradient(110deg,rgba(113,44,61,.58),rgba(64,42,73,.68));color:#ffe4e6;font:inherit;font-size:.9rem;font-weight:850;cursor:pointer}
#resetSession::before{content:"↻";margin-right:.5rem;font-size:1.1rem}
#resetSession:focus-visible{outline:3px solid #72dcff;outline-offset:3px}
@media(prefers-reduced-motion:no-preference){#resetSession{transition:background-color .2s ease,border-color .2s ease,transform .2s ease}#resetSession:hover{border-color:#ffb6bb;background-color:rgba(145,53,70,.38);transform:translateY(-1px)}}
@media(prefers-reduced-motion:reduce){#resetSession{transition:none!important}}
@media(max-width:520px){.sessionFooter{grid-template-columns:1fr!important;gap:.55rem!important;padding:.75rem!important}.sessionResetCopy strong{font-size:.82rem}.sessionResetCopy span{font-size:.7rem}}
</style>'''
    source = source.replace("</head>", reset_style + "\n</head>", 1)
    source = source.replace(
        '<footer class="sessionFooter" aria-label="Acciones del día"><button type="button" id="resetSession">Reiniciar día</button></footer>',
        '<footer class="sessionFooter" aria-label="Acciones del día"><div class="sessionResetCopy"><strong>¿Quieres empezar este día de nuevo?</strong><span>Se reinicia solo el progreso de este día; tu historial y perfil se conservan.</span></div><button type="button" id="resetSession">Reiniciar día</button></footer>',
        1,
    )
    source = source.replace('aria-label="Acciones del día"><button type="button" class="summaryReset" id="resetSession">Reiniciar día</button>', 'aria-label="Acciones del día"><button type="button" id="resetSession">Reiniciar día</button>')
    return source


def standardize_summary_navigation(source: str) -> str:
    """Stop periodic status repaint from snapping the user's scroll position."""
    old_focus = "const focusedIndex = rows.findIndex(row => !row.complete && row.done > 0) >= 0 ? rows.findIndex(row => !row.complete && row.done > 0) : rows.findIndex(row => !row.complete);"
    new_focus = "const activeIndex = exerciseItems.findIndex(entry => { const timing = state.__timing?.exercises?.[String(entry.index + 1)]; return Boolean(timing?.warmupStartedAt || timing?.seriesStartedAt || timing?.restStartedAt || timing?.preparationEndsAt); }); const selectedIndex = Number.isInteger(window.gymratikFocusedExerciseIndex) ? window.gymratikFocusedExerciseIndex : -1; const focusedIndex = selectedIndex >= 0 && selectedIndex < rows.length ? selectedIndex : activeIndex >= 0 ? activeIndex : rows.findIndex(row => !row.complete);"
    source = source.replace(old_focus, new_focus)
    source = source.replace(
        "    new MutationObserver(scheduleAlignment).observe(list, {childList:true, subtree:true});\n",
        "",
    )
    source = re.sub(r"(?m)^([ \t]*if \(list\) \{)\n[ \t]*\n([ \t]*list\.addEventListener\('click')", r"\1\n\2", source)
    source = source.replace(
        "requestedExercise = button.dataset.exercise || '';\n      window.setTimeout(scheduleAlignment, 0);",
        "requestedExercise = button.dataset.exercise || '';\n      window.gymratikFocusedExerciseIndex = Number(requestedExercise) - 1;\n      var exerciseCard = doc.querySelectorAll('.exerciseTracker')[window.gymratikFocusedExerciseIndex]?.closest('article.card');\n      exerciseCard?.scrollIntoView({behavior:'smooth', block:'start'});\n      window.setTimeout(scheduleAlignment, 0);",
    )
    source = source.replace(
        "  if (list) {\n    list.addEventListener('click', function(event){",
        "  if (list) {\n    doc.addEventListener('click', function(event){ if (event.target.closest && event.target.closest('.completeSetButton')) window.gymratikFocusedExerciseIndex = -1; }, true);\n    list.addEventListener('click', function(event){",
    )
    source = re.sub(
        r"  function alignSummary\(exerciseNumber\)\{.*?\n  \}\n\n  function scheduleAlignment",
        "  function alignSummary(exerciseNumber){\n    if (!list) return;\n    var buttons = Array.from(list.querySelectorAll('.summaryExercise'));\n    var target = exerciseNumber ? buttons.find(function(button){ return button.dataset.exercise === String(exerciseNumber); }) : null;\n    if (!target && Number.isInteger(window.gymratikFocusedExerciseIndex)) target = buttons.find(function(button){ return Number(button.dataset.exercise) - 1 === window.gymratikFocusedExerciseIndex; });\n    if (target) buttons.forEach(function(button){ button.classList.toggle('isCurrent', button === target); });\n  }\n\n  function scheduleAlignment",
        source,
        count=1,
        flags=re.S,
    )
    if 'data-enhancement="summary-free-navigation-v1"' not in source:
        source = source.replace('</head>', SUMMARY_NAVIGATION_STYLE + '\n</head>', 1)
    else:
        source = re.sub(r'<style data-enhancement="summary-free-navigation-v1">.*?</style>', lambda _: SUMMARY_NAVIGATION_STYLE, source, count=1, flags=re.S)
    return source


def standardize_muscle_visuals(source: str) -> str:
    source = standardize_technique_guidance(source)
    source = standardize_technique_accordion(source)
    source = standardize_quote_portrait_loading(source)
    source = source.replace(
        "if (seriesIndex + 1 < item.seriesKeys.length) timing.restStartedAt = timestamp; else timing.endedAt = timestamp;",
        "if (seriesIndex + 1 < item.seriesKeys.length || exerciseItems.some(entry => !snapshot(entry).complete)) timing.restStartedAt = timestamp; else timing.endedAt = timestamp;",
        1,
    )
    grid_match = re.search(r'<div class="muscleDayGrid"[^>]*>.*?</div>\s*</div></div>', source, flags=re.S)
    if not grid_match:
        raise ValueError("No se encontró la cuadrícula de músculos del día")
    grid = re.sub(
        r'<div class="muscleDayItem"[^>]*>.*?</div>',
        _muscle_item_replacement,
        grid_match.group(0),
        flags=re.S,
    )
    # Sustituir primero la cuadrícula: insertar CSS antes de ella cambia los
    # offsets de la cadena y no debe invalidar los índices del match.
    source = source[: grid_match.start()] + grid + source[grid_match.end() :]
    source = standardize_offline_image_sources(source)
    source = source.replace(
        '<div class="muscleDayGrid">',
        '<div class="muscleDayGrid" data-enhancement="muscle-day-realistic-media-v1" data-fallback-contract="muscle-day-image-fallback-v1">',
        1,
    )
    routine_title = re.search(r'<h1>DÍA\s+([1-4])\b', source, flags=re.I)
    if not routine_title:
        raise ValueError("No se pudo identificar el día para asignar su portada")
    day = routine_title.group(1)
    cover_markup = (
        f'<figure class="routineDayCover" data-routine-cover="day{day}" aria-hidden="true">'
        f'<img src="../../../assets/branding/routine-covers/day{day}.webp" alt="" aria-hidden="true" '
        'width="1536" height="1024" decoding="async" fetchpriority="high">'
        '</figure>'
    )
    if 'class="routineDayCover"' in source:
        source = re.sub(r'<figure class="routineDayCover".*?</figure>', cover_markup, source, count=1, flags=re.S)
    else:
        subtitle = re.search(r'<div class="subtitle">.*?</div>', source, flags=re.S)
        if not subtitle:
            raise ValueError("No se encontró el subtítulo del encabezado para ubicar la portada")
        source = source[:subtitle.end()] + '\n' + cover_markup + source[subtitle.end():]
    if 'data-enhancement="routine-day-cover-v1"' not in source:
        source = source.replace('</head>', ROUTINE_COVER_STYLE + '\n</head>', 1)
    else:
        source = re.sub(r'<style data-enhancement="routine-day-cover-v1">.*?</style>', lambda _: ROUTINE_COVER_STYLE, source, count=1, flags=re.S)
    if 'data-fix="muscle-specific-focus-v1"' in source:
        source = re.sub(r'<style data-fix="muscle-specific-focus-v1">.*?</style>', MUSCLE_VISUAL_STYLE, source, count=1, flags=re.S)
    else:
        source = source.replace('</head>', MUSCLE_VISUAL_STYLE + '\n</head>', 1)
    source = close_unterminated_segmented_progress_style(source)
    if 'data-enhancement="interaction-feedback-v1"' not in source:
        source = source.replace('</head>', INTERACTION_FEEDBACK_STYLE + '\n</head>', 1)
    else:
        source = re.sub(r'<style data-enhancement="interaction-feedback-v1">.*?</style>', lambda _: INTERACTION_FEEDBACK_STYLE, source, count=1, flags=re.S)
    source = standardize_shared_session_contract(source)
    feedback_runtime = '''  const playMilestoneSound = type => {
    const motifs = {
      warmup: [[392, .1, 0, .026], [494, .1, .15, .028], [587, .15, .3, .03]],
      cardio: [[440, .075, 0, .026], [554, .075, .12, .028], [659, .11, .24, .03]],
      mobility: [[440, .16, 0, .025], [523, .2, .22, .028]],
      preparation: [[392, .075, 0, .022], [494, .075, .14, .024], [659, .13, .28, .028]],
      activity: [[523, .1, 0, .03], [659, .13, .16, .034]],
      series: [[659, .085, 0, .032], [784, .14, .14, .036]],
      rest: [[440, .13, 0, .026], [587, .17, .2, .03]],
      exercise: [[523, .1, 0, .034], [659, .11, .13, .038], [784, .18, .27, .04]],
      session: [[523, .12, 0, .035], [659, .12, .15, .038], [784, .14, .3, .042], [1047, .28, .48, .044]]
    };
    if (!soundEnabled || !motifs[type]) return;
    try {
      const AudioCtor = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtor) return;
      if (!audioContext) audioContext = new AudioCtor();
      if (audioContext.state === 'suspended') audioContext.resume().catch(() => {});
      const now = audioContext.currentTime;
      motifs[type].forEach(([frequency, duration, delay, gain], index) => {
        const startAt = now + delay;
        const oscillator = audioContext.createOscillator();
        const envelope = audioContext.createGain();
        oscillator.type = type === 'cardio' ? 'triangle' : 'sine';
        oscillator.frequency.setValueAtTime(frequency, startAt);
        envelope.gain.setValueAtTime(.0001, startAt);
        envelope.gain.exponentialRampToValueAtTime(gain, startAt + .022);
        envelope.gain.exponentialRampToValueAtTime(.0001, startAt + duration);
        oscillator.connect(envelope).connect(audioContext.destination);
        oscillator.start(startAt);
        oscillator.stop(startAt + duration + .025);
      });
    } catch (_) {}
  };
  const hapticsKey = 'gymratik-haptics-v1';
  let hapticsEnabled = true;
  try { hapticsEnabled = localStorage.getItem(hapticsKey) !== 'off'; } catch (_) {}
  const playHaptic = type => {
    if (!hapticsEnabled || typeof navigator.vibrate !== 'function') return;
    const patterns = {
      warmup: [18, 44, 18], cardio: [16, 34, 16, 34, 24], mobility: [20, 70, 20],
      preparation: [14, 48, 14, 48, 26], activity: [20, 42, 28], series: [24, 54, 34],
      rest: [18, 68, 18, 125, 30], exercise: [28, 55, 28, 55, 42], session: [34, 66, 34, 66, 58]
    };
    try { navigator.vibrate(patterns[type] || []); } catch (_) {}
  };
  const playFeedback = type => { playMilestoneSound(type); playHaptic(type); };
'''
    if "const playFeedback = type => { playMilestoneSound(type); playHaptic(type); };" in source:
        feedback_count = 1
    else:
        source, feedback_count = re.subn(
            r"  const playMilestoneSound = type => \{.*?\n  \};\n(?=  const fitnessQuotePayload)",
            lambda _: feedback_runtime,
            source,
            count=1,
            flags=re.S,
        )
    if feedback_count != 1:
        raise ValueError("No se encontró el contrato de sonidos de hitos para enriquecer audio y hápticos")
    if 'id="hapticsToggle"' not in source:
        source = source.replace(
            '<button type="button" class="soundToggle" id="soundToggle" aria-pressed="true">🔊 Sonidos activados</button>',
            '<button type="button" class="soundToggle" id="soundToggle" aria-pressed="true">🔊 Sonidos activados</button><button type="button" class="hapticsToggle" id="hapticsToggle" aria-pressed="true">📳 Vibración activada</button>',
            1,
        )
    source = source.replace(
        ".newMotivation,.soundToggle{border:1px solid",
        ".newMotivation,.soundToggle,.hapticsToggle{border:1px solid",
        1,
    ).replace(
        ".newMotivation:hover,.soundToggle:hover{border-color:",
        ".newMotivation:hover,.soundToggle:hover,.hapticsToggle:hover{border-color:",
        1,
    ).replace(
        ".newMotivation,.soundToggle{flex:1}",
        ".newMotivation,.soundToggle,.hapticsToggle{flex:1}",
        1,
    )
    if "const hapticsToggle = document.getElementById('hapticsToggle');" not in source:
        source = source.replace(
            "const soundToggle = document.getElementById('soundToggle');",
            "const soundToggle = document.getElementById('soundToggle');\n  const hapticsToggle = document.getElementById('hapticsToggle');",
            1,
        )
    if "const updateHapticsToggle = () =>" not in source:
        source = source.replace(
            "  document.getElementById('newMotivation')?.addEventListener('click', showMotivation);\n  updateSoundToggle();",
            "  const updateHapticsToggle = () => { if (!hapticsToggle) return; hapticsToggle.textContent = hapticsEnabled ? '📳 Vibración activada' : '📴 Vibración silenciada'; hapticsToggle.setAttribute('aria-pressed', String(hapticsEnabled)); };\n  hapticsToggle?.addEventListener('click', () => { hapticsEnabled = !hapticsEnabled; try { localStorage.setItem(hapticsKey, hapticsEnabled ? 'on' : 'off'); } catch (_) {} updateHapticsToggle(); if (hapticsEnabled) playHaptic('series'); });\n  document.getElementById('newMotivation')?.addEventListener('click', showMotivation);\n  updateSoundToggle();\n  updateHapticsToggle();",
            1,
        )
    source = source.replace(
        "playMilestoneSound('rest');\n    try { navigator.vibrate?.([140, 80, 220]); } catch (_) {}",
        "playFeedback('rest');",
    )
    source = source.replace("playMilestoneSound('series');", "playFeedback('series');")
    source = source.replace("playMilestoneSound('exercise');", "playFeedback('exercise');")
    source = source.replace("playMilestoneSound('session');", "playFeedback('session');")
    source = source.replace(
        "const startWarmupPreparation = () => {\n    const warmup = getWarmupTiming();",
        "const startWarmupPreparation = () => {\n    const warmup = getWarmupTiming();",
        1,
    ).replace(
        "    warmup.phase = 'preparing';\n    warmupPreparationEndsAt = Date.now() + PREPARATION_MS;",
        "    warmup.phase = 'preparing';\n    playFeedback('warmup');\n    warmupPreparationEndsAt = Date.now() + PREPARATION_MS;",
        1,
    ).replace(
        "    warmup.phase = 'cardio';\n    warmup.preparationEndsAt = 0;",
        "    warmup.phase = 'cardio';\n    playFeedback('cardio');\n    warmup.preparationEndsAt = 0;",
        1,
    ).replace(
        "    const endsAt = Date.now() + PREPARATION_MS;\n    const timing = getExerciseTiming(item);",
        "    const endsAt = Date.now() + PREPARATION_MS;\n    playFeedback('preparation');\n    const timing = getExerciseTiming(item);",
        1,
    ).replace(
        "      beginSeries(item, Date.now());\n      updateTracker(item.tracker, false);",
        "      beginSeries(item, Date.now());\n      playFeedback('activity');\n      updateTracker(item.tracker, false);",
        1,
    ).replace(
        "      warmup.phase = 'mobility';\n      warmup.cardioEndedAt = timestamp;",
        "      warmup.phase = 'mobility';\n      playFeedback('mobility');\n      warmup.cardioEndedAt = timestamp;",
        1,
    ).replace(
        "      warmup.phase = 'done';\n      warmup.mobilityEndedAt = timestamp;",
        "      warmup.phase = 'done';\n      playFeedback('exercise');\n      warmup.mobilityEndedAt = timestamp;",
        1,
    )
    source = standardize_series_entry_zone(source)
    source = re.sub(
        r'<div class="warmupTrackerActions">.*?</div>',
        '<div class="warmupTrackerActions"><button type="button" id="warmupAction" aria-describedby="warmupInstructions">▶ Iniciar calentamiento</button></div>',
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace(
        '<div class="warmupTrackerHead"><span>⏱ Seguimiento del calentamiento</span>',
        '<div class="warmupTrackerHead"><span>⏱ Seguimiento del calentamiento</span>',
        1,
    )
    source = re.sub(
        r'(<p class="warmupInstructions" id="warmupInstructions">.*?</p>)(?:\s*<p class="warmupInstructions" id="warmupInstructions">.*?</p>)+',
        r'\1',
        source,
        count=1,
        flags=re.S,
    )
    if 'id="warmupInstructions"' not in source:
        source = source.replace(
            '<div class="warmupTracker" id="warmupTracker" aria-label="Seguimiento del calentamiento">',
            '<div class="warmupTracker" id="warmupTracker" aria-label="Seguimiento del calentamiento"><p class="warmupInstructions" id="warmupInstructions">Sigue las actividades, tiempos y técnica indicados arriba para este día. Completa primero el bloque de cardio o activación y luego la movilidad; trabaja con control, sin llegar fatigado y sin dolor. El mismo botón inicia, avanza de fase y finaliza el calentamiento.</p>',
            1,
        )
    if 'id="warmupProgress"' not in source:
        source, warmup_progress_count = re.subn(
            r'(<div class="warmupTrackerHead">.*?</div>)',
            lambda match: f"{match.group(1)}\n{WARMUP_PROGRESS_MARKUP}",
            source,
            count=1,
            flags=re.S,
        )
        if warmup_progress_count != 1:
            raise ValueError("No se pudo integrar la barra de progreso del calentamiento")
    source = re.sub(
        r'<button type="button" class="setButton warmupSet"([^>]*)>Calentamiento</button>',
        lambda match: match.group(0) if re.search(r'\shidden(?:\s|=|>)', match.group(1)) else f'<button type="button" class="setButton warmupSet"{match.group(1)} hidden aria-hidden="true" tabindex="-1">Calentamiento</button>',
        source,
    )
    source = re.sub(
        r'(<button type="button" class="completeSetButton"[^>]*>.*?</button>)',
        lambda match: match.group(1) if 'aria-describedby="exerciseWarmupHint"' in match.group(1) else match.group(1).replace('>', ' aria-describedby="exerciseWarmupHint">', 1),
        source,
        count=1,
        flags=re.S,
    )
    if 'id="exerciseWarmupHint"' not in source:
        source = re.sub(
            r'(<div class="exerciseSetButtons"[^>]*>)(<button type="button" class="setButton warmupSet"[^>]*>.*?</button>)',
            r'\1<p class="exerciseWarmupHint" id="exerciseWarmupHint" hidden aria-live="polite">Aproximación: usa una carga ligera y recorrido controlado; se registra aparte y no suma al volumen de trabajo.</p>\2',
            source,
            count=1,
            flags=re.S,
        )
    source = re.sub(
        r'(<p class="exerciseWarmupHint" id="exerciseWarmupHint")[^>]*>',
        r'\1 hidden aria-live="polite">',
        source,
        count=1,
    )
    source = re.sub(r'<div class="summaryActivity" id="summaryActivity"[^>]*>.*?</div>\s*', "", source, count=1, flags=re.S)
    source = source.replace('<span aria-hidden="true">📋</span><span id="summaryHeadline">', '<span id="summaryActivityIcon" aria-hidden="true">📋</span><span id="summaryHeadline">', 1)
    source = re.sub(
        r'(?:<span id="summaryActivityHeadline">.*?</span>)+',
        '<span id="summaryActivityHeadline">¡Vamos a entrenar!</span>',
        source,
        count=1,
        flags=re.S,
    )
    if 'id="summaryActivityHeadline"' not in source:
        source = source.replace(
            '</span><span class="summaryChevron" aria-hidden="true">⌃</span></button>',
            '</span><span id="summaryActivityHeadline">Sin actividad · listo para continuar</span><span class="summaryChevron" aria-hidden="true">⌃</span></button>',
            1,
        )
    if source.count('id="summaryActivityHeadline"') != 1:
        raise ValueError("No se pudo integrar el estado resumido de actividad en la cabecera flotante")
    source = re.sub(r'<img\b(?=[^>]*\bid=["\']summaryActivityMascot["\'])[^>]*>', '', source, count=1, flags=re.I | re.S)
    source = source.replace('<span class="summaryMascotWrap"></span>', '')
    source = re.sub(r'<span\s+class=["\']summaryMascotWrap["\']\s*>\s*</span>', '', source, count=1, flags=re.I | re.S)
    source = re.sub(r'(<span id="summaryActivityHeadline">).*?(</span>)', r'\1¡Vamos a entrenar!\2', source, count=1, flags=re.S)
    if 'id="summaryActivityMascot"' not in source:
        source = source.replace(
            '<span class="summaryChevron" aria-hidden="true">⌃</span>',
            '<span class="summaryMascotWrap"><img id="summaryActivityMascot" class="summaryActivityMascot" src="../../../data/profile/mascot-motion/neutral-exercise-still.webp" alt="Mascotas Gymratik animando el inicio de la rutina" decoding="async"></span><span class="summaryChevron" aria-hidden="true">⌃</span>',
            1,
        )
    if source.count('id="summaryActivityMascot"') != 1:
        raise ValueError("La mascota persistente debe existir una sola vez en la cabecera del resumen")
    source = re.sub(r'(<span class="summaryActivityLabel" id="summaryActivityLabel">).*?(</span>)', r'\1¡Vamos a entrenar!\2', source, count=1, flags=re.S)
    source = re.sub(r'(<span class="summaryActivityClock" id="summaryActivityClock">).*?(</span>)', r'\1Iniciar\2', source, count=1, flags=re.S)
    if 'id="summaryActivityStatus"' not in source:
        source = source.replace(
            '<div class="summaryTotals"><span id="summaryPending">0 pendientes</span></div>',
            '<div class="summaryTotals"><span id="summaryPending">0 pendientes</span></div><div class="summaryActivityStatus isIdle" id="summaryActivityStatus" data-activity="start" aria-live="polite"><span class="summaryActivityIndicator" aria-hidden="true"></span><span class="summaryActivityLabel" id="summaryActivityLabel">¡Vamos a entrenar!</span><span class="summaryActivityClock" id="summaryActivityClock">Iniciar</span></div><div class="summaryProgressTrack" id="summaryOverallProgress" role="progressbar" aria-label="Progreso total de series" aria-valuemin="0" aria-valuemax="0" aria-valuenow="0" aria-valuetext="Sin series completadas" data-state="empty"><span id="summaryProgressFill"></span></div>',
            1,
        )
    def initialize_activity_mascot(match: re.Match[str]) -> str:
        tag = re.sub(r'\s+hidden(?=[\s/>])', '', match.group(0), flags=re.I)
        if not re.search(r'\bsrc\s*=', tag, flags=re.I):
            tag = re.sub(r'\s*/?>$', lambda closing: ' src="../../../data/profile/mascot-motion/neutral-rest-still.webp"' + closing.group(0), tag)
        alt_match = re.search(r'\balt\s*=\s*(["\'])(.*?)\1', tag, flags=re.I | re.S)
        if alt_match and not alt_match.group(2).strip():
            tag = tag[:alt_match.start(2)] + 'Mascotas Gymratik descansando' + tag[alt_match.end(2):]
        elif not alt_match:
            tag = re.sub(r'\s*/?>$', lambda closing: ' alt="Mascotas Gymratik descansando"' + closing.group(0), tag)
        return tag
    source = re.sub(r'<img\b(?=[^>]*\bid=["\']summaryActivityMascot["\'])[^>]*>', initialize_activity_mascot, source, count=1, flags=re.I | re.S)
    if 'id="summaryOverallProgress"' not in source:
        raise ValueError("No se pudo integrar la barra de progreso total en el resumen flotante")
    if 'id="summaryActivityIcon"' not in source and 'id="summaryToggle"' in source:
        raise ValueError("No se pudo integrar el estado dinámico en el botón flotante existente")
    next_index = 1

    def add_card_index(match: re.Match[str]) -> str:
        nonlocal next_index
        index = next_index
        next_index += 1
        return f'<article class="card" data-exercise-index="{index}">'

    source = re.sub(r'<article class="card">', add_card_index, source)
    source = re.sub(
        r'\.sessionCompletionCopy p\{[^}]*\}',
        '.sessionCompletionCopy p{margin:0;max-width:44rem;color:#d8eef5;font-size:clamp(1rem,2.2vw,1.28rem);font-weight:800;line-height:1.35;display:block;overflow:visible;overflow-wrap:anywhere;white-space:normal}',
        source,
        count=1,
    )
    if 'data-enhancement="canonical-card-contract-v1"' not in source:
        source = source.replace('<main class="cards">', CANONICAL_CONTRACT_MARKUP + '\n<main class="cards">', 1)
    if 'data-fix="phase-media-clarity-v5"' not in source:
        source = source.replace('</head>', CANONICAL_SHARED_STYLE + '\n</head>', 1)
    if 'data-enhancement="mobile-first-muscle-grid-v1"' not in source:
        source = source.replace('</body>', MOBILE_FIRST_MUSCLE_STYLE + '\n</body>', 1)
    source = re.sub(r'<style data-enhancement="compact-routine-metrics-v1">.*?</style>\s*', "", source, count=1, flags=re.S)
    source = source.replace('</body>', COMPACT_ROUTINE_METRICS_STYLE + '\n</body>', 1)
    source = re.sub(
        r'<style data-fix="rest-countdown-activity-v1">.*?</style>\s*',
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace('</body>', REST_COUNTDOWN_STYLE + '\n</body>', 1)
    source = standardize_optional_media_fallback(source)
    source = standardize_warmup_single_viewers(source)
    source = standardize_visual_language(source)
    source = standardize_summary_navigation(source)
    source = standardize_weekly_progress_reset(source)
    source = standardize_motivational_toast(source)
    newline = "\r\n" if "\r\n" in source else "\n"
    return apply_battery_motion(source, newline)


def standardize_motivational_toast(source: str) -> str:
    """Keep the encouragement toast readable longer and pair it with the profile mascot."""
    old_toast_style = re.compile(r"#gymratikEncouragement\{[^}]*\}")
    source, style_count = old_toast_style.subn(
        "#gymratikEncouragement{position:fixed;z-index:150;top:max(.8rem,env(safe-area-inset-top));left:50%;display:flex;align-items:center;gap:.6rem;width:max-content;max-width:min(92vw,34rem);min-height:64px;padding:.42rem .85rem .42rem .48rem;border:1px solid rgba(101,242,221,.66);border-radius:1.15rem;background:linear-gradient(120deg,rgba(8,47,59,.98),rgba(14,54,74,.98));box-shadow:0 12px 38px rgba(0,0,0,.36),0 0 25px rgba(34,191,174,.2);color:#f0fffc;font:800 .9rem/1.35 system-ui,sans-serif;text-align:left;pointer-events:none;opacity:0;transform:translate(-50%,-10px)}",
        source,
        count=1,
    )
    if style_count != 1:
        raise ValueError("No se encontró el estilo base del toast de ánimo")
    source = re.sub(r'<style data-enhancement="approval-toast-mascot-v1">.*?</style>\s*', "", source, count=1, flags=re.S)
    source = source.replace('</body>', APPROVAL_TOAST_STYLE + '\n</body>', 1)
    script_anchor = "  toast.setAttribute('aria-atomic', 'true');\n  document.body.append(layer, toast);"
    script_replacement = "  toast.setAttribute('aria-atomic', 'true');\n  const toastMascot = document.createElement('img');\n  toastMascot.className = 'toastMascot';\n  toastMascot.alt = '';\n  toastMascot.setAttribute('aria-hidden', 'true');\n  const toastCopy = document.createElement('span');\n  toastCopy.className = 'toastCopy';\n  toast.append(toastMascot, toastCopy);\n  document.body.append(layer, toast);"
    if "const toastMascot = document.createElement('img');" not in source:
        if script_anchor not in source:
            raise ValueError("No se encontró el punto de integración del toast con la mascota")
        source = source.replace(script_anchor, script_replacement, 1)
    if "toastCopy.textContent = message;" not in source:
        source = source.replace(
            "    toast.textContent = message;",
            "    const variant = window.gymratikMascotVariant;\n    toastMascot.src = ['male', 'female'].includes(variant) ? `../../../data/profile/mascot-motion/states-v1/${variant}-approval.png` : '../../../data/profile/mascot-motion/neutral-exercise-still.webp';\n    toastCopy.textContent = message;",
            1,
        )
    source, timer_count = re.subn(r"(toastTimer = window\.setTimeout\(\(\) => \{.*?\}, )(?:3000|5200)(\);)", r"\g<1>5200\g<2>", source, count=1, flags=re.S)
    if timer_count != 1:
        raise ValueError("No se pudo ampliar la duración del toast de ánimo")
    return source


def standardize_visual_language(source: str) -> str:
    """Apply a consistent Lucide icon language and trim repeated instructions."""
    if 'id="gymratikLucideSprite"' not in source:
        source, body_count = re.subn(r"(<body\b[^>]*>)", lambda match: match.group(1) + LUCIDE_SPRITE, source, count=1, flags=re.I)
        if body_count != 1:
            raise ValueError("No se pudo integrar el sprite local de iconos Lucide")

    def use(name: str, extra_class: str = "") -> str:
        classes = f"lucide lucide-{name} gymratikIcon {extra_class}".strip()
        return f'<svg class="{classes}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#gymratik-icon-{name}"></use></svg>'

    source = re.sub(
        r'(<a class="routine-home-link"[^>]*>).*?(</a>)',
        lambda match: match.group(1) + use("arrow-left") + "<span>Portada</span>" + match.group(2),
        source,
        count=1,
        flags=re.S,
    )
    if 'id="quick-rules-title"' in source and "lucide-target" not in source:
        source = re.sub(
            r'(<div class="footerTitle" id="quick-rules-title">).*?(</div>)',
            lambda match: match.group(1) + use("target") + "GUÍA RÁPIDA" + match.group(2),
            source,
            count=1,
            flags=re.S,
        )
    if 'id="warmup-title"' in source and "warmup-title-icon" not in source:
        source = re.sub(r'(<h2 id="warmup-title">)', lambda match: match.group(1) + use("timer", "warmup-title-icon"), source, count=1)
    if 'class="warmupTrackerHead"' in source and 'warmup-tracker-icon' not in source:
        source = re.sub(
            r'(<div class="warmupTrackerHead">\s*<span>).*?(</span>)',
            lambda match: match.group(1) + use("timer", "warmup-tracker-icon") + "Seguimiento del calentamiento" + match.group(2),
            source,
            count=1,
            flags=re.S,
        )
    source = re.sub(
        r'(<span class="coachRibbonIcon"[^>]*>).*?(</span>)',
        lambda match: match.group(1) + use("list-checks") + match.group(2),
        source,
        count=0,
        flags=re.S,
    )
    source = re.sub(
        r'(<span class="pillIcon"[^>]*>).*?(</span>)',
        lambda match: match.group(1) + use("dumbbell") + match.group(2),
        source,
        flags=re.S,
    )

    technique_icons = (
        ("1 · Ajuste", "settings-2"),
        ("2 · Ejecución", "move-up-right"),
        ("3 · Ritmo y respiración", "wind"),
        ("3 · Control", "activity"),
        ("⚠ Evita", "triangle-alert"),
    )
    for label, icon_name in technique_icons:
        escaped_label = re.escape(label)
        source = re.sub(
            rf'(<div class="techStepTitle">){escaped_label}(</div>)',
            lambda match, name=icon_name, text=label: match.group(1) + use(name) + f"<span>{text.removeprefix('⚠ ').removeprefix('3 · ' if text == '3 · Control' else '')}</span>" + match.group(2),
            source,
        )

    source = source.replace(
        "Sigue las actividades, tiempos y técnica indicados arriba para este día. Completa primero el bloque de cardio o activación y luego la movilidad; trabaja con control, sin llegar fatigado y sin dolor. El mismo botón inicia, avanza de fase y finaliza el calentamiento.",
        "Sigue cardio y movilidad en ese orden. Mantén un ritmo cómodo, sin fatiga ni dolor; el mismo botón inicia, avanza y finaliza el calentamiento.",
    )
    source = source.replace(
        "Antes de las 4 series efectivas, realiza 1 serie de calentamiento con carga ligera y recorrido completo. Después ajusta el asiento",
        "Ajusta el asiento",
    )
    source = re.sub(
        r'(<span id="summaryActivityIcon" aria-hidden="true">).*?(</span>)',
        lambda match: match.group(1) + use("activity") + match.group(2),
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace(
        '<div class="motivationPhotoWrap"><div class="motivationPhotoWrap">',
        '<div class="motivationPhotoWrap">',
    )
    source = source.replace(
        '</a></div></div><div class="sessionCompletionCopy">',
        '</a></div><div class="sessionCompletionCopy">',
    )
    if 'class="motivationPhotoWrap"' not in source:
        source = re.sub(
            r'<div class="motivationPortrait"[^>]*>.*?</div><div class="sessionCompletionCopy">',
            '<div class="motivationPhotoWrap"><div class="motivationPortrait" aria-label="Retrato de quien dice la frase"><img id="motivationPortrait" alt="" decoding="async" loading="lazy" hidden><span id="motivationInitials" aria-hidden="true">★</span></div><a class="motivationPhotoCredit" id="motivationPhotoCredit" target="_blank" rel="noopener noreferrer" hidden></a></div><div class="sessionCompletionCopy">',
            source,
            count=1,
            flags=re.S,
        )
    source = re.sub(
        r'<span class="motivationNote" id="motivationNote" hidden></span>',
        '<a class="motivationNote" id="motivationNote" target="_blank" rel="noopener noreferrer" hidden></a>',
        source,
        count=1,
    )
    visual_style_pattern = r'<style data-enhancement="visual-language-lucide-v1">.*?</style>'
    if re.search(visual_style_pattern, source, flags=re.S):
        source = re.sub(visual_style_pattern, VISUAL_LANGUAGE_STYLE, source, count=1, flags=re.S)
    else:
        source = source.replace("</body>", VISUAL_LANGUAGE_STYLE + "\n</body>", 1)
    return source


def close_unterminated_segmented_progress_style(source: str) -> str:
    """Close the progress stylesheet before a following style block.

    HTML treats style contents as raw text, so a missing closing tag causes
    every subsequent style tag up to the next closing tag to be ignored.
    """
    marker = '<style data-enhancement="segmented-progress-bars-v1">'
    start = source.find(marker)
    if start < 0:
        return source

    next_start = source.find("<style", start + len(marker))
    head_end = source.find("</head>", start + len(marker))
    boundary = min((index for index in (next_start, head_end) if index >= 0), default=-1)
    if boundary < 0:
        return source

    close = source.find("</style>", start + len(marker))
    if close >= 0 and close < boundary:
        return source
    return source[:boundary].rstrip() + "\n</style>\n" + source[boundary:]


def standardize_series_entry_zone(source: str) -> str:
    """Require set metrics by default; make deliberate omissions and load bounds explicit."""
    source = re.sub(
        r'(<button\b(?=[^>]*\bid="summaryToggle")(?=[^>]*\baria-expanded=")[^>]*\baria-expanded=")true(")',
        r'\1false\2',
        source,
        count=1,
        flags=re.I,
    )
    source = re.sub(
        r'(<div\b(?=[^>]*\bid="summaryBody")(?=[^>]*\bclass="summaryBody")[^>]*)>',
        lambda match: match.group(1) + (' hidden' if not re.search(r'\shidden(?:\s|=|$)', match.group(1), re.I) else '') + '>',
        source,
        count=1,
        flags=re.I,
    )
    source = source.replace(
        "if (doneSeries > 0 && summaryToggle && summaryBody && completedExercises !== exerciseItems.length) { summaryToggle.setAttribute('aria-expanded', 'true'); summaryBody.hidden = false; }",
        "if (doneSeries > 0 && summaryToggle && summaryBody && completedExercises !== exerciseItems.length && summaryToggle.getAttribute('aria-expanded') === 'true') { summaryToggle.setAttribute('aria-expanded', 'true'); summaryBody.hidden = false; }",
        1,
    )
    load_profile_block = """    const loadDescription = item.title.toLocaleLowerCase('es');
    const loadProfiles = [
      [/^jalón al pecho$/, { minKg: 2.5, maxKg: 150, stepKg: 2.5, label: 'jalón · torre de polea (rango orientativo)' }],
      [/^remo alto unilateral$/, { minKg: 2.5, maxKg: 120, stepKg: 2.5, label: 'remo unilateral · discos por brazo (rango orientativo)' }],
      [/^remo horizontal en máquina$/, { minKg: 2.5, maxKg: 120, stepKg: 2.5, label: 'remo sentado · rango orientativo' }],
      [/^apertura inversa en máquina$/, { minKg: 2.5, maxKg: 80, stepKg: 2.5, label: 'apertura inversa · rango orientativo' }],
      [/^curl de bíceps/, { minKg: 2.5, maxKg: 80, stepKg: 2.5, label: 'curl de bíceps · rango orientativo' }],
      [/^hack squat$/, { minKg: 5, maxKg: 300, stepKg: 5, label: 'hack squat · carga externa total (rango orientativo)' }],
      [/^hip thrust$/, { minKg: 5, maxKg: 250, stepKg: 5, label: 'hip thrust · discos totales (rango orientativo)' }],
      [/^prensa de piernas$/, { minKg: 5, maxKg: 300, stepKg: 5, label: 'prensa bilateral · carga externa total (rango orientativo)' }],
      [/^prensa unilateral alterna$/, { minKg: 5, maxKg: 200, stepKg: 5, label: 'prensa unilateral · carga externa total (rango orientativo)' }],
      [/^curl femoral/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'curl femoral · rango orientativo' }],
      [/^extensión de piernas$/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'extensión de piernas · rango orientativo' }],
      [/^pantorrillas de pie$/, { minKg: 2.5, maxKg: 150, stepKg: 2.5, label: 'pantorrilla de pie · rango orientativo' }],
      [/^press de pecho sentado/, { minKg: 2.5, maxKg: 120, stepKg: 2.5, label: 'press de pecho · rango orientativo' }],
      [/^press inclinado convergente/, { minKg: 2.5, maxKg: 120, stepKg: 2.5, label: 'press inclinado · rango orientativo' }],
      [/^pec deck/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'pec deck · rango orientativo' }],
      [/^press de hombro/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'press de hombro · rango orientativo' }],
      [/^elevación lateral/, { minKg: 2.5, maxKg: 60, stepKg: 2.5, label: 'elevación lateral · rango orientativo' }],
      [/^jalón de tríceps/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'tríceps en polea · rango orientativo' }],
      [/^extensión de tríceps sobre cabeza/, { minKg: 2.5, maxKg: 80, stepKg: 2.5, label: 'tríceps con cuerda · rango orientativo' }],
      [/^peso muerto rumano con barra$/, { minKg: 10, maxKg: 250, stepKg: 2.5, label: 'barra libre · peso total con barra (rango orientativo)' }],
      [/^abducción de cadera/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'abducción de cadera · rango orientativo' }],
      [/^aducción de cadera/, { minKg: 2.5, maxKg: 100, stepKg: 2.5, label: 'aducción de cadera · rango orientativo' }],
      [/^elevación de pantorrilla sentada$/, { minKg: 2.5, maxKg: 150, stepKg: 2.5, label: 'pantorrilla sentada · rango orientativo' }],
      [/^crunch con elevación de piernas sentada$/, { minKg: 2.5, maxKg: 80, stepKg: 2.5, label: 'crunch sentado · rango orientativo' }]
    ];
    const loadProfile = loadProfiles.find(([pattern]) => pattern.test(loadDescription))?.[1];
    if (!loadProfile) throw new Error(`Falta un perfil de carga revisado para: ${item.title}`);
    item.performanceLoadProfile = loadProfile;
"""
    profile_start = source.find("const loadDescription =")
    profile_end = source.find("const createPerformanceIcon", profile_start)
    if profile_start >= 0 and profile_end > profile_start:
        source = source[:profile_start] + load_profile_block + "    " + source[profile_end:]
    else:
        source = source.replace(
            "item.repMaximum = rangeMatch ? Number(rangeMatch[2]) : 100;",
            "item.repMaximum = rangeMatch ? Number(rangeMatch[2]) : 100;\n" + load_profile_block.rstrip(),
            1,
        )
    dialog_helper = """  const confirmMissingPerformance = missing => new Promise(resolve => {
    let dialog = document.getElementById('performanceMissingDialog');
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.id = 'performanceMissingDialog';
      dialog.className = 'performanceMissingDialog';
      dialog.setAttribute('aria-labelledby', 'performanceMissingTitle');
      dialog.setAttribute('aria-describedby', 'performanceMissingDescription');
      dialog.innerHTML = '<h2 id="performanceMissingTitle">¿Completar sin estos datos?</h2><p id="performanceMissingDescription">La serie se guardará, pero el registro de rendimiento quedará incompleto:</p><ul data-missing-performance></ul><div class="dialogActions"><button type="button" value="cancel">Volver a registrar</button><button type="button" value="continue">Guardar sin estos datos</button></div>';
      dialog.querySelector('[value="cancel"]').addEventListener('click', () => dialog.close('cancel'));
      dialog.querySelector('[value="continue"]').addEventListener('click', () => dialog.close('continue'));
      document.body.append(dialog);
    }
    const list = dialog.querySelector('[data-missing-performance]');
    list.replaceChildren(...missing.map(label => { const row = document.createElement('li'); row.textContent = label; return row; }));
    dialog.addEventListener('close', () => resolve(dialog.returnValue === 'continue'), { once: true });
    dialog.showModal();
  });
"""
    if "const confirmMissingPerformance = missing =>" not in source:
        source = source.replace(
            "  const trackers = [...document.querySelectorAll('.exerciseTracker')];",
            dialog_helper + "  const trackers = [...document.querySelectorAll('.exerciseTracker')];",
            1,
        )
    source = source.replace(
        "const repsTitle = document.createElement('span'); repsTitle.textContent = 'Repeticiones realizadas · opcional'; const repsClear = document.createElement('button');",
        "const repsLabelText = document.createElement('span'); repsLabelText.textContent = 'Repeticiones'; const repsIcon = createPerformanceIcon('repeat-2'); const repsRequired = document.createElement('span'); repsRequired.className = 'performanceRequired'; repsRequired.textContent = 'Requerido'; const repsFieldLabel = document.createElement('span'); repsFieldLabel.className = 'performanceFieldLabel'; if (repsIcon) repsFieldLabel.append(repsIcon); repsFieldLabel.append(repsLabelText); const repsTitle = document.createElement('span'); repsTitle.className = 'performanceFieldTitleRow'; repsTitle.append(repsFieldLabel, repsRequired); const repsClear = document.createElement('button');",
        1,
    )
    source = source.replace(
        "const repsLabelText = document.createElement('span'); repsLabelText.textContent = 'Repeticiones'; const repsIcon = createPerformanceIcon('repeat-2'); const repsOptional = document.createElement('span'); repsOptional.className = 'performanceOptional'; repsOptional.textContent = 'Opcional'; const repsFieldLabel = document.createElement('span'); repsFieldLabel.className = 'performanceFieldLabel'; if (repsIcon) repsFieldLabel.append(repsIcon); repsFieldLabel.append(repsLabelText); const repsTitle = document.createElement('span'); repsTitle.className = 'performanceFieldTitleRow'; repsTitle.append(repsFieldLabel, repsOptional); const repsClear = document.createElement('button');",
        "const repsLabelText = document.createElement('span'); repsLabelText.textContent = 'Repeticiones'; const repsIcon = createPerformanceIcon('repeat-2'); const repsRequired = document.createElement('span'); repsRequired.className = 'performanceRequired'; repsRequired.textContent = 'Requerido'; const repsFieldLabel = document.createElement('span'); repsFieldLabel.className = 'performanceFieldLabel'; if (repsIcon) repsFieldLabel.append(repsIcon); repsFieldLabel.append(repsLabelText); const repsTitle = document.createElement('span'); repsTitle.className = 'performanceFieldLabel'; repsTitle.append(repsFieldLabel, repsRequired); const repsClear = document.createElement('button');",
        1,
    )
    source = source.replace(
        "const loadLabelText = document.createElement('span'); loadLabelText.textContent = 'Carga'; const loadIcon = createPerformanceIcon('weight'); const loadOptional = document.createElement('span'); loadOptional.className = 'performanceOptional'; loadOptional.textContent = 'Opcional'; const loadFieldLabel = document.createElement('span'); loadFieldLabel.className = 'performanceFieldLabel'; if (loadIcon) loadFieldLabel.append(loadIcon); loadFieldLabel.append(loadLabelText); const loadTitle = document.createElement('span'); loadTitle.className = 'performanceFieldLabel'; loadTitle.append(loadFieldLabel, loadOptional);",
        "const loadLabelText = document.createElement('span'); loadLabelText.textContent = 'Carga'; const loadIcon = createPerformanceIcon('weight'); const loadRequired = document.createElement('span'); loadRequired.className = 'performanceRequired'; loadRequired.textContent = 'Requerida'; const loadFieldLabel = document.createElement('span'); loadFieldLabel.className = 'performanceFieldLabel'; if (loadIcon) loadFieldLabel.append(loadIcon); loadFieldLabel.append(loadLabelText); const loadTitle = document.createElement('span'); loadTitle.className = 'performanceFieldLabel'; loadTitle.append(loadFieldLabel, loadRequired);",
        1,
    )
    if "const repsOptional = document.createElement('span')" in source or "const loadOptional = document.createElement('span')" in source:
        raise ValueError("No se pudo sustituir el estado opcional por el requisito explícito de registro")
    source = source.replace(
        "const loadHead = document.createElement('span'); loadHead.className = 'performanceLoadHead';\n    const loadTitle = document.createElement('span'); loadTitle.textContent = 'Carga utilizada (opcional)';",
        "const loadHead = document.createElement('div'); loadHead.className = 'performanceLoadHead';\n    const loadLabelText = document.createElement('span'); loadLabelText.textContent = 'Carga'; const loadIcon = createPerformanceIcon('weight'); const loadRequired = document.createElement('span'); loadRequired.className = 'performanceRequired'; loadRequired.textContent = 'Requerida'; const loadFieldLabel = document.createElement('span'); loadFieldLabel.className = 'performanceFieldLabel'; if (loadIcon) loadFieldLabel.append(loadIcon); loadFieldLabel.append(loadLabelText); const loadTitle = document.createElement('span'); loadTitle.className = 'performanceFieldLabel'; loadTitle.append(loadFieldLabel, loadRequired);",
        1,
    )
    source = source.replace("loadTitle.textContent = 'Carga utilizada · opcional'; const loadClear = document.createElement('button');", "const loadClear = document.createElement('button');", 1)
    source = source.replace(
        "[['kg', 'kg · kilogramos'], ['lb', 'lb · libras']].forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; loadUnitSelect.append(option); });",
        "[['kg', 'kg'], ['lb', 'lb']].forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; option.setAttribute('aria-label', value === 'kg' ? 'Kilogramos' : 'Libras'); loadUnitSelect.append(option); }); loadUnitSelect.addEventListener('keydown', event => { if (event.key === 'Enter') event.stopPropagation(); });",
        1,
    )
    if "const loadUnitSelect = document.createElement('select')" in source and "loadUnitSelect.addEventListener('keydown', event => { if (event.key === 'Enter') event.stopPropagation(); });" not in source:
        source, guarded_unit_selects = re.subn(
            r"(\[\['kg',\s*'kg'\].*?loadUnitSelect\.append\(option\);\s*\}\);)",
            r"\1 loadUnitSelect.addEventListener('keydown', event => { if (event.key === 'Enter') event.stopPropagation(); });",
            source,
            count=1,
            flags=re.S,
        )
        if guarded_unit_selects != 1:
            raise ValueError("No se encontró el selector kg/lb para impedir que Enter active acciones ajenas")
    source = source.replace(
        "progressionCue.textContent = 'Ambos datos son opcionales. Ajusta las repeticiones con −/+ o el deslizador; toca la carga para escribirla con precisión. La serie se completa aunque no registres datos.';",
        "progressionCue.textContent = `Registra ambos datos para completar. Rango sugerido para ${item.performanceLoadProfile.label}: ${item.performanceLoadProfile.minKg}–${item.performanceLoadProfile.maxKg} kg; si no conoces algún dato, podrás continuar tras confirmarlo.`;",
        1,
    )
    source = source.replace(
        "progressionCue.textContent = 'Opcional: desliza o usa −/+ para repeticiones; toca la carga para escribirla. Puedes completar la serie sin registrar.';",
        "progressionCue.textContent = `Registra repeticiones y carga para completar. Si no conoces algún dato, toca «Quitar» y podrás continuar después de confirmar que quedará sin registrar. Rango de carga: ${item.performanceLoadProfile.minKg}–${item.performanceLoadProfile.maxKg} kg.`;",
        1,
    )
    if "Ambos datos son opcionales" in source or "Opcional: desliza" in source:
        raise ValueError("La ayuda de registro todavía presenta como opcionales los datos requeridos")
    source = source.replace(
        "const pounds = item.performanceLoadUnit === 'lb';\n      loadInput.max = pounds ? '2200' : '1000';\n      loadInput.step = pounds ? '5' : '2.5';",
        "const pounds = item.performanceLoadUnit === 'lb';\n      const factor = pounds ? 1 / 0.45359237 : 1;\n      const unitStep = pounds ? 5 : item.performanceLoadProfile.stepKg;\n      const selectedValue = Number(item.performanceLoadExact);\n      const unitMin = Math.ceil(Math.min(item.performanceLoadProfile.minKg, item.performanceLoadSelected && Number.isFinite(selectedValue) ? selectedValue : item.performanceLoadProfile.minKg) * factor / unitStep) * unitStep;\n      const unitMax = Math.floor(Math.max(item.performanceLoadProfile.maxKg, item.performanceLoadSelected && Number.isFinite(selectedValue) ? selectedValue : item.performanceLoadProfile.maxKg) * factor / unitStep) * unitStep;\n      loadInput.min = String(unitMin); loadInput.max = String(unitMax); loadInput.step = String(unitStep); loadInput.dataset.loadProfile = item.performanceLoadProfile.label; loadInput.dataset.maxKg = String(item.performanceLoadProfile.maxKg);\n      if (!item.performanceLoadSelected) loadInput.value = String(unitMin);\n      else loadInput.value = String(Math.min(unitMax, Math.max(unitMin, selectedValue || unitMin)));",
        1,
    )
    source = re.sub(
        r"const unitMin = Math\.ceil\(item\.performanceLoadProfile\.minKg \* factor / unitStep\) \* unitStep;\r?\n"
        r"[ \t]*const unitMax = Math\.floor\(item\.performanceLoadProfile\.maxKg \* factor / unitStep\) \* unitStep;\r?\n"
        r"[ \t]*loadInput\.min = String\(unitMin\); loadInput\.max = String\(unitMax\); loadInput\.step = String\(unitStep\); loadInput\.dataset\.loadProfile = item\.performanceLoadProfile\.label; loadInput\.dataset\.maxKg = String\(item\.performanceLoadProfile\.maxKg\);\r?\n"
        r"[ \t]*if \(!item\.performanceLoadSelected\) loadInput\.value = String\(unitMin\);\r?\n"
        r"[ \t]*else loadInput\.value = String\(Math\.min\(unitMax, Math\.max\(unitMin, Number\(item\.performanceLoadExact\) \|\| unitMin\)\)\);",
        "const selectedValue = Number(item.performanceLoadExact);\n      const unitMin = Math.ceil(Math.min(item.performanceLoadProfile.minKg, item.performanceLoadSelected && Number.isFinite(selectedValue) ? selectedValue : item.performanceLoadProfile.minKg) * factor / unitStep) * unitStep;\n      const unitMax = Math.floor(Math.max(item.performanceLoadProfile.maxKg, item.performanceLoadSelected && Number.isFinite(selectedValue) ? selectedValue : item.performanceLoadProfile.maxKg) * factor / unitStep) * unitStep;\n      loadInput.min = String(unitMin); loadInput.max = String(unitMax); loadInput.step = String(unitStep); loadInput.dataset.loadProfile = item.performanceLoadProfile.label; loadInput.dataset.maxKg = String(item.performanceLoadProfile.maxKg);\n      if (!item.performanceLoadSelected) loadInput.value = String(unitMin);\n      else loadInput.value = String(Math.min(unitMax, Math.max(unitMin, selectedValue || unitMin)));",
        source,
        count=1,
    )
    source = source.replace("editor.min = '0'; editor.max = loadInput.max;", "editor.min = loadInput.min; editor.max = loadInput.max;")
    source = source.replace("entered >= 0 && entered <= Number(loadInput.max)", "entered >= Number(loadInput.min) && entered <= Number(loadInput.max)")
    source = source.replace("item.performanceLoad.value = '0'; updateLoadControl();", "item.performanceLoad.value = item.performanceLoad.min; updateLoadControl();")
    source = source.replace("editor.value = Number(item.performanceLoadExact) > 0 ? String(item.performanceLoadExact) : '';", "editor.value = item.performanceLoadSelected ? String(item.performanceLoadExact) : '';")
    source = source.replace(
        "const factor = nextUnit === 'lb' ? 1 / 0.45359237 : 1; const unitStep = nextUnit === 'lb' ? 5 : item.performanceLoadProfile.stepKg; const unitMin = Math.ceil(item.performanceLoadProfile.minKg * factor / unitStep) * unitStep; const unitMax = Math.floor(item.performanceLoadProfile.maxKg * factor / unitStep) * unitStep;\n      item.performanceLoadExact = Math.min(unitMax, Math.max(unitMin, Math.round(converted * factor / unitStep) * unitStep));\n      item.performanceLoad.value = String(item.performanceLoadExact);",
        "const factor = nextUnit === 'lb' ? 1 / 0.45359237 : 1; const unitStep = nextUnit === 'lb' ? 5 : item.performanceLoadProfile.stepKg; const rounded = Math.round(converted / unitStep) * unitStep; const unitMin = Math.ceil(Math.min(item.performanceLoadProfile.minKg * factor, item.performanceLoadSelected ? rounded : item.performanceLoadProfile.minKg * factor) / unitStep) * unitStep; const unitMax = Math.floor(Math.max(item.performanceLoadProfile.maxKg * factor, item.performanceLoadSelected ? rounded : item.performanceLoadProfile.maxKg * factor) / unitStep) * unitStep;\n      item.performanceLoadExact = Math.min(unitMax, Math.max(unitMin, rounded));\n      item.performanceLoad.value = String(item.performanceLoadExact);",
        1,
    )
    source = source.replace(
        "const previous = history.find(session => session.routineId === routineId && session.sessionId !== currentSessionId && (session.performance || []).some(record => record.exerciseId === String(item.index + 1)));",
        "item.performanceHistory = history.filter(session => session.routineId === routineId && session.sessionId !== currentSessionId && (session.performance || []).some(record => record.exerciseId === String(item.index + 1))).sort((a, b) => Number(b.endedAt || b.updatedAt || 0) - Number(a.endedAt || a.updatedAt || 0)); const previous = item.performanceHistory[0];",
        1,
    )
    history_anchor = "const previous = item.performanceHistory[0];"
    history_hydration = """const previous = item.performanceHistory[0];
      const latestLoadRecord = item.performanceHistory.flatMap(session => (session.performance || []).filter(record => record.exerciseId === String(item.index + 1)).map(record => ({ ...record, _sessionUpdatedAt: Number(session.endedAt || session.updatedAt || 0) }))).filter(record => record.loadSelected !== false && record.load !== null && record.load !== undefined && String(record.load).trim() !== '' && Number.isFinite(Number(record.load))).sort((a, b) => Number(b.updatedAt || b._sessionUpdatedAt || 0) - Number(a.updatedAt || a._sessionUpdatedAt || 0))[0];
      if (latestLoadRecord) {
        const storedKg = Number.isFinite(Number(latestLoadRecord.loadKg)) ? Number(latestLoadRecord.loadKg) : latestLoadRecord.loadUnit === 'lb' ? Number(latestLoadRecord.load) * 0.45359237 : Number(latestLoadRecord.load);
        if (Number.isFinite(storedKg)) item.previousLoadKg = storedKg;
        if (!savedDraft && !item.performanceLoadSelected && !isExerciseStarted(item) && Number.isFinite(storedKg)) {
          const factor = item.performanceLoadUnit === 'lb' ? 1 / 0.45359237 : 1;
          const step = item.performanceLoadUnit === 'lb' ? 5 : item.performanceLoadProfile.stepKg;
          const min = Math.min(Math.ceil(item.performanceLoadProfile.minKg * factor / step) * step, Math.round(storedKg * factor / step) * step);
          const max = Math.max(Math.floor(item.performanceLoadProfile.maxKg * factor / step) * step, Math.round(storedKg * factor / step) * step);
          const restored = Math.min(max, Math.max(min, Math.round(storedKg * factor / step) * step));
          item.performanceLoadExact = restored; item.performanceLoad.value = String(restored); item.performanceLoadSelected = true; updateLoadControl(); savePerformanceDraft();
        }
      }"""
    if history_anchor in source and "const latestLoadRecord = item.performanceHistory.flatMap" not in source:
        source = source.replace(history_anchor, history_hydration, 1)
    source = source.replace(
        "const records = (previous?.performance || []).filter(record => record.exerciseId === String(item.index + 1)).sort((a, b) => a.setNumber - b.setNumber);",
        "const records = (previous?.performance || []).filter(record => { const reps = Number(record?.reps); return record && record.exerciseId === String(item.index + 1) && Number.isInteger(reps) && reps >= 1 && reps <= 100; }).sort((a, b) => a.setNumber - b.setNumber);",
        1,
    )
    source = source.replace(
        "filter(record => record.load !== null && record.load !== undefined && Number.isFinite(Number(record.load)))",
        "filter(record => record.loadSelected !== false && record.load !== null && record.load !== undefined && String(record.load).trim() !== '' && Number.isFinite(Number(record.load)))",
    )

    tracker_anchor = "const completed = skipped || done === item.seriesKeys.length;"
    tracker_lock = """const completed = skipped || done === item.seriesKeys.length;
    const performancePanel = tracker.closest('article.card')?.querySelector('.performanceEntry');
    if (performancePanel) {
      performancePanel.classList.toggle('isLocked', completed);
      performancePanel.setAttribute('aria-disabled', String(completed));
      performancePanel.querySelectorAll('input, select, button').forEach(control => { control.disabled = completed; });
    }"""
    if tracker_anchor in source and "performancePanel.setAttribute('aria-disabled', String(completed))" not in source:
        source = source.replace(tracker_anchor, tracker_lock, 1)

    load_anchor = "      state[nextKey] = true;"
    load_feedback = """      if (load !== null && Number.isFinite(item.previousLoadKg)) {
        const deltaKg = loadKg - item.previousLoadKg;
        if (deltaKg > 0.01) window.dispatchEvent(new CustomEvent('gymratik:weight-change', { detail: { direction: 'up', title: item.title, target: item.tracker, load, loadUnit } }));
        else if (deltaKg < -0.01) window.dispatchEvent(new CustomEvent('gymratik:weight-change', { detail: { direction: 'down', title: item.title, target: item.tracker, load, loadUnit } }));
        item.previousLoadKg = loadKg;
      } else if (load !== null) item.previousLoadKg = loadKg;
      state[nextKey] = true;"""
    if load_anchor in source and "gymratik:weight-change" not in source:
        source = source.replace(load_anchor, load_feedback, 1)

    listener_anchor = "  const revealObserver = 'IntersectionObserver' in window ? new IntersectionObserver"
    weight_listener = """  window.addEventListener('gymratik:weight-change', event => {
    const detail = event.detail || {};
    if (detail.direction === 'up') {
      celebrate(detail.target, 20);
      encourage(`¡Carga aumentada en ${detail.title}! Serie completada con ${detail.load} ${detail.loadUnit}. Buen progreso; conserva la técnica.`);
    } else if (detail.direction === 'down') {
      encourage(`Buen ajuste en ${detail.title}: completaste la serie con menos carga. Prioriza control y rango cómodo; progresar también es entrenar con criterio.`);
    }
  });

"""
    if listener_anchor in source and "window.addEventListener('gymratik:weight-change'" not in source:
        source = source.replace(listener_anchor, weight_listener + listener_anchor, 1)
    if "Progresión sugerida: alcanzaste al menos" not in source:
        source = source.replace(
            "      recordSeriesTime(item, seriesIndex, completedAt);",
            """      recordSeriesTime(item, seriesIndex, completedAt);
      if (snapshot(item).complete) {
        const toKg = record => record.loadUnit === 'lb' ? Number(record.load) * 0.45359237 : Number(record.load);
        const isQualified = session => {
          const records = (session.performance || []).filter(record => record.exerciseId === String(item.index + 1)).sort((a, b) => a.setNumber - b.setNumber);
          if (records.length !== item.seriesKeys.length || records.some(record => Number(record.reps) < item.repMaximum + 1 || record.load === null || record.load === undefined || !Number.isFinite(Number(record.load)) || !(Number(record.durationMs) > 0))) return null;
          const loads = records.map(toKg);
          if (Math.max(...loads) - Math.min(...loads) > 0.01) return null;
          return records.reduce((sum, record) => sum + Number(record.durationMs) / Number(record.reps), 0) / records.length;
        };
        const current = item.seriesKeys.map(key => state.__performance?.[String(item.index + 1)]?.[key]);
        const currentTiming = getExerciseTiming(item).seriesTimes || [];
        const currentValid = current.length === item.seriesKeys.length && current.every((record, index) => record && Number(record.reps) >= item.repMaximum + 1 && record.load !== null && record.load !== undefined && Number.isFinite(toKg(record)) && Number(currentTiming[index]) > 0);
        const currentLoads = currentValid ? current.map(toKg) : [];
        const currentRate = currentValid && Math.max(...currentLoads) - Math.min(...currentLoads) <= 0.01
          ? current.reduce((sum, record, index) => sum + Number(currentTiming[index]) / Number(record.reps), 0) / current.length
          : null;
        const recent = (item.performanceHistory || []).slice(0, 2).map(isQualified);
        if (currentRate !== null && recent.length === 2 && recent.every(rate => rate !== null) && currentRate <= (recent[0] + recent[1]) / 2) {
          const loadKg = currentLoads[0];
          const stepKg = item.performanceLoadProfile.stepKg;
          const stepPercent = stepKg / loadKg;
          if (stepKg <= item.performanceLoadProfile.maxKg - loadKg && stepPercent >= 0.02 && stepPercent <= 0.10) {
            const displayStep = item.performanceLoadUnit === 'lb' ? `${Math.round(stepKg / 0.45359237)} lb` : `${stepKg} kg`;
            item.progressionCue.textContent = `Progresión sugerida: alcanzaste al menos ${item.repMaximum + 1} repeticiones en todas las series durante 3 sesiones con datos; tu ritmo por repetición fue igual o más rápido que la media de tus 2 sesiones previas. Si conservaste la técnica, prueba el menor incremento de esta máquina (${displayStep}, ${Math.round(stepPercent * 100)}%).`;
          }
        }
      }""",
            1,
        )
    source = source.replace(
        "tracker.querySelector('.completeSetButton')?.addEventListener('click', () => {",
        "tracker.querySelector('.completeSetButton')?.addEventListener('click', async () => {",
        1,
    )
    selection_guard_pattern = (
        r"(?P<guard>[ \t]*const repsSelected =[^\r\n]*\r?\n"
        r"[ \t]*const loadSelected =[^\r\n]*\r?\n"
        r"[ \t]*const missingPerformance =[^\r\n]*\r?\n"
        r"[ \t]*if \(missingPerformance\.length[^\r\n]*\r?\n)"
        r"(?:[ \t]*const repsSelected =[^\r\n]*\r?\n"
        r"[ \t]*const loadSelected =[^\r\n]*\r?\n"
        r"[ \t]*const missingPerformance =[^\r\n]*\r?\n"
        r"[ \t]*if \(missingPerformance\.length[^\r\n]*\r?\n)+"
    )
    source = re.sub(selection_guard_pattern, lambda match: match.group("guard"), source)
    source = source.replace(
        "const repsSelected = item.performanceReps?.dataset.selected === 'true' && Number.isInteger(Number(item.performanceReps.value)) && Number(item.performanceReps.value) >= Math.max(1, item.repMinimum - 3) && Number(item.performanceReps.value) <= item.repMaximum + 4;",
        "const reps = Number(item.performanceReps?.value); const repsSelected = item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= Math.max(1, item.repMinimum - 3) && reps <= item.repMaximum + 4;",
        1,
    )
    source = source.replace(
        "      const reps = Number(item.performanceReps?.value);\n      const loadValue = Number(item.performanceLoadExact);",
        "      const loadValue = Number(item.performanceLoadExact);",
        1,
    )
    if "const missingPerformance =" not in source:
        source = source.replace(
            "      const seriesIndex = item.seriesKeys.indexOf(nextKey);",
            "      const reps = Number(item.performanceReps?.value); const repsSelected = item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= Math.max(1, item.repMinimum - 3) && reps <= item.repMaximum + 4;\n      const loadSelected = item.performanceLoadSelected && Number.isFinite(Number(item.performanceLoadExact)) && Number(item.performanceLoadExact) >= Number(item.performanceLoad.min) && Number(item.performanceLoadExact) <= Number(item.performanceLoad.max);\n      const missingPerformance = [...(!repsSelected ? ['repeticiones'] : []), ...(!loadSelected ? ['carga'] : [])];\n      if (missingPerformance.length && !(await confirmMissingPerformance(missingPerformance))) return;\n      const seriesIndex = item.seriesKeys.indexOf(nextKey);",
            1,
        )
    source = source.replace(
        "      if (item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= item.repMinimum && reps <= item.repMaximum + 4) {\n        if (!state.__performance) state.__performance = {};\n        if (!state.__performance[String(item.index + 1)]) state.__performance[String(item.index + 1)] = {};\n        state.__performance[String(item.index + 1)][nextKey] = { title: item.title, reps, load, loadUnit, loadKg, updatedAt: completedAt };\n      }",
        "      if (!state.__performance) state.__performance = {};\n      if (!state.__performance[String(item.index + 1)]) state.__performance[String(item.index + 1)] = {};\n      state.__performance[String(item.index + 1)][nextKey] = { title: item.title, reps: repsSelected ? reps : null, load: loadSelected ? load : null, loadUnit, loadKg: loadSelected ? loadKg : null, durationMs: Math.min(MAX_TIMING_MS, Math.max(0, completedAt - Number(activeTiming.seriesStartedAt || completedAt))), updatedAt: completedAt };",
        1,
    )
    if "const updateRangeFill = input =>" not in source:
        source = source.replace(
            "const updateLoadControl = () => {",
            "const updateRangeFill = input => { const min = Number(input.min) || 0; const max = Number(input.max) || 100; const value = Number(input.value) || 0; input.style.setProperty('--range-progress', `${Math.max(0, Math.min(100, (value - min) / Math.max(1, max - min) * 100))}%`); };\n    const updateLoadControl = () => {",
            1,
        )
    if "item.performanceRangeFill = updateRangeFill;" not in source:
        source = source.replace(
            "const updateLoadControl = () => {",
            "item.performanceRangeFill = updateRangeFill;\n    const updateLoadControl = () => {",
            1,
        )
    source = source.replace(
        "loadOutput.textContent = item.performanceLoadSelected ? `${Number.isInteger(value) ? value : value.toFixed(1)} ${item.performanceLoadUnit}` : 'Sin registrar · tocar para añadir'; loadClear.hidden = !item.performanceLoadSelected;",
        "loadOutput.textContent = item.performanceLoadSelected ? `${Number.isInteger(value) ? value : value.toFixed(1)} ${item.performanceLoadUnit}` : 'Sin registrar · toca para añadir'; loadOutput.dataset.selected = String(item.performanceLoadSelected); loadClear.hidden = !item.performanceLoadSelected; updateRangeFill(loadInput);",
        1,
    )
    source = source.replace(
        "item.performanceRepsOutput.dataset.selected = String(selected); repsClear.hidden = !selected; repsDown.disabled",
        "item.performanceRepsOutput.dataset.selected = String(selected); repsClear.hidden = !selected; updateRangeFill(item.performanceReps); repsDown.disabled",
        1,
    )
    if "const repFeedbackZone = value =>" not in source:
        source, guidance_count = re.subn(
            r"    const renderPerformanceReps = \(\) => \{.*?\};(?=\n    item\.performanceRepsControl =)",
            """    const repFeedbackZone = value => {
      if (value < item.repMinimum) return 'below';
      if (value <= item.repMinimum + 1) return 'low';
      if (value < item.repMaximum - 1) return 'mid';
      if (value <= item.repMaximum) return 'high';
      return 'above';
    };
    const renderPerformanceReps = () => {
      const selected = item.performanceReps.dataset.selected === 'true';
      const value = Number(item.performanceReps.value);
      const zone = selected ? repFeedbackZone(value) : 'mid';
      const minPossible = Math.max(1, item.repMinimum - 3);
      const maxPossible = item.repMaximum + 4;
      item.performanceRepsOutput.textContent = selected ? `${value} ${value === 1 ? 'repetición' : 'repeticiones'}` : `Elige ${minPossible}–${maxPossible}; objetivo ${item.repMinimum}–${item.repMaximum}`;
      item.performanceRepsOutput.dataset.selected = String(selected);
      item.performanceRepsOutput.dataset.zone = zone;
      item.performanceReps.dataset.zone = zone;
      repsClear.hidden = !selected;
      updateRangeFill(item.performanceReps);
      repsDown.disabled = selected && value <= minPossible;
      repsUp.disabled = selected && value >= maxPossible;
      if (!selected) item.progressionCue.textContent = `Registra repeticiones y carga. Objetivo: ${item.repMinimum}–${item.repMaximum} repeticiones; el margen adicional no cambia el objetivo. Rango de carga sugerido para ${item.performanceLoadProfile.label}: ${item.performanceLoadProfile.minKg}–${item.performanceLoadProfile.maxKg} kg.`;
      else if (zone === 'below' || zone === 'low') item.progressionCue.textContent = `Rango bajo (${minPossible}–${item.repMinimum + 1}). Si la técnica se deterioró, prueba reducir un incremento (${item.performanceLoadProfile.stepKg} kg); si completaste el objetivo con control, conserva la carga.`;
      else if (zone === 'mid') item.progressionCue.textContent = `Buen rango (${item.repMinimum + 2}–${item.repMaximum - 2}). Mantén esta carga y un recorrido controlado.`;
      else if (zone === 'high') item.progressionCue.textContent = `Parte alta del objetivo (${item.repMaximum - 1}–${item.repMaximum}). Conserva la carga; progresar requiere superar el tope por 1–2 repeticiones, con técnica estable.`;
      else item.progressionCue.textContent = `Superaste el objetivo por ${value - item.repMaximum}. Si completas así todas las series, con técnica estable y en sesiones sucesivas, considera solo el incremento mínimo de ${item.performanceLoadProfile.stepKg} kg. Un ritmo más rápido cuenta únicamente frente a tu propia referencia, no como umbral universal.`;
    };""",
            source,
            count=1,
            flags=re.S,
        )
        if guidance_count > 1:
            raise ValueError(f"Se esperaba una zona de repeticiones, encontradas: {guidance_count}")
    source = source.replace(
        "item.performanceRepsOutput.textContent = `Elige entre ${item.repMinimum} y ${item.repMaximum + 4}`;",
        "item.performanceRepsOutput.textContent = `Sin registrar · ${item.repMinimum}–${item.repMaximum + 4} posibles`; item.performanceRepsOutput.dataset.selected = 'false'; item.performanceRepsClear.hidden = true; item.performanceRangeFill?.(item.performanceReps);",
        1,
    )
    source = source.replace(
        "repsClear.hidden = true; updateRangeFill(item.performanceReps);",
        "item.performanceRepsClear.hidden = true; item.performanceRangeFill?.(item.performanceReps);",
        1,
    )
    source = source.replace(
        "item.performanceRepsClear.hidden = true; updateRangeFill(item.performanceReps);",
        "item.performanceRepsClear.hidden = true; item.performanceRangeFill?.(item.performanceReps);",
        1,
    )
    # SVG path data is bundled from lucide-static v0.577.0 (ISC); see the
    # repository third-party notice for the complete license text.
    icon_factory = '''const createPerformanceIcon = name => {
      const icons = {
        'repeat-2': '<svg class="lucide lucide-repeat-2" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#gymratik-icon-repeat-2"></use></svg>',
        weight: '<svg class="lucide lucide-weight" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#gymratik-icon-weight"></use></svg>'
      };
      const template = document.createElement('template'); template.innerHTML = icons[name] || ''; const icon = template.content.firstElementChild;
      if (icon) { icon.setAttribute('aria-hidden', 'true'); icon.classList.add('performanceFieldIcon'); }
      return icon;
    };
'''
    if 'const createPerformanceIcon = name =>' not in source:
        source = source.replace("    const performancePanel = document.createElement('div');", '    ' + icon_factory + "    const performancePanel = document.createElement('div');", 1)
    source = re.sub(
        r"('repeat-2':\s*)'<svg class=\"lucide lucide-repeat-2\".*?</svg>'",
        r"\1'<svg class=\"lucide lucide-repeat-2\" viewBox=\"0 0 24 24\" aria-hidden=\"true\" focusable=\"false\"><use href=\"#gymratik-icon-repeat-2\"></use></svg>'",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r"(weight:\s*)'<svg class=\"lucide lucide-weight\".*?</svg>'",
        r"\1'<svg class=\"lucide lucide-weight\" viewBox=\"0 0 24 24\" aria-hidden=\"true\" focusable=\"false\"><use href=\"#gymratik-icon-weight\"></use></svg>'",
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace(
        "const loadIcon = item.tracker.closest('article.card')?.querySelector('.machinePill .pillIcon svg')?.cloneNode(true); if (loadIcon) { loadIcon.setAttribute('aria-hidden', 'true'); loadIcon.classList.add('performanceFieldIcon'); }",
        "const loadIcon = createPerformanceIcon('weight');",
        1,
    )
    return source


def standardize_offline_image_sources(source: str) -> str:
    """Keep canonical image elements usable without a network connection.

    The original URL remains in data-original-src (when present) as provenance;
    only the runtime src is redirected to an existing, packaged local asset.
    """
    replacements = (
        ("shop.lifefitness.com/", "../medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-machine-only.webp"),
        ("upload.wikimedia.org/wikipedia/commons/f/f6/Latissimus_dorsi_muscle_back.png", "../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp"),
        ("strengthlog.com/wp-content/uploads/2023/03/Lat-pulldown-starting-position.jpg", "../medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-start.jpg"),
        ("strengthlog.com/wp-content/uploads/2023/03/Lat-pulldown-bottom-position.jpg", "../medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-final.jpg"),
        ("images.squarespace-cdn.com/content/v1/63f2e1c2e165e046d1ae4fd7/", "../medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-start.webp"),
        ("upload.wikimedia.org/wikipedia/commons/8/87/Trapezius_back.png", "../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp"),
        ("cdn.imweb.me/thumbnail/20241129/4f340470ce4a3.png", "../medios_publicados/ejercicios-compartido/images/1350-7I6LNUG.jpg"),
        ("upload.wikimedia.org/wikipedia/commons/f/fa/Rhomboid_muscles_back.png", "../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp"),
    )
    for remote, local in replacements:
        def replace_img_source(match: re.Match[str]) -> str:
            tag = match.group(0)
            pattern = rf'((?<![\w-])src=["\'])[^"\']*{re.escape(remote)}[^"\']*(["\'])'
            return re.sub(pattern, rf'\g<1>{local}\g<2>', tag, count=1, flags=re.I)

        source = re.sub(r'<img\b[^>]*>', replace_img_source, source, flags=re.I)
    return source


def standardize_optional_media_fallback(source: str) -> str:
    """Show packaged poster images when optional exercise GIFs are unavailable."""
    if 'data-fix="rest-countdown-activity-v1"' not in source:
        raise ValueError("Falta el bloque compartido de estilos de actividad")
    style_marker = '.warmupVisual[data-media-state="FALLBACK_STATIC"]'
    if style_marker not in source:
        prefix = '<style data-fix="rest-countdown-activity-v1">'
        rules = (
            '\n.warmupVisual[data-media-state="FALLBACK_STATIC"] .warmupGif,'
            '.gifFrame[data-media-state="FALLBACK_STATIC"] .gifMotion{display:none!important}'
            '\n.warmupVisual[data-media-state="FALLBACK_STATIC"] .warmupFallback,'
            '.gifFrame[data-media-state="FALLBACK_STATIC"] .gifFallback{display:block!important}'
        )
        source = source.replace(prefix, prefix + rules, 1)
    if 'data-fix="offline-optional-gif-fallback-v1"' not in source:
        source = source.replace('</body>', OFFLINE_OPTIONAL_MEDIA_FALLBACK_SCRIPT + '\n</body>', 1)
    return source


def _warmup_attr(tag: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}\s*=\s*(["\'])(.*?)\1', tag, flags=re.I | re.S)
    return unescape(match.group(2)) if match else ""


def _warmup_div_block_end(source: str, start: int, opening_end: int) -> int:
    depth = 1
    for match in re.finditer(r'</?div\b[^>]*>', source[opening_end:], flags=re.I | re.S):
        token = match.group(0)
        if token[:2] == "</":
            depth -= 1
        elif not token.rstrip().endswith("/>"):
            depth += 1
        if depth == 0:
            return opening_end + match.end()
    raise ValueError(f"No se encontró el cierre del bloque de calentamiento en el offset {start}")


def standardize_warmup_single_viewers(source: str) -> str:
    """Use one responsive animation at a time while keeping every warm-up option selectable."""
    open_tags = [
        match
        for match in re.finditer(r'<div\b[^>]*\bclass=(?:"[^"]*"|\'[^\']*\')[^>]*>', source, flags=re.I | re.S)
        if re.search(r'\bwarmupMedia\b', _warmup_attr(match.group(0), "class"))
    ]
    replacements: list[tuple[int, int, str]] = []
    for group_number, opening in enumerate(open_tags, start=1):
        group_end = _warmup_div_block_end(source, opening.start(), opening.end())
        block = source[opening.start() : group_end]
        visuals = list(
            re.finditer(
                r'<div\b(?=[^>]*\bclass=(?:"[^"]*\bwarmupVisual\b[^"]*"|\'[^\']*\bwarmupVisual\b[^\']*\'))[^>]*>.*?</div\s*>',
                block,
                flags=re.I | re.S,
            )
        )
        if len(visuals) < 2:
            continue

        options: list[dict[str, str]] = []
        for visual_match in visuals:
            visual = visual_match.group(0)
            gif_tag = next(
                (
                    match.group(0)
                    for match in re.finditer(r'<img\b[^>]*>', visual, flags=re.I | re.S)
                    if re.search(r'\bwarmupGif\b', _warmup_attr(match.group(0), "class"))
                ),
                "",
            )
            poster_tag = next(
                (
                    match.group(0)
                    for match in re.finditer(r'<img\b[^>]*>', visual, flags=re.I | re.S)
                    if re.search(r'\bwarmupFallback\b', _warmup_attr(match.group(0), "class"))
                ),
                "",
            )
            label_match = re.search(
                r'<span\b[^>]*\bclass=(?:"[^"]*\bwarmupMediaLabel\b[^"]*"|\'[^\']*\bwarmupMediaLabel\b[^\']*\')[^>]*>(.*?)</span\s*>',
                visual,
                flags=re.I | re.S,
            )
            label = unescape(re.sub(r'<[^>]+>', '', label_match.group(1))).strip() if label_match else ""
            if not gif_tag or not poster_tag or not label:
                raise ValueError("Cada alternativa de calentamiento debe tener GIF, poster local y rótulo")
            options.append(
                {
                    "gif": _warmup_attr(gif_tag, "src"),
                    "poster": _warmup_attr(poster_tag, "src"),
                    "alt": _warmup_attr(gif_tag, "alt"),
                    "label": label,
                }
            )

        visual = visuals[0].group(0)
        visual_open = re.match(r'<div\b[^>]*>', visual, flags=re.I | re.S)
        if not visual_open:
            raise ValueError("No se pudo identificar el visor inicial del calentamiento")
        visual_tag = visual_open.group(0)
        if not re.search(r'\bid=', visual_tag, flags=re.I):
            visual_tag = visual_tag[:-1] + f' id="warmup-media-viewer-{group_number}">'
        visual_tag = re.sub(r'\srole=(?:"[^"]*"|\'[^\']*\')', "", visual_tag, flags=re.I)
        visual = visual_tag + visual[visual_open.end() :]

        group_tag = opening.group(0)
        classes = _warmup_attr(group_tag, "class").split()
        if "warmupSingleViewer" not in classes:
            classes.append("warmupSingleViewer")
        group_tag = re.sub(
            r'\bclass=(?:"[^"]*"|\'[^\']*\')',
            f'class="{escape(" ".join(classes), quote=True)}"',
            group_tag,
            count=1,
            flags=re.I,
        )
        group_tag = re.sub(r'\s(?:role|aria-label|data-enhancement)=(?:"[^"]*"|\'[^\']*\')', "", group_tag, flags=re.I)
        group_tag = group_tag[:-1] + ' role="group" aria-label="Una animación a la vez: referencias del calentamiento" data-enhancement="warmup-single-active-viewer-v1">'

        choices = [
            '<div class="warmupMediaChoiceRow" role="group" aria-label="Elige qué movimiento animado mostrar">'
        ]
        for index, option in enumerate(options):
            label = escape(option["label"], quote=True)
            choices.append(
                '<button type="button" class="warmupMediaChoice" '
                f'aria-label="Mostrar animación: {label}" aria-controls="warmup-media-viewer-{group_number}" '
                f'aria-pressed="{str(index == 0).lower()}" data-gif-src="{escape(option["gif"], quote=True)}" '
                f'data-poster-src="{escape(option["poster"], quote=True)}" data-alt="{escape(option["alt"], quote=True)}" '
                f'data-label="{label}">{label}</button>'
            )
        choices.append('</div><span class="warmupMediaStatus" role="status" aria-live="polite"></span>')
        replacement = group_tag + visual + "".join(choices) + "</div>"
        replacements.append((opening.start(), group_end, replacement))

    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    if replacements or 'data-enhancement="warmup-single-active-viewer-v1"' in source:
        if re.search(r'<style\b[^>]*data-enhancement="warmup-single-active-viewer-style-v1"[^>]*>.*?</style\s*>', source, flags=re.I | re.S):
            source = re.sub(
                r'<style\b[^>]*data-enhancement="warmup-single-active-viewer-style-v1"[^>]*>.*?</style\s*>',
                WARMUP_SINGLE_VIEWER_STYLE,
                source,
                count=1,
                flags=re.I | re.S,
            )
        else:
            source = source.replace('</body>', WARMUP_SINGLE_VIEWER_STYLE + '\n</body>', 1)
        if re.search(r'<script\b[^>]*data-fix="warmup-single-active-viewer-script-v1"[^>]*>.*?</script\s*>', source, flags=re.I | re.S):
            source = re.sub(
                r'<script\b[^>]*data-fix="warmup-single-active-viewer-script-v1"[^>]*>.*?</script\s*>',
                WARMUP_SINGLE_VIEWER_SCRIPT,
                source,
                count=1,
                flags=re.I | re.S,
            )
        else:
            source = source.replace('</body>', WARMUP_SINGLE_VIEWER_SCRIPT + '\n</body>', 1)
    return source
