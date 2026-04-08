/* ================================
   clipboard.js — Paste button handler
   ================================ */

export function initClipboard() {
  const btn   = document.getElementById('pasteBtn');
  const input = document.getElementById('urlInput');

  btn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      input.value = text;
      input.focus();
    } catch {
      // Clipboard permission denied — just focus the input
      input.focus();
    }
  });
}
