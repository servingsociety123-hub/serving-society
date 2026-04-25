(function () {
  try {
    var path = location.pathname;
    var page = path === '/' || path.match(/index\.html$/) ? 'index'
      : path.includes('/services/') ? 'services/' + path.split('/').pop().replace('.html', '')
      : path.split('/').pop().replace('.html', '') || 'index';

    var content = JSON.parse(localStorage.getItem('ss_content') || '{}');
    var fields = content[page];
    if (fields) {
      Object.keys(fields).forEach(function (sel) {
        var el = document.querySelector(sel);
        if (el) el.innerHTML = fields[sel];
      });
    }

    var images = JSON.parse(localStorage.getItem('ss_images') || '{}');
    Object.keys(images).forEach(function (src) {
      document.querySelectorAll('img').forEach(function (img) {
        var imgSrc = img.getAttribute('src') || '';
        if (imgSrc === src || imgSrc.endsWith(src.replace(/^\//, ''))) {
          img.src = images[src];
        }
      });
    });
  } catch (e) {}
})();
