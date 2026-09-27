/* TLEMCENYA — Shopify theme. Progressive enhancement only: every form on
 * the site posts and works with this file absent. The hero, header, reveal
 * and navigation code is assets/js/site.js from the static site; the basket
 * is new and talks to Shopify's AJAX Cart API.
 */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var T = window.theme || { routes: {} };
  var R = T.routes || {};

  /* ---------------------------------------------------------------- *
   * Hero: one orchestrated entrance, once. The oil field stops when the
   * hero is off screen, so a long scroll costs no GPU work.
   * ---------------------------------------------------------------- */
  var hero = document.querySelector('[data-oil]');
  if (hero) {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { hero.classList.add('is-lit'); });
    });
    if ('IntersectionObserver' in window) {
      var field = hero.querySelector('.oil-field');
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!field) return;
          Array.prototype.forEach.call(field.children, function (n) {
            n.style.animationPlayState = en.isIntersecting ? 'running' : 'paused';
          });
          field.style.willChange = en.isIntersecting ? 'transform' : 'auto';
        });
      }, { rootMargin: '120px' }).observe(hero);
    }
  }

  /* ---------------------------------------------------------------- *
   * Optional hero video. Opt-in, never opt-out: fetched only on a wide
   * viewport, without reduced motion, on a connection that is not metered
   * or slow. If any of that fails the CSS oil field simply stays.
   * ---------------------------------------------------------------- */
  var video = document.querySelector('[data-hero-video]');
  if (video) {
    var conn = navigator.connection || {};
    var slow = conn.saveData === true ||
               /(^|-)2g$/.test(conn.effectiveType || '') ||
               conn.effectiveType === 'slow-2g';
    var wide = window.matchMedia('(min-width: 62rem)').matches;
    if (wide && !slow && !reduced.matches) {
      video.querySelectorAll('source[data-src]').forEach(function (src) {
        src.src = src.getAttribute('data-src');
      });
      video.load();
      video.addEventListener('playing', function () {
        video.classList.add('is-playing');
      }, { once: true });
      video.addEventListener('error', function () { video.remove(); });
      var p = video.play();
      if (p && p.catch) p.catch(function () { video.remove(); });
    } else {
      video.remove();
    }
  }

  /* ---------------------------------------------------------------- *
   * Header: solid once the hero has scrolled past the bar.
   * ---------------------------------------------------------------- */
  var head = document.querySelector('[data-head]');
  if (head) {
    var ticking = false;
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        head.classList.toggle('is-stuck', window.scrollY > 24);
        ticking = false;
      });
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------------------------------------------------------------- *
   * Reveals. IntersectionObserver latches .seen once and never regresses.
   * In the theme editor everything is shown at once: a merchant moving a
   * section must not have to scroll it into view to see it.
   * ---------------------------------------------------------------- */
  var revealAll = function () {
    document.querySelectorAll('.reveal').forEach(function (n) { n.classList.add('seen'); });
  };
  var observeReveals = function (root) {
    if (!('IntersectionObserver' in window) || reduced.matches || window.Shopify && Shopify.designMode) {
      revealAll();
      return;
    }
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('seen');
        obs.unobserve(en.target);
      });
    }, { rootMargin: '0px', threshold: 0 });
    (root || document).querySelectorAll('.reveal:not(.seen)').forEach(function (n) { io.observe(n); });
  };
  observeReveals();
  window.addEventListener('scroll', function () {
    if (window.scrollY + window.innerHeight >= document.body.scrollHeight - 4) revealAll();
  }, { passive: true });
  document.addEventListener('shopify:section:load', function (ev) {
    revealAll();
    if (ev.target.querySelector('[data-oil]')) {
      ev.target.querySelector('[data-oil]').classList.add('is-lit');
    }
  });

  /* ---------------------------------------------------------------- *
   * Mobile navigation.
   * ---------------------------------------------------------------- */
  var toggle = document.querySelector('[data-nav-toggle]');
  var panel = document.querySelector('[data-nav-panel]');
  if (toggle && panel) {
    var labelEl = toggle.querySelector('[data-nav-label]');
    var iconEl = toggle.querySelector('[data-nav-icon]');
    var iconOpen = iconEl ? iconEl.innerHTML : '';
    var iconClose =
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
    var labelOpen = labelEl ? labelEl.textContent : '';
    var labelClose = toggle.getAttribute('data-label-close') || labelOpen;
    var setNav = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      if (open) panel.setAttribute('data-open', ''); else panel.removeAttribute('data-open');
      if (labelEl) labelEl.textContent = open ? labelClose : labelOpen;
      if (iconEl) iconEl.innerHTML = open ? iconClose : iconOpen;
    };
    toggle.addEventListener('click', function () {
      setNav(toggle.getAttribute('aria-expanded') !== 'true');
    });
    panel.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) setNav(false);
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setNav(false);
        toggle.focus();
      }
    });
  }

  /* ---------------------------------------------------------------- *
   * Money, in the shop's own format ({{amount}} DA, {{amount_no_decimals}}…).
   * ---------------------------------------------------------------- */
  function formatMoney(cents) {
    var fmt = T.moneyFormat || '{{amount}}';
    var group = function (n, dec, thou, dp) {
      var s = (n / 100).toFixed(dp);
      var parts = s.split('.');
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thou);
      return parts.join(dp ? dec : '');
    };
    return fmt.replace(/\{\{\s*(\w+)\s*\}\}/, function (_, k) {
      switch (k) {
        case 'amount_no_decimals': return group(cents, '.', ',', 0);
        case 'amount_with_comma_separator': return group(cents, ',', '.', 2);
        case 'amount_no_decimals_with_comma_separator': return group(cents, ',', '.', 0);
        case 'amount_with_space_separator': return group(cents, ',', ' ', 2);
        case 'amount_no_decimals_with_space_separator': return group(cents, ',', ' ', 0);
        case 'amount_with_apostrophe_separator': return group(cents, '.', "'", 2);
        default: return group(cents, '.', ',', 2);
      }
    });
  }

  /* ---------------------------------------------------------------- *
   * Basket drawer.
   * The drawer is a section (sections/cart-drawer.liquid). Every change
   * asks Shopify to re-render it and swaps the body in, so the markup has
   * exactly one author.
   * ---------------------------------------------------------------- */
  var SECTION = 'cart-drawer';
  var drawer = document.querySelector('[data-cart]');
  var veil = document.querySelector('[data-cart-veil]');
  var live = document.querySelector('[data-cart-live]');
  var lastFocus = null;

  function announce(msg) {
    if (!live || !msg) return;
    live.textContent = '';
    setTimeout(function () { live.textContent = msg; }, 60);
  }

  function focusables() {
    return drawer.querySelectorAll('a[href], button:not([disabled]), input, select, textarea');
  }

  function openCart() {
    if (!drawer) return false;
    lastFocus = document.activeElement;
    drawer.hidden = false;
    if (veil) veil.hidden = false;
    document.body.classList.add('cart-on');
    var close = drawer.querySelector('[data-cart-close]');
    if (close) close.focus();
    return true;
  }

  function closeCart() {
    if (!drawer || drawer.hidden) return;
    drawer.hidden = true;
    if (veil) veil.hidden = true;
    document.body.classList.remove('cart-on');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function applySection(html) {
    if (!html || !drawer) return;
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var fresh = doc.querySelector('[data-cart-body]');
    var body = drawer.querySelector('[data-cart-body]');
    if (fresh && body) body.replaceWith(fresh);
    var count = fresh ? parseInt(fresh.getAttribute('data-count'), 10) || 0 : 0;
    document.querySelectorAll('[data-cart-count]').forEach(function (n) {
      n.textContent = count;
      if (!n.closest('.cart-fab')) n.hidden = count === 0;
    });
    document.querySelectorAll('.cart-fab').forEach(function (b) { b.hidden = count === 0; });
  }

  function post(url, payload) {
    payload.sections = SECTION;
    payload.sections_url = window.location.pathname;
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok || data.status) throw data;
        return data;
      });
    });
  }

  if (drawer) {
    document.addEventListener('click', function (ev) {
      var opener = ev.target.closest('[data-cart-open]');
      if (opener) {
        // The header link is a real /cart link; with the drawer at hand it
        // opens the drawer instead, and still works as a link without JS.
        if (openCart()) ev.preventDefault();
        return;
      }
      if (ev.target.closest('[data-cart-close]') || ev.target === veil) {
        closeCart();
        return;
      }
      var q = ev.target.closest('[data-qty-line]');
      if (q && drawer.contains(q)) {
        var line = parseInt(q.getAttribute('data-qty-line'), 10);
        var qty = Math.max(0, parseInt(q.getAttribute('data-qty'), 10) || 0);
        var removing = qty === 0;
        drawer.setAttribute('aria-busy', 'true');
        post(R.cartChange + '.js', { line: line, quantity: qty })
          .then(function (data) {
            applySection(data.sections && data.sections[SECTION]);
            if (removing) announce(drawer.getAttribute('data-removed'));
            var first = drawer.querySelector('[data-cart-body] button, [data-cart-body] a');
            (first || drawer.querySelector('[data-cart-close]')).focus();
          })
          .catch(function () { window.location.href = R.cart; })
          .finally(function () { drawer.removeAttribute('aria-busy'); });
      }
    });

    document.addEventListener('keydown', function (ev) {
      if (drawer.hidden) return;
      if (ev.key === 'Escape') { closeCart(); return; }
      if (ev.key !== 'Tab') return;
      var f = focusables();
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (ev.shiftKey && document.activeElement === first) { last.focus(); ev.preventDefault(); }
      else if (!ev.shiftKey && document.activeElement === last) { first.focus(); ev.preventDefault(); }
    });
  }

  /* ---------------------------------------------------------------- *
   * Add to basket. Any product form (cards and the product page) posts
   * through /cart/add.js when the drawer exists, and falls back to a
   * normal form post — which lands on /cart — when anything goes wrong.
   * ---------------------------------------------------------------- */
  document.addEventListener('submit', function (ev) {
    var form = ev.target.closest('[data-product-form]');
    if (!form || !drawer || !window.fetch) return;
    ev.preventDefault();
    var btn = form.querySelector('[type="submit"]');
    var err = form.querySelector('[data-form-error]');
    var fd = new FormData(form);
    var payload = {
      items: [{ id: parseInt(fd.get('id'), 10), quantity: parseInt(fd.get('quantity') || '1', 10) || 1 }]
    };
    if (btn) { btn.disabled = true; btn.setAttribute('aria-busy', 'true'); }
    if (err) err.hidden = true;
    post(R.cartAdd + '.js', payload)
      .then(function (data) {
        applySection(data.sections && data.sections[SECTION]);
        announce(drawer.getAttribute('data-added'));
        openCart();
      })
      .catch(function (e) {
        if (err && e && e.description) {
          err.textContent = e.description;
          err.hidden = false;
        } else {
          form.submit();
        }
      })
      .finally(function () {
        if (btn) { btn.disabled = false; btn.removeAttribute('aria-busy'); }
      });
  });

  /* ---------------------------------------------------------------- *
   * Variant picker, for a product sold in more than one format.
   * ---------------------------------------------------------------- */
  document.querySelectorAll('.pdp-form').forEach(function (form) {
    var json = form.querySelector('[data-variants]');
    if (!json) return;
    var variants = JSON.parse(json.textContent);
    var selects = form.querySelectorAll('[data-option]');
    var idInput = form.querySelector('[data-variant-id]');
    var btn = form.querySelector('[data-add-button]');
    var price = document.querySelector('[data-price]');

    var update = function () {
      var chosen = Array.prototype.map.call(selects, function (s) { return s.value; });
      var v = variants.find(function (x) {
        return x.options.every(function (o, i) { return o === chosen[i]; });
      });
      if (!v) {
        btn.disabled = true;
        btn.textContent = btn.getAttribute('data-label-unavailable');
        return;
      }
      idInput.value = v.id;
      var url = new URL(window.location.href);
      url.searchParams.set('variant', v.id);
      history.replaceState(null, '', url.toString());
      if (v.price <= 0) {
        btn.disabled = true;
        btn.textContent = btn.getAttribute('data-label-pending');
        if (price) price.innerHTML = '<span class="pending">' + btn.getAttribute('data-label-pending') + '</span>';
        return;
      }
      if (price) {
        price.innerHTML = (v.compare_at_price > v.price
          ? '<s class="price-was">' + formatMoney(v.compare_at_price) + '</s> ' : '') +
          '<span class="price-now">' + formatMoney(v.price) + '</span>';
      }
      btn.disabled = !v.available;
      btn.textContent = btn.getAttribute(v.available ? 'data-label-add' : 'data-label-sold');
    };
    selects.forEach(function (s) { s.addEventListener('change', update); });
  });

  /* ---------------------------------------------------------------- *
   * Customer addresses: country / province selects, delete confirmation.
   * ---------------------------------------------------------------- */
  var initAddresses = function () {
    if (!window.Shopify || !Shopify.CountryProvinceSelector) return;
    document.querySelectorAll('[data-address-country]').forEach(function (c) {
      new Shopify.CountryProvinceSelector(c.id, c.getAttribute('data-province-id'), {
        hideElement: c.getAttribute('data-province-wrap')
      });
    });
  };
  if (document.querySelector('[data-address-country]')) {
    if (document.readyState === 'complete') initAddresses();
    else window.addEventListener('load', initAddresses);
  }
  document.querySelectorAll('.acct-del').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      if (!window.confirm(f.getAttribute('data-confirm'))) ev.preventDefault();
    });
  });
})();
