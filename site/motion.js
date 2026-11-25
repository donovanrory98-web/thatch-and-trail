(function () {
  var root = document.documentElement;
  window.addEventListener('load', function () { root.classList.add('hero-ready'); });
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var sel = '.vcard,.card,.sec,.v4-discover-card,.favourite-card,.v4-step,.fq,.estate-answer,.warm-promises>*,.stat,.ak-trails,.trail-facts,.v4-link-grid>a';
  var els = [].slice.call(document.querySelectorAll(sel));
  var fold = window.innerHeight;
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  var n = 0;
  els.forEach(function (el) {
    if (el.getBoundingClientRect().top < fold) return; /* never hide what is already on screen */
    el.style.setProperty('--rd', (n++ % 3) * 70 + 'ms');
    el.classList.add('reveal'); io.observe(el);
  });
})();
