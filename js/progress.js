/* ================================
   progress.js — Progress bar controller
   ================================ */

const wrap  = () => document.getElementById('progressWrap');
const fill  = () => document.getElementById('progressFill');
const pct   = () => document.getElementById('progressPct');
const label = () => document.getElementById('progressLabel');

export function showProgress() {
  wrap().classList.add('show');
  setProgress(0, 'Starting...');
}

export function hideProgress() {
  wrap().classList.remove('show');
}

export function setProgress(value, text) {
  fill().style.width  = value + '%';
  pct().textContent   = value + '%';
  label().textContent = text;
}

/**
 * Runs a simulated multi-stage progress animation.
 * Replace with real backend progress events when wiring up the API.
 *
 * @param {Function} onComplete - called when simulation finishes
 */
export function runSimulatedProgress(onComplete) {
  const stages = [
    { pct: 15,  label: 'Fetching video info...',   delay: 600  },
    { pct: 35,  label: 'Extracting stream URL...',  delay: 1200 },
    { pct: 60,  label: 'Downloading...',            delay: 2000 },
    { pct: 85,  label: 'Processing file...',        delay: 2800 },
    { pct: 100, label: 'Ready!',                    delay: 3400 },
  ];

  showProgress();

  stages.forEach(({ pct: value, label: text, delay }) => {
    setTimeout(() => {
      setProgress(value, text);
      if (value === 100) {
        setTimeout(() => {
          hideProgress();
          onComplete?.();
        }, 800);
      }
    }, delay);
  });
}
