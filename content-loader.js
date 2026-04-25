(function () {
  try {
    var path = location.pathname;
    var page = path === '/' || path.match(/index\.html$/) ? 'index'
      : path.includes('/services/') ? 'services/' + path.split('/').pop().replace('.html', '')
      : path.split('/').pop().replace('.html', '') || 'index';

    /* ── Text content overrides (localStorage) ── */
    var content = JSON.parse(localStorage.getItem('ss_content') || '{}');
    var fields = content[page];
    if (fields) {
      Object.keys(fields).forEach(function (sel) {
        var el = document.querySelector(sel);
        if (el) el.innerHTML = fields[sel];
      });
    }

    /* ── Image overrides — fetch from Supabase image_overrides table ── */
    var url = window.SUPABASE_URL;
    var key = window.SUPABASE_ANON_KEY;
    if (url && url !== 'YOUR_SUPABASE_URL' && key) {
      fetch(url + '/rest/v1/image_overrides?select=original_path,storage_url', {
        headers: {
          'apikey': key,
          'Authorization': 'Bearer ' + key
        }
      })
      .then(function (r) { return r.json(); })
      .then(function (rows) {
        if (!Array.isArray(rows)) return;
        rows.forEach(function (row) {
          document.querySelectorAll('img').forEach(function (img) {
            var imgSrc = img.getAttribute('src') || '';
            if (imgSrc === row.original_path ||
                imgSrc.endsWith(row.original_path.replace(/^\//, ''))) {
              img.src = row.storage_url;
            }
          });
        });
      })
      .catch(function () {});
    }
  } catch (e) {}
})();
