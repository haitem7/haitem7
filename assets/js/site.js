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
   * Scroll-scrubbed hero.
   * Frames are drawn to a canvas rather than seeking a video: seeking a
   * compressed stream on scroll stutters, and iOS Safari refuses to seek
   * smoothly at all. Opt-in on the same three conditions as any other
   * heavy enhancement -- wide viewport, unmetered connection, motion
   * allowed -- so a phone downloads nothing.
   * ---------------------------------------------------------------- */
  var stage = document.querySelector('[data-hero-scroll]');
  var canvas = document.querySelector('[data-hero-canvas]');

  if (stage && canvas) {
    var count = parseInt(stage.getAttribute('data-frame-count'), 10) || 0;
    var conn = navigator.connection || {};
    var metered = conn.saveData === true ||
                  /(^|-)2g$/.test(conn.effectiveType || '') ||
                  conn.effectiveType === 'slow-2g';
    var roomy = window.matchMedia('(min-width: 62rem)').matches;

    if (count && roomy && !metered && !reduced.matches) {
      var base = stage.getAttribute('data-frame-base');
      var ext = stage.getAttribute('data-frame-ext') || '.webp';
      var pad = parseInt(stage.getAttribute('data-frame-pad'), 10) || 3;
      var ctx = canvas.getContext('2d', { alpha: false });
      var frames = new Array(count);
      var current = -1;
      var failed = 0;

      var name = function (i) {
        var s = String(i + 1);
        while (s.length < pad) s = '0' + s;
        return base + s + ext;
      };

      var paint = function (i) {
        var img = frames[i];
        if (!img || !img.complete || !img.naturalWidth) return;
        var cw = canvas.width, ch = canvas.height;
        var scale = Math.max(cw / img.naturalWidth, ch / img.naturalHeight);
        var w = img.naturalWidth * scale, h = img.naturalHeight * scale;
        ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
        current = i;
      };

      var size = function () {
        var r = canvas.getBoundingClientRect();
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(r.width * dpr);
        canvas.height = Math.round(r.height * dpr);
        var i = current;
        current = -1;
        paint(i < 0 ? 0 : i);
      };

      var frameFor = function () {
        var r = stage.getBoundingClientRect();
        var travel = stage.offsetHeight - window.innerHeight;
        if (travel <= 0) return 0;
        var p = Math.min(1, Math.max(0, -r.top / travel));
        return Math.round(p * (count - 1));
      };

      // Distinct names on purpose: `var` is function scoped, and the
      // header below declares its own ticking/onScroll in this same
      // function. Sharing them makes the two handlers steal each other's
      // guard flag, and the scrub silently stops repainting.
      var scrubTicking = false;
      var onScrubScroll = function () {
        if (scrubTicking) return;
        scrubTicking = true;
        requestAnimationFrame(function () {
          var i = frameFor();
          if (i !== current) paint(i);
          scrubTicking = false;
        });
      };

      // The section takes its full height immediately, so the page never
      // reflows under the reader once the frames arrive.
      stage.classList.add('is-scrubbing');
      size();

      for (var i = 0; i < count; i++) {
        (function (i) {
          var img = new Image();
          img.decoding = 'async';
          img.onload = function () {
            if (i === 0) {
              size();
              canvas.classList.add('is-ready');
              window.addEventListener('scroll', onScrubScroll, { passive: true });
              onScrubScroll();
            }
          };
          img.onerror = function () {
            failed++;
            // Every frame missing means the sequence was never deployed:
            // give the height back and let the CSS oil field stand alone.
            if (failed >= count) {
              stage.classList.remove('is-scrubbing');
              canvas.remove();
            }
          };
          img.src = name(i);
          frames[i] = img;
        })(i);
      }

      window.addEventListener('resize', size, { passive: true });
    } else {
      canvas.remove();
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
