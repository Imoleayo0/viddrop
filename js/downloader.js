/* ================================
   downloader.js — Core download handler
   ================================ */

import { getSelectedPlatform } from './platform.js';
import { getSelectedQuality } from './quality.js';
import { showProgress, setProgress, hideProgress } from './progress.js';

function resolveApiUrl() {
  const configuredUrl =
    window.VIDDROP_API_URL ||
    document.querySelector('meta[name="viddrop-api-url"]')?.content?.trim();

  if (configuredUrl) {
    return configuredUrl;
  }

  const isLocalHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  if (window.location.protocol.startsWith('http') && !isLocalHost) {
    return `${window.location.origin}/api/download`;
  }

  return 'viddrop-production-6131.up.railway.app';
}

const API_URL = resolveApiUrl();

const SPINNER_SVG = `
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       stroke-width="2" style="animation:spin 1s linear infinite">
    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83
             M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
  </svg>`;

const DEFAULT_BTN_HTML = `
  <svg width="18" height="18" fill="none" viewBox="0 0 24 24"
       stroke="currentColor" stroke-width="2.5">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
  Download Video`;

function setButtonLoading(btn) {
  btn.disabled      = true;
  btn.style.opacity = '0.6';
  btn.innerHTML     = SPINNER_SVG + ' Processing...';
}

function resetButton(btn) {
  btn.disabled      = false;
  btn.style.opacity = '';
  btn.innerHTML     = DEFAULT_BTN_HTML;
}

function flashInputError(input) {
  input.style.outline = '2px solid rgba(255,80,80,0.5)';
  input.focus();
  setTimeout(() => { input.style.outline = ''; }, 1500);
}

function triggerBrowserDownload(blob, res) {
  const filename = res.headers.get('content-disposition')
                     ?.split('filename=')[1]?.replace(/"/g, '')
                   || 'video.mp4';

  const blobUrl = URL.createObjectURL(blob);
  const a       = document.createElement('a');
  a.href        = blobUrl;
  a.download    = filename;
  a.click();
  URL.revokeObjectURL(blobUrl);
}

export function initDownloader() {
  const btn   = document.getElementById('dlBtn');
  const input = document.getElementById('urlInput');

  btn.addEventListener('click', async () => {
    const url      = input.value.trim();
    const platform = getSelectedPlatform();
    const quality  = getSelectedQuality();

    if (!url) {
      flashInputError(input);
      return;
    }

    console.log('[VidDrop] Download requested:', { url, platform, quality });

    setButtonLoading(btn);
    showProgress();
    setProgress(10, 'Connecting to server...');

    try {
      setProgress(30, 'Fetching video info...');

      const res = await fetch(API_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ url, platform, quality }),
      });

      setProgress(60, 'Downloading...');

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Download failed');
      }

      setProgress(85, 'Processing file...');
      const blob = await res.blob();

      setProgress(100, 'Done!');
      triggerBrowserDownload(blob, res);

      setTimeout(() => {
        hideProgress();
        resetButton(btn);
      }, 800);

    } catch (err) {
      console.error('[VidDrop] Error:', err);
      setProgress(0, `Error: ${err.message}`);
      setTimeout(() => {
        hideProgress();
        resetButton(btn);
      }, 3000);
    }
  });
}
