(() => {
  let timer = null;

  const formatUpdatedTime = () => {
    try {
      return new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(new Date());
    } catch {
      return 'just now';
    }
  };

  const update = async () => {
    const refresh = document.getElementById('live-refresh');
    try {
      const response = await fetch('/api/status', {
        headers: { accept: 'application/json' },
        cache: 'no-store'
      });
      if (!response.ok) throw new Error(`status ${response.status}`);

      const data = await response.json();
      const status = document.getElementById('live-status');
      const players = document.getElementById('live-players');
      const channels = document.getElementById('live-channels');
      const dot = document.getElementById('live-dot');
      const stateLabel = document.getElementById('live-state-label');

      if (status) {
        status.textContent = data.online ? 'ONLINE' : 'OFFLINE';
        status.classList.toggle('online', Boolean(data.online));
      }
      if (players) {
        players.textContent = data.players === null || data.players === undefined
          ? '—'
          : Number(data.players).toLocaleString();
      }
      if (channels) channels.textContent = `${Number(data.channels || 0)}/${Number(data.totalChannels || 0)}`;
      if (dot) dot.classList.toggle('online', Boolean(data.online));
      if (stateLabel) stateLabel.textContent = data.online ? 'Open for adventure' : 'Currently unavailable';
      if (refresh) refresh.textContent = `Updated ${formatUpdatedTime()} · refreshes every 30 seconds`;
    } catch {
      if (refresh) refresh.textContent = 'Live refresh unavailable · showing the last known status';
    }
  };

  const start = () => {
    if (timer) window.clearInterval(timer);
    update();
    timer = window.setInterval(update, 30000);
  };

  start();
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) start();
  });
})();
