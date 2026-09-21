// With the studio open in agent-browser:
// agent-browser eval --stdin < scripts/verify_research_browser.js
(async () => {
  const element = id => document.getElementById(id);
  const assert = (condition, message) => { if (!condition) throw Error(message); };
  const until = async predicate => {
    for (let attempt = 0; attempt < 100; attempt++) {
      if (predicate()) return;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    throw Error('Timed out waiting for research UI');
  };
  const originalFetch = window.fetch;
  const originalCreateURL = URL.createObjectURL;
  const originalClick = HTMLAnchorElement.prototype.click;
  const downloads = [];
  try {
    element('another').click();
    element('scenario-example').click();
    element('prompt').value += ' <img src=x onerror="window.evidenceExecuted=true">';
    element('composer').requestSubmit();
    await until(() => !element('json').disabled);
    assert(element('status').textContent.includes('complete'), 'Run did not complete');
    assert(document.querySelectorAll('.completed').length === 4, 'Missing completed tools');
    assert(element('chart').querySelectorAll('polyline').length === 2, 'Missing trajectories');
    assert(!element('source').querySelector('img') && !window.evidenceExecuted, 'Evidence rendered as HTML');
    URL.createObjectURL = blob => { downloads.push(blob); return originalCreateURL(blob); };
    HTMLAnchorElement.prototype.click = function () {}; // Inspect export bytes without OS downloads.
    element('json').click();
    element('brief').click();
    const bundle = JSON.parse(await downloads[0].text());
    assert(bundle.scenario.baseline.length === 90, 'Incomplete JSON artifact');
    assert((await downloads[1].text()).includes(bundle.run_id), 'Brief provenance mismatch');

    element('another').click();
    window.fetch = async () => new Response('', {status: 503});
    element('composer').requestSubmit();
    await until(() => !element('error').hidden);
    assert(element('error').textContent.includes('503'), 'Missing service failure feedback');
    assert(element('json').disabled, 'Stale artifact remained enabled');

    element('another').click();
    window.fetch = (_, options) => new Promise((resolve, reject) => {
      options.signal.addEventListener('abort', () => reject(new DOMException('Stopped', 'AbortError')));
    });
    element('composer').requestSubmit();
    element('stop').click();
    await until(() => element('status').textContent.includes('stopped'));
    assert(element('json').disabled, 'Stopped run exposed an artifact');
    assert(document.documentElement.scrollWidth <= innerWidth, 'Horizontal overflow');
    return 'PASS: scenario API → UI, literal evidence, chart, artifact bytes, 503 failure, stop, viewport';
  } finally {
    window.fetch = originalFetch;
    URL.createObjectURL = originalCreateURL;
    HTMLAnchorElement.prototype.click = originalClick;
    element('another').click();
  }
})();
