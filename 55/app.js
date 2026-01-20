let svgs = []
let activeTags = new Set()
let tagMode = 'OR'
let favoritesOnly = false
let showAllTags = false

const TAG_LIMIT = 8
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
        !svg.id.toLowerCase().includes(search) &&
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

  svgs.forEach(s => {
    s.tags.forEach(t => counts[t] = (counts[t] || 0) + 1)
  })

  const sortedTags = Object.entries(counts)
    .sort((a,b) => b[1] - a[1])
    .map(([t]) => t)

  tagList.innerHTML = ''

  const visible = showAllTags ? sortedTags : sortedTags.slice(0, TAG_LIMIT)

  visible.forEach(tag => {
    const el = document.createElement('div')
    el.className = 'tag' + (activeTags.has(tag) ? ' active' : '')
    el.textContent = tag
    el.onclick = () => {
      activeTags.has(tag) ? activeTags.delete(tag) : activeTags.add(tag)
      renderTags()
      renderSvgs()
    }
    tagList.appendChild(el)
  })

  if (sortedTags.length > TAG_LIMIT) {
    const more = document.createElement('div')
    more.className = 'tag more'
    more.textContent = showAllTags ? 'less' : '…'
    more.onclick = () => {
      showAllTags = !showAllTags
      renderTags()
    }
    tagList.appendChild(more)
  }
}

function copySVG(svg) {
  const code = `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`
  navigator.clipboard.writeText(code)
}

searchInput.addEventListener('input', renderSvgs)

document.getElementById('orBtn').onclick = () => {
  tagMode = 'OR'
  document.getElementById('orBtn').classList.add('active')
  document.getElementById('andBtn').classList.remove('active')
  renderSvgs()
}

document.getElementById('andBtn').onclick = () => {
  tagMode = 'AND'
  document.getElementById('andBtn').classList.add('active')
  document.getElementById('orBtn').classList.remove('active')
  renderSvgs()
}

document.getElementById('favToggle').onclick = e => {
  favoritesOnly = !favoritesOnly
  e.target.classList.toggle('active', favoritesOnly)
  renderSvgs()
}
