let icons = []
let activeTags = new Set()
let tagMode = 'OR'
let favoritesOnly = false

const gallery = document.getElementById('gallery')
const tagList = document.getElementById('tagList')
const searchInput = document.getElementById('search')

const FAVORITES_KEY = 'svg-favorites'

fetch('catalog.svgs.json')
  .then(res => res.json())
  .then(data => {
    icons = data
    renderTags()
    renderIcons()
  })

function getFavorites() {
  return new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'))
}

function toggleFavorite(id) {
  const favs = getFavorites()
  favs.has(id) ? favs.delete(id) : favs.add(id)
  localStorage.setItem(FAVORITES_KEY, JSON.stringify([...favs]))
  renderIcons()
}

function matchesTags(icon) {
  if (activeTags.size === 0) return true
  return tagMode === 'AND'
    ? [...activeTags].every(t => icon.tags.includes(t))
    : [...activeTags].some(t => icon.tags.includes(t))
}

function renderIcons() {
  const search = searchInput.value.toLowerCase()
  const favs = getFavorites()

  gallery.innerHTML = ''

  icons
    .filter(icon => {
      if (favoritesOnly && !favs.has(icon.id)) return false
      if (!matchesTags(icon)) return false
      if (
        !icon.name.toLowerCase().includes(search) &&
        !icon.tags.some(t => t.includes(search))
      ) return false
      return true
    })
    .forEach(icon => {
      const div = document.createElement('div')
      div.className = 'item'

      div.innerHTML = `
        <svg viewBox="${icon.viewBox}" xmlns="http://www.w3.org/2000/svg">
          ${icon.svg}
        </svg>
        <div>${icon.name}</div>
        <div class="actions">
          <button onclick="toggleFavorite('${icon.id}')">
            ${favs.has(icon.id) ? '★' : '☆'}
          </button>
          <button onclick='copySVG(${JSON.stringify(icon)})'><b>⿻</b></button>
        </div>
      `
      gallery.appendChild(div)
    })
}

function renderTags() {
  const tags = new Set()
  icons.forEach(i => i.tags.forEach(t => tags.add(t)))

  tagList.innerHTML = ''
  tags.forEach(tag => {
    const el = document.createElement('div')
    el.className = 'tag'
    el.textContent = tag
    el.onclick = () => {
      activeTags.has(tag) ? activeTags.delete(tag) : activeTags.add(tag)
      el.classList.toggle('active')
      renderIcons()
    }
    tagList.appendChild(el)
  })
}

function copySVG(icon) {
  const code = `<svg viewBox="${icon.viewBox}" xmlns="http://www.w3.org/2000/svg">${icon.svg}</svg>`
  navigator.clipboard.writeText(code)
}

searchInput.addEventListener('input', renderIcons)

document.getElementById('orBtn').onclick = () => {
  tagMode = 'OR'
  renderIcons()
}

document.getElementById('andBtn').onclick = () => {
  tagMode = 'AND'
  renderIcons()
}

document.getElementById('favToggle').onclick = () => {
  favoritesOnly = !favoritesOnly
  renderIcons()
  }
