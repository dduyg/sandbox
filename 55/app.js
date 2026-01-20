let svgs = []
let activeTags = new Set()
let tagMode = 'OR'
let favoritesOnly = false
let tagsExpanded = false

const gallery = document.getElementById('gallery')
const tagList = document.getElementById('tagList')
const searchInput = document.getElementById('search')

const FAVORITES_KEY = 'svg-favorites'
const VISIBLE_TAGS = 12

fetch('catalog.svgs.json')
  .then(r => r.json())
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
  if (!activeTags.size) return true
  return tagMode === 'AND'
    ? [...activeTags].every(t => svg.tags.includes(t))
    : [...activeTags].some(t => svg.tags.includes(t))
}

function renderSvgs() {
  const search = searchInput.value.toLowerCase()
  const favs = getFavorites()
  gallery.innerHTML = ''

  svgs.filter(svg => {
    if (favoritesOnly && !favs.has(svg.id)) return false
    if (!matchesTags(svg)) return false
    if (
      !svg.name.toLowerCase().includes(search) &&
      !svg.tags.some(t => t.includes(search))
    ) return false
    return true
  }).forEach(svg => {
    const el = document.createElement('div')
    el.className = 'item'
    el.innerHTML = `
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
    gallery.appendChild(el)
  })
}

function renderTags() {
  const counts = {}
  svgs.forEach(s => s.tags.forEach(t => counts[t] = (counts[t] || 0) + 1))

  const sortedTags = Object.entries(counts)
    .sort((a,b) => b[1] - a[1])
    .map(e => e[0])

  tagList.innerHTML = ''

  const visible = tagsExpanded ? sortedTags : sortedTags.slice(0, VISIBLE_TAGS)

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

  if (sortedTags.length > VISIBLE_TAGS) {
    const more = document.createElement('div')
    more.className = 'tag more'
    more.textContent = tagsExpanded ? 'less' : '…'
    more.onclick = () => {
      tagsExpanded = !tagsExpanded
      renderTags()
    }
    tagList.appendChild(more)
  }
}

function copySVG(svg) {
  navigator.clipboard.writeText(
    `<svg viewBox="${svg.viewBox}" xmlns="http://www.w3.org/2000/svg">${svg.svg}</svg>`
  )
}

searchInput.addEventListener('input', renderSvgs)

document.getElementById('orBtn').onclick = e => {
  tagMode = 'OR'
  e.target.classList.add('active')
  document.getElementById('andBtn').classList.remove('active')
  renderSvgs()
}

document.getElementById('andBtn').onclick = e => {
  tagMode = 'AND'
  e.target.classList.add('active')
  document.getElementById('orBtn').classList.remove('active')
  renderSvgs()
}

document.getElementById('favToggle').onclick = () => {
  favoritesOnly = !favoritesOnly
  renderSvgs()
}
