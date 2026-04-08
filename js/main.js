/* ================================
   main.js — App entry point
   Boots all modules on DOMContentLoaded
   ================================ */

import { initPlatforms } from './platform.js';
import { initQuality }   from './quality.js';
import { initClipboard } from './clipboard.js';
import { initDownloader } from './downloader.js';

document.addEventListener('DOMContentLoaded', () => {
  initPlatforms();
  initQuality();
  initClipboard();
  initDownloader();
});
