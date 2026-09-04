(() => {
  const routeSegment = String(window.location.pathname || '/').split('/').filter(Boolean)[0] || 'home';
  const routeClass = `site-${routeSegment.toLowerCase().replace(/[^a-z0-9-]/g, '-')}`;
  document.body.classList.add(routeClass);

  const nav = document.querySelector('.nav');
  const mobileMenu = document.querySelector('.mobileMenu');
  const mobileSummary = mobileMenu?.querySelector('summary');
  const siteTopbarMenu = document.querySelector('.siteTopbarMenu');

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

  const hydrateLiveAvatars = () => {
    document.querySelectorAll('img[data-live-avatar]').forEach((image) => {
      const liveUrl = String(image.dataset.liveAvatar || '').trim();
      if (!liveUrl || image.dataset.liveAvatarBound === '1') return;
      image.dataset.liveAvatarBound = '1';

      const probe = new Image();
      probe.decoding = 'async';
      probe.onload = () => {
        image.src = liveUrl;
        image.dataset.liveAvatarLoaded = '1';
      };
      probe.onerror = () => {
        image.dataset.liveAvatarFailed = '1';
      };
      probe.src = liveUrl;
    });
  };

  const bindPasswordToggles = () => {
    document.querySelectorAll('[data-password-toggle]').forEach((button) => {
      const targetId = String(button.getAttribute('data-password-toggle') || '').trim();
      const input = targetId ? document.getElementById(targetId) : null;
      if (!input || input.dataset.passwordToggleBound === '1') return;
      input.dataset.passwordToggleBound = '1';

      button.addEventListener('click', () => {
        const showing = input.type === 'text';
        input.type = showing ? 'password' : 'text';
        button.setAttribute('aria-pressed', String(!showing));
        button.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
        input.focus({ preventScroll: true });
      });
    });
  };

  const bindTopbarMenu = () => {
    if (!siteTopbarMenu) return;
    siteTopbarMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => { siteTopbarMenu.open = false; });
    });
    document.addEventListener('click', (event) => {
      if (!siteTopbarMenu.open || siteTopbarMenu.contains(event.target)) return;
      siteTopbarMenu.open = false;
    });
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !siteTopbarMenu.open) return;
      siteTopbarMenu.open = false;
      siteTopbarMenu.querySelector('summary')?.focus();
    });
  };

  syncNav();
  syncMobileState();
  hydrateLiveAvatars();
  bindPasswordToggles();
  bindTopbarMenu();
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
