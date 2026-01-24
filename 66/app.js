let svgs = [];
let selectedTags = [];
let tagMode = 'OR';
let favoritesOnly = false;

const gallery = document.getElementById('gallery');
const tagList = document.getElementById('tagList');
const dropdownSearch = document.getElementById('dropdownSearch');
const toggleBtn = document.getElementById('toggleBtn');
const toggleSwitch = document.getElementById('toggleSwitch');
const favToggle = document.getElementById('favToggle');

const FAVORITES_KEY = 'svg-favorites';

// Load JSON
fetch('https://cdn.jsdelivr.net/gh/dduyg/LiminalLoop@main/catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data;
    generateTagList();
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
  if (selectedTags.length === 0) return true;
  return tagMode === 'AND'
    ? selectedTags.every(t => svg.tags.includes(t))
    : selectedTags.some(t => svg.tags.includes(t));
}

function renderIcons() {
  const favs = getFavorites();
  gallery.innerHTML = '';

  svgs
    .filter(svg => {
      if (favoritesOnly && !favs.has(svg.id)) return false;
      if (!matchesTags(svg)) return false;
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

function generateTagList() {
  const tagCounts = {};
  svgs.forEach(svg => svg.tags.forEach(t => tagCounts[t] = (tagCounts[t] || 0) + 1));
  const sortedTags = Object.keys(tagCounts).sort((a, b) => a.localeCompare(b));

  tagList.innerHTML = '';
  
  sortedTags.forEach(tag => {
    const div = document.createElement('div');
    div.className = 'dropdown-item';
    div.textContent = tag;
    div.onclick = () => toggleTag(tag, div);
    tagList.appendChild(div);
  });
}

function toggleTag(tag, element) {
  const index = selectedTags.indexOf(tag);
  
  if (index > -1) {
    selectedTags.splice(index, 1);
    element.classList.remove('selected');
  } else {
    selectedTags.push(tag);
    element.classList.add('selected');
  }

  updatePlaceholder();
  renderIcons();
}

function updatePlaceholder() {
  dropdownSearch.placeholder = selectedTags.length > 0 
    ? selectedTags.join(', ') 
    : 'Search tags...';
}

function showDropdown() {
  tagList.classList.add('show');
}

function hideDropdown() {
  tagList.classList.remove('show');
}

function filterDropdown() {
  const input = dropdownSearch.value.toLowerCase();
  const items = tagList.querySelectorAll('.dropdown-item');
  
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    item.style.display = text.includes(input) ? 'block' : 'none';
  });
}

function toggleMode() {
  tagMode = tagMode === 'OR' ? 'AND' : 'OR';
  toggleSwitch.classList.toggle('and-mode');
  renderIcons();
}

function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code);
}

// Event listeners
dropdownSearch.addEventListener('focus', showDropdown);
dropdownSearch.addEventListener('input', filterDropdown);

window.addEventListener('click', (event) => {
  if (!event.target.matches('.dropdown-search') && !event.target.closest('.dropdown-list')) {
    hideDropdown();
  }
});

toggleBtn.addEventListener('click', toggleMode);

favToggle.addEventListener('click', () => {
  favoritesOnly = !favoritesOnly;
  favToggle.classList.toggle('active', favoritesOnly);
  favToggle.textContent = favoritesOnly ? '★' : '☆';
  renderIcons();
});
