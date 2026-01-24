let svgs = [];
let selectedTags = [];
let tagMode = 'OR';
let favoritesOnly = false;

const gallery = document.getElementById('gallery');
const tagList = document.getElementById('tagList');
const dropdownSearch = document.querySelector('.dropdown-search');
const favToggle = document.getElementById('favToggle');

const FAVORITES_KEY = 'svg-favorites';

// Load JSON
fetch('https://cdn.jsdelivr.net/gh/dduyg/LiminalLoop@main/catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data;
    generateTagList();
    renderSVGs();
  });

function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'));
}

function toggleFavorite(id) {
  const favs = getFavorites();
  favs.has(id) ? favs.delete(id) : favs.add(id);
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]));
  renderSVGs();
}

function matchesTags(svg) {
  if (selectedTags.length === 0) return true;
  return tagMode === 'AND'
    ? selectedTags.every(t => svg.tags.includes(t))
    : selectedTags.some(t => svg.tags.includes(t));
}

function showTagPanel(event, tags) {
  event.stopPropagation();
  
  // Close any open panels
  document.querySelectorAll('.tag-panel').forEach(panel => {
    panel.classList.remove('show');
  });
  
  // Find the panel in this item
  const button = event.currentTarget;
  const item = button.closest('.item');
  const panel = item.querySelector('.tag-panel');
  
  panel.classList.add('show');
  
  // Close panel when clicking outside
  setTimeout(() => {
    const closePanel = (e) => {
      if (!panel.contains(e.target) && e.target !== button) {
        panel.classList.remove('show');
        document.removeEventListener('click', closePanel);
      }
    };
    document.addEventListener('click', closePanel);
  }, 0);
}

function renderSVGs() {
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
      
      const tagsHTML = svg.tags.map(tag => 
        `<span class="tag-panel-tag">${tag}</span>`
      ).join('');
      
      div.innerHTML = `
        <svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">
          ${svg.svg}
        </svg>
        <div class="actions">
          <button onclick="showTagPanel(event, ${JSON.stringify(svg.tags).replace(/"/g, '&quot;')})">꒰ ꒱</button>
          <button onclick='copySVG(${JSON.stringify(svg)})'>⿻</button>
          <button onclick="toggleFavorite('${svg.id}')">
            ${favs.has(svg.id) ? '★' : '☆'}
          </button>
        </div>
        <div class="tag-panel">
          <div class="tag-panel-title">Tags</div>
          <div class="tag-panel-tags">
            ${tagsHTML}
          </div>
        </div>
      `;
      gallery.appendChild(div);
    });
  
  // Update tag counts after rendering
  updateTagCounts();
}

function getTagCounts() {
  const tagCounts = {};
  
  // Count tags from full dataset
  svgs.forEach(svg => {
    svg.tags.forEach(tag => {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    });
  });
  
  return tagCounts;
}

function updateTagCounts() {
  const tagCounts = getTagCounts();
  const items = tagList.querySelectorAll('.dropdown-item');
  
  items.forEach(item => {
    const tagName = item.querySelector('.tag-name').textContent;
    const countSpan = item.querySelector('.tag-count');
    const count = tagCounts[tagName] || 0;
    countSpan.textContent = `(${count})`;
  });
}

function generateTagList() {
  const tagCounts = getTagCounts();
  const sortedTags = Object.keys(tagCounts).sort();

  tagList.innerHTML = '';
  
  sortedTags.forEach(tag => {
    const div = document.createElement('div');
    div.className = 'dropdown-item';
    
    const tagName = document.createElement('span');
    tagName.className = 'tag-name';
    tagName.textContent = tag;
    
    const tagCount = document.createElement('span');
    tagCount.className = 'tag-count';
    tagCount.textContent = `(${tagCounts[tag]})`;
    
    div.appendChild(tagName);
    div.appendChild(tagCount);
    
    div.onclick = () => toggleTag(tag);
    tagList.appendChild(div);
  });
}

function showDropdown() {
  tagList.classList.add('show');
}

function filterDropdown() {
  const input = dropdownSearch.value.toLowerCase();
  const items = tagList.querySelectorAll('.dropdown-item');
  
  items.forEach(item => {
    const text = item.querySelector('.tag-name').textContent.toLowerCase();
    item.style.display = text.includes(input) ? 'flex' : 'none';
  });
}

function toggleTag(tag) {
  const index = selectedTags.indexOf(tag);
  const items = tagList.querySelectorAll('.dropdown-item');
  
  if (index > -1) {
    selectedTags.splice(index, 1);
  } else {
    selectedTags.push(tag);
  }

  items.forEach(item => {
    const tagName = item.querySelector('.tag-name').textContent;
    if (tagName === tag) {
      item.classList.toggle('selected');
    }
  });

  dropdownSearch.placeholder = selectedTags.length > 0 
    ? selectedTags.join(', ') 
    : "Search & filter by tags...";
  
  renderSVGs();
}

function toggleMode() {
  const toggleSwitch = document.querySelector('.toggle-switch');
  tagMode = tagMode === 'OR' ? 'AND' : 'OR';
  toggleSwitch.classList.toggle('and-mode');
  renderSVGs();
}

function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code);
}

// Event listeners
dropdownSearch.addEventListener('focus', showDropdown);
dropdownSearch.addEventListener('input', filterDropdown);

window.onclick = function(event) {
  if (!event.target.matches('.dropdown-search')) {
    tagList.classList.remove('show');
  }
};

favToggle.onclick = () => {
  favoritesOnly = !favoritesOnly;
  favToggle.classList.toggle('active', favoritesOnly);
  renderSVGs();
};
