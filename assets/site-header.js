// iOS Safari only evaluates :active on an element (and thus only paints the
// LED-lighting `.site-nav a:active`, `.btn:active`, etc. across the site)
// when the page has at least one touch listener somewhere in the document --
// with none registered, tapping a hardware button on a phone gave no
// feedback at all, since :hover doesn't fire on touch and :active was never
// being evaluated to begin with. An empty, passive, document-level listener
// is the standard fix: it costs nothing and turns :active back on everywhere.
document.addEventListener('touchstart', function () {}, { passive: true });

// Mark the LCD's own app as selected so the closed label (and the checkmark
// in the open list) reflect where we actually are, not just "-Select-".
// Matched on filename rather than the full option value because index.html's
// options are relative ("apps/x.html") while every app page's options are
// root-relative ("/apps/x.html") -- both resolve fine as hrefs, but neither
// string equals location.pathname on its own.
(function () {
  var here = location.pathname.split('/').pop() || 'index.html';
  var sels = document.querySelectorAll('#siteAppSelect');
  for (var i = 0; i < sels.length; i++) {
    var opts = sels[i].querySelectorAll('option');
    for (var j = 0; j < opts.length; j++) {
      var file = (opts[j].getAttribute('value') || '').split('/').pop();
      if (file && file === here) opts[j].selected = true;
    }
  }
})();

// Inject the non-interactive <button><selectedcontent> child into selects
// so the closed label can ellipsise the long text exactly like the app.
function wireSelectEllipsis(root) {
  var sels = (root || document).querySelectorAll('select');
  for (var i = 0; i < sels.length; i++) {
    if (sels[i].querySelector(':scope > button')) continue;
    var b = document.createElement('button');
    b.setAttribute('tabindex', '-1');
    b.appendChild(document.createElement('selectedcontent'));
    sels[i].insertBefore(b, sels[i].firstChild);
  }
}
wireSelectEllipsis();
var selPassQueued = false;
function queueSelectPass() {
  if (selPassQueued) return; selPassQueued = true;
  requestAnimationFrame(function () { selPassQueued = false; wireSelectEllipsis(); });
}
new MutationObserver(function (recs) {
  for (var i = 0; i < recs.length; i++) {
    var t = recs[i].target;
    if (t && t.tagName === 'SELECT') { queueSelectPass(); return; }
    var added = recs[i].addedNodes;
    for (var k = 0; k < added.length; k++) {
      var n = added[k]; if (!(n instanceof HTMLElement)) continue;
      if (n.tagName === 'SELECT' || n.querySelector('select')) { queueSelectPass(); return; }
    }
  }
}).observe(document.body, { childList: true, subtree: true });

// Custom popup picker for the header .hero-lcd-select to reproduce
// MutationStation's open-list exactly across all browsers.
(function () {
  var popup = document.createElement('div');
  popup.className = 'hero-lcd-popup';
  document.body.appendChild(popup);

  function closePopup() {
    popup.classList.remove('open'); popup.style.left = popup.style.top = '';
    popup.innerHTML = '';
    document.removeEventListener('click', outsideListener);
    document.removeEventListener('keydown', keyListener);
  }

  function outsideListener(e) {
    if (!popup.contains(e.target) && !currentTrigger.contains(e.target)) closePopup();
  }
  function keyListener(e) {
    if (e.key === 'Escape') closePopup();
  }

  var currentTrigger = null;

  function buildOptionsFromSelect(sel) {
    popup.innerHTML = '';
    var opts = sel.querySelectorAll('option');
    for (var i = 0; i < opts.length; i++) {
      (function(opt){
        var row = document.createElement('div');
        row.className = 'opt';
        row.textContent = opt.textContent;
        row.dataset.value = opt.value;
        if (opt.selected) row.setAttribute('aria-selected', 'true');
        if (opt.disabled) row.setAttribute('aria-disabled','true');
        row.addEventListener('click', function () {
          if (opt.disabled) return;
          sel.value = opt.value;
          sel.dispatchEvent(new Event('change', { bubbles: true }));
          closePopup();
          if (opt.value) location.href = opt.value;
        });
        popup.appendChild(row);
      })(opts[i]);
    }
  }

  function openFor(selectEl, triggerEl) {
    currentTrigger = triggerEl || selectEl;
    buildOptionsFromSelect(selectEl);
    // The injected <button> lives inside a <select>, which browsers without
    // the customizable-select API never lay out (its rect is always
    // 0,0,0,0) -- anchor off the <select> itself instead, which is always
    // rendered and sized.
    var rect = selectEl.getBoundingClientRect();
    popup.style.left = (rect.left) + 'px';
    popup.style.top = (rect.bottom + 6) + 'px';
    popup.style.minWidth = Math.max(140, rect.width) + 'px';
    popup.classList.add('open');
    setTimeout(function(){
      document.addEventListener('click', outsideListener);
      document.addEventListener('keydown', keyListener);
    }, 0);
  }

  // The <select> itself has pointer-events:none (styles.css) so that engines
  // without `appearance: base-select` support (Safari, Firefox, older
  // Chrome) can never fall through to their own native popup -- instead an
  // invisible overlay button, sized/positioned to match the select exactly,
  // owns every click and keypress and always opens .hero-lcd-popup. This
  // replaces an earlier approach that hooked the injected <button> child
  // (from wireSelectEllipsis) directly: that button is only hit-testable in
  // engines that support customizable <select>, so on Safari the click went
  // straight through to the real native control instead.
  function attachToHeroSelects(root) {
    var sels = (root || document).querySelectorAll('select.hero-lcd-select');
    for (var i = 0; i < sels.length; i++) {
      (function(sel){
        if (sel._heroHooked) { positionOverlay(sel); return; }
        sel._heroHooked = true;
        var ov = document.createElement('button');
        ov.type = 'button';
        ov.className = 'hero-lcd-overlay';
        ov.setAttribute('aria-hidden', 'true');
        sel._heroOverlay = ov;
        document.body.appendChild(ov);
        positionOverlay(sel);
        ov.addEventListener('click', function (e) {
          e.preventDefault(); e.stopPropagation();
          if (popup.classList.contains('open')) { closePopup(); return; }
          openFor(sel, ov);
        });
        ov.addEventListener('keydown', function (ev) {
          if (ev.key === 'Enter' || ev.key === ' ' || ev.key === 'ArrowDown') { ev.preventDefault(); openFor(sel, ov); }
        });
      })(sels[i]);
    }
  }

  function positionOverlay(sel) {
    var ov = sel._heroOverlay; if (!ov) return;
    var r = sel.getBoundingClientRect();
    ov.style.left = (r.left + window.scrollX) + 'px';
    ov.style.top = (r.top + window.scrollY) + 'px';
    ov.style.width = r.width + 'px';
    ov.style.height = r.height + 'px';
  }

  function positionAllOverlays() {
    var sels = document.querySelectorAll('select.hero-lcd-select');
    for (var i = 0; i < sels.length; i++) positionOverlay(sels[i]);
  }

  attachToHeroSelects(document);
  window.addEventListener('resize', positionAllOverlays);
  window.addEventListener('scroll', positionAllOverlays, true);
  // re-run when the DOM changes (e.g. wireSelectEllipsis inserting buttons,
  // or a select being added later) so new/moved selects get an overlay too
  var mo = new MutationObserver(function(recs){ attachToHeroSelects(document); });
  mo.observe(document.body, { childList: true, subtree: true });
})();

// GLOBAL SCROLL REPLACEMENT -- both wheel and touch hijacking removed.
// This used to intercept wheel events with `preventDefault()` + a manual
// `window.scrollBy(dy)` per tick, on the theory that the right-edge
// Juno-style fader should be the "primary scroll control". Touch was
// hijacked the same way first, and was removed 2026-08-17: on an actual
// touchscreen that replaces the OS's native touch-scroll -- which batches
// input and drives scrolling with real momentum/inertia off the compositor
// thread -- with a synchronous JS scrollBy on every single touchmove, which
// read as "extremely extremely slow" scrolling on mobile (no momentum, no
// deceleration, one janky jump per finger movement).
//
// 2026-08-18: a report of "very slow scroll" on a non-Mac laptop turned out
// to be the exact same defect on wheel input, just needing a different
// device to surface it. macOS trackpads batch a whole gesture into a
// handful of large-delta wheel events, so the per-event synchronous
// scrollBy was cheap enough there to feel fine; a Windows precision
// touchpad (or a plain mouse wheel) fires many more, smaller-delta wheel
// events per gesture, and the same hijack loop that was invisible on the
// machine this was built on became visibly janky elsewhere. Fix is the
// same as the touch fix: stop hijacking, let the OS drive native (smooth,
// momentum, off-thread) wheel scrolling. The fader cap still tracks scroll
// position fine via `updateFromScroll` below, which listens for the native
// `scroll` event regardless of what produced it -- it never needed to be
// the thing driving the scroll, only the thing displaying it.

// Page-level fader: fixed Juno-style fader on the right edge of the page.
(function(){
  var pf = document.createElement('div');
  pf.className = 'page-fader';
  pf.innerHTML = '<div class="fader-slot"><div class="fader-fill"></div></div><div class="fader-cap" tabindex="0" role="slider" aria-orientation="vertical"></div>';
  document.body.appendChild(pf);

  var slot = pf.querySelector('.fader-slot');
  var fill = pf.querySelector('.fader-fill');
  var cap = pf.querySelector('.fader-cap');

  // styles.css's `top: 74px` clears the desktop header's single row, but
  // the mobile header wraps to two rows (see the 720px breakpoint) and is
  // taller, so a fixed top landed the fader's track inside the header/body
  // copy. Measure the real header instead, with the same ~15px gap the CSS
  // value already used, and re-measure on resize/orientation change.
  var header = document.querySelector('.site-header');
  function positionFader() {
    if (!header) return;
    pf.style.top = (header.getBoundingClientRect().bottom + 15) + 'px';
  }
  positionFader();
  window.addEventListener('resize', positionFader);

  // Gumroad's overlay (assets.gumroad.com/js/gumroad-bundle.js) builds its
  // checkout popup as a shadow-DOM host appended to document.body with
  // style.zIndex = "999999", and only ever sets document.body.style.overflow
  // to "hidden" while that popup is open/visible -- there's no other public
  // signal. Reading the bundle source directly confirmed the checkout
  // <iframe> auto-sizes to its own content height via a `{type:"height"}`
  // postMessage (h.style.height = ...), so the iframe itself never scrolls;
  // the actual scrolling happens on the *wrapper* div around it
  // (className "fixed inset-0 overflow-scroll bg-backdrop", inside the open
  // shadow root). That wrapper is a normal element reachable via
  // shadowHost.shadowRoot.querySelector(...), so the fader can drive it
  // exactly like it drives window scroll -- the cross-origin iframe boundary
  // never has to be crossed.
  function getOverlayScroller() {
    var kids = document.body.children;
    for (var i = kids.length - 1; i >= 0; i--) {
      var sr = kids[i].shadowRoot;
      if (sr) {
        var scroller = sr.querySelector('.overflow-scroll');
        if (scroller) return scroller;
      }
    }
    return null;
  }

  function overlayEl() {
    return document.body.style.overflow === 'hidden' ? getOverlayScroller() : null;
  }

  // Reported flicker while Gumroad's checkout iframe is open turned out to
  // line up with this: the iframe reports its content height to the overlay
  // via postMessage repeatedly as its own view changes (product -> login ->
  // account, each a different height), and each report fired both the
  // MutationObserver below (body style churns as Gumroad toggles its own
  // scroll-lock) and this ResizeObserver, each running a synchronous
  // updateFromScroll -> positionFader (a getBoundingClientRect + style write)
  // back to back, same frame. Individually cheap; in a burst of several per
  // second it reads as jank. Coalescing bursts into one rAF-scheduled update
  // costs nothing when they're not bursting (a burst of 1 still updates next
  // frame) and removes the redundant synchronous layout work when they are.
  var updateScheduled = false;
  function scheduleUpdate() {
    if (updateScheduled) return;
    updateScheduled = true;
    requestAnimationFrame(function () { updateScheduled = false; updateFromScroll(); });
  }

  var overlayScrollWired = null;
  var overlayResizeObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(function(){ scheduleUpdate(); }) : null;
  function ensureOverlayScrollListener() {
    var el = overlayEl();
    if (el && el !== overlayScrollWired) {
      el.addEventListener('scroll', updateFromScroll, { passive: true });
      // The checkout iframe reports its real content height to the overlay
      // asynchronously (a postMessage after the popup is already open), so
      // the wrapper's scrollHeight -- and therefore whether the fader has
      // anything to show -- keeps changing for a moment after open. A
      // ResizeObserver on the wrapper catches that instead of leaving the
      // fader hidden/stale until the visitor happens to scroll first.
      if (overlayResizeObserver) overlayResizeObserver.observe(el);
      // The fader takes over as the overlay's scroll control (see the
      // z-index bump above), but Gumroad's own ".overflow-scroll" wrapper is
      // still a plain scrollable element with its own native browser
      // scrollbar -- reported as "double scrolls (our Juno one and the
      // gumroad scroll)". html/body's scrollbar is hidden site-wide (top of
      // this file's styles.css), but that rule can't reach across the shadow
      // boundary into Gumroad's own root, so the wrapper needs it set
      // directly. `scrollbar-width`/`-ms-overflow-style` are plain CSS
      // properties settable inline; the `::-webkit-scrollbar` pseudo-element
      // is not, so that half is a tiny stylesheet injected into the shadow
      // root once (guarded by a data attribute so re-opening the popup
      // doesn't inject it twice).
      el.style.scrollbarWidth = 'none';
      el.style.msOverflowStyle = 'none';
      var root = el.getRootNode();
      if (root && root.host && !root.host.hasAttribute('data-juno-scrollbar-hidden')) {
        var style = document.createElement('style');
        style.textContent = '.overflow-scroll::-webkit-scrollbar{width:0;height:0;display:none;}';
        root.appendChild(style);
        root.host.setAttribute('data-juno-scrollbar-hidden', '');
      }
      overlayScrollWired = el;
    }
  }

  // The fader (z-index 60) would otherwise sit visually beneath the
  // overlay's shadow host (z-index 999999). Bump it above the overlay only
  // while the overlay is open, so it stays reachable as the popup's scroll
  // control instead of disappearing under it.
  new MutationObserver(function(){
    pf.classList.toggle('on-overlay', document.body.style.overflow === 'hidden');
    ensureOverlayScrollListener();
    scheduleUpdate();
  }).observe(document.body, { attributes: true, attributeFilter: ['style'] });

  function updateFromScroll() {
    positionFader();
    var target = overlayEl();
    var scrollTop, scrollable;
    if (target) {
      ensureOverlayScrollListener();
      scrollTop = target.scrollTop;
      scrollable = Math.max(0, target.scrollHeight - target.clientHeight);
    } else {
      var doc = document.documentElement;
      scrollTop = window.scrollY || doc.scrollTop;
      scrollable = Math.max(0, doc.scrollHeight - window.innerHeight);
    }
    if (scrollable <= 0) { pf.style.display = 'none'; return; }
    pf.style.display = 'block';
    var ratio = scrollTop / scrollable;
    var slotH = slot.clientHeight;
    var capH = cap.clientHeight || 16;
    // `bottom` is a distance from the track's BOTTOM edge, so driving it
    // directly from `ratio` put the cap at the bottom of the track at
    // scrollTop 0 and walked it upward while scrolling down -- backwards
    // from the expected top-to-bottom scrollbar-style motion. Inverting the
    // ratio here (1 - ratio) puts the cap at the top of the track on load
    // and lets it descend as the page scrolls down.
    var bottomPx = Math.round((1 - ratio) * Math.max(0, slotH - capH));
    cap.style.bottom = bottomPx + 'px';
    // Fill height must track the cap's own center, in the same px space as
    // bottomPx above -- deriving this from `ratio * 100%` independently (the
    // previous approach) only agreed with the cap at the very top/bottom of
    // the scroll range, so the LED fill visibly led or lagged the handle
    // everywhere in between.
    var fillPx = Math.min(slotH, Math.max(2, bottomPx + capH / 2));
    fill.style.height = fillPx + 'px';
  }

  window.addEventListener('scroll', updateFromScroll, { passive: true });
  window.addEventListener('resize', updateFromScroll);
  setTimeout(updateFromScroll, 50);

  // dragging behaviour
  function scrollTarget() {
    var el = overlayEl();
    if (el) {
      return {
        scrollable: Math.max(0, el.scrollHeight - el.clientHeight),
        current: el.scrollTop,
        to: function(top){ el.scrollTop = top; }
      };
    }
    return {
      scrollable: Math.max(0, document.documentElement.scrollHeight - window.innerHeight),
      current: window.scrollY,
      to: function(top){ window.scrollTo({ top: top, behavior: 'auto' }); }
    };
  }
  function scrollByTarget(delta, smooth) {
    var el = overlayEl();
    if (el) { el.scrollTop += delta; return; }
    window.scrollBy({ top: delta, behavior: smooth ? 'smooth' : 'auto' });
  }

  var dragging = false; var startY = 0; var startRatio = 0;
  cap.addEventListener('pointerdown', function(ev){ ev.preventDefault(); cap.setPointerCapture(ev.pointerId); dragging=true; startY = ev.clientY; var t = scrollTarget(); startRatio = t.scrollable>0 ? t.current/t.scrollable : 0; });
  // `dy` used to be `startY - ev.clientY` (positive when the pointer moves
  // UP), which matched a `bottomPx = ratio * range` cap mapping -- ratio and
  // scroll both rose as the cap rose. `updateFromScroll` above now inverts
  // that mapping (`bottomPx = (1 - ratio) * range`) so the cap sits at the
  // TOP on load and descends as the page scrolls, but this drag math was
  // never flipped to match: dragging the handle down still increased `dy`
  // the old (now backwards) way, so a downward drag decreased scroll instead
  // of increasing it. Flipping the sign here (`ev.clientY - startY`) makes a
  // downward drag increase `ratio`/scroll, back in step with the cap's own
  // now-inverted on-screen direction.
  cap.addEventListener('pointermove', function(ev){ if(!dragging) return; var dy = ev.clientY - startY; var slotH = slot.clientHeight; var frac = dy / slotH; var newRatio = Math.min(1, Math.max(0, startRatio + frac)); var t = scrollTarget(); t.to(Math.round(newRatio * t.scrollable)); });
  cap.addEventListener('pointerup', function(ev){ dragging=false; try{ cap.releasePointerCapture(ev.pointerId); }catch(e){} });
  cap.addEventListener('pointercancel', function(){ dragging=false; });
  cap.addEventListener('keydown', function(ev){ var t = scrollTarget(); if (t.scrollable<=0) return; var step = Math.max(40, Math.round(window.innerHeight/10)); if (ev.key==='ArrowUp'){ scrollByTarget(-step, true); ev.preventDefault(); } if (ev.key==='ArrowDown'){ scrollByTarget(step, true); ev.preventDefault(); } if (ev.key==='PageUp'){ scrollByTarget(-window.innerHeight, true); ev.preventDefault(); } if (ev.key==='PageDown'){ scrollByTarget(window.innerHeight, true); ev.preventDefault(); } });
})();
