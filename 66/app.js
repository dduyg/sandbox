let svgs = [];
let selectedTags = [];
let filterMode = 'OR';
let favoritesOnly = false;

const gallery = document.getElementById('gallery');
const tagList = document.getElementById('tagList');
const dropdownInput = document.getElementById('dropdownInput');
const modeSwitch = document.getElementById('modeSwitch');
const favToggle = document.getElementById('favToggle');

const FAVORITES_KEY = 'svg-favorites';

// 1. Initial Data Fetch
fetch('https://cdn.jsdelivr.net/gh/dduyg/LiminalLoop@main/catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data;
    generateTagList();
    renderIcons();
  });

// 2. Favorites Logic
function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'));
}

function toggleFavorite(id) {
  const favs = getFavorites();
  favs.has(id) ? favs.delete(id) : favs.add(id);
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]));
  renderIcons();
}

// 3. Dropdown Logic
function generateTagList() {
  const tagSet = new Set();
  svgs.forEach(svg => svg.tags.forEach(t => tagSet.add(t)));
  
  const sortedTags = Array.from(tagSet).sort();
  tagList.innerHTML = '';
  
  sortedTags.forEach(tag => {
    const div = document.createElement('div');
    div.className = 'dropdown-item';
    div.textContent = tag;
    div.onclick = (e) => {
        e.stopPropagation(); // Keep dropdown open
        toggleTag(tag);
    };
    tagList.appendChild(div);
  });
}

function showDropdown() { tagList.classList.add('show'); }

// Close dropdown when clicking outside
window.onclick = function(event) {
  if (!event.target.matches('.dropdown-search')) {
    tagList.classList.remove('show');
    dropdownInput.value = ''; // Clear search text on close
    filterDropdown(); // Reset visibility of items
  }
};

function filterDropdown() {
  const input = dropdownInput.value.toLowerCase();
  const items = document.querySelectorAll('.dropdown-item');
  items.forEach(item => {
    item.style.display = item.textContent.toLowerCase().includes(input) ? 'flex' : 'none';
  });
}

function toggleTag(tag) {
  const index = selectedTags.indexOf(tag);
  if (index > -1) {
    selectedTags.splice(index, 1);
  } else {
    selectedTags.push(tag);
  }

  // Update UI items
  const items = document.querySelectorAll('.dropdown-item');
  items.forEach(item => {
    if (item.textContent === tag) item.classList.toggle('selected');
  });

  dropdownInput.placeholder = selectedTags.length > 0 ? selectedTags.join(', ') : "Search tags...";
  renderIcons();
}

// 4. Mode & Filter Logic
function toggleMode() {
  filterMode = (filterMode === 'OR') ? 'AND' : 'OR';
  modeSwitch.classList.toggle('and-mode');
  renderIcons();
}

favToggle.onclick = () => {
    favoritesOnly = !favoritesOnly;
    favToggle.classList.toggle('active', favoritesOnly);
    favToggle.textContent = favoritesOnly ? '★' : '☆';
    renderIcons();
};

function renderIcons() {
  const favs = getFavorites();
  gallery.innerHTML = '';

  const filtered = svgs.filter(svg => {
    // Favorite Filter
    if (favoritesOnly && !favs.has(svg.id)) return false;

    // Tag Filter
    if (selectedTags.length > 0) {
      if (filterMode === 'OR') {
        if (!selectedTags.some(t => svg.tags.includes(t))) return false;
      } else {
        if (!selectedTags.every(t => svg.tags.includes(t))) return false;
      }
    }
    return true;
  });

  filtered.forEach(svg => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
      <svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>
      <div class="actions">
        <button onclick="toggleFavorite('${svg.id}')">${favs.has(svg.id) ? '★' : '☆'}</button>
        <button onclick='copySVG(${JSON.stringify(svg)})'>⿻</button>
      </div>
    `;
    gallery.appendChild(div);
  });
}

function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code).then(() => alert('SVG Copied!'));
}
