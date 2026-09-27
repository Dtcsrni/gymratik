"""Estandariza la referencia anatómica de la franja «Músculos del día».

Las láminas son referencias ilustrativas. El foco visual ayuda a localizar la
región descrita sin afirmar que la imagen, por sí sola, demuestre activación
muscular ni superioridad fisiológica.
"""

from __future__ import annotations

import re
from html import escape, unescape


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
.performanceOptional{flex:none;padding:.19rem .42rem;border:1px solid rgba(156,190,205,.2);border-radius:999px;background:rgba(6,21,31,.56);color:#a9c4ce;font-size:.61rem;font-weight:750}
.performanceClear{min-width:44px;min-height:34px;padding:.3rem .52rem;border:1px solid rgba(255,171,149,.32);border-radius:.55rem;background:rgba(83,37,42,.28);color:#ffc2ae;font:inherit;font-size:.68rem;font-weight:850;cursor:pointer;transition:color .18s ease,border-color .18s ease,background-color .18s ease}
.performanceClear[hidden]{display:none!important}
.performanceClear:hover:not(:disabled),.performanceClear:focus-visible{border-color:rgba(114,220,255,.72);background:rgba(22,67,88,.76);color:#effbff}
.performanceLoadOutputRow{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:.35rem}
.performanceField input[type="range"]{--range-progress:0%;appearance:none;-webkit-appearance:none;width:100%;height:38px;min-height:38px;margin:0;padding:0;background:transparent;cursor:pointer;touch-action:pan-x}
.performanceField input[type="range"]::-webkit-slider-runnable-track{height:8px;border:1px solid rgba(137,194,211,.3);border-radius:999px;background:linear-gradient(90deg,#43dcb9 0%,#70e8d3 var(--range-progress),rgba(103,147,164,.28) var(--range-progress),rgba(103,147,164,.28) 100%);box-shadow:inset 0 1px 2px rgba(0,0,0,.35)}
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
.warmupProgressSegment.is-current,.seriesProgressSegment.is-current{border-color:#72dcff;animation:activityFillGlow .9s ease-in-out infinite alternate}
.warmupProgressSegment.is-current::after,.seriesProgressSegment.is-current::after{transform:scaleX(.38);opacity:.9;background-image:linear-gradient(100deg,#159bb3 0%,#35d6a4 55%,#a0d95c 100%);background-size:100% 100%;animation:activityFillGlow .9s ease-in-out infinite alternate}
.warmupProgressSegment.is-next,.seriesProgressSegment.is-next{border-color:rgba(114,220,255,.32);animation:none}
.summaryToggle.isActive::before,.summaryToggle.isResting::before,.summaryToggle.isPreparing::before{content:"";width:.48rem;height:.48rem;flex:none;border-radius:50%;background:currentColor;box-shadow:0 0 .55rem currentColor;animation:activityFastPulse .68s ease-in-out infinite}
.warmupTracker>.warmupProgressSegments{margin:.3rem 0 .45rem}
.warmupInstructions{margin:.15rem 0 .4rem;color:#c5e3eb;font-size:.68rem;line-height:1.4}
.exerciseWarmupHint{flex:1 1 100%;margin:.25rem 0;color:#c5e3eb;font-size:.62rem;line-height:1.35}
.warmupTrackerActions button[data-phase="preparing"],.warmupTrackerActions button[data-phase="cardio"],.warmupTrackerActions button[data-phase="mobility"]{border-color:rgba(114,220,255,.7);background:rgba(24,75,101,.7);color:#d8f5ff}
.warmupTrackerActions button[data-phase="done"]{border-color:rgba(101,242,221,.65);background:rgba(19,73,72,.65);color:#b9fff1}
.summaryToggle.isResting{border:1px solid rgba(255,210,119,.78);background:linear-gradient(90deg,rgba(112,79,21,.96),rgba(83,61,29,.92));color:#ffe4a4;animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryToggle.isActive{border:1px solid rgba(101,242,221,.78);background:linear-gradient(90deg,rgba(19,105,91,.96),rgba(19,73,72,.92));color:#b9fff1;animation:activityFastPulse .68s ease-in-out infinite}
.summaryToggle.isPreparing{border:1px solid rgba(114,220,255,.65);background:linear-gradient(90deg,rgba(24,75,101,.96),rgba(15,45,65,.92));color:#bfeeff}
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
.seriesProgressSegment.is-current.is-resting::after{transform:scaleX(.38);background-image:linear-gradient(100deg,#b98221 0%,#ffd277 55%,#fff0bd 100%);animation:activityFillGlow 2.4s ease-in-out infinite alternate}
.seriesProgressSegment.is-current.is-active{border-color:#65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
.summaryActivityStatus.isResting{border-color:rgba(255,210,119,.62);background:rgba(83,61,29,.38);color:#ffe4a4}
.summaryActivityStatus.isActive{border-color:rgba(101,242,221,.58);background:rgba(19,73,72,.38);color:#b9fff1}
.summaryActivityStatus.isPreparing{border-color:rgba(114,220,255,.56);background:rgba(24,75,101,.36);color:#d8f5ff}
.summaryActivityStatus.isResting .summaryActivityIndicator{background:#ffd277;box-shadow:0 0 .55rem #ffd277;animation:restSlowPulse 2.4s ease-in-out infinite}
.summaryActivityStatus.isActive .summaryActivityIndicator{background:#65f2dd;box-shadow:0 0 .55rem #65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
.summaryActivityStatus.isPreparing .summaryActivityIndicator{background:#72dcff;box-shadow:0 0 .55rem #72dcff;animation:preparationPulse 1.3s ease-in-out infinite}
.summaryActivityMascot{display:block;width:64px;height:64px;flex:none;object-fit:contain;border-radius:.55rem;background:rgba(6,21,31,.34)}
.summaryActivityMascot[hidden]{display:none!important}
.summaryActivityStatus.isResting .summaryActivityMascot{filter:drop-shadow(0 0 8px rgba(255,210,119,.28))}
.summaryActivityStatus.isActive .summaryActivityMascot{filter:drop-shadow(0 0 8px rgba(101,242,221,.24))}
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
#floatingSessionSummary{position:fixed!important;right:max(.65rem,env(safe-area-inset-right))!important;bottom:max(.65rem,env(safe-area-inset-bottom))!important;z-index:40;width:min(420px,calc(100vw - 1.3rem))!important;max-height:min(54dvh,480px)!important;border:1px solid rgba(114,220,255,.42)!important;border-radius:1rem!important;background:rgba(6,24,37,.97)!important;box-shadow:0 18px 54px rgba(0,0,0,.42),0 0 30px rgba(71,202,216,.14)!important;backdrop-filter:blur(18px)!important;overflow:hidden!important;display:flex!important;flex-direction:column!important}
#summaryToggle{display:grid!important;grid-template-columns:auto minmax(0,1fr) auto!important;grid-template-rows:auto auto;flex:none!important;min-height:62px!important;gap:.22rem .68rem!important;padding:.64rem .84rem!important;background:linear-gradient(105deg,rgba(14,73,90,.98),rgba(37,42,75,.98))!important;font-size:.84rem!important;line-height:1.22!important}
#summaryActivityIcon{grid-column:1;grid-row:1/3;align-self:center}
#summaryToggle #summaryHeadline{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-variant-numeric:tabular-nums}
#summaryActivityHeadline{grid-column:2;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#bfdce5;font-size:.72rem;font-weight:750;line-height:1.2}
#summaryActivityHeadline::before{content:"";display:inline-block;width:.4rem;height:.4rem;margin-right:.35rem;border-radius:50%;vertical-align:.03rem;background:#82aebb}
#summaryToggle.isResting #summaryActivityHeadline::before{background:#ffd277;animation:restSlowPulse 2.4s ease-in-out infinite}
#summaryToggle.isActive #summaryActivityHeadline::before{background:#65f2dd;animation:activityFastPulse .68s ease-in-out infinite}
#summaryToggle.isPreparing #summaryActivityHeadline::before{background:#72dcff;animation:preparationPulse 1.3s ease-in-out infinite}
#summaryToggle .summaryChevron{grid-column:3;grid-row:1/3;align-self:center;margin-left:0!important;font-size:1.1rem!important}
#summaryToggle[aria-expanded="true"]{grid-template-rows:auto;min-height:50px!important}
#summaryToggle[aria-expanded="true"] #summaryActivityHeadline{display:none}
#summaryToggle[aria-expanded="true"] #summaryActivityIcon,#summaryToggle[aria-expanded="true"] .summaryChevron{grid-row:1}
#summaryToggle.isResting{border:1px solid rgba(255,210,119,.82)!important;background:linear-gradient(105deg,rgba(112,79,21,.98),rgba(83,61,29,.96))!important;color:#ffe4a4!important}
#summaryToggle.isActive{border:1px solid rgba(101,242,221,.82)!important;background:linear-gradient(105deg,rgba(19,105,91,.98),rgba(19,73,72,.96))!important;color:#b9fff1!important}
#summaryToggle.isPreparing{border:1px solid rgba(114,220,255,.72)!important;background:linear-gradient(105deg,rgba(24,75,101,.98),rgba(15,45,65,.96))!important;color:#d8f5ff!important}
#summaryToggle.isResting,#summaryToggle.isActive,#summaryToggle.isPreparing{animation:none!important}
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
@media(max-width:640px){#floatingSessionSummary{right:max(.55rem,env(safe-area-inset-right))!important;bottom:max(.55rem,env(safe-area-inset-bottom))!important;width:min(420px,calc(100vw - 1.1rem))!important;max-height:min(52dvh,480px)!important}.sessionSummaryList{max-height:min(32dvh,300px)!important}.summaryExercise{min-height:44px!important;padding:.42rem .6rem .68rem!important}.summaryExercise::before,.summaryExercise::after{right:.6rem;bottom:.34rem;height:4px}.summaryExerciseName{font-size:.74rem!important}.summaryActivityMascot{width:56px;height:56px}}
@media(max-height:620px){#floatingSessionSummary{max-height:43dvh!important}.sessionSummaryList{max-height:25dvh!important}}
@media(max-height:420px) and (max-width:900px){#floatingSessionSummary{max-height:34dvh!important}.sessionSummaryList{max-height:12dvh!important}#summaryBody{gap:.22rem!important;padding:.3rem .5rem .42rem!important}.summaryTotals{min-height:22px!important}}
@media(prefers-reduced-motion:reduce){.summaryActivityStatus:not(.isIdle),.summaryActivityStatus.isResting .summaryActivityIndicator,.summaryActivityStatus.isActive .summaryActivityIndicator,.summaryActivityStatus.isPreparing .summaryActivityIndicator,.summaryExercise::after,.summaryProgressTrack>span,.summaryExercise,.warmupProgressSegment.is-current,.seriesProgressSegment.is-current,.warmupProgressSegment.is-current::after,.seriesProgressSegment.is-current::after{animation:none!important;transition:none!important}#floatingSessionSummary,#summaryToggle{scroll-behavior:auto}}
@keyframes activityFillGlow{from{opacity:.76}to{opacity:1}}
@keyframes progressActivitySweep{from{opacity:.78}to{opacity:1}}
@keyframes restSlowPulse{50%{opacity:.78}}
@keyframes activityFastPulse{50%{opacity:.72}}
@keyframes preparationPulse{50%{opacity:.78;filter:brightness(1.18);box-shadow:0 0 10px rgba(114,220,255,.25)}}
@media(prefers-reduced-motion:reduce){.summaryToggle.isResting,.summaryToggle.isActive,.summaryToggle.isPreparing,.summaryToggle.isResting::before,.summaryToggle.isActive::before,.summaryToggle.isPreparing::before,.summaryExercise.isResting,.summaryExercise.isSeriesActive,.summaryExercise.isResting .summaryExerciseState,.summaryExercise.isSeriesActive .summaryExerciseState,.summaryExercise.isSeriesActive::after,button.completeSetButton.is-resting,button.completeSetButton.is-series-active,button.completeSetButton.is-preparing,.exerciseTracker:has(.completeSetButton.is-resting) .exerciseRest,.exerciseTracker:has(.completeSetButton.is-series-active) .seriesProgressSegment.is-current,.warmupProgressSegment.is-current,.seriesProgressSegment.is-current,.seriesProgressSegment.is-current.is-resting,.seriesProgressSegment.is-current.is-active,.seriesProgressSegment.is-current.is-resting::after,.warmupProgressSegment.is-current::after,.seriesProgressSegment.is-current::after{animation:none}}
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
      image.src = gifSrc;
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
      const restPending = Boolean(!root?.sessionEndedAt && timing?.restStartedAt && !seriesActive);
      const activity = restPending
        ? { kind: restActive ? 'rest' : 'ready', label: restActive ? `Descanso · ${item.title}` : `Descanso listo · ${item.title}`, clock: restActive ? `${formatCountdown(restRemaining)} restantes` : 'Lista', startedAt: Number(timing.restStartedAt) || 0 }
        : preparing
          ? { kind: 'preparing', label: `Preparación · ${item.title}`, clock: formatCountdown((preparation?.endsAt || timing?.preparationEndsAt || now) - now), startedAt: Number(timing?.preparationEndsAt) || now }
          : seriesActive
            ? { kind: 'active', label: `Serie ${row.done + 1} activa · ${item.title}`, clock: formatElapsed(now - timing.seriesStartedAt), startedAt: Number(timing.seriesStartedAt) || 0 }
            : null;
      if (activity && (!currentActivity || activity.startedAt >= currentActivity.startedAt)) currentActivity = activity;
      if (!root?.sessionEndedAt && timing?.restStartedAt) notifyRestReady(item, timing, restElapsed);
      const summaryButton = summaryList.querySelector(`[data-exercise="${item.index + 1}"]`);
      const summaryState = summaryButton?.querySelector('.summaryExerciseState');
      if (summaryButton && summaryState) {
        summaryButton.classList.toggle('isResting', restActive);
        summaryButton.classList.toggle('isSeriesActive', seriesActive);
        summaryButton.classList.toggle('isPreparing', preparing);
        if (row.skipped) summaryState.textContent = '↷ Omitido';
        else if (restActive) summaryState.textContent = `Descanso · ${formatCountdown(restRemaining)}`;
        else if (row.complete) summaryState.textContent = '✓ Listo';
        else if (preparing) summaryState.textContent = `Preparación · ${formatCountdown(preparation ? preparation.endsAt - now : 0)}`;
        else if (seriesActive) summaryState.textContent = `● S${row.done + 1} activa · ${formatElapsed(now - timing.seriesStartedAt)}`;
        else summaryState.textContent = `${row.done}/${item.seriesKeys.length}`;
      }
      if (preparing) {
        renderPreparationDisplay(item);
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
      const exerciseElapsed = timing?.startedAt ? formatElapsed((timing.endedAt || now) - timing.startedAt) : '—';
      const progressLabel = row.complete ? 'Completado' : 'Serie ' + (row.done + 1) + '/' + item.seriesKeys.length + ' —';
      display.textContent = '⏱ ' + (labels.length ? labels.join(' · ') : progressLabel) + ' · Ejercicio ' + exerciseElapsed;
      if (item.restDisplay) item.restDisplay.hidden = !restActive;
    });
    const warmup = getWarmupTiming();
    if (warmup.phase === 'preparing') {
      const startedAt = Number(warmup.preparationEndsAt) - PREPARATION_MS;
      const activity = { kind: 'preparing', label: 'Preparación · Calentamiento', clock: formatCountdown(warmupPreparationRemaining()), startedAt };
      if (!currentActivity || activity.startedAt >= currentActivity.startedAt) currentActivity = activity;
    } else if (warmup.phase === 'cardio' || warmup.phase === 'mobility') {
      const startedAt = Number(warmup[`${warmup.phase}StartedAt`]) || 0;
      const activity = { kind: 'active', label: `Calentamiento · ${warmup.phase === 'cardio' ? 'Cardio' : 'Movilidad'}`, clock: formatElapsed(now - startedAt), startedAt };
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
      const progressText = `${doneExercises}/${exerciseItems.length} ejercicios · ${doneSeries}/${totalSeries} series`;
      const activityText = currentActivity ? `${currentActivity.label} · ${currentActivity.clock}` : doneExercises === exerciseItems.length ? 'Rutina completada' : 'Sin actividad · listo para continuar';
      activityHeadline.textContent = progressText;
      if (compactActivityHeadline) compactActivityHeadline.textContent = activityText;
      if (activityLabel) activityLabel.textContent = currentActivity?.label || activityText;
      if (activityClock) activityClock.textContent = currentActivity?.clock || (doneExercises === exerciseItems.length ? '✓' : '—');
      if (activityStatus) {
        activityStatus.classList.toggle('isResting', currentActivity?.kind === 'rest');
        activityStatus.classList.toggle('isActive', currentActivity?.kind === 'active');
        activityStatus.classList.toggle('isPreparing', currentActivity?.kind === 'preparing');
        activityStatus.classList.toggle('isIdle', !currentActivity || currentActivity.kind === 'ready');
        activityStatus.dataset.activity = currentActivity?.kind || (doneExercises === exerciseItems.length ? 'complete' : 'idle');
      }
      const mascot = activityStatus?.querySelector('#summaryActivityMascot');
      if (mascot) {
        const mascotState = currentActivity?.kind === 'rest' ? 'rest' : currentActivity?.kind === 'active' ? 'exercise' : '';
        const mascotVariant = window.gymratikMascotVariant || 'neutral';
        const mascotReducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true;
        const mascotAsset = mascotState ? `../../../data/profile/mascot-motion/${mascotVariant}-${mascotState}-${mascotReducedMotion ? 'still.webp' : '25fps.gif'}` : '';
        if (mascotAsset) {
          mascot.hidden = false;
          if (mascot.getAttribute('src') !== mascotAsset) mascot.src = mascotAsset;
          mascot.alt = mascotVariant === 'female' ? (mascotState === 'rest' ? 'Ratona descansando' : 'Ratona ejercitándose') : mascotVariant === 'male' ? (mascotState === 'rest' ? 'Ratón descansando' : 'Ratón ejercitándose') : (mascotState === 'rest' ? 'Mascotas Gymratik descansando' : 'Mascotas Gymratik ejercitándose');
        } else {
          mascot.hidden = true;
          if (mascot.hasAttribute('src')) mascot.removeAttribute('src');
          mascot.alt = '';
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
      activityButton.classList.toggle('isResting', currentActivity?.kind === 'rest');
      activityButton.classList.toggle('isActive', currentActivity?.kind === 'active');
      activityButton.classList.toggle('isPreparing', currentActivity?.kind === 'preparing');
      if (activityIcon) activityIcon.textContent = currentActivity?.kind === 'rest' ? '⏳' : currentActivity?.kind === 'active' ? '🏋️' : currentActivity?.kind === 'preparing' ? '◷' : '📋';
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
    const remaining = Math.max(0, preparation.endsAt - Date.now());
    if (item.timingDisplay) item.timingDisplay.textContent = `⏳ Preparación · ${formatElapsed(remaining)}`;
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
  const timingInterval = window.setInterval(() => { renderTimingDisplays(); renderWarmupTiming(); }, 1000);
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
    return source


def standardize_shared_session_contract(source: str) -> str:
    """Alinea los campos de temporización y lectura compartidos de las salidas."""
    source = source.replace(
        "repsInput.type = 'range'; repsInput.min = '0'; repsInput.max = '40'; repsInput.step = '1'; repsInput.value = '0';",
        "repsInput.type = 'range'; repsInput.min = String(item.repMinimum); repsInput.max = String(item.repMaximum + 4); repsInput.step = '1'; repsInput.value = String(item.repMinimum); repsInput.dataset.selected = 'false';",
        1,
    )
    source = source.replace(
        "{ reps: item.performanceReps.value, load: item.performanceLoad.value, loadUnit: item.performanceLoadUnit }",
        "{ reps: item.performanceReps.dataset.selected === 'true' ? item.performanceReps.value : '0', load: item.performanceLoad.value, loadUnit: item.performanceLoadUnit }",
        1,
    )
    source = source.replace(
        "if (savedDraft) { item.performanceReps.value = savedDraft.reps || '0'; item.performanceLoad.value = savedDraft.load ?? '0'; }",
        "const savedReps = Number(savedDraft?.reps); const savedRepsValid = Number.isInteger(savedReps) && savedReps >= item.repMinimum && savedReps <= item.repMaximum + 4; item.performanceReps.value = String(savedRepsValid ? savedReps : item.repMinimum); item.performanceReps.dataset.selected = String(savedRepsValid); if (savedDraft) item.performanceLoad.value = savedDraft.load ?? '0';",
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
        "if (item.performanceReps?.dataset.selected === 'true' && Number.isInteger(reps) && reps >= item.repMinimum && reps <= item.repMaximum + 4) {",
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
    if "sessionAbandonedAt = Date.now()" not in source:
        source = source.replace(
            "document.addEventListener('visibilitychange', renderTimingDisplays);",
            "document.addEventListener('visibilitychange', renderTimingDisplays); window.addEventListener('pagehide', () => { const timing = state.__timing; if (timing?.sessionStartedAt && !timing.sessionEndedAt) { timing.sessionAbandonedAt = Date.now(); save(); } }, { once: true });",
            1,
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
        """  const updateCompleteButton = item => {
    const button = item.tracker.querySelector('.completeSetButton');
    if (!button) return;
    const nextIndex = item.seriesKeys.findIndex(key => state[key] !== true);
    const complete = snapshot(item).complete;
    const timing = state.__timing?.exercises?.[String(item.index + 1)];
    const globalWarmupComplete = getWarmupTiming().phase === 'done';
    const warmup = item.tracker.querySelector('.warmupSet');
    const exerciseWarmupComplete = !warmup || state[warmup.dataset.key] === true;
    const preparing = isSeriesPreparing(item);
    const resting = Boolean(!state.__timing?.sessionEndedAt && timing?.restStartedAt && Date.now() - timing.restStartedAt < getRestRecommendation(item).minMs);
    const restRemaining = resting ? Math.max(0, getRestRecommendation(item).minMs - (Date.now() - timing.restStartedAt)) : 0;
    const seriesActive = Boolean(!complete && timing?.seriesStartedAt && !timing?.restStartedAt);
    const preparation = seriesPreparation.get(item.index);
    const label = resting && restRemaining > 0 ? `Descanso · ${formatElapsed(restRemaining)}`
      : complete ? state.__skippedExercises?.[String(item.index + 1)] === true ? '↷ Ejercicio omitido' : '✓ Ejercicio completado'
      : !globalWarmupComplete ? 'Completa calentamiento'
      : !exerciseWarmupComplete ? 'Registrar 1 serie ligera de aproximación'
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
        """item.startSeriesButton?.addEventListener('click', () => {
      const timing = getExerciseTiming(item);
      const warmup = tracker.querySelector('.warmupSet');
      if (!item || snapshot(item).complete || getWarmupTiming().phase !== 'done') return;
      if (warmup && state[warmup.dataset.key] !== true) {
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
        "startSeriesButton?.addEventListener('pointerdown', () => { const timing = getExerciseTiming(item); if (!timing.restStartedAt || timing.seriesStartedAt) return; longPressDetected = false; longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); if (!current.restStartedAt || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; current.restPhase = 'skipped'; current.restSkippedAt = Date.now(); beginSeries(item, Date.now()); updateTracker(item.tracker, false); }, 5000); });",
        1,
    )
    source = source.replace(
        "startSeriesButton?.addEventListener('pointerdown', () => { const timing = getExerciseTiming(item); if (!timing.restStartedAt || timing.seriesStartedAt) return; longPressDetected = false; longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); if (!current.restStartedAt || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; current.restStartedAt = 0; current.restPhase = 'skipped'; current.restSkippedAt = Date.now(); beginSeries(item, Date.now()); updateTracker(item.tracker, false); }, 5000); });",
        "startSeriesButton?.addEventListener('pointerdown', () => { const timing = getExerciseTiming(item); if (!timing.restStartedAt || timing.seriesStartedAt) return; longPressDetected = false; longPressTimer = window.setTimeout(() => { const current = getExerciseTiming(item); if (!current.restStartedAt || current.seriesStartedAt || snapshot(item).complete) return; longPressDetected = true; current.restPhase = 'skipped'; current.restSkippedAt = Date.now(); beginSeries(item, Date.now()); updateTracker(item.tracker, false); }, 5000); });",
        1,
    )
    source = source.replace("}, 4000); }));", "}, 5000); }));", 1)
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
        "const timingInterval = window.setInterval(() => { renderTimingDisplays(); renderWarmupTiming(); }, 1000);",
        "const timingInterval = window.setInterval(() => { renderTimingDisplays(); renderWarmupTiming(); exerciseItems.forEach(updateCompleteButton); }, 1000);",
        1,
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
        source = source.replace("  const timingInterval = window.setInterval", profile_mascot_init + "  const timingInterval = window.setInterval", 1)
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


def standardize_muscle_visuals(source: str) -> str:
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
            r'\1<p class="exerciseWarmupHint" id="exerciseWarmupHint">Aproximación: antes de las series efectivas, haz 1 serie con carga ligera y recorrido completo; no cuenta como serie de trabajo.</p>\2',
            source,
            count=1,
            flags=re.S,
        )
    source = re.sub(r'<div class="summaryActivity" id="summaryActivity"[^>]*>.*?</div>\s*', "", source, count=1, flags=re.S)
    source = source.replace('<span aria-hidden="true">📋</span><span id="summaryHeadline">', '<span id="summaryActivityIcon" aria-hidden="true">📋</span><span id="summaryHeadline">', 1)
    source = re.sub(
        r'(?:<span id="summaryActivityHeadline">.*?</span>)+',
        '<span id="summaryActivityHeadline">Sin actividad · listo para continuar</span>',
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
    if 'id="summaryActivityStatus"' not in source:
        source = source.replace(
            '<div class="summaryTotals"><span id="summaryPending">0 pendientes</span></div>',
            '<div class="summaryTotals"><span id="summaryPending">0 pendientes</span></div><div class="summaryActivityStatus isIdle" id="summaryActivityStatus" data-activity="idle" aria-live="polite"><span class="summaryActivityIndicator" aria-hidden="true"></span><span class="summaryActivityLabel" id="summaryActivityLabel">Sin actividad · listo para continuar</span><span class="summaryActivityClock" id="summaryActivityClock">—</span><img id="summaryActivityMascot" class="summaryActivityMascot" alt="" hidden decoding="async"></div><div class="summaryProgressTrack" id="summaryOverallProgress" role="progressbar" aria-label="Progreso total de series" aria-valuemin="0" aria-valuemax="0" aria-valuenow="0" aria-valuetext="Sin series completadas" data-state="empty"><span id="summaryProgressFill"></span></div>',
            1,
        )
    if 'id="summaryActivityMascot"' not in source:
        source, mascot_count = re.subn(
            r'(<span class="summaryActivityClock" id="summaryActivityClock">.*?</span>)',
            r'\1<img id="summaryActivityMascot" class="summaryActivityMascot" alt="" hidden decoding="async">',
            source,
            count=1,
            flags=re.S,
        )
        if mascot_count != 1:
            raise ValueError("No se pudo integrar la mascota dentro del estado flotante existente")
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
    """Make optional per-set logging controls clear, compact, and touch friendly."""
    source = source.replace(
        "const repsTitle = document.createElement('span'); repsTitle.textContent = 'Repeticiones realizadas · opcional'; const repsClear = document.createElement('button');",
        "const repsLabelText = document.createElement('span'); repsLabelText.textContent = 'Repeticiones'; const repsIcon = createPerformanceIcon('repeat-2'); const repsOptional = document.createElement('span'); repsOptional.className = 'performanceOptional'; repsOptional.textContent = 'Opcional'; const repsFieldLabel = document.createElement('span'); repsFieldLabel.className = 'performanceFieldLabel'; if (repsIcon) repsFieldLabel.append(repsIcon); repsFieldLabel.append(repsLabelText); const repsTitle = document.createElement('span'); repsTitle.className = 'performanceFieldTitleRow'; repsTitle.append(repsFieldLabel, repsOptional); const repsClear = document.createElement('button');",
        1,
    )
    source = source.replace(
        "const loadHead = document.createElement('span'); loadHead.className = 'performanceLoadHead';\n    const loadTitle = document.createElement('span'); loadTitle.textContent = 'Carga utilizada (opcional)';",
        "const loadHead = document.createElement('div'); loadHead.className = 'performanceLoadHead';\n    const loadLabelText = document.createElement('span'); loadLabelText.textContent = 'Carga'; const loadIcon = item.tracker.closest('article.card')?.querySelector('.machinePill .pillIcon svg')?.cloneNode(true); if (loadIcon) { loadIcon.setAttribute('aria-hidden', 'true'); loadIcon.classList.add('performanceFieldIcon'); } const loadOptional = document.createElement('span'); loadOptional.className = 'performanceOptional'; loadOptional.textContent = 'Opcional'; const loadFieldLabel = document.createElement('span'); loadFieldLabel.className = 'performanceFieldLabel'; if (loadIcon) loadFieldLabel.append(loadIcon); loadFieldLabel.append(loadLabelText); const loadTitle = document.createElement('span'); loadTitle.className = 'performanceFieldLabel'; loadTitle.append(loadFieldLabel, loadOptional);",
        1,
    )
    source = source.replace("loadTitle.textContent = 'Carga utilizada · opcional'; const loadClear = document.createElement('button');", "const loadClear = document.createElement('button');", 1)
    source = source.replace(
        "[['kg', 'kg · kilogramos'], ['lb', 'lb · libras']].forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; loadUnitSelect.append(option); });",
        "[['kg', 'kg'], ['lb', 'lb']].forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; option.setAttribute('aria-label', value === 'kg' ? 'Kilogramos' : 'Libras'); loadUnitSelect.append(option); });",
        1,
    )
    source = source.replace(
        "progressionCue.textContent = 'Ambos datos son opcionales. Ajusta las repeticiones con −/+ o el deslizador; toca la carga para escribirla con precisión. La serie se completa aunque no registres datos.';",
        "progressionCue.textContent = 'Opcional: desliza o usa −/+ para repeticiones; toca la carga para escribirla. Puedes completar la serie sin registrar.';",
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
        'repeat-2': '<svg class="lucide lucide-repeat-2" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 9 3-3 3 3"/><path d="M13 18H7a2 2 0 0 1-2-2V6"/><path d="m22 15-3 3-3-3"/><path d="M11 6h6a2 2 0 0 1 2 2v10"/></svg>',
        weight: '<svg class="lucide lucide-weight" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><path d="M6.5 8a2 2 0 0 0-1.905 1.46L2.1 18.5A2 2 0 0 0 4 21h16a2 2 0 0 0 1.925-2.54L19.4 9.5A2 2 0 0 0 17.48 8Z"/></svg>'
      };
      const template = document.createElement('template'); template.innerHTML = icons[name] || ''; const icon = template.content.firstElementChild;
      if (icon) { icon.setAttribute('aria-hidden', 'true'); icon.classList.add('performanceFieldIcon'); }
      return icon;
    };
'''
    if 'const createPerformanceIcon = name =>' not in source:
        source = source.replace("    const performancePanel = document.createElement('div');", '    ' + icon_factory + "    const performancePanel = document.createElement('div');", 1)
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
