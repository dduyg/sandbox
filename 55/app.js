let svgs = [];
let activeTags = new Set();
let tagMode = 'OR';
let favoritesOnly = false;

const gallery = document.getElementById('gallery');
const tagList = document.getElementById('tagList');
const searchInput = document.getElementById('search');
const FAVORITES_KEY = 'svg-favorites';
const MAX_VISIBLE_TAGS = 20;

fetch('catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data;
    renderTags();
    renderSvgs();
  });

// Favorites
function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'));
}

function toggleFavorite(id) {
  const favs = getFavorites();
  favs.has(id) ? favs.delete(id) : favs.add(id);
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]));
  renderSvgs();
}

// Tag matching
function matchesTags(svg) {
  if (activeTags.size === 0) return true;
  return tagMode === 'AND'
    ? [...activeTags].every(t => svg.tags.includes(t))
    : [...activeTags].some(t => svg.tags.includes(t));
}

// Render SVGs
function renderSvgs() {
  const search = searchInput.value.toLowerCase();
  const favs = getFavorites();

  gallery.innerHTML = '';

  svgs
    .filter(svg => {
      if (favoritesOnly && !favs.has(svg.id)) return false;
      if (!matchesTags(svg)) return false;
      if (!svg.tags.some(t => t.includes(search))) return false;
      return true;
    })
    .forEach(svg => {
      const div = document.createElement('div');
      div.className = 'item';

      div.innerHTML = `
        <svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">
          ${svg.svg}
        </svg>
        <div class="actions">
          <button onclick="toggleFavorite('${svg.id}')">
            ${favs.has(svg.id) ? '★' : '☆'}
          </button>
          <button onclick='copySVG(${JSON.stringify(svg)})'>⿻</button>
        </div>
      `;
      gallery.appendChild(div);
    });
}

// Render Tags
function renderTags() {
  const tagsCount = {};
  svgs.forEach(svg => svg.tags.forEach(t => {
    tagsCount[t] = (tagsCount[t] || 0) + 1;
  }));

  // Sort tags by count descending
  const sortedTags = Object.keys(tagsCount).sort((a,b)=>tagsCount[b]-tagsCount[a]);
  let expanded = false;

  function render() {
    tagList.innerHTML = '';
    const visibleTags = expanded ? sortedTags : sortedTags.slice(0, MAX_VISIBLE_TAGS);

    visibleTags.forEach(tag => {
      const el = document.createElement('div');
      el.className = 'tag';
      el.textContent = tag;
      if (activeTags.has(tag)) el.classList.add('active');
      el.onclick = () => {
        activeTags.has(tag) ? activeTags.delete(tag) : activeTags.add(tag);
        el.classList.toggle('active');
        renderSvgs();
      };
      tagList.appendChild(el);
    });

    if (sortedTags.length > MAX_VISIBLE_TAGS) {
      const toggleEl = document.createElement('div');
      toggleEl.className = 'tag more-toggle';
      toggleEl.textContent = expanded ? '... less' : '... more';
      toggleEl.onclick = () => {
        expanded = !expanded;
        render();
      };
      tagList.appendChild(toggleEl);
    }
  }

  render();
}

// Copy SVG
function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code);
}

searchInput.addEventListener('input', renderSvgs);

document.getElementById('orBtn').onclick = () => {
  tagMode = 'OR';
  document.getElementById('orBtn').classList.add('active');
  document.getElementById('andBtn').classList.remove('active');
  renderSvgs();
};

document.getElementById('andBtn').onclick = () => {
  tagMode = 'AND';
  document.getElementById('andBtn').classList.add('active');
  document.getElementById('orBtn').classList.remove('active');
  renderSvgs();
};

document.getElementById('favToggle').onclick = () => {
  favoritesOnly = !favoritesOnly;
  renderSvgs();
};
