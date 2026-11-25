(function () {
  var grid = document.getElementById('grid');
  var cards = [].slice.call(grid.querySelectorAll('.vcard'));
  var original = cards.slice();
  var chips = [].slice.call(document.querySelectorAll('.chip'));
  var keyBtns = [].slice.call(document.querySelectorAll('.ak-trail'));
  var sel = document.getElementById('fTrail'), n = document.getElementById('n'), empty = document.getElementById('empty');
  var mapEl = document.getElementById('atlas-map');
  var data = JSON.parse(document.getElementById('atlas-data').textContent);
  var bySlug = {}; data.forEach(function (d) { bySlug[d.s] = d; });
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var map = null, markers = {}, picked = null, pending = null;

  function card(slug) { return document.getElementById('v-' + slug); }

  function visible() {
    var trail = sel.value, want = {}, out = {};
    chips.forEach(function (c) { if (c.getAttribute('aria-pressed') === 'true') want[c.dataset.f] = 1; });
    cards.forEach(function (c) {
      var ok = !(trail && c.dataset.trail !== trail) && !(want.visit && c.dataset.visit !== 'open') &&
        !(want.food && c.dataset.food !== 'Yes') && !(want.stay && c.dataset.stay !== 'Yes') && !(want.wed && c.dataset.wed !== 'Yes');
      c.hidden = !ok; if (ok) out[c.dataset.slug] = 1;
    });
    return out;
  }

  function apply(fit) {
    var vis = visible(), shown = Object.keys(vis).length;
    n.textContent = shown; empty.hidden = shown > 0;
    keyBtns.forEach(function (b) { b.setAttribute('aria-pressed', sel.value === b.dataset.trail ? 'true' : 'false'); });
    if (picked && !vis[picked]) unpick();
    if (!map) return;
    var pts = [];
    data.forEach(function (d) {
      var m = markers[d.s];
      if (vis[d.s]) { if (!map.hasLayer(m)) m.addTo(map); pts.push([d.lat, d.lng]); }
      else if (map.hasLayer(m)) map.removeLayer(m);
    });
    if (fit !== false && pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 11, animate: !reduce });
  }

  function unpick() {
    if (!picked) return;
    var c = card(picked); if (c) c.classList.remove('is-picked');
    var m = markers[picked]; if (m && m._icon) m._icon.classList.remove('is-picked');
    picked = null;
  }

  // bring a vineyard to the top of the list and mark it on the map
  function pick(slug) {
    unpick(); picked = slug;
    var c = card(slug); grid.insertBefore(c, grid.firstChild); c.classList.add('is-picked');
    var m = markers[slug]; if (m && m._icon) m._icon.classList.add('is-picked');
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (ch) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]; }); }

  function build() {
    var L = window.L; mapEl.innerHTML = '';
    map = L.map(mapEl, { scrollWheelZoom: false, zoomSnap: 0.25 });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 15, minZoom: 7,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    map.on('click', function () { map.scrollWheelZoom.enable(); });
    data.forEach(function (d) {
      var icon = L.divIcon({ className: 'pin-wrap', html: '<span class="pin ' + (d.v ? 'pin--v' : 'pin--o') + '" style="--tc:' + d.c + ';--d:' + (data.indexOf(d) * 28) + 'ms"></span>', iconSize: [26, 26], iconAnchor: [13, 13], popupAnchor: [0, -12] });
      var m = L.marker([d.lat, d.lng], { icon: icon, title: d.n, alt: d.n, riseOnHover: true });
      m.bindPopup(
        '<div class="pop" style="--tc:' + d.c + '"><a class="pop-img" href="' + d.h + '"><img src="' + d.img + '" alt="" width="260" height="195"></a>' +
        '<span class="pop-trail">' + esc(d.tl) + '</span><a class="pop-name" href="' + d.h + '">' + esc(d.n) + '</a>' +
        '<span class="pop-town">' + esc(d.town) + '</span>' + (d.v ? '<span class="pop-v">&#10003; Estate-verified</span>' : '') +
        '<span class="pop-actions"><a class="pop-go" href="' + d.h + '">View the guide</a><button type="button" class="pop-list" data-slug="' + d.s + '">See it in the list</button></span></div>',
        { maxWidth: 280, minWidth: 240 });
      m.on('click', function () { pick(d.s); });
      markers[d.s] = m;
    });
    mapEl.addEventListener('click', function (ev) {
      var b = ev.target.closest('.pop-list'); if (!b) return;
      var c = card(b.dataset.slug); c.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
      var a = c.querySelector('.vc-name a'); if (a) a.focus({ preventScroll: true });
    });
    cards.forEach(function (c) {
      var on = function () { var m = markers[c.dataset.slug]; if (m && m._icon) m._icon.classList.add('is-on'); };
      var off = function () { var m = markers[c.dataset.slug]; if (m && m._icon) m._icon.classList.remove('is-on'); };
      c.addEventListener('mouseenter', on); c.addEventListener('mouseleave', off);
      c.addEventListener('focusin', on); c.addEventListener('focusout', off);
    });
    apply();
    if (pending) { showOnMap(pending); pending = null; }
  }

  function showOnMap(slug) {
    if (!map) { pending = slug; load(); mapEl.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); return; }
    var d = bySlug[slug], m = markers[slug];
    if (!map.hasLayer(m)) m.addTo(map);
    mapEl.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    map.setView([d.lat, d.lng], Math.max(map.getZoom(), 11), { animate: !reduce });
    pick(slug); m.openPopup();
  }

  grid.addEventListener('click', function (ev) {
    var b = ev.target.closest('.vc-map'); if (b) showOnMap(b.dataset.slug);
  });
  chips.forEach(function (c) {
    c.addEventListener('click', function () { c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); apply(); });
  });
  keyBtns.forEach(function (b) {
    b.addEventListener('click', function () { sel.value = sel.value === b.dataset.trail ? '' : b.dataset.trail; apply(); });
  });
  sel.addEventListener('change', function () { apply(); });
  document.getElementById('clear').addEventListener('click', function () {
    sel.value = ''; chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    unpick(); original.forEach(function (c) { grid.insertBefore(c, empty); });
    if (map) map.closePopup(); apply();
  });

  function load() {
    if (load.done) return; load.done = true;
    var css = document.createElement('link'); css.rel = 'stylesheet'; css.href = '/vendor/leaflet/leaflet.css'; document.head.appendChild(css);
    var js = document.createElement('script'); js.src = '/vendor/leaflet/leaflet.js'; js.onload = build; document.head.appendChild(js);
  }

  apply();
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { if (es.some(function (x) { return x.isIntersecting; })) { io.disconnect(); load(); } }, { rootMargin: '600px' });
    io.observe(mapEl);
  } else { load(); }
})();
