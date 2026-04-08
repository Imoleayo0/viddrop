/* ================================
   platforms.js — Platform selector
   ================================ */

export function initPlatforms() {
  const platforms = document.querySelectorAll('.plat');

  platforms.forEach(p => {
    p.addEventListener('click', () => {
      platforms.forEach(x => x.classList.remove('active'));
      p.classList.add('active');
    });
  });
}

export function getSelectedPlatform() {
  const active = document.querySelector('.plat.active');
  return active ? active.dataset.p : null;
}
