// Builds the map scenes from window.MAPS (see build_page.py). Natural Earth 1:50m via world-atlas.
window.buildMaps = function () {
  const NS = 'http://www.w3.org/2000/svg';
  const world = topojson.feature(WORLD, WORLD.objects.countries).features;
  const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const el = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  };
  const largest = f => {
    if (!f || f.geometry.type !== 'MultiPolygon') return f;
    let best = null, area = -1;
    for (const c of f.geometry.coordinates) {
      const g = { type: 'Feature', geometry: { type: 'Polygon', coordinates: c } };
      const a = d3.geoArea(g); if (a > area) { area = a; best = g; }
    }
    return best;
  };

  for (const M of (window.MAPS || [])) {
    const host = document.getElementById(M.id);
    const W = M.w, H = M.h;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'mapsvg' }, host);
    const focusNames = (M.focus || []).map(norm);
    const focus = world.filter(f => focusNames.includes(norm(f.properties.name)));
    const fitFeatures = [];
    if (M.bbox) {
      const [x0, y0, x1, y1] = M.bbox;
      fitFeatures.push({ type: 'Feature', geometry: { type: 'MultiPoint', coordinates: [[x0, y0], [x1, y1], [x0, y1], [x1, y0]] } });
    } else {
      focus.forEach(f => fitFeatures.push(largest(f)));
    }
    (M.places || []).forEach(p => fitFeatures.push({ type: 'Feature', geometry: { type: 'Point', coordinates: [p.lon, p.lat] } }));
    const pad = M.pad || 70;
    const proj = d3.geoMercator().fitExtent([[pad, pad], [W - pad, H - pad]], { type: 'FeatureCollection', features: fitFeatures });
    if (M.maxScale && proj.scale() > M.maxScale) {  // do not zoom in absurdly far for a single point
      const c = proj.invert([W / 2, H / 2]); proj.scale(M.maxScale).center(c).translate([W / 2, H / 2]);
    }
    const path = d3.geoPath(proj);
    const g0 = el('g', { 'data-in': M.t0, 'data-out': M.tout, 'data-k': 'fade', 'data-d': 0.6 }, svg);
    el('path', { d: path(d3.geoGraticule10()), class: 'grat' }, g0);
    const fset = new Set(focus.map(f => f.properties.name));
    for (const f of world) {
      if (fset.has(f.properties.name)) continue;
      const d = path(f); if (d) el('path', { d, class: 'land' }, g0);
    }
    const g1 = el('g', { 'data-in': M.t0 + 0.25, 'data-out': M.tout, 'data-k': 'fade', 'data-d': 0.6 }, svg);
    for (const f of focus) { const d = path(f); if (d) el('path', { d, class: 'hl' }, g1); }

    const pts = {};
    (M.places || []).forEach(p => { pts[p.name] = proj([p.lon, p.lat]); });
    if (M.route && M.route.length > 1) {
      const d = 'M' + M.route.filter(n => pts[n]).map(n => pts[n].map(v => v.toFixed(1)).join(' ')).join(' L');
      el('path', { d, class: 'route', pathLength: 1, 'data-in': M.tPlaces, 'data-out': M.tout, 'data-k': 'draw' }, svg);
    }
    (M.labels || []).forEach((l, i) => {
      const [x, y] = proj([l.lon, l.lat]);
      const t = el('text', { x, y, class: 'cname', 'text-anchor': 'middle', 'data-in': M.t0 + 0.4, 'data-out': M.tout, 'data-k': 'fade' }, svg);
      t.textContent = l.name;
    });
    const mains = [];
    (M.places || []).forEach((p, i) => {
      const [x, y] = pts[p.name];
      const right = x < W - 300;
      if (p.main) { mains.push({ p, x, y, right }); return; }
      const g = el('g', { 'data-in': M.tPlaces + 0.15 * i, 'data-out': M.tout, 'data-k': 'fade' }, svg);
      el('circle', { cx: x, cy: y, r: 11, class: 'city' }, g);
      const t = el('text', { x: right ? x + 24 : x - 24, y: y + 14, class: 'clabel', 'text-anchor': right ? 'start' : 'end' }, g);
      t.textContent = p.name;
    });
    mains.forEach((m, i) => {
      const t0 = M.tMain + 0.3 * i;
      const ring = el('circle', { cx: m.x, cy: m.y, r: 44, class: 'ring', 'data-pulse': t0 + 0.3, 'data-out': M.tout }, svg);
      ring.style.transformBox = 'fill-box'; ring.style.transformOrigin = 'center';
      el('circle', { cx: m.x, cy: m.y, r: 20, class: 'mdot', 'data-in': t0, 'data-out': M.tout, 'data-k': 'fade' }, svg);
      const g = el('g', { 'data-in': t0 + 0.2, 'data-out': M.tout, 'data-dy': 16 }, svg);
      const rect = el('rect', { rx: 14, class: 'pcard', height: 76 }, g);
      const t = el('text', { class: 'plabel', y: m.y + 17 }, g);
      t.textContent = m.p.name;
      const w = t.getComputedTextLength() + 52;
      const x0 = m.right ? m.x + 40 : m.x - 40 - w;
      t.setAttribute('x', x0 + 26); rect.setAttribute('x', x0); rect.setAttribute('y', m.y - 38); rect.setAttribute('width', w);
    });
  }
};
