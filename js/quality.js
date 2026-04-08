/* ================================
   quality.js — Quality chip selector
   ================================ */

export function initQuality() {
  const chips = document.querySelectorAll('.q-chip');

  chips.forEach(q => {
    q.addEventListener('click', () => {
      chips.forEach(x => x.classList.remove('active'));
      q.classList.add('active');
    });
  });
}

export function getSelectedQuality() {
  const active = document.querySelector('.q-chip.active');
  return active ? active.dataset.q : null;
}
