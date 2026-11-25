/* Thatch & Trail maps (v33): the UK map + directory on the homepage, and a simple map on each region page. */
(function () {
  var ukData = document.getElementById('uk-data'), hubData = document.getElementById('hub-map-data');
  if (!ukData && !hubData) return;
  var el = document.getElementById(ukData ? 'uk-map' : 'hub-map');
  if (!el) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var data = JSON.parse((ukData || hubData).textContent);
  var regions = ukData ? JSON.parse(document.getElementById('uk-regions').textContent) : {};
  var map = null, markers = {};
  var state = { r: '', v: false, food: false, stay: false };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function colour(d) { return d.c || (regions[d.r] && regions[d.r].c) || '#3B5A3F'; }
  function ok(d) {
    return !(state.r && d.r !== state.r) && !(state.v && !d.v) && !(state.food && !d.f) && !(state.stay && !d.st);
  }

  // ----- directory list (homepage only) -----
  var rows = [].slice.call(document.querySelectorAll('.ud-row'));
  var groups = [].slice.call(document.querySelectorAll('.ud-group'));
  var count = document.getElementById('uk-n'), empty = document.getElementById('uk-empty');
  var bySlug = {}; data.forEach(function (d) { bySlug[d.s] = d; });

  function apply(fit) {
    var shown = 0, pts = [];
    rows.forEach(function (row) { var d = bySlug[row.dataset.s]; var on = d && ok(d); row.hidden = !on; if (on) shown++; });
    groups.forEach(function (g) { g.hidden = !g.querySelector('.ud-row:not([hidden])'); });
    if (count) count.textContent = shown;
    if (empty) empty.hidden = shown > 0;
    if (!map) return;
    data.forEach(function (d) {
      var m = markers[d.s], on = ok(d);
      if (on) { if (!map.hasLayer(m)) m.addTo(map); pts.push([d.lat, d.lng]); }
      else if (map.hasLayer(m)) map.removeLayer(m);
    });
    if (fit !== false && pts.length) map.fitBounds(pts, { padding: [36, 36], maxZoom: 11, animate: !reduce });
  }

  [].slice.call(document.querySelectorAll('.uk-key')).forEach(function (b) {
    b.addEventListener('click', function () {
      state.r = b.dataset.r;
      document.querySelectorAll('.uk-key').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      apply();
    });
  });
  [].slice.call(document.querySelectorAll('.uk-chips .chip')).forEach(function (b) {
    b.addEventListener('click', function () {
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on ? 'true' : 'false'); state[b.dataset.f] = on; apply();
    });
  });

  // ----- the map itself, loaded when it scrolls into view -----
  function build() {
    if (map || !window.L) return;
    el.innerHTML = '';
    map = L.map(el, { scrollWheelZoom: false, zoomSnap: 0.25 });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 15, minZoom: 5,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    map.on('click', function () { map.scrollWheelZoom.enable(); });
    data.forEach(function (d, i) {
      var icon = L.divIcon({ className: 'pin-wrap', html: '<span class="pin ' + (d.v ? 'pin--v' : 'pin--o') + '" style="--tc:' + colour(d) + ';--d:' + Math.min(i * 12, 900) + 'ms"></span>', iconSize: [26, 26], iconAnchor: [13, 13], popupAnchor: [0, -12] });
      var m = L.marker([d.lat, d.lng], { icon: icon, title: d.n, alt: d.n, riseOnHover: true });
      var reg = regions[d.r] ? '<span class="pop-trail">' + esc(regions[d.r].n) + '</span>' : '';
      m.bindPopup('<div class="pop upop" style="--tc:' + colour(d) + '">' + reg + '<a class="pop-name" href="' + d.h + '">' + esc(d.n) + '</a>' +
        '<span class="pop-town">' + esc(d.t) + '</span>' + (d.v ? '<span class="pop-v">&#10003; Estate-verified</span>' : '<span class="pop-town">Details being confirmed</span>') +
        '<span class="pop-actions"><a class="pop-go" href="' + d.h + '">View the guide</a></span></div>');
      markers[d.s] = m; m.addTo(map);
    });
    var pts = data.map(function (d) { return [d.lat, d.lng]; });
    map.fitBounds(pts, { padding: [30, 30], maxZoom: 11 });
    apply(false);
  }
  function load() {
    if (window.L) return build();
    var css = document.createElement('link'); css.rel = 'stylesheet'; css.href = '/vendor/leaflet/leaflet.css'; document.head.appendChild(css);
    var js = document.createElement('script'); js.src = '/vendor/leaflet/leaflet.js'; js.onload = build; document.head.appendChild(js);
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { if (es.some(function (x) { return x.isIntersecting; })) { io.disconnect(); load(); } }, { rootMargin: '500px' });
    io.observe(el);
  } else { load(); }
  apply(false);
})();
