(() => {
  const update = async () => {
    try {
      const response = await fetch('/api/status', { headers: { accept: 'application/json' } });
      if (!response.ok) return;
      const data = await response.json();
      const status = document.getElementById('live-status');
      const players = document.getElementById('live-players');
      const channels = document.getElementById('live-channels');
      if (status) {
        status.textContent = data.online ? 'ONLINE' : 'OFFLINE';
        status.classList.toggle('online', Boolean(data.online));
      }
      if (players) players.textContent = data.players === null || data.players === undefined
        ? '—'
        : Number(data.players).toLocaleString();
      if (channels) channels.textContent = `${Number(data.channels || 0)}/${Number(data.totalChannels || 0)}`;
    } catch {}
  };
  update();
  window.setInterval(update, 30000);
})();
