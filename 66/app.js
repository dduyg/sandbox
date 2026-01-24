let svgs = [];
let selectedTags = new Set();
let filterMode = 'OR';
let favoritesOnly = false;

const gallery = document.getElementById('gallery');
const searchInput = document.getElementById('search');
const tagSearch = document.getElementById('tagSearch');
const tagDropdown = document.getElementById('tagDropdown');
const toggleSwitch = document.getElementById('toggleSwitch');
const modeToggle = document.getElementById('modeToggle');

const FAVORITES_KEY = 'svg-favorites';

/* ===== Load Data ===== */
fetch('https://cdn.jsdelivr.net/gh/dduyg/LiminalLoop@main/catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data;
    renderDropdownTags();
    renderIcons();
  });

/* ===== Favorites ===== */
function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'));
}

function toggleFavorite(id) {
  const favs = getFavorites();
  favs.has(id) ? favs.delete(id) : favs.add(id);
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]));
  renderIcons();
}

/* ===== Filtering ===== */
function matchesTags(svg) {
  if (selectedTags.size === 0) return true;

  return filterMode === 'AND'
    ? [...selectedTags].every(t => svg.tags.includes(t))
    : [...selectedTags].some(t => svg.tags.includes(t));
}

/* ===== Render Icons ===== */
function renderIcons() {
  const search = searchInput.value.toLowerCase();
  const favs = getFavorites();

  gallery.innerHTML = '';

  svgs
    .filter(svg => {
      if (favoritesOnly && !favs.has(svg.id)) return false;
      if (!matchesTags(svg)) return false;
      if (search && !svg.tags.some(t => t.includes(search))) return false;
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

/* ===== Dropdown Tags ===== */
function renderDropdownTags() {
  const allTags = [...new Set(svgs.flatMap(svg => svg.tags))].sort();
  tagDropdown.innerHTML = '';

  allTags.forEach(tag => {
    const div = document.createElement('div');
    div.className = 'dropdown-item';
    div.textContent = tag;

    div.onclick = () => {
      selectedTags.has(tag)
        ? selectedTags.delete(tag)
        : selectedTags.add(tag);

      div.classList.toggle('selected');
      updateTagPlaceholder();
      renderIcons();
    };

    tagDropdown.appendChild(div);
  });
}

function updateTagPlaceholder() {
  tagSearch.placeholder = selectedTags.size
    ? [...selectedTags].join(', ')
    : 'Search tags…';
}

/* ===== Dropdown Behavior ===== */
tagSearch.addEventListener('focus', () => {
  tagDropdown.classList.add('show');
});

document.addEventListener('click', e => {
  if (!e.target.closest('.dropdown-container')) {
    tagDropdown.classList.remove('show');
  }
});

tagSearch.addEventListener('input', () => {
  const q = tagSearch.value.toLowerCase();
  [...tagDropdown.children].forEach(item => {
    item.style.display = item.textContent.toLowerCase().includes(q)
      ? 'block'
      : 'none';
  });
});

/* ===== Toggle AND / OR ===== */
modeToggle.onclick = () => {
  filterMode = filterMode === 'OR' ? 'AND' : 'OR';
  toggleSwitch.classList.toggle('and');
  renderIcons();
};

/* ===== Copy SVG ===== */
function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code);
}

/* ===== Search ===== */
searchInput.addEventListener('input', renderIcons);
