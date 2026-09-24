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
  let booksData = null;
  let booksFilter = { category: 'all', query: '', sort: 'title-asc' };

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
    const playIcon = '<span class="clip-play" aria-hidden="true"></span>';
    if (isVideoFile(clip)) {
      const url = clipUrl(clip);
      return `<div class="clip-thumb"><video src="${url}" muted playsinline ${autoplay ? 'autoplay loop' : 'preload="metadata"'}></video>${playIcon}</div>`;
    }
    const poster = data.heroPortrait || (data.portraits && data.portraits[0]) || '';
    return `<div class="clip-thumb clip-thumb-poster"${poster ? ` style="background-image:url('${poster}')"` : ''}>${playIcon}</div>`;
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

  const SUBTITLE_LABELS = { en: 'English', es: 'Español', fr: 'Français' };

  const CLIP_I18N = {
    'zerizus-miracle': {
      es: { title: 'El milagro del zerizut', hook: 'Cuando la urgencia encuentra la fe' },
      fr: { title: 'Le miracle du zerizut', hook: 'Quand l\'urgence rencontre la foi' },
    },
    'yud-tes-kislev': {
      es: { title: 'Yud Tes Kislev', hook: 'Luz en el exilio — una historia del Rebe' },
      fr: { title: 'Yud Tes Kislev', hook: 'Lumière en exil — une histoire du Rebbe' },
    },
  };

  const LANG_TRANSCRIPTS = {
    es: [
      { id: 'accident-miracle', title: 'Milagro del accidente', clipId: 'zerizus-miracle' },
      { id: 'litvak-becomes-a-chasid', title: 'El litvak se convierte en jasíd', clipId: 'yud-tes-kislev' },
    ],
    fr: [
      { id: 'accident-miracle', title: 'Miracle de l\'accident', clipId: 'zerizus-miracle' },
      { id: 'litvak-becomes-a-chasid', title: 'Le Litvak devient hassid', clipId: 'yud-tes-kislev' },
    ],
  };

  function pageSubtitleLang() {
    const param = new URLSearchParams(location.search).get('lang');
    if (param && ['en', 'es', 'fr'].includes(param)) return param;
    const page = document.body.dataset.page;
    if (page === 'es') return 'es';
    if (page === 'fr') return 'fr';
    const htmlLang = (document.documentElement.lang || 'en').slice(0, 2);
    return ['en', 'es', 'fr'].includes(htmlLang) ? htmlLang : 'en';
  }

  function transcriptLang() {
    return pageSubtitleLang();
  }

  function transcriptFileUrl(id, lang) {
    if (lang === 'en') return `/data/transcripts/${encodeURIComponent(id)}.json`;
    return `/data/transcripts/${encodeURIComponent(id)}.${lang}.json`;
  }

  function clipSubtitleLang(clip) {
    const preferred = pageSubtitleLang();
    const subs = clip.subtitles || {};
    if (subs[preferred]) return preferred;
    if (subs[clip.language]) return clip.language;
    return subs.en ? 'en' : Object.keys(subs)[0] || 'en';
  }

  function renderSubtitleTracks(clip) {
    const subs = clip.subtitles;
    if (!subs) return '';
    const defaultLang = clipSubtitleLang(clip);
    return Object.entries(subs).map(([lang, file]) => {
      const src = `/public/clips/${file}`;
      const label = SUBTITLE_LABELS[lang] || lang;
      const isDefault = lang === defaultLang;
      return `<track kind="captions" src="${escapeAttr(src)}" srclang="${lang}" label="${escapeAttr(label)}"${isDefault ? ' default' : ''}>`;
    }).join('');
  }

  function renderVideoPlayer(clip, opts) {
    const url = clipUrl(clip);
    if (!isVideoFile(clip) || !url) return '';
    const attrs = [
      `src="${escapeAttr(url)}"`,
      'controls',
      'playsinline',
      'crossorigin="anonymous"',
    ];
    if (opts && opts.autoplay) attrs.push('autoplay');
    if (opts && opts.poster) attrs.push(`poster="${escapeAttr(opts.poster)}"`);
    const tracks = renderSubtitleTracks(clip);
    const wrapClass = 'video-wrap';
    return `<div class="${wrapClass}"><video ${attrs.join(' ')}>${tracks}</video></div>`;
  }

  function enableDefaultCaptions(video, clip) {
    if (!video || !video.textTracks) return;
    const lang = clip ? clipSubtitleLang(clip) : pageSubtitleLang();
    function apply() {
      const tracks = Array.from(video.textTracks);
      const preferred = tracks.find(t => t.language === lang)
        || tracks.find(t => t.language === 'en')
        || tracks.find(t => t.default)
        || tracks[0];
      tracks.forEach(t => { t.mode = t === preferred ? 'showing' : 'hidden'; });
    }
    apply();
    video.querySelectorAll('track').forEach(trackEl => {
      trackEl.addEventListener('load', apply);
    });
    video.textTracks.addEventListener('addtrack', apply);
  }

  function clipDisplay(clip) {
    const lang = pageSubtitleLang();
    const i18n = CLIP_I18N[clip.id] && CLIP_I18N[clip.id][lang];
    return {
      title: (i18n && i18n.title) || clip.title,
      hook: (i18n && i18n.hook) || clip.hook,
    };
  }

  function clipPageHref(clip) {
    const lang = pageSubtitleLang();
    let href = `/clip.html?id=${encodeURIComponent(clip.id)}`;
    if (lang !== 'en') href += `&lang=${lang}`;
    return href;
  }

  function renderClipCard(clip) {
    const { title, hook } = clipDisplay(clip);
    return `<a class="clip-card" href="${clipPageHref(clip)}">
      ${renderThumb(clip, false)}
      <div class="clip-body"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(hook)}</p></div>
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
    if (isVideoFile(clip)) {
      el.innerHTML = renderVideoPlayer(clip, { vertical: true, poster: data.heroPortrait || '' });
      enableDefaultCaptions(el.querySelector('video'), clip);
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
    const lang = pageSubtitleLang();
    const clip = publishedClips().find(c => c.id === id);
    if (!clip) {
      el.innerHTML = '<p>Clip not found.</p>';
      return;
    }
    const { title, hook } = clipDisplay(clip);
    document.title = `RCD | ${title}`;
    const meta = qs('meta[name="description"]');
    if (meta) meta.content = hook;
    const player = isVideoFile(clip) ? renderVideoPlayer(clip, { vertical: true, autoplay: true }) : '';
    const backHref = lang === 'es' ? '/es.html' : lang === 'fr' ? '/fr.html' : '/watch.html';
    const backLabel = lang === 'es' ? 'Más clipes' : lang === 'fr' ? 'Plus de clips' : 'More clips';
    const transcriptBtn = clip.transcriptId
      ? `<a class="btn" href="${transcriptListHref(clip.transcriptId)}">${lang === 'es' ? 'Transcripción' : lang === 'fr' ? 'Transcription' : 'Transcript'}</a>`
      : '';
    el.innerHTML = `
      <div class="clip-page-header">
        <h1>${escapeHtml(title)}</h1>
        <p class="lead">${escapeHtml(hook)}</p>
      </div>
      ${player}
      <div class="cta-row">
        <a class="btn primary" href="${backHref}">${backLabel}</a>
        ${transcriptBtn}
        <a class="btn" href="https://www.youtube.com/@RabbiDalfin" target="_blank" rel="noopener">RCD YouTube</a>
      </div>`;
    enableDefaultCaptions(el.querySelector('video'), clip);
  }

  function renderTranscriptLangSwitcher(id, activeLang) {
    const langs = [
      { code: 'en', label: 'English' },
      { code: 'es', label: 'Español' },
      { code: 'fr', label: 'Français' },
    ];
    return `<nav class="transcript-lang-switch" aria-label="Transcript language">
      ${langs.map(l => {
        const href = l.code === 'en'
          ? `/transcript.html?id=${encodeURIComponent(id)}`
          : `/transcript.html?id=${encodeURIComponent(id)}&lang=${l.code}`;
        const active = l.code === activeLang ? ' is-active' : '';
        return `<a class="transcript-lang-btn${active}" href="${href}" hreflang="${l.code}">${l.label}</a>`;
      }).join('')}
    </nav>`;
  }

  function renderTranscriptLine(line) {
    return `<div class="transcript-line"><time class="transcript-time">${escapeHtml(line.time)}</time><p class="transcript-text">${escapeHtml(line.text)}</p></div>`;
  }

  function transcriptListHref(id) {
    const lang = transcriptLang();
    if (lang === 'en') return `/transcript.html?id=${encodeURIComponent(id)}`;
    return `/transcript.html?id=${encodeURIComponent(id)}&lang=${lang}`;
  }

  function mountLangTranscriptList(el) {
    if (!el) return;
    const lang = pageSubtitleLang();
    const items = LANG_TRANSCRIPTS[lang];
    if (!items || !items.length) return;
    const heading = lang === 'es' ? 'Transcripciones' : 'Transcriptions';
    const watchClip = lang === 'es' ? 'Ver clip' : 'Voir le clip';
    el.innerHTML = `
      <h2>${heading}</h2>
      <ul class="link-list transcript-list">${items.map(t =>
        `<li><a href="${transcriptListHref(t.id)}">${escapeHtml(t.title)}</a><span class="transcript-meta"><a href="${clipPageHref({ id: t.clipId })}">${watchClip}</a></span></li>`
      ).join('')}</ul>`;
  }

  function mountTranscriptList(el) {
    if (!el || !transcriptsIndex) return;
    const items = transcriptsIndex.transcripts || [];
    const lang = transcriptLang();
    const langNote = lang === 'es'
      ? ' · Español disponible'
      : lang === 'fr'
        ? ' · Français disponible'
        : ' · English · Español · Français';
    el.innerHTML = items.length
      ? `<ul class="link-list transcript-list">${items.map(t =>
          `<li><a href="${transcriptListHref(t.id)}">${t.title}</a><span class="transcript-meta">${t.lineCount} segments${langNote} · <a href="${t.youtubeUrl}" target="_blank" rel="noopener">YouTube</a></span></li>`
        ).join('')}</ul>`
      : '<p>No transcripts available yet.</p>';
  }

  function formatPrice(amount, currency) {
    if (!amount || amount <= 0) return 'See shop';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(amount);
  }

  function bookBadgeClass(tag) {
    const t = String(tag).toLowerCase();
    if (t.includes('new')) return 'badge-new';
    if (t.includes('limited')) return 'badge-limited';
    return 'badge-default';
  }

  function renderBookBadges(tags) {
    if (!tags || !tags.length) return '';
    return tags.slice(0, 2).map(tag =>
      `<span class="book-badge ${bookBadgeClass(tag)}">${escapeHtml(tag)}</span>`
    ).join('');
  }

  function filteredBooks() {
    if (!booksData) return [];
    let items = (booksData.products || []).slice();
    if (booksFilter.category !== 'all') {
      items = items.filter(b => b.category === booksFilter.category);
    }
    if (booksFilter.query) {
      const q = booksFilter.query.toLowerCase();
      items = items.filter(b =>
        b.title.toLowerCase().includes(q) ||
        (b.category || '').toLowerCase().includes(q)
      );
    }
    const sort = booksFilter.sort;
    items.sort((a, b) => {
      if (sort === 'price-asc') return (a.price || 0) - (b.price || 0);
      if (sort === 'price-desc') return (b.price || 0) - (a.price || 0);
      if (sort === 'title-desc') return b.title.localeCompare(a.title);
      return a.title.localeCompare(b.title);
    });
    return items;
  }

  function renderBookCard(book) {
    const cover = book.image
      ? `<img src="${escapeAttr(book.image)}" alt="" loading="lazy">`
      : '<div class="book-cover-placeholder"></div>';
    return `<a class="book-shop-card" href="/product.html?id=${encodeURIComponent(book.id)}">
      <div class="book-cover">${cover}${renderBookBadges(book.tags)}</div>
      <div class="book-shop-body">
        <p class="book-shop-category">${escapeHtml(book.category || '')}</p>
        <h3>${escapeHtml(book.title)}</h3>
        <p class="book-shop-price">${formatPrice(book.price, book.currency)}</p>
      </div>
    </a>`;
  }

  function mountBooksCatalog() {
    const grid = qs('[data-books-grid]');
    const chips = qs('[data-books-categories]');
    const countEl = qs('[data-books-count]');
    const emptyEl = qs('[data-books-empty]');
    const searchEl = qs('[data-books-search]');
    const sortEl = qs('[data-books-sort]');
    if (!grid || !booksData) return;

    function render() {
      const items = filteredBooks();
      grid.innerHTML = items.map(renderBookCard).join('');
      if (countEl) {
        countEl.textContent = `${items.length} of ${booksData.products.length} titles`;
      }
      if (emptyEl) {
        emptyEl.hidden = items.length > 0;
      }
    }

    if (chips) {
      const cats = ['all', ...(booksData.categories || [])];
      chips.innerHTML = cats.map(cat => {
        const label = cat === 'all' ? 'All' : cat;
        const active = booksFilter.category === cat ? ' is-active' : '';
        return `<button type="button" class="books-chip${active}" data-category="${escapeAttr(cat)}">${escapeHtml(label)}</button>`;
      }).join('');
      chips.querySelectorAll('.books-chip').forEach(btn => {
        btn.addEventListener('click', () => {
          booksFilter.category = btn.dataset.category || 'all';
          chips.querySelectorAll('.books-chip').forEach(b =>
            b.classList.toggle('is-active', b === btn)
          );
          render();
        });
      });
    }

    if (searchEl) {
      searchEl.addEventListener('input', () => {
        booksFilter.query = searchEl.value.trim();
        render();
      });
    }

    if (sortEl) {
      sortEl.value = booksFilter.sort;
      sortEl.addEventListener('change', () => {
        booksFilter.sort = sortEl.value;
        render();
      });
    }

    render();
  }

  function mountProductPage(el) {
    if (!el || !booksData) return;
    const id = new URLSearchParams(location.search).get('id');
    const book = (booksData.products || []).find(b => b.id === id);
    if (!book) {
      el.innerHTML = '<p>Book not found. <a href="/books.html">Browse all books</a></p>';
      return;
    }
    document.title = `RCD | ${book.title}`;
    const meta = qs('meta[name="description"]');
    if (meta) meta.content = `${book.title} — ${book.category}. ${formatPrice(book.price, book.currency)}`;
    const cover = book.image
      ? `<img class="product-cover" src="${escapeAttr(book.image)}" alt="${escapeAttr(book.title)}">`
      : '';
    const tags = renderBookBadges(book.tags);
    const desc = book.description
      ? `<div class="product-desc prose"><p>${escapeHtml(book.description)}</p></div>`
      : `<p class="product-desc-muted">Full description available on the Rabbi Dalfin shop.</p>`;
    el.innerHTML = `
      <nav class="product-breadcrumb"><a href="/books.html">Books</a><span aria-hidden="true"> / </span><span>${escapeHtml(book.title)}</span></nav>
      <article class="product-detail">
        <div class="product-cover-wrap">${cover}${tags ? `<div class="product-badges">${tags}</div>` : ''}</div>
        <div class="product-info">
          <p class="book-shop-category">${escapeHtml(book.category || '')}</p>
          <h1>${escapeHtml(book.title)}</h1>
          <p class="product-format">${escapeHtml((book.format || 'book').toUpperCase())}</p>
          <p class="product-price">${formatPrice(book.price, book.currency)}</p>
          ${desc}
          <div class="cta-row">
            <a class="btn primary" href="${escapeAttr(book.purchaseUrl)}" target="_blank" rel="noopener">Buy on RabbiDalfin.com</a>
            <a class="btn" href="/books.html">All books</a>
          </div>
        </div>
      </article>`;
  }

  function mountTranscriptPage(el) {
    if (!el) return;
    const id = new URLSearchParams(location.search).get('id');
    const meta = (transcriptsIndex && transcriptsIndex.transcripts || []).find(t => t.id === id);
    if (!meta) {
      el.innerHTML = '<p>Transcript not found.</p>';
      return;
    }
    const lang = transcriptLang();
    const langLabels = { en: 'English', es: 'Español', fr: 'Français' };
    el.innerHTML = '<p class="transcript-loading">Loading transcript…</p>';
    fetch(transcriptFileUrl(id, lang))
      .then(r => {
        if (!r.ok) throw new Error('missing');
        return r.json();
      })
      .then(t => {
        document.title = `RCD | ${t.title} — Transcript (${langLabels[lang] || lang})`;
        const desc = qs('meta[name="description"]');
        if (desc) desc.content = `Full transcript: ${t.title} (${langLabels[lang] || lang})`;
        const lead = lang === 'es'
          ? 'Transcripción completa con marcas de tiempo.'
          : lang === 'fr'
            ? 'Transcription complète avec horodatage.'
            : 'Word-for-word transcript with timestamps.';
        const allHref = lang === 'es' ? '/es.html' : lang === 'fr' ? '/fr.html' : '/transcripts.html';
        const allLabel = lang === 'es' ? 'Todos los clipes' : lang === 'fr' ? 'Tous les clips' : 'All transcripts';
        const watchLabel = lang === 'es' ? 'Ver en YouTube' : lang === 'fr' ? 'Voir sur YouTube' : 'Watch on YouTube';
        el.innerHTML = `
          ${renderTranscriptLangSwitcher(id, lang)}
          <h1>${escapeHtml(t.title)}</h1>
          <p class="lead">${lead}</p>
          <div class="cta-row">
            <a class="btn primary" href="${t.youtubeUrl}" target="_blank" rel="noopener">${watchLabel}</a>
            <a class="btn" href="${allHref}">${allLabel}</a>
          </div>
          <div class="transcript-body">${(t.lines || []).map(renderTranscriptLine).join('')}</div>`;
      })
      .catch(() => {
        if (lang !== 'en') {
          location.replace(`/transcript.html?id=${encodeURIComponent(id)}`);
          return;
        }
        el.innerHTML = '<p>Failed to load transcript.</p>';
      });
  }

  function initMobileNav() {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.site-nav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  function wrapFeaturedSection() {
    const player = qs('[data-featured-player]');
    if (!player || !player.parentElement) return;
    const section = player.closest('section');
    if (section) section.classList.add('featured-section');
  }

  function highlightNav() {
    const path = location.pathname.replace(/\\/g, '/');
    document.querySelectorAll('.site-nav a, nav a').forEach(a => {
      const href = a.getAttribute('href');
      const isTranscriptPage = path === '/transcript.html' && href === '/transcripts.html';
      if (href === path || isTranscriptPage || (path === '/' && href === '/index.html')) {
        a.classList.add('active');
      }
    });
  }

  function init() {
    const page = document.body.dataset.page;
    initMobileNav();
    highlightNav();
    wrapFeaturedSection();
    mountHeroPortrait(qs('[data-hero-portrait]'));
    mountPortraitStrip(qs('[data-portrait-strip]'));
    mountClipGrid(qs('[data-clip-grid]'));
    mountClipGrid(qs('[data-rebbe-clips]'), c => (c.tags || []).includes('rebbe-stories'));
    mountFeaturedPlayer(qs('[data-featured-player]'), data.featuredClipId);
    mountClipPage(qs('[data-clip-player]'));
    mountTranscriptList(qs('[data-transcript-list]'));
    mountLangTranscriptList(qs('[data-lang-transcripts]'));
    mountTranscriptPage(qs('[data-transcript-view]'));
    mountBooksCatalog();
    mountProductPage(qs('[data-product-detail]'));
    if (page === 'es' || page === 'fr') {
      const lang = page === 'es' ? 'es' : 'fr';
      mountClipGrid(qs('[data-lang-clips]'), c => c.language === lang || c.language === 'en');
    }
  }

  Promise.all([
    fetch('/data/clips.json').then(r => r.json()),
    fetch('/data/transcripts.json').then(r => r.json()).catch(() => ({ transcripts: [] })),
    fetch('/data/books.json').then(r => r.json()).catch(() => ({ products: [], categories: [] })),
  ])
    .then(([clips, transcripts, books]) => {
      data = clips;
      transcriptsIndex = transcripts;
      booksData = books;
      init();
    })
    .catch(err => console.error('RCD: failed to load site data', err));
})();
