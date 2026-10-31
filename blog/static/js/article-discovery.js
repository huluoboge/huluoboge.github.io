(function () {
  'use strict';
  document.querySelectorAll('[data-article-discovery]').forEach(function (root) {
    var search = root.querySelector('[data-article-search]');
    var sectionButtons = Array.from(root.querySelectorAll('[data-article-section]'));
    var kindButtons = Array.from(root.querySelectorAll('[data-article-kind]'));
    var buttons = Array.from(root.querySelectorAll('[data-article-topic]'));
    var kindNavigation = root.querySelector('[data-kind-navigation]');
    var topicNavigation = root.querySelector('[data-topic-navigation]');
    var selectedSection = 'work';
    var selectedKind = 'technical';
    var selectedTopic = '';
    var count = root.querySelector('[data-article-count]');
    var empty = root.querySelector('[data-article-empty]');
    var items = Array.from(root.querySelectorAll('[data-article-item]'));
    function update() {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      items.forEach(function (item) {
        var matchesQuery = !query || (item.dataset.search || '').includes(query);
        var matchesSection = (item.dataset.section || 'work') === selectedSection;
        var matchesKind = selectedSection !== 'work' || !selectedKind || item.dataset.kind === selectedKind;
        var matchesTopic = !selectedTopic || (item.dataset.category || '').split(' ').includes(selectedTopic);
        item.hidden = !(matchesQuery && matchesSection && matchesKind && matchesTopic);
        if (!item.hidden) visible += 1;
      });
      var topicBase = items.filter(function (item) {
        return item.dataset.section === selectedSection
          && (selectedSection !== 'work' || item.dataset.kind === selectedKind);
      });
      buttons.forEach(function (button) {
        var topic = button.dataset.articleTopic;
        var topicCount = topicBase.filter(function (item) {
          return !topic || (item.dataset.category || '').split(' ').includes(topic);
        }).length;
        var badge = button.querySelector('.topic-count');
        if (badge) badge.textContent = topicCount;
      });
      count.textContent = visible + ' 篇文章';
      empty.hidden = visible !== 0;
      if (selectedSection === 'life' && visible === 0) {
        empty.textContent = '生活随记还没有文章。';
      } else {
        empty.textContent = '没有匹配的文章。';
      }
      if (kindNavigation) kindNavigation.hidden = selectedSection !== 'work';
      if (topicNavigation) topicNavigation.hidden = selectedSection !== 'work';
    }
    search.addEventListener('input', update);
    sectionButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        selectedSection = button.dataset.articleSection;
        selectedKind = selectedSection === 'work' ? 'technical' : '';
        selectedTopic = '';
        sectionButtons.forEach(function (item) {
          item.setAttribute('aria-pressed', String(item === button));
        });
        kindButtons.forEach(function (item) {
          item.setAttribute('aria-pressed', String(item.dataset.articleKind === selectedKind));
        });
        buttons.forEach(function (item) {
          item.setAttribute('aria-pressed', String(item.dataset.articleTopic === ''));
        });
        update();
      });
    });
    kindButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        selectedKind = button.dataset.articleKind;
        kindButtons.forEach(function (item) {
          item.setAttribute('aria-pressed', String(item === button));
        });
        update();
      });
    });
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
