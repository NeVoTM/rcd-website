(function () {
  const NAV = [
    { href: '/watch.html', label: 'Watch' },
    { href: '/rebbe.html', label: 'The Rebbe' },
    { href: '/about.html', label: 'About' },
    { href: '/books.html', label: 'Books' },
    { href: '/book.html', label: 'Book RCD' },
    { href: '/es.html', label: 'Español' },
    { href: '/fr.html', label: 'Français' },
  ];

  let data = null;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function clipUrl(clip) {
    if (clip.file) return `/public/clips/${clip.file}`;
    if (clip.youtubeId) return `https://www.youtube.com/embed/${clip.youtubeId}`;
    return null;
  }

  function isVideoFile(clip) {
    return clip.file && clip.file.endsWith('.mp4');
  }

  function renderThumb(clip, autoplay) {
    const url = clipUrl(clip);
    if (!url) return '<div class="clip-thumb"></div>';
    if (isVideoFile(clip)) {
      return `<div class="clip-thumb"><video src="${url}" muted playsinline ${autoplay ? 'autoplay loop' : 'preload="metadata"'}></video></div>`;
    }
    return `<div class="clip-thumb"><iframe src="${url}" title="${escapeAttr(clip.title)}" loading="lazy" allowfullscreen></iframe></div>`;
  }

  function escapeAttr(s) {
    return String(s).replace(/"/g, '&quot;');
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
    } else if (clip.youtubeId) {
      el.innerHTML = `<div class="video-wrap"><iframe src="https://www.youtube.com/embed/${clip.youtubeId}" title="${escapeAttr(clip.title)}" allowfullscreen loading="lazy"></iframe></div>`;
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
    } else if (clip.youtubeId) {
      player = `<div class="video-wrap vertical"><iframe src="https://www.youtube.com/embed/${clip.youtubeId}" title="${escapeAttr(clip.title)}" allowfullscreen></iframe></div>`;
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

  function highlightNav() {
    const path = location.pathname.replace(/\\/g, '/');
    document.querySelectorAll('nav a').forEach(a => {
      const href = a.getAttribute('href');
      if (href === path || (path === '/' && href === '/index.html')) a.classList.add('active');
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
    if (page === 'es' || page === 'fr') {
      const lang = page === 'es' ? 'es' : 'fr';
      mountClipGrid(qs('[data-lang-clips]'), c => c.language === lang || c.language === 'en');
    }
  }

  fetch('/data/clips.json')
    .then(r => r.json())
    .then(d => { data = d; init(); })
    .catch(err => console.error('RCD: failed to load clips.json', err));
})();
