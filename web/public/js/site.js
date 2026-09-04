(() => {
  const nav = document.querySelector('.nav');
  const mobileMenu = document.querySelector('.mobileMenu');
  const mobileSummary = mobileMenu?.querySelector('summary');

  const syncNav = () => {
    if (!nav) return;
    nav.classList.toggle('navScrolled', window.scrollY > 12);
  };

  const closeMobileMenu = () => {
    if (!mobileMenu?.open) return;
    mobileMenu.open = false;
  };

  const syncMobileState = () => {
    if (!mobileSummary || !mobileMenu) return;
    mobileSummary.setAttribute('aria-expanded', String(Boolean(mobileMenu.open)));
  };

  syncNav();
  syncMobileState();
  window.addEventListener('scroll', syncNav, { passive: true });

  if (mobileMenu) {
    mobileMenu.addEventListener('toggle', syncMobileState);
    mobileMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', closeMobileMenu);
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeMobileMenu();
        mobileSummary?.focus();
      }
    });

    document.addEventListener('click', (event) => {
      if (!mobileMenu.open || mobileMenu.contains(event.target)) return;
      closeMobileMenu();
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 820) closeMobileMenu();
    });
  }
})();
