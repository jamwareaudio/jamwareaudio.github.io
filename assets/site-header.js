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

// GLOBAL SCROLL REPLACEMENT
// Capture wheel/touch events and route them to page scrolling so the
// right-edge Juno-style fader becomes the primary scroll control.
// Respects focused form controls and modifier keys (Ctrl/Meta/Alt) so we
// avoid breaking expected platform behaviours (zoom, shortcuts, typing).
(function wireGlobalScrollReplacement(){
  var enabled = true;
  function shouldIgnoreEvent(e){
    // allow shortcuts (zoom / platform gestures)
    if (e.ctrlKey || e.metaKey || e.altKey) return true;
    // if a form control has focus, do not hijack
    var af = document.activeElement;
    if (!af) return false;
    var tag = (af.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
    if (af.isContentEditable) return true;
    return false;
  }

  function wheelHandler(e){
    if (!enabled) return;
    if (shouldIgnoreEvent(e)) return;
    // if the event target itself is a scrollable element (not body), let it be
    // unless you really want global-only. We treat body/document as target.
    var t = e.target;
    while (t && t !== document.body && t !== document.documentElement){
      try{
        if (t.scrollHeight > t.clientHeight) return; // let inner scrolls pass
      } catch(err) { break; }
      t = t.parentElement;
    }

    e.preventDefault();
    var delta = e.deltaY;
    if (e.deltaMode === 1) delta *= 24; // line -> pixels
    if (e.deltaMode === 2) delta *= window.innerHeight; // page -> pixels
    // Scale a touchpad delta slightly for a similar feel to a fader
    delta = Math.round(delta * 1.0);
    window.scrollBy({ top: delta, left: 0, behavior: 'auto' });
  }

  var lastTouchY = null;
  function touchStart(e){ if (e.touches && e.touches[0]) lastTouchY = e.touches[0].clientY; }
  function touchMove(e){
    if (!enabled) return; if (!lastTouchY) { if (e.touches && e.touches[0]) lastTouchY = e.touches[0].clientY; return; }
    if (shouldIgnoreEvent(e)) return;
    var y = e.touches[0].clientY; var dy = lastTouchY - y; lastTouchY = y;
    e.preventDefault();
    window.scrollBy({ top: Math.round(dy), left: 0, behavior: 'auto' });
  }
  function touchEnd(){ lastTouchY = null; }

  // Keyboard focus on the fader already handles keys; we don't capture keys globally.

  window.addEventListener('wheel', wheelHandler, { passive: false });
  window.addEventListener('touchstart', touchStart, { passive: false });
  window.addEventListener('touchmove', touchMove, { passive: false });
  window.addEventListener('touchend', touchEnd, { passive: true });

  // Expose a toggle for debugging or temporary disable via window
  window.__junoGlobalFader = {
    enabled: function(v){ if (typeof v === 'boolean') enabled = !!v; return enabled; }
  };
})();

// Page-level fader: fixed Juno-style fader on the right edge of the page.
(function(){
  var pf = document.createElement('div');
  pf.className = 'page-fader';
  pf.innerHTML = '<div class="fader-slot"><div class="fader-fill"></div></div><div class="fader-cap" tabindex="0" role="slider" aria-orientation="vertical"></div>';
  document.body.appendChild(pf);

  var slot = pf.querySelector('.fader-slot');
  var fill = pf.querySelector('.fader-fill');
  var cap = pf.querySelector('.fader-cap');

  function updateFromScroll() {
    var doc = document.documentElement;
    var scrollTop = window.scrollY || doc.scrollTop;
    var scrollable = Math.max(0, doc.scrollHeight - window.innerHeight);
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
  var dragging = false; var startY = 0; var startRatio = 0;
  cap.addEventListener('pointerdown', function(ev){ ev.preventDefault(); cap.setPointerCapture(ev.pointerId); dragging=true; startY = ev.clientY; var scrollable = Math.max(0, document.documentElement.scrollHeight - window.innerHeight); startRatio = scrollable>0 ? window.scrollY/scrollable : 0; });
  cap.addEventListener('pointermove', function(ev){ if(!dragging) return; var dy = startY - ev.clientY; var slotH = slot.clientHeight; var frac = dy / slotH; var newRatio = Math.min(1, Math.max(0, startRatio + frac)); var scrollable = Math.max(0, document.documentElement.scrollHeight - window.innerHeight); window.scrollTo({ top: Math.round(newRatio * scrollable), behavior: 'auto' }); });
  cap.addEventListener('pointerup', function(ev){ dragging=false; try{ cap.releasePointerCapture(ev.pointerId); }catch(e){} });
  cap.addEventListener('pointercancel', function(){ dragging=false; });
  cap.addEventListener('keydown', function(ev){ var scrollable = Math.max(0, document.documentElement.scrollHeight - window.innerHeight); if (scrollable<=0) return; var step = Math.max(40, Math.round(window.innerHeight/10)); if (ev.key==='ArrowUp'){ window.scrollBy({ top: -step, behavior:'smooth' }); ev.preventDefault(); } if (ev.key==='ArrowDown'){ window.scrollBy({ top: step, behavior:'smooth' }); ev.preventDefault(); } if (ev.key==='PageUp'){ window.scrollBy({ top: -window.innerHeight, behavior:'smooth' }); ev.preventDefault(); } if (ev.key==='PageDown'){ window.scrollBy({ top: window.innerHeight, behavior:'smooth' }); ev.preventDefault(); } });
})();
