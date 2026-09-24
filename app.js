(function () {
  const NAV = [
    { href: '/watch.html', label: 'Watch' },
    { href: '/transcripts.html', label: 'Transcripts' },
    { href: '/rebbe.html', label: 'The Rebbe' },
    { href: '/about.html', label: 'About' },
    { href: '/books.html', label: 'Books' },
    { href: '/book.html', label: 'Book RCD' },
    { href: '/es.html', label: 'Español' },
    { href: '/fr.html', label: 'Français' },
  ];

  let data = null;
  let transcriptsIndex = null;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function clipUrl(clip) {
    if (clip.file) return `/public/clips/${clip.file}`;
    return null;
  }

  function isVideoFile(clip) {
    return clip.file && clip.file.endsWith('.mp4');
  }

  function renderThumb(clip, autoplay) {
    if (isVideoFile(clip)) {
      const url = clipUrl(clip);
      return `<div class="clip-thumb"><video src="${url}" muted playsinline ${autoplay ? 'autoplay loop' : 'preload="metadata"'}></video></div>`;
    }
    const poster = data.heroPortrait || (data.portraits && data.portraits[0]) || '';
    return `<div class="clip-thumb clip-thumb-poster"${poster ? ` style="background-image:url('${poster}')"` : ''}></div>`;
  }

  function escapeAttr(s) {
    return String(s).replace(/"/g, '&quot;');
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function renderClipCard(clip) {
    return `<a class="clip-card" href="/clip.html?id=${encodeURIComponent(clip.id)}">
      ${renderThumb(clip, false)}
      <div class="clip-body"><h3>${clip.title}</h3><p>${clip.hook}</p></div>
    </a>`;
  }

  function publishedClips(filterFn) {
    const clips = (data.clips || []).filter(c => c.published !== false);
    return filterFn ? clips.filter(filterFn) : clips;
  }

  function mountClipGrid(el, filterFn) {
    if (!el) return;
    const clips = publishedClips(filterFn);
    el.innerHTML = clips.length
      ? clips.map(renderClipCard).join('')
      : '<p>No clips published yet.</p>';
  }

  function mountFeaturedPlayer(el, clipId) {
    if (!el) return;
    const clip = publishedClips().find(c => c.id === clipId) || publishedClips()[0];
    if (!clip) {
      el.innerHTML = '<p>Featured clip coming soon.</p>';
      return;
    }
    const url = clipUrl(clip);
    if (isVideoFile(clip)) {
      el.innerHTML = `<div class="video-wrap vertical"><video src="${url}" controls playsinline poster="${data.heroPortrait || ''}"></video></div>`;
    } else {
      el.innerHTML = '<p>Featured clip coming soon.</p>';
    }
  }

  function mountHeroPortrait(el) {
    if (!el || !data.heroPortrait) return;
    el.src = data.heroPortrait;
    el.alt = 'Rabbi Chaim Dalfin';
  }

  function mountPortraitStrip(el) {
    if (!el || !data.portraits) return;
    el.innerHTML = data.portraits.map(src =>
      `<img src="${src}" alt="Rabbi Chaim Dalfin" loading="lazy">`
    ).join('');
  }

  function mountClipPage(el) {
    if (!el) return;
    const id = new URLSearchParams(location.search).get('id') || data.featuredClipId;
    const clip = publishedClips().find(c => c.id === id);
    if (!clip) {
      el.innerHTML = '<p>Clip not found.</p>';
      return;
    }
    document.title = `RCD | ${clip.title}`;
    const meta = qs('meta[name="description"]');
    if (meta) meta.content = clip.hook;
    let player = '';
    if (isVideoFile(clip)) {
      player = `<div class="video-wrap vertical"><video src="/public/clips/${clip.file}" controls autoplay playsinline></video></div>`;
    }
    el.innerHTML = `
      <h1>${clip.title}</h1>
      <p class="lead">${clip.hook}</p>
      ${player}
      <div class="cta-row">
        <a class="btn primary" href="/watch.html">More clips</a>
        <a class="btn" href="https://www.youtube.com/@RabbiDalfin" target="_blank" rel="noopener">RCD YouTube</a>
      </div>`;
  }

  function renderTranscriptLine(line) {
    return `<div class="transcript-line"><time class="transcript-time">${escapeHtml(line.time)}</time><p class="transcript-text">${escapeHtml(line.text)}</p></div>`;
  }

  function mountTranscriptList(el) {
    if (!el || !transcriptsIndex) return;
    const items = transcriptsIndex.transcripts || [];
    el.innerHTML = items.length
      ? `<ul class="link-list transcript-list">${items.map(t =>
          `<li><a href="/transcript.html?id=${encodeURIComponent(t.id)}">${t.title}</a><span class="transcript-meta">${t.lineCount} segments · <a href="${t.youtubeUrl}" target="_blank" rel="noopener">YouTube</a></span></li>`
        ).join('')}</ul>`
      : '<p>No transcripts available yet.</p>';
  }

  function mountTranscriptPage(el) {
    if (!el) return;
    const id = new URLSearchParams(location.search).get('id');
    const meta = (transcriptsIndex && transcriptsIndex.transcripts || []).find(t => t.id === id);
    if (!meta) {
      el.innerHTML = '<p>Transcript not found.</p>';
      return;
    }
    el.innerHTML = '<p class="transcript-loading">Loading transcript…</p>';
    fetch(`/data/transcripts/${encodeURIComponent(id)}.json`)
      .then(r => r.json())
      .then(t => {
        document.title = `RCD | ${t.title} — Transcript`;
        const desc = qs('meta[name="description"]');
        if (desc) desc.content = `Full transcript: ${t.title}`;
        el.innerHTML = `
          <h1>${t.title}</h1>
          <p class="lead">Word-for-word transcript with timestamps.</p>
          <div class="cta-row">
            <a class="btn primary" href="${t.youtubeUrl}" target="_blank" rel="noopener">Watch on YouTube</a>
            <a class="btn" href="/transcripts.html">All transcripts</a>
          </div>
          <div class="transcript-body">${(t.lines || []).map(renderTranscriptLine).join('')}</div>`;
      })
      .catch(() => { el.innerHTML = '<p>Failed to load transcript.</p>'; });
  }

  function highlightNav() {
    const path = location.pathname.replace(/\\/g, '/');
    document.querySelectorAll('nav a').forEach(a => {
      const href = a.getAttribute('href');
      const isTranscriptPage = path === '/transcript.html' && href === '/transcripts.html';
      if (href === path || isTranscriptPage || (path === '/' && href === '/index.html')) {
        a.classList.add('active');
      }
    });
  }

  function init() {
    const page = document.body.dataset.page;
    highlightNav();
    mountHeroPortrait(qs('[data-hero-portrait]'));
    mountPortraitStrip(qs('[data-portrait-strip]'));
    mountClipGrid(qs('[data-clip-grid]'));
    mountClipGrid(qs('[data-rebbe-clips]'), c => (c.tags || []).includes('rebbe-stories'));
    mountFeaturedPlayer(qs('[data-featured-player]'), data.featuredClipId);
    mountClipPage(qs('[data-clip-player]'));
    mountTranscriptList(qs('[data-transcript-list]'));
    mountTranscriptPage(qs('[data-transcript-view]'));
    if (page === 'es' || page === 'fr') {
      const lang = page === 'es' ? 'es' : 'fr';
      mountClipGrid(qs('[data-lang-clips]'), c => c.language === lang || c.language === 'en');
    }
  }

  Promise.all([
    fetch('/data/clips.json').then(r => r.json()),
    fetch('/data/transcripts.json').then(r => r.json()).catch(() => ({ transcripts: [] })),
  ])
    .then(([clips, transcripts]) => {
      data = clips;
      transcriptsIndex = transcripts;
      init();
    })
    .catch(err => console.error('RCD: failed to load site data', err));
})();
