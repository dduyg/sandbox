let svgs = []
let activeTags = new Set()
let tagMode = 'OR'
let favoritesOnly = false
let tagsExpanded = false

const MAX_VISIBLE_TAGS = 12
const FAVORITES_KEY = 'svg-favorites'

const gallery = document.getElementById('gallery')
const tagList = document.getElementById('tagList')
const searchInput = document.getElementById('search')

fetch('catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    svgs = data
    renderTags()
    renderSvgs()
  })

function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'))
}

function toggleFavorite(id) {
  const favs = getFavorites()
  favs.has(id) ? favs.delete(id) : favs.add(id)
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]))
  renderSvgs()
}

function matchesTags(svg) {
  if (activeTags.size === 0) return true
  return tagMode === 'AND'
    ? [...activeTags].every(t => svg.tags.includes(t))
    : [...activeTags].some(t => svg.tags.includes(t))
}

function renderSvgs() {
  const search = searchInput.value.toLowerCase()
  const favs = getFavorites()

  gallery.innerHTML = ''

  svgs
    .filter(svg => {
      if (favoritesOnly && !favs.has(svg.id)) return false
      if (!matchesTags(svg)) return false

      if (
        !svg.name.toLowerCase().includes(search) &&
        !svg.tags.some(t => t.includes(search))
      ) return false

      return true
    })
    .forEach(svg => {
      const div = document.createElement('div')
      div.className = 'item'

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
      `
      gallery.appendChild(div)
    })
}

function renderTags() {
  const counts = {}

  svgs.forEach(svg => {
    svg.tags.forEach(tag => {
      counts[tag] = (counts[tag] || 0) + 1
    })
  })

  const sorted = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([tag]) => tag)

  const visible = tagsExpanded
    ? sorted
    : sorted.slice(0, MAX_VISIBLE_TAGS)

  tagList.innerHTML = ''

  visible.forEach(tag => {
    const el = document.createElement('div')
    el.className = 'tag'
    el.textContent = tag
    if (activeTags.has(tag)) el.classList.add('active')

    el.onclick = () => {
      activeTags.has(tag) ? activeTags.delete(tag) : activeTags.add(tag)
      el.classList.toggle('active')
      renderSvgs()
    }

    tagList.appendChild(el)
  })

  if (sorted.length > MAX_VISIBLE_TAGS) {
    const more = document.createElement('div')
    more.className = 'tag'
    more.textContent = tagsExpanded ? 'less' : '…'
    more.onclick = () => {
      tagsExpanded = !tagsExpanded
      renderTags()
    }
    tagList.appendChild(more)
  }
}

function copySVG(svg) {
  const code =
    `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`
  navigator.clipboard.writeText(code)
}

searchInput.addEventListener('input', renderSvgs)

document.getElementById('orBtn').onclick = () => {
  tagMode = 'OR'
  renderSvgs()
}

document.getElementById('andBtn').onclick = () => {
  tagMode = 'AND'
  renderSvgs()
}

document.getElementById('favToggle').onclick = () => {
  favoritesOnly = !favoritesOnly
  renderSvgs()
}
