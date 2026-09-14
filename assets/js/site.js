/* TLEMCENYA — progressive enhancement only.
 * Every section reads and works with this file absent. ~3 KB unminified.
 */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  /* ---------------------------------------------------------------- *
   * Hero: one orchestrated entrance, once.
   * ---------------------------------------------------------------- */
  var hero = document.querySelector('[data-oil]');
  if (hero) {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { hero.classList.add('is-lit'); });
    });

    /* The oil field is four animated gradients. Stop them whenever the
     * hero is off screen so a long scroll costs no GPU work. */
    if ('IntersectionObserver' in window) {
      var field = hero.querySelector('.oil-field');
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!field) return;
          field.style.animationPlayState = en.isIntersecting ? '' : 'paused';
          Array.prototype.forEach.call(field.children, function (n) {
            n.style.animationPlayState = en.isIntersecting ? 'running' : 'paused';
          });
          field.style.willChange = en.isIntersecting ? 'transform' : 'auto';
        });
      }, { rootMargin: '120px' }).observe(hero);
    }
  }

  /* ---------------------------------------------------------------- *
   * Optional hero video.
   * Opt-in, never opt-out: the file is fetched only when the viewport is
   * wide enough to justify it, the visitor has not asked for reduced
   * motion, and the connection is not metered or slow. If any of that
   * fails -- or the file is missing -- the CSS oil field simply stays.
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
      // Only the element's own error means every source failed. Listening
      // in the capture phase would also catch a single <source> 404 -- a
      // missing optional webm would then take the working mp4 down with it.
      video.addEventListener('error', function () { video.remove(); });
      var p = video.play();
      if (p && p.catch) p.catch(function () { video.remove(); });
    } else {
      video.remove();
    }
  }

  /* ---------------------------------------------------------------- *
   * Header state. Solid once the hero has scrolled past the bar.
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
   * Reveals. One mechanism, deliberately: a scroll-driven timeline
   * cannot complete for a tall final section (the page runs out of
   * scroll first), which leaves that section permanently faded.
   * IntersectionObserver latches .seen once and never regresses.
   * ---------------------------------------------------------------- */
  var revealAll = function () {
    document.querySelectorAll('.reveal').forEach(function (n) { n.classList.add('seen'); });
  };

  if ('IntersectionObserver' in window && !reduced.matches) {
    /* rootMargin stays at 0: shrinking the root from the bottom strands
     * anything that sits in that band at maximum scroll, and it never
     * reveals. The reveal is worth less than the content. */
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('seen');
        obs.unobserve(en.target);
      });
    }, { rootMargin: '0px', threshold: 0 });
    document.querySelectorAll('.reveal').forEach(function (n) { io.observe(n); });

    /* Safety net: at the foot of the document nothing may still be hidden. */
    window.addEventListener('scroll', function () {
      if (window.scrollY + window.innerHeight >= document.body.scrollHeight - 4) revealAll();
    }, { passive: true });
  } else {
    revealAll();
  }

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

    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      if (open) panel.setAttribute('data-open', ''); else panel.removeAttribute('data-open');
      if (labelEl) labelEl.textContent = open ? labelClose : labelOpen;
      if (iconEl) iconEl.innerHTML = open ? iconClose : iconOpen;
    };

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    panel.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* ---------------------------------------------------------------- *
   * Quotation form.
   * Validates on submit, then on blur for fields already flagged.
   * Errors stay inline AND are summarised at the top, linked to fields.
   * ---------------------------------------------------------------- */
  var form = document.querySelector('[data-rfq]');
  if (!form) return;

  var summary = form.querySelector('[data-summary]');
  var summaryList = form.querySelector('[data-summary-list]');
  var submit = form.querySelector('[data-submit]');
  var done = form.querySelector('[data-done]');
  var live = form.querySelector('[data-live]');
  var fieldsWrap = form.querySelector('.fields');
  var submitted = false;

  var emailOk = function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); };

  function check(control) {
    var wrap = control.closest('[data-field]');
    if (!wrap) return true;
    var value = (control.value || '').trim();
    var bad = false;
    if (control.required && !value) bad = true;
    if (!bad && control.type === 'email' && value && !emailOk(value)) bad = true;

    var err = wrap.querySelector('.err');
    wrap.setAttribute('data-invalid', bad ? 'true' : 'false');
    control.setAttribute('aria-invalid', bad ? 'true' : 'false');
    if (err) err.querySelector('span').textContent = bad ? err.getAttribute('data-msg') : '';
    return !bad;
  }

  var controls = form.querySelectorAll('input, select, textarea');
  controls.forEach(function (c) {
    c.addEventListener('blur', function () {
      if (submitted || c.getAttribute('aria-invalid') === 'true') check(c);
    });
  });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    submitted = true;

    var broken = [];
    controls.forEach(function (c) { if (!check(c)) broken.push(c); });

    if (broken.length) {
      summaryList.innerHTML = '';
      broken.forEach(function (c) {
        var wrap = c.closest('[data-field]');
        var label = wrap.querySelector('label');
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = '#' + c.id;
        a.textContent = (label ? label.textContent : c.name).replace(/\s*\*\s*$/, '');
        a.addEventListener('click', function (e2) { e2.preventDefault(); c.focus(); });
        li.appendChild(a);
        summaryList.appendChild(li);
      });
      summary.hidden = false;
      summary.focus();
      if (live) live.textContent = summary.querySelector('.summary-title span').textContent;
      return;
    }

    summary.hidden = true;
    submit.disabled = true;
    submit.textContent = submit.getAttribute('data-busy');

    var payload = {};
    controls.forEach(function (c) { payload[c.name] = c.value; });

    var finish = function () {
      if (fieldsWrap) fieldsWrap.hidden = true;
      submit.hidden = true;
      done.hidden = false;
      done.focus();
      if (live) live.textContent = done.querySelector('.done-title span').textContent;
    };

    var endpoint = form.getAttribute('data-endpoint');
    if (endpoint) {
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          finish();
        })
        .catch(function () {
          // Never swallow a failure: hand the request back to the operator.
          submit.disabled = false;
          submit.textContent = submit.getAttribute('data-idle');
          mailto(payload);
        });
    } else {
      mailto(payload);
      finish();
    }
  });

  function mailto(payload) {
    var to = form.getAttribute('data-mailto');
    if (!to) return;
    var lines = Object.keys(payload).map(function (k) { return k + ': ' + payload[k]; });
    window.location.href =
      'mailto:' + to +
      '?subject=' + encodeURIComponent('Quotation request — ' + (payload.company || '')) +
      '&body=' + encodeURIComponent(lines.join('\n'));
  }
})();

/* ------------------------------------------------------------------ *
 * Basket — retail page only.
 *
 * Entirely client side: the basket lives in localStorage, so it survives
 * a reload and a language switch without a server, a cookie or an
 * account. Only the finished order leaves the browser.
 *
 * Every price comes from the markup, which build.py writes from
 * content/*.json. Nothing here invents, rounds or converts a figure, and
 * an item with no price has no add button at all.
 * ------------------------------------------------------------------ */
(function () {
  'use strict';

  var drawer = document.querySelector('[data-cart]');
  if (!drawer) return;

  var KEY = 'tly.cart.v1';
  var CUR = document.documentElement.getAttribute('data-currency') || '';
  var lines = drawer.querySelector('[data-cart-lines]');
  var emptyMsg = drawer.querySelector('[data-cart-empty]');
  var foot = drawer.querySelector('[data-cart-foot]');
  var subtotalEl = drawer.querySelector('[data-cart-subtotal]');
  var fab = document.querySelector('[data-cart-open]');
  var countEl = document.querySelector('[data-cart-count]');
  var veil = document.querySelector('[data-cart-veil]');
  var live = document.querySelector('[data-cart-live]');
  var labels = JSON.parse(drawer.getAttribute('data-labels') || '{}');
  var lastFocus = null;

  function read() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY));
      return Array.isArray(v) ? v.filter(valid) : [];
    } catch (e) { return []; }
  }
  function valid(l) {
    return l && typeof l.sku === 'string' && isFinite(l.price) && l.qty > 0;
  }
  function write(items) {
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) { /* private mode */ }
  }
  function fmt(n) {
    /* Integer dinars. Grouped with a narrow no-break space, which is the
     * French and Arabic convention and never collides with a decimal. */
    return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ' + CUR;
  }
  function say(msg) { if (live && msg) { live.textContent = ''; live.textContent = msg; } }

  function render() {
    var items = read();
    var total = 0, count = 0;
    lines.textContent = '';
    items.forEach(function (l, i) {
      total += l.price * l.qty;
      count += l.qty;
      var li = document.createElement('li');
      li.className = 'cart-line';

      var name = document.createElement('p');
      name.className = 'cart-name tnum';
      name.textContent = l.size;

      var unit = document.createElement('p');
      unit.className = 'cart-unit tnum';
      unit.textContent = fmt(l.price);

      var qty = document.createElement('div');
      qty.className = 'qty';
      qty.appendChild(stepper('-', labels.dec, i, -1));
      var n = document.createElement('span');
      n.className = 'qty-n tnum';
      n.setAttribute('aria-label', (labels.qty || '') + ' ' + l.size);
      n.textContent = l.qty;
      qty.appendChild(n);
      qty.appendChild(stepper('+', labels.inc, i, 1));

      var rm = document.createElement('button');
      rm.type = 'button';
      rm.className = 'cart-rm';
      rm.textContent = labels.remove || '×';
      rm.addEventListener('click', function () {
        var cur = read(); cur.splice(i, 1); write(cur); render();
        say(labels.removed);
      });

      li.appendChild(name); li.appendChild(unit); li.appendChild(qty); li.appendChild(rm);
      lines.appendChild(li);
    });

    emptyMsg.hidden = items.length > 0;
    foot.hidden = items.length === 0;
    if (subtotalEl) subtotalEl.textContent = fmt(total);
    if (countEl) countEl.textContent = count;
    if (fab) fab.hidden = count === 0;
    syncOrder(items, total);
  }

  function stepper(glyph, label, index, delta) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'qty-btn';
    b.textContent = glyph;
    b.setAttribute('aria-label', label || glyph);
    b.addEventListener('click', function () {
      var cur = read();
      if (!cur[index]) return;
      cur[index].qty = Math.max(0, Math.min(99, cur[index].qty + delta));
      if (cur[index].qty === 0) cur.splice(index, 1);
      write(cur); render();
    });
    return b;
  }

  /* ---- add ------------------------------------------------------- */
  document.querySelectorAll('[data-add]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var price = parseFloat(btn.getAttribute('data-price'));
      if (!isFinite(price)) return;            /* never basket an unpriced item */
      var sku = btn.getAttribute('data-sku');
      var items = read();
      var found = items.filter(function (l) { return l.sku === sku; })[0];
      if (found) found.qty = Math.min(99, found.qty + 1);
      else items.push({ sku: sku, size: btn.getAttribute('data-size'), price: price, qty: 1 });
      write(items); render(); open();
      say(labels.added_live);
    });
  });

  /* ---- open / close ---------------------------------------------- */
  function open() {
    lastFocus = document.activeElement;
    drawer.hidden = false; if (veil) veil.hidden = false;
    document.body.classList.add('cart-on');
    var close = drawer.querySelector('[data-cart-close]');
    if (close) close.focus();
  }
  function close() {
    drawer.hidden = true; if (veil) veil.hidden = true;
    document.body.classList.remove('cart-on');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (fab) fab.addEventListener('click', open);
  if (veil) veil.addEventListener('click', close);
  drawer.querySelectorAll('[data-cart-close]').forEach(function (b) {
    b.addEventListener('click', close);
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && !drawer.hidden) close();
  });
  /* A dialog that lets focus wander behind it is not a dialog. */
  drawer.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Tab') return;
    var f = drawer.querySelectorAll('button, a[href], input, select, textarea');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
    else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
  });

  /* ---- order summary + submission -------------------------------- */
  var form = document.querySelector('[data-order]');
  var sumLines = document.querySelector('[data-summary-lines]');
  var sumTotal = document.querySelector('[data-summary-total]');

  function syncOrder(items, total) {
    if (!sumLines) return;
    sumLines.textContent = '';
    items.forEach(function (l) {
      var li = document.createElement('li');
      li.className = 'tnum';
      li.textContent = l.qty + ' × ' + l.size + '  ' + fmt(l.price * l.qty);
      sumLines.appendChild(li);
    });
    if (sumTotal) sumTotal.textContent = fmt(total);
    var box = document.querySelector('[data-order-summary]');
    if (box) box.hidden = items.length === 0;
  }

  if (form) {
    /* Collection needs no address; delivery does. */
    var modes = form.querySelectorAll('input[name="mode"]');
    var addrFields = ['wilaya', 'commune', 'address'];
    function applyMode() {
      var pickup = form.querySelector('input[name="mode"]:checked').value === 'pickup';
      addrFields.forEach(function (n) {
        var p = form.querySelector('.field-' + n);
        var input = form.querySelector('[name="' + n + '"]');
        if (!p || !input) return;
        p.hidden = pickup;
        if (pickup) input.removeAttribute('required');
        else input.setAttribute('required', '');
      });
    }
    modes.forEach(function (m) { m.addEventListener('change', applyMode); });
    applyMode();

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var items = read();
      var box = form.querySelector('[data-summary]');
      var list = form.querySelector('[data-summary-list]');
      list.textContent = '';

      if (!items.length) {
        var li = document.createElement('li');
        li.textContent = form.getAttribute('data-empty-warning');
        list.appendChild(li); box.hidden = false; box.focus();
        return;
      }
      var bad = [];
      form.querySelectorAll('input[required], select[required], textarea[required]')
        .forEach(function (f) {
          var p = f.closest('.field');
          var err = form.querySelector('[data-err="' + f.id + '"]');
          var ok = f.checkValidity() && f.value.trim() !== '';
          if (err) err.hidden = ok;
          if (p) p.classList.toggle('is-bad', !ok);
          f.setAttribute('aria-invalid', ok ? 'false' : 'true');
          if (!ok) bad.push(f);
        });
      if (bad.length) {
        bad.forEach(function (f) {
          var li = document.createElement('li');
          var a = document.createElement('a');
          a.href = '#' + f.id;
          a.textContent = (form.querySelector('label[for="' + f.id + '"]') || {}).textContent || f.name;
          a.addEventListener('click', function (e) { e.preventDefault(); f.focus(); });
          li.appendChild(a); list.appendChild(li);
        });
        box.hidden = false; box.focus();
        return;
      }
      box.hidden = true;

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.order = items.map(function (l) {
        return l.qty + ' × ' + l.size + ' = ' + Math.round(l.price * l.qty) + ' ' + CUR;
      }).join('\n');
      data.total = Math.round(items.reduce(function (s, l) { return s + l.price * l.qty; }, 0)) + ' ' + CUR;

      var submit = form.querySelector('[data-submit]');
      submit.disabled = true;
      submit.textContent = submit.getAttribute('data-busy');

      function finish() {
        form.querySelector('[data-done]').hidden = false;
        form.querySelector('[data-done]').focus();
        form.querySelector('.fields').hidden = true;
        submit.hidden = true;
        write([]); render();
      }
      function fallback() {
        submit.disabled = false;
        submit.textContent = submit.getAttribute('data-idle');
        var to = form.getAttribute('data-mailto');
        if (!to) return;
        var body = Object.keys(data).map(function (k) { return k + ': ' + data[k]; }).join('\n');
        window.location.href = 'mailto:' + to +
          '?subject=' + encodeURIComponent('Commande — ' + (data.name || '')) +
          '&body=' + encodeURIComponent(body);
      }

      var endpoint = form.getAttribute('data-endpoint');
      if (endpoint) {
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(data)
        }).then(function (r) {
          if (!r.ok) throw new Error(r.status);
          finish();
        }).catch(fallback);
      } else {
        fallback();
      }
    });

    /* WhatsApp carries the same order as the form, pre-written. */
    var waLink = form.querySelector('[data-wa-order]');
    if (waLink) {
      waLink.addEventListener('click', function () {
        var items = read();
        if (!items.length) return;
        var txt = items.map(function (l) { return l.qty + ' × ' + l.size; }).join('\n');
        waLink.href = waLink.href.split('?')[0] + '?text=' + encodeURIComponent(txt);
      });
    }
  }

  render();
})();
