// Masonry for the closing .panel-grid group (see the CSS comment above
// .panel-grid in styles.css for why plain `columns: 3 320px` balancing was
// replaced by this). The grid starts as a flat flex-wrap row of .panel
// children; this reparents them into per-column .panel-grid-col stacks,
// picking each panel's column with a shortest-column-first greedy placement
// instead of trusting CSS's single-estimate column balance.
(function () {
  function layoutPanelGrid(grid) {
    // Undo any previous masonry pass first, back to flat flex-wrap children --
    // that's what lets flex-wrap pick the column count fresh for whatever
    // width we're laying out at now, rather than reusing a stale count from
    // the last viewport size.
    var existingCols = grid.querySelectorAll(':scope > .panel-grid-col');
    if (existingCols.length) {
      var flat = [];
      existingCols.forEach(function (col) {
        flat.push.apply(flat, col.children);
      });
      flat.forEach(function (panel) { grid.appendChild(panel); });
      // The unwrap above only drains each col's children out to the grid --
      // the now-empty .panel-grid-col wrapper itself is still sitting in the
      // grid as a dead sibling. Left in place, every re-layout (fonts.ready,
      // each debounced resize) stacks another empty wrapper on top of the
      // last, which is exactly the "extra blank column" bug this reset step
      // exists to prevent. Remove the drained wrappers explicitly.
      existingCols.forEach(function (col) { col.remove(); });
    }

    var panels = Array.prototype.slice.call(grid.querySelectorAll(':scope > .panel'));
    if (panels.length < 2) return;

    // How many columns did flex-wrap actually give us? Count panels sharing
    // the first panel's top edge, rather than recomputing the 320px/24px
    // breakpoint math here -- that keeps this in sync with the CSS
    // automatically if the track width or gap ever changes.
    var firstTop = panels[0].getBoundingClientRect().top;
    var colCount = panels.filter(function (p) {
      return Math.abs(p.getBoundingClientRect().top - firstTop) < 1;
    }).length;
    if (colCount < 2) return; // one column: flex-wrap's own stacking is already right

    var heights = panels.map(function (p) { return p.getBoundingClientRect().height; });

    var colHeights = new Array(colCount).fill(0);
    var colEls = [];
    for (var i = 0; i < colCount; i++) {
      var col = document.createElement('div');
      col.className = 'panel-grid-col';
      colEls.push(col);
    }
    panels.forEach(function (p, i) {
      var shortest = 0;
      for (var c = 1; c < colCount; c++) {
        if (colHeights[c] < colHeights[shortest]) shortest = c;
      }
      colEls[shortest].appendChild(p);
      colHeights[shortest] += heights[i];
    });
    colEls.forEach(function (col) { grid.appendChild(col); });
  }

  function layoutAll() {
    var grids = document.querySelectorAll('.panel-grid');
    for (var i = 0; i < grids.length; i++) layoutPanelGrid(grids[i]);
  }

  layoutAll();
  // Panel heights depend on the loaded font metrics, not just markup --
  // re-run once webfonts land in case that shifted line counts.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(layoutAll);

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(layoutAll, 150);
  });
})();
