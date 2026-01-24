let svgs = [];
let activeTags = new Set();
let tagMode = 'OR';
let favoritesOnly = false;

const gallery = document.getElementById('gallery');
const tagList = document.getElementById('tagList');
const searchInput = document.getElementById('search');

const orBtn = document.getElementById('orBtn');
const andBtn = document.getElementById('andBtn');
const favToggle = document.getElementById('favToggle');

const FAVORITES_KEY = 'svg-favorites';

// Load JSON
fetch('https://cdn.jsdelivr.net/gh/dduyg/LiminalLoop@main/catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data;
    renderTags();
    renderIcons();
  });

function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'));
}

function toggleFavorite(id) {
  const favs = getFavorites();
  favs.has(id) ? favs.delete(id) : favs.add(id);
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]));
  renderIcons();
}

function matchesTags(svg) {
  if (activeTags.size === 0) return true;
  return tagMode === 'AND'
    ? [...activeTags].every(t => svg.tags.includes(t))
    : [...activeTags].some(t => svg.tags.includes(t));
}

function renderIcons() {
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

function renderTags() {
  const tagCounts = {};
  svgs.forEach(svg => svg.tags.forEach(t => tagCounts[t] = (tagCounts[t] || 0) + 1));
  const sortedTags = Object.keys(tagCounts).sort((a,b) => tagCounts[b] - tagCounts[a]);

  tagList.innerHTML = '';
  const maxVisible = 20;
  let hiddenTags = [];

  sortedTags.forEach((tag, i) => {
    if (i < maxVisible) {
      tagList.appendChild(createTagElement(tag));
    } else {
      hiddenTags.push(tag);
    }
  });

  if (hiddenTags.length) {
    const moreEl = document.createElement('div');
    moreEl.className = 'tag more';
    moreEl.textContent = '...';
    moreEl.onclick = () => {
      hiddenTags.forEach(tag => tagList.appendChild(createTagElement(tag)));
      moreEl.remove();
    };
    tagList.appendChild(moreEl);
  }
}

function createTagElement(tag) {
  const el = document.createElement('div');
  el.className = 'tag';
  el.textContent = tag;
  el.onclick = () => {
    activeTags.has(tag) ? activeTags.delete(tag) : activeTags.add(tag);
    el.classList.toggle('active');
    renderIcons();
  };
  return el;
}

function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code);
}

// Event listeners
searchInput.addEventListener('input', renderIcons);

orBtn.onclick = () => {
  tagMode = 'OR';
  orBtn.classList.add('active');
  andBtn.classList.remove('active');
  renderIcons();
};

andBtn.onclick = () => {
  tagMode = 'AND';
  andBtn.classList.add('active');
  orBtn.classList.remove('active');
  renderIcons();
};

favToggle.onclick = () => {
  favoritesOnly = !favoritesOnly;
  favToggle.classList.toggle('active', favoritesOnly);
  renderIcons();
};
