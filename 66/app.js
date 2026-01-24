let svgs = [];
let selectedTags = new Set();
let filterMode = 'OR';

const gallery = document.getElementById('gallery');
const searchInput = document.getElementById('search');
const tagSearch = document.getElementById('tagSearch');
const tagList = document.getElementById('tagList');
const toggleSwitch = document.getElementById('toggleSwitch');
const modeToggle = document.getElementById('modeToggle');

fetch('https://cdn.jsdelivr.net/gh/dduyg/LiminalLoop@main/catalog.svgs.json')
  .then(r => r.json())
  .then(data => {
    svgs = data;
    renderTags();
    renderIcons();
  });

/* ===== Rendering ===== */
function renderIcons() {
  const query = searchInput.value.toLowerCase();
  gallery.innerHTML = '';

  svgs
    .filter(svg => {
      if (query && !svg.tags.some(t => t.includes(query))) return false;

      if (selectedTags.size === 0) return true;

      return filterMode === 'AND'
        ? [...selectedTags].every(t => svg.tags.includes(t))
        : [...selectedTags].some(t => svg.tags.includes(t));
    })
    .forEach(svg => {
      const el = document.createElement('div');
      el.className = 'item';
      el.innerHTML = `
        <svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">
          ${svg.svg}
        </svg>
        <div class="actions">
          <button onclick="copySVG(${JSON.stringify(svg)})">⿻</button>
        </div>
      `;
      gallery.appendChild(el);
    });
}

/* ===== Tags ===== */
function renderTags() {
  const tags = [...new Set(svgs.flatMap(s => s.tags))].sort();
  tagList.innerHTML = '';

  tags.forEach(tag => {
    const el = document.createElement('div');
    el.className = 'dropdown-item';
    el.textContent = tag;
    el.onclick = () => toggleTag(tag, el);
    tagList.appendChild(el);
  });
}

function toggleTag(tag, el) {
  selectedTags.has(tag) ? selectedTags.delete(tag) : selectedTags.add(tag);
  el.classList.toggle('selected');
  tagSearch.placeholder = selectedTags.size
    ? [...selectedTags].join(', ')
    : 'Search tags…';
  renderIcons();
}

/* ===== Toggle Mode ===== */
modeToggle.onclick = () => {
  filterMode = filterMode === 'OR' ? 'AND' : 'OR';
  toggleSwitch.classList.toggle('and', filterMode === 'AND');
  renderIcons();
};

/* ===== Dropdown ===== */
tagSearch.onfocus = () => tagList.classList.add('show');
document.addEventListener('click', e => {
  if (!e.target.closest('.dropdown')) tagList.classList.remove('show');
});

tagSearch.oninput = () => {
  const q = tagSearch.value.toLowerCase();
  [...tagList.children].forEach(i => {
    i.style.display = i.textContent.includes(q) ? 'block' : 'none';
  });
};

/* ===== Search ===== */
searchInput.oninput = renderIcons;

/* ===== Copy ===== */
function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`;
  navigator.clipboard.writeText(code);
}
