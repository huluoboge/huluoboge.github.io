(function () {
  'use strict';
  document.querySelectorAll('[data-article-discovery]').forEach(function (root) {
    var search = root.querySelector('[data-article-search]');
    var buttons = Array.from(root.querySelectorAll('[data-article-topic]'));
    var selectedTopic = '';
    var count = root.querySelector('[data-article-count]');
    var empty = root.querySelector('[data-article-empty]');
    var items = Array.from(root.querySelectorAll('[data-article-item]'));
    function update() {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      items.forEach(function (item) {
        var matchesQuery = !query || (item.dataset.search || '').includes(query);
        var matchesTopic = !selectedTopic || (item.dataset.category || '').split(' ').includes(selectedTopic);
        item.hidden = !(matchesQuery && matchesTopic);
        if (!item.hidden) visible += 1;
      });
      count.textContent = visible + ' 篇文章';
      empty.hidden = visible !== 0;
    }
    search.addEventListener('input', update);
    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        selectedTopic = button.dataset.articleTopic;
        buttons.forEach(function (item) {
          item.setAttribute('aria-pressed', String(item === button));
        });
        update();
      });
    });
    update();
  });
})();
