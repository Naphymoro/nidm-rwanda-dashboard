// Run via agent-browser eval --stdin on Studio, then on the returned Workbench
// link, then on the returned Academy link. Uses only synthetic evidence.
(async () => {
  const el=id=>document.getElementById(id);
  const assert=(condition,message)=>{if(!condition)throw Error(message);};
  const until=async predicate=>{for(let attempt=0;attempt<160;attempt++){if(predicate())return;await new Promise(resolve=>setTimeout(resolve,50));}throw Error('Timed out waiting for engine UI');};
  const bundle=async()=>{const response=await fetch(el('download-json').href);assert(response.ok,'Audit download failed');return response.json();};
  const page=document.body.dataset.page;
  await until(()=>el('workspace').options.length>0);
  if(page==='studio'){
    document.querySelector('[data-example="sensitivity"]').click();
    el('profile').value='economy';
    el('evidence').value+=' <img src=x onerror="window.evidenceExecuted=true">';
    el('experiment-form').requestSubmit();
    await until(()=>!el('run-section').hidden&&!el('start-run').disabled);
    assert(el('run-state').textContent==='planned','Plan ran without review');
    const plan=await bundle();
    assert(plan.execution.sensitivity_grid.length===3,'Wrong resource grid');
    assert(Object.keys(plan.outputs).length===0,'Plan executed tools implicitly');
    el('start-run').click();
    await until(()=>el('run-state').textContent==='completed');
    assert(document.querySelectorAll('.chart polyline').length===2,'Paired scenario chart missing');
    assert(!document.querySelector('.evidence-quote img')&&!window.evidenceExecuted,'Evidence executed as HTML');
    const result=await bundle();
    assert(result.outputs.sweep_2&&result.outputs.check.passed,'Sweep or checks missing');
    const brief=await (await fetch(el('download-brief').href)).text();
    assert(brief.includes(result.run_id),'Brief lacks provenance');
    el('review-note').value='Synthetic browser test: results need field calibration before policy use.';
    el('review-form').requestSubmit();
    await until(()=>el('review-status').textContent.startsWith('Review saved'));
    sessionStorage.setItem('engine-test-source',result.run_id);
    return {pass:'Studio: reviewed plan, real sweep, escaped evidence, chart, artifacts, review',next:el('open-workbench').href};
  }
  if(page==='workbench'){
    await until(()=>el('run-state').textContent==='completed');
    assert((await bundle()).run_id===sessionStorage.getItem('engine-test-source'),'Cross-route context lost');
    el('followup').click();
    assert(!el('experiment-editor').hidden&&el('model-details').open,'Direct experiment controls unavailable');
    el('skill').value='scenario';el('intervention').value='0';
    el('experiment-form').requestSubmit();
    await until(()=>!el('run-section').hidden&&!el('start-run').disabled);
    el('start-run').click();await until(()=>el('run-state').textContent==='completed');
    const result=await bundle();
    assert(JSON.stringify(result.outputs.baseline.trajectory)===JSON.stringify(result.outputs.intervention.trajectory),'Zero-intervention control differs');
    sessionStorage.setItem('engine-test-control',result.run_id);
    return {pass:'Workbench: same experiment restored, direct controls, new zero-intervention control',next:el('open-academy').href};
  }
  if(page==='academy'){
    await until(()=>document.querySelectorAll('.lesson-card').length===3);
    if(new URLSearchParams(location.search).has('run')){
      await until(()=>el('run-state').textContent==='completed');
      assert((await bundle()).run_id===sessionStorage.getItem('engine-test-control'),'Academy handoff lost the experiment');
    }
    document.querySelectorAll('.lesson-card')[1].click();
    assert(!el('lesson-detail').hidden,'Lesson instructions missing');
    el('experiment-form').requestSubmit();
    await until(()=>!el('run-section').hidden&&!el('start-run').disabled);
    el('start-run').click();await until(()=>el('run-state').textContent==='completed');
    assert(!el('learning-check').hidden,'Executed lesson has no check');
    document.querySelector('input[name=choice][value="0"]').checked=true;
    el('quiz-form').requestSubmit();await until(()=>el('quiz-feedback').textContent.startsWith('Try again'));
    document.querySelector('input[name=choice][value="1"]').checked=true;
    el('quiz-form').requestSubmit();await until(()=>el('quiz-feedback').textContent.startsWith('✓ Correct'));
    const result=await bundle();assert(result.lesson_check.correct,'Lesson progress not persisted');
    sessionStorage.setItem('engine-test-lesson',result.run_id);
    return {pass:'Academy: handoff, runnable lesson, wrong/correct feedback, persisted learning progress',reload:location.href};
  }
  throw Error('Open one of the new engine routes');
})()
