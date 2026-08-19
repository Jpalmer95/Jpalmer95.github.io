/**
 * JK Music Player — shared background-music system for the portfolio.
 *
 * Ported & enhanced from the SuperSonic WebXR game's RadioSystem
 * (github.com/Jpalmer95/SuperSonic). Decoupled from Three.js so the
 * exact same queue/playback engine powers both the flat site and the
 * immersive XR page.
 *
 * Loads an open-source track library directly from a GitHub repo
 * (jpalmer95/OpenMusic) via the GitHub Contents API, streams raw MP3s
 * through a plain HTMLAudioElement, and supports:
 *   - queue add / remove / reorder (up/down)
 *   - play / pause / next / prev
 *   - local MP3/WAV upload (Blob URLs, no CORS issues)
 *   - volume, shuffle, and localStorage persistence
 *
 * Exposes two globals:
 *   window.MusicPlayer  — the pure playback engine
 *   window.MusicDock    — a self-contained floating dock UI
 */
(function () {
  'use strict';

  const LS_KEY = 'jk-portfolio-music';

  class MusicPlayer {
    constructor(opts = {}) {
      this.owner = opts.owner || 'jpalmer95';
      this.repo = opts.repo || 'OpenMusic';
      this.audio = new Audio();
      this.audio.loop = false;
      this.audio.preload = 'auto';

      this.queue = [];
      this.currentIndex = -1;
      this.isPlaying = false;
      this.volume = 0.6;
      this.shuffle = false;
      this.library = [];      // tracks available from GitHub
      this.listeners = { trackchange: [], state: [] };

      this._restore();
      this.audio.volume = this.volume;

      this.audio.addEventListener('ended', () => this.playNext(true));
      this.audio.addEventListener('error', () => {
        if (this.audio.src && this.audio.src !== window.location.href) {
          this._emit('state');
          if (this.queue.length > 0) setTimeout(() => this.playNext(true), 800);
        }
      });
      this.audio.addEventListener('playing', () => { this.isPlaying = true; this._emit('state'); });
      this.audio.addEventListener('pause', () => { this.isPlaying = false; this._emit('state'); });

      this.fetchLibrary();
    }

    on(event, fn) { (this.listeners[event] || (this.listeners[event] = [])).push(fn); return this; }
    _emit(event) { (this.listeners[event] || []).forEach((fn) => { try { fn(this); } catch (e) {} }); }

    _restore() {
      try {
        const saved = JSON.parse(localStorage.getItem(LS_KEY) || '{}');
        if (typeof saved.volume === 'number') this.volume = Math.min(1, Math.max(0, saved.volume));
        if (typeof saved.shuffle === 'boolean') this.shuffle = saved.shuffle;
        // Only persist GitHub-hosted tracks (Blob URLs don't survive reload).
        if (Array.isArray(saved.queue)) {
          this.queue = saved.queue
            .filter((t) => t && t.url && /^https?:\/\//.test(t.url))
            .slice(0, 50);
        }
      } catch (e) { /* ignore */ }
    }
    _persist() {
      try {
        localStorage.setItem(LS_KEY, JSON.stringify({
          volume: this.volume,
          shuffle: this.shuffle,
          queue: this.queue.filter((t) => t.url && /^https?:\/\//.test(t.url)),
        }));
      } catch (e) { /* ignore */ }
    }

    async fetchLibrary() {
      try {
        const res = await fetch(
          `https://api.github.com/repos/${this.owner}/${this.repo}/contents/`
        );
        if (!res.ok) throw new Error('repo not found');
        const files = await res.json();
        this.library = files
          .filter((f) => f.name && /\.(mp3|wav|ogg|m4a)$/i.test(f.name))
          .map((f) => ({ name: f.name.replace(/\.[^.]+$/, ''), url: f.download_url }));
      } catch (e) {
        console.warn('[MusicPlayer] library fetch failed', e);
        this.library = [];
      }
      this._emit('state');
    }

    addToQueue(track) {
      if (!track || !track.url) return;
      this.queue.push({ name: track.name || 'Untitled', url: track.url, isBlob: track.isBlob || false });
      if (this.currentIndex === -1) { this.currentIndex = 0; this._load(0, false); }
      this._persist();
      this._emit('state');
    }

    addLocalFiles(fileList) {
      if (!fileList || !fileList.length) return;
      Array.from(fileList).forEach((file) => {
        if (!/\.(mp3|wav|ogg|m4a)$/i.test(file.name)) return;
        this.queue.push({ name: file.name.replace(/\.[^.]+$/, ''), url: URL.createObjectURL(file), isBlob: true });
      });
      if (this.currentIndex === -1) { this.currentIndex = 0; this._load(0, false); }
      this._emit('state');
    }

    removeFromQueue(index) {
      if (index < 0 || index >= this.queue.length) return;
      if (index === this.currentIndex) {
        this.audio.pause();
        this.queue.splice(index, 1);
        if (this.queue.length === 0) this.currentIndex = -1;
        else { if (this.currentIndex >= this.queue.length) this.currentIndex = 0; this._load(this.currentIndex, false); }
      } else {
        this.queue.splice(index, 1);
        if (index < this.currentIndex) this.currentIndex--;
      }
      this._persist();
      this._emit('state');
    }

    moveQueueItem(index, direction) {
      const j = index + direction;
      if (index < 0 || j < 0 || j >= this.queue.length) return;
      const tmp = this.queue[index]; this.queue[index] = this.queue[j]; this.queue[j] = tmp;
      if (this.currentIndex === index) this.currentIndex = j;
      else if (this.currentIndex === j) this.currentIndex = index;
      this._persist();
      this._emit('state');
    }

    clearQueue() {
      this.audio.pause();
      this.queue = [];
      this.currentIndex = -1;
      this.isPlaying = false;
      this._persist();
      this._emit('state');
    }

    _load(index, autoplay) {
      if (index < 0 || index >= this.queue.length) return;
      this.currentIndex = index;
      const track = this.queue[index];
      this.audio.src = track.url;
      this._emit('trackchange');
      if (autoplay) { this.play(); }
      this._emit('state');
    }

    play() {
      if (this.queue.length === 0) return;
      if (this.currentIndex === -1) { this._load(0, false); }
      this.audio.play().catch((e) => console.warn('[MusicPlayer] play blocked', e));
      this._emit('state');
    }

    pause() { this.audio.pause(); this._emit('state'); }

    toggle() {
      if (this.queue.length === 0) return;
      if (this.isPlaying) this.pause(); else this.play();
    }

    playTrack(index) { if (index >= 0 && index < this.queue.length) this._load(index, true); }

    playNext(auto = false) {
      if (this.queue.length === 0) return;
      if (this.shuffle && this.queue.length > 1) {
        let n;
        do { n = Math.floor(Math.random() * this.queue.length); } while (n === this.currentIndex);
        this._load(n, auto || this.isPlaying);
      } else {
        let n = this.currentIndex + 1;
        if (n >= this.queue.length) n = 0;
        this._load(n, auto || this.isPlaying);
      }
    }

    playPrev() {
      if (this.queue.length === 0) return;
      let n = this.currentIndex - 1;
      if (n < 0) n = this.queue.length - 1;
      this._load(n, true);
    }

    setVolume(v) {
      this.volume = Math.min(1, Math.max(0, v));
      this.audio.volume = this.volume;
      this._persist();
      this._emit('state');
    }

    toggleShuffle() { this.shuffle = !this.shuffle; this._persist(); this._emit('state'); }

    currentTrack() { return this.queue[this.currentIndex] || null; }
  }

  // ---------------------------------------------------------------------------
  // Floating dock UI (self-contained: injects its own stylesheet).
  // ---------------------------------------------------------------------------
  class MusicDock {
    constructor(player) {
      this.player = player;
      this.open = false;
      this._injectStyles();
      this._buildDOM();
      player.on('state', () => this._render());
      player.on('trackchange', () => this._render());
      this._render();
    }

    _injectStyles() {
      if (document.getElementById('jk-music-dock-css')) return;
      const css = `
        .jk-music-dock { position: fixed; right: 18px; bottom: 18px; z-index: 9999; font-family: Inter, system-ui, sans-serif; }
        .jk-music-dock * { box-sizing: border-box; }
        .jk-music-toggle { width: 52px; height: 52px; border-radius: 50%; background: linear-gradient(135deg,#007bff,#0056b3); color:#fff; border:none; cursor:pointer; font-size:22px; box-shadow: 0 8px 24px rgba(0,123,255,.4); display:flex; align-items:center; justify-content:center; transition: transform .2s; }
        .jk-music-toggle:hover { transform: scale(1.08); }
        .jk-music-toggle.playing { animation: jk-pulse 1.6s ease-in-out infinite; }
        @keyframes jk-pulse { 0%,100%{box-shadow:0 8px 24px rgba(0,123,255,.4)} 50%{box-shadow:0 8px 32px rgba(0,123,255,.8)} }
        .jk-music-panel { position: absolute; right:0; bottom:64px; width: 320px; max-height: 70vh; background: rgba(18,18,18,.96); border:1px solid rgba(255,255,255,.08); border-radius:14px; backdrop-filter: blur(12px); box-shadow: 0 16px 48px rgba(0,0,0,.6); display:none; flex-direction:column; overflow:hidden; }
        .jk-music-panel.open { display:flex; }
        .jk-music-head { padding:14px 16px; border-bottom:1px solid rgba(255,255,255,.08); display:flex; align-items:center; justify-content:space-between; }
        .jk-music-head h4 { margin:0; font-size:14px; color:#fff; letter-spacing:.3px; }
        .jk-music-close { background:none; border:none; color:#888; cursor:pointer; font-size:18px; }
        .jk-music-close:hover { color:#fff; }
        .jk-music-now { padding:10px 16px; color:#b3b3b3; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .jk-music-controls { display:flex; align-items:center; gap:8px; padding:0 16px 12px; }
        .jk-music-controls button { background:#2d2d2d; color:#fff; border:1px solid #444; border-radius:8px; padding:8px 10px; cursor:pointer; font-size:14px; }
        .jk-music-controls button:hover { background:#007bff; border-color:#007bff; }
        .jk-music-controls .jk-play { flex:1; font-weight:600; }
        .jk-music-controls .jk-shuf.on { background:#007bff; border-color:#007bff; }
        .jk-music-vol { display:flex; align-items:center; gap:8px; padding:0 16px 12px; color:#888; font-size:12px; }
        .jk-music-vol input { flex:1; accent-color:#007bff; }
        .jk-music-scroll { overflow-y:auto; padding:0 16px 16px; }
        .jk-music-scroll label { display:block; font-size:10px; text-transform:uppercase; letter-spacing:1px; color:#666; margin:10px 0 6px; }
        .jk-music-item { display:flex; align-items:center; justify-content:space-between; gap:8px; padding:8px 10px; border-radius:8px; background:#1e1e1e; margin-bottom:6px; cursor:pointer; font-size:12px; color:#e0e0e0; }
        .jk-music-item:hover { background:#2a2a2a; }
        .jk-music-item .jk-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .jk-music-item.playing { border-left:3px solid #007bff; color:#fff; }
        .jk-music-item .jk-acts { display:flex; gap:4px; }
        .jk-music-item .jk-acts button { background:#2d2d2d; border:1px solid #444; color:#aaa; border-radius:6px; width:24px; height:24px; cursor:pointer; font-size:12px; line-height:1; padding:0; }
        .jk-music-item .jk-acts button:hover { background:#007bff; color:#fff; border-color:#007bff; }
        .jk-music-add { background:#007bff !important; border-color:#007bff !important; color:#fff !important; }
        .jk-music-empty { color:#666; font-size:12px; text-align:center; padding:12px 0; }
        .jk-music-upload { background:#224444; border:1px solid #44aaaa; color:#9fe; border-radius:8px; padding:8px 10px; cursor:pointer; font-size:12px; width:100%; margin-top:4px; }
        .jk-music-upload:hover { background:#2a5555; }
      `;
      const style = document.createElement('style');
      style.id = 'jk-music-dock-css';
      style.textContent = css;
      document.head.appendChild(style);
    }

    _buildDOM() {
      const root = document.createElement('div');
      root.className = 'jk-music-dock';
      root.innerHTML = `
        <button class="jk-music-toggle" title="Music" aria-label="Open music player">♪</button>
        <div class="jk-music-panel">
          <div class="jk-music-head"><h4>Music</h4><button class="jk-music-close">✕</button></div>
          <div class="jk-music-now">—</div>
          <div class="jk-music-controls">
            <button data-act="prev" title="Previous">⏮</button>
            <button data-act="play" class="jk-play">Play</button>
            <button data-act="next" title="Next">⏭</button>
            <button data-act="shuffle" class="jk-shuf" title="Shuffle">🔀</button>
          </div>
          <div class="jk-music-vol"><span>Vol</span><input type="range" min="0" max="100" step="1"><span class="jk-music-volval">60</span></div>
          <div class="jk-music-scroll">
            <label>Library</label>
            <div data-role="library"></div>
            <label>Queue</label>
            <div data-role="queue"></div>
            <button class="jk-music-upload">📂 Upload MP3s</button>
            <input type="file" accept="audio/*" multiple style="display:none">
          </div>
        </div>`;
      document.body.appendChild(root);
      this.root = root;
      this.panel = root.querySelector('.jk-music-panel');
      this.toggleBtn = root.querySelector('.jk-music-toggle');
      this.toggleBtn.addEventListener('click', () => { this.open = !this.open; this._render(); });
      root.querySelector('.jk-music-close').addEventListener('click', () => { this.open = false; this._render(); });
      root.querySelector('[data-act="play"]').addEventListener('click', () => this.player.toggle());
      root.querySelector('[data-act="next"]').addEventListener('click', () => this.player.playNext());
      root.querySelector('[data-act="prev"]').addEventListener('click', () => this.player.playPrev());
      root.querySelector('[data-act="shuffle"]').addEventListener('click', () => this.player.toggleShuffle());
      const vol = root.querySelector('input[type="range"]');
      vol.addEventListener('input', () => this.player.setVolume(vol.value / 100));
      root.querySelector('.jk-music-upload').addEventListener('click', () => root.querySelector('input[type="file"]').click());
      root.querySelector('input[type="file"]').addEventListener('change', (e) => { this.player.addLocalFiles(e.target.files); e.target.value = ''; });
    }

    _render() {
      const p = this.player;
      const track = p.currentTrack();
      const now = this.root.querySelector('.jk-music-now');
      now.textContent = track ? `▶ ${track.name}` : (p.queue.length ? 'Ready' : 'Add a track to start listening');

      this.panel.classList.toggle('open', this.open);
      this.toggleBtn.classList.toggle('playing', p.isPlaying);
      this.root.querySelector('[data-act="play"]').textContent = p.isPlaying ? 'Pause' : 'Play';
      this.root.querySelector('[data-act="shuffle"]').classList.toggle('on', p.shuffle);
      const vol = this.root.querySelector('input[type="range"]');
      vol.value = Math.round(p.volume * 100);
      this.root.querySelector('.jk-music-volval').textContent = Math.round(p.volume * 100);

      // Library
      const lib = this.root.querySelector('[data-role="library"]');
      if (!p.library.length) {
        lib.innerHTML = '<div class="jk-music-empty">Loading library…</div>';
      } else {
        lib.innerHTML = p.library.map((t, i) => `
          <div class="jk-music-item">
            <span class="jk-name">${this._esc(t.name)}</span>
            <div class="jk-acts"><button class="jk-music-add" data-add="${i}">+</button></div>
          </div>`).join('');
        lib.querySelectorAll('[data-add]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); this.player.addToQueue(p.library[+b.dataset.add]); }));
      }

      // Queue
      const q = this.root.querySelector('[data-role="queue"]');
      if (!p.queue.length) {
        q.innerHTML = '<div class="jk-music-empty">Queue is empty</div>';
      } else {
        q.innerHTML = p.queue.map((t, i) => `
          <div class="jk-music-item ${i === p.currentIndex ? 'playing' : ''}">
            <span class="jk-name">${i + 1}. ${this._esc(t.name)}</span>
            <div class="jk-acts">
              <button data-up="${i}">↑</button>
              <button data-dn="${i}">↓</button>
              <button data-rm="${i}">✖</button>
            </div>
          </div>`).join('');
        q.querySelectorAll('.jk-music-item').forEach((item, i) => item.addEventListener('click', (e) => { if (e.target.tagName !== 'BUTTON') this.player.playTrack(i); }));
        q.querySelectorAll('[data-up]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); this.player.moveQueueItem(+b.dataset.up, -1); }));
        q.querySelectorAll('[data-dn]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); this.player.moveQueueItem(+b.dataset.dn, 1); }));
        q.querySelectorAll('[data-rm]').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); this.player.removeFromQueue(+b.dataset.rm); }));
      }
    }

    _esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  }

  window.MusicPlayer = MusicPlayer;
  window.MusicDock = MusicDock;
})();
