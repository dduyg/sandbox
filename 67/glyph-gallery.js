/**
 * Glyph Gallery - Duygu Dağdelen (@dduyg)
 * Data-driven gallery with search by color, filtering, and export functionality
 */

const DATA_URL = `https://cdn.jsdelivr.net/gh/dduyg/glyph-data-library@main/data/glyphs.catalog.json`;
let allGlyphs = [];
let filteredGlyphs = [];
let selectedGlyphs = new Set();
let filters = {
    pickedColor: null,
    sort: 'newest',
    mood: null,
    shape: null,
    harmony: null
};

let currentHue = 0;
let isDraggingGradient = false;
let isDraggingHue = false;
let pendingColor = null;

const moods = ['serene', 'calm', 'playful', 'energetic', 'futuristic', 'mysterious', 'dramatic', 'chaotic'];
const shapes = ['circular', 'angular', 'wide', 'tall'];
const harmonies = ['analogous', 'complementary'];

// ==================== INITIALIZATION ====================

// Initialize mood tags
const moodTagsEl = document.getElementById('moodTags');
moods.forEach(mood => {
    const tag = document.createElement('div');
    tag.className = 'tag';
    tag.textContent = mood;
    tag.onclick = () => toggleFilter('mood', mood, tag);
    moodTagsEl.appendChild(tag);
});

// Initialize shape tags
const shapeTagsEl = document.getElementById('shapeTags');
shapes.forEach(shape => {
    const tag = document.createElement('div');
    tag.className = 'tag';
    tag.textContent = shape;
    tag.onclick = () => toggleFilter('shape', shape, tag);
    shapeTagsEl.appendChild(tag);
});

// Initialize harmony tags
const harmonyTagsEl = document.getElementById('harmonyTags');
harmonies.forEach(harmony => {
    const tag = document.createElement('div');
    tag.className = 'tag';
    tag.textContent = harmony;
    tag.onclick = () => toggleFilter('harmony', harmony, tag);
    harmonyTagsEl.appendChild(tag);
});

// ==================== COLOR PICKER ====================

// Color picker elements
const canvas = document.getElementById('gradientCanvas');
const ctx = canvas.getContext('2d');
const gradientCursor = document.getElementById('gradientCursor');
const hueSlider = document.getElementById('hueSlider');
const hueCursor = document.getElementById('hueCursor');
const colorPreview = document.getElementById('colorPreview');
const colorHexInput = document.getElementById('colorHexInput');
const searchColorBtn = document.getElementById('searchColorBtn');

// Canvas initialization
function initCanvas() {
    const container = document.getElementById('colorGradient');
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    drawGradient();
}

function drawGradient() {
    const width = canvas.width;
    const height = canvas.height;

    for (let x = 0; x < width; x++) {
        const satGradient = ctx.createLinearGradient(0, 0, 0, height);
        const sat = (x / width) * 100;
        
        satGradient.addColorStop(0, 'white');
        satGradient.addColorStop(0.5, `hsl(${currentHue}, ${sat}%, 50%)`);
        satGradient.addColorStop(1, 'black');
        
        ctx.fillStyle = satGradient;
        ctx.fillRect(x, 0, 1, height);
    }
}

// ==================== COLOR UTILITIES ====================

function hslToRgb(h, s, l) {
    s /= 100;
    l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    return [Math.round(255 * f(0)), Math.round(255 * f(8)), Math.round(255 * f(4))];
}

function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('').toUpperCase();
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0;
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
            case g: h = ((b - r) / d + 2) / 6; break;
            case b: h = ((r - g) / d + 4) / 6; break;
        }
    }
    return [h * 360, s * 100, l * 100];
}

function getColorFromCanvas(x, y) {
    const pixel = ctx.getImageData(x, y, 1, 1).data;
    return { r: pixel[0], g: pixel[1], b: pixel[2] };
}

function updateColorDisplay(rgb) {
    const hex = rgbToHex(rgb.r, rgb.g, rgb.b);
    colorPreview.style.background = hex;
    colorHexInput.value = hex;
    pendingColor = hex;
}

// RGB to LAB conversion for color distance calculations
function rgbToLab(rgb) {
    let r = rgb.r / 255;
    let g = rgb.g / 255;
    let b = rgb.b / 255;

    r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
    g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
    b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

    let x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047;
    let y = r * 0.2126 + g * 0.7152 + b * 0.0722;
    let z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883;

    x = x > 0.008856 ? Math.pow(x, 1/3) : 7.787 * x + 16/116;
    y = y > 0.008856 ? Math.pow(y, 1/3) : 7.787 * y + 16/116;
    z = z > 0.008856 ? Math.pow(z, 1/3) : 7.787 * z + 16/116;

    return [116 * y - 16, 500 * (x - y), 200 * (y - z)];
}

function labDistance(lab1, lab2) {
    const dL = lab1[0] - lab2[0];
    const da = lab1[1] - lab2[1];
    const db = lab1[2] - lab2[2];
    return Math.sqrt(dL * dL + da * da + db * db);
}

// ==================== COLOR PICKER INTERACTIONS ====================

const colorGradient = document.getElementById('colorGradient');

colorGradient.addEventListener('mousedown', (e) => {
    isDraggingGradient = true;
    updateGradientPosition(e);
});

document.addEventListener('mousemove', (e) => {
    if (isDraggingGradient) updateGradientPosition(e);
    if (isDraggingHue) updateHuePosition(e);
});

document.addEventListener('mouseup', () => {
    isDraggingGradient = false;
    isDraggingHue = false;
});

function updateGradientPosition(e) {
    const rect = canvas.getBoundingClientRect();
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;
    x = Math.max(0, Math.min(x, rect.width));
    y = Math.max(0, Math.min(y, rect.height));

    const canvasX = (x / rect.width) * canvas.width;
    const canvasY = (y / rect.height) * canvas.height;

    gradientCursor.style.left = x + 'px';
    gradientCursor.style.top = y + 'px';

    const rgb = getColorFromCanvas(canvasX, canvasY);
    updateColorDisplay(rgb);
}

hueSlider.addEventListener('mousedown', (e) => {
    isDraggingHue = true;
    updateHuePosition(e);
});

function updateHuePosition(e) {
    const rect = hueSlider.getBoundingClientRect();
    let x = e.clientX - rect.left;
    x = Math.max(0, Math.min(x, rect.width));

    hueCursor.style.left = x + 'px';
    currentHue = (x / rect.width) * 360;
    drawGradient();
    
    const cursorX = parseFloat(gradientCursor.style.left || rect.width / 2);
    const cursorY = parseFloat(gradientCursor.style.top || rect.height / 2);
    const canvasRect = canvas.getBoundingClientRect();
    const canvasX = (cursorX / canvasRect.width) * canvas.width;
    const canvasY = (cursorY / canvasRect.height) * canvas.height;
    const rgb = getColorFromCanvas(canvasX, canvasY);
    updateColorDisplay(rgb);
}

colorHexInput.addEventListener('input', (e) => {
    let value = e.target.value;
    if (!value.startsWith('#')) value = '#' + value;
    
    if (/^#[0-9A-F]{6}$/i.test(value)) {
        const rgb = hexToRgb(value);
        if (rgb) {
            colorPreview.style.background = value;
            const [h, s, l] = rgbToHsl(rgb.r, rgb.g, rgb.b);
            currentHue = h;
            hueCursor.style.left = (h / 360 * hueSlider.offsetWidth) + 'px';
            drawGradient();
            
            pendingColor = value;
        }
    }
});

searchColorBtn.addEventListener('click', () => {
    if (pendingColor) {
        filters.pickedColor = pendingColor;
        applyFilters();
        closeSidebar(colorSidebar);
    }
});

// Initialize color picker on load
window.addEventListener('load', () => {
    initCanvas();
    hueCursor.style.left = '0px';
    gradientCursor.style.left = '50%';
    gradientCursor.style.top = '50%';
    const rgb = getColorFromCanvas(canvas.width / 2, canvas.height / 2);
    const hex = rgbToHex(rgb.r, rgb.g, rgb.b);
    colorPreview.style.background = hex;
    colorHexInput.value = hex;
    pendingColor = hex;
});

window.addEventListener('resize', () => {
    initCanvas();
});

// ==================== SIDEBAR & DROPDOWN CONTROLS ====================

const sidebarOverlay = document.getElementById('sidebarOverlay');
const colorSidebar = document.getElementById('colorSidebar');
const filterSidebar = document.getElementById('filterSidebar');

document.getElementById('colorControl').onclick = (e) => {
    e.stopPropagation();
    closeSortDropdown();
    closeExportDropdown();
    toggleSidebar(colorSidebar);
};

document.getElementById('filterControl').onclick = (e) => {
    e.stopPropagation();
    closeSortDropdown();
    closeExportDropdown();
    toggleSidebar(filterSidebar);
};

function toggleSidebar(sidebar) {
    const isActive = sidebar.classList.contains('active');
    
    document.querySelectorAll('.sidebar').forEach(s => s.classList.remove('active'));
    sidebarOverlay.classList.remove('active');
    
    if (!isActive) {
        sidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
    }
}

function closeSidebar(sidebar) {
    sidebar.classList.remove('active');
    sidebarOverlay.classList.remove('active');
}

sidebarOverlay.onclick = () => {
    document.querySelectorAll('.sidebar').forEach(s => s.classList.remove('active'));
    sidebarOverlay.classList.remove('active');
};

document.getElementById('sortControl').onclick = (e) => {
    e.stopPropagation();
    closeAllSidebars();
    closeExportDropdown();
    toggleDropdown('sortPanel', 'sortControl');
};

document.getElementById('exportControl').onclick = (e) => {
    e.stopPropagation();
    closeAllSidebars();
    closeSortDropdown();
    toggleDropdown('exportPanel', 'exportControl');
};

function toggleDropdown(panelId, controlId) {
    const panel = document.getElementById(panelId);
    const control = document.getElementById(controlId);
    const wasActive = panel.classList.contains('active');
    
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('active'));
    document.querySelectorAll('.control-btn').forEach(c => c.classList.remove('active'));
    
    if (!wasActive) {
        panel.classList.add('active');
        control.classList.add('active');
    }
}

function closeSortDropdown() {
    document.getElementById('sortPanel').classList.remove('active');
    document.getElementById('sortControl').classList.remove('active');
}

function closeExportDropdown() {
    document.getElementById('exportPanel').classList.remove('active');
    document.getElementById('exportControl').classList.remove('active');
}

function closeAllSidebars() {
    document.querySelectorAll('.sidebar').forEach(s => s.classList.remove('active'));
    sidebarOverlay.classList.remove('active');
}

document.addEventListener('click', () => {
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('active'));
    document.querySelectorAll('.control-btn').forEach(c => c.classList.remove('active'));
});

document.querySelectorAll('.dropdown').forEach(panel => {
    panel.onclick = (e) => e.stopPropagation();
});

// ==================== CLEAR CONTROLS ====================

// Clear color sidebar
document.getElementById('clearColorSidebar').onclick = () => {
    filters.pickedColor = null;
    
    currentHue = 0;
    hueCursor.style.left = '0px';
    gradientCursor.style.left = '50%';
    gradientCursor.style.top = '50%';
    drawGradient();
    const rgb = getColorFromCanvas(canvas.width / 2, canvas.height / 2);
    const hex = rgbToHex(rgb.r, rgb.g, rgb.b);
    colorPreview.style.background = hex;
    colorHexInput.value = hex;
    pendingColor = hex;
    
    applyFilters();
};

// Clear filter sidebar
document.getElementById('clearFilterSidebar').onclick = () => {
    filters.mood = null;
    filters.shape = null;
    filters.harmony = null;
    
    document.querySelectorAll('.tag').forEach(tag => tag.classList.remove('active'));
    
    applyFilters();
};

// ==================== FILTER CONTROLS ====================

// Toggle filter tags
function toggleFilter(type, value, element) {
    const parent = element.parentElement;
    parent.querySelectorAll('.tag').forEach(tag => tag.classList.remove('active'));
    
    if (filters[type] === value) {
        filters[type] = null;
    } else {
        filters[type] = value;
        element.classList.add('active');
    }
    applyFilters();
}

// Sort options
document.querySelectorAll('[data-sort]').forEach(option => {
    option.onclick = () => {
        const sortValue = option.dataset.sort;
        document.querySelectorAll('[data-sort]').forEach(opt => opt.classList.remove('active'));
        option.classList.add('active');
        filters.sort = sortValue;
        applyFilters();
        closeSortDropdown();
    };
});

// ==================== DATA LOADING ====================

async function loadGlyphs() {
    try {
        const response = await fetch(DATA_URL);
        const data = await response.json();
        allGlyphs = data.glyphs;
        filteredGlyphs = [...allGlyphs];
        document.getElementById('totalCount').textContent = allGlyphs.length;
        document.querySelector('.dropdown-option[data-sort="newest"]').classList.add('active');
        applyFilters();
    } catch (error) {
        document.getElementById('gallery').innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <h2>Failed to load glyphs</h2>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// ==================== FILTERING & SORTING ====================

function applyFilters() {
    filteredGlyphs = allGlyphs.filter(glyph => {
        if (filters.mood && glyph.mood !== filters.mood) return false;
        
        if (filters.shape) {
            const circ = glyph.metrics.circularity;
            const ar = glyph.metrics.aspect_ratio;
            if (filters.shape === 'circular' && circ <= 0.85) return false;
            if (filters.shape === 'angular' && circ >= 0.5) return false;
            if (filters.shape === 'wide' && ar <= 1.5) return false;
            if (filters.shape === 'tall' && ar >= 0.7) return false;
        }
        
        if (filters.harmony && glyph.color_harmony !== filters.harmony) return false;
        
        return true;
    });

    // Color filtering - checks both dominant and secondary colors
    if (filters.pickedColor) {
        const pickedRgb = hexToRgb(filters.pickedColor);
        if (pickedRgb) {
            const pickedLab = rgbToLab(pickedRgb);
            
            filteredGlyphs = filteredGlyphs
                .map(g => {
                    // Check both dominant and secondary colors
                    const dominantLab = g.color.dominant.lab || rgbToLab({
                        r: g.color.dominant.rgb[0],
                        g: g.color.dominant.rgb[1],
                        b: g.color.dominant.rgb[2]
                    });
                    
                    const secondaryLab = g.color.secondary.lab || rgbToLab({
                        r: g.color.secondary.rgb[0],
                        g: g.color.secondary.rgb[1],
                        b: g.color.secondary.rgb[2]
                    });
                    
                    const dominantDistance = labDistance(pickedLab, dominantLab);
                    const secondaryDistance = labDistance(pickedLab, secondaryLab);
                    
                    // Use the minimum distance (closest match from either color)
                    const minDistance = Math.min(dominantDistance, secondaryDistance);
                    
                    return {
                        ...g,
                        colorDistance: minDistance
                    };
                })
                .filter(g => g.colorDistance < 50)
                .sort((a, b) => a.colorDistance - b.colorDistance);
        }
    }

    // Sort glyphs
    filteredGlyphs.sort((a, b) => {
        switch(filters.sort) {
            case 'newest':
                return new Date(`${b.created_at.date}T${b.created_at.time}`) - 
                       new Date(`${a.created_at.date}T${a.created_at.time}`);
            case 'oldest':
                return new Date(`${a.created_at.date}T${a.created_at.time}`) - 
                       new Date(`${b.created_at.date}T${b.created_at.time}`);
            case 'detail-high':
                return b.metrics.edge_density - a.metrics.edge_density;
            case 'detail-low':
                return a.metrics.edge_density - b.metrics.edge_density;
            default:
                return 0;
        }
    });

    renderGallery();
}

// ==================== GALLERY RENDERING ====================

function renderGallery() {
    const gallery = document.getElementById('gallery');
    document.getElementById('showingCount').textContent = filteredGlyphs.length;

    if (filteredGlyphs.length === 0) {
        gallery.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <h2>No glyphs found</h2>
                <p>Try adjusting your filters</p>
            </div>
        `;
        return;
    }

    gallery.innerHTML = filteredGlyphs.map(glyph => `
        <div class="glyph-card ${selectedGlyphs.has(glyph.id) ? 'selected' : ''}" 
             data-id="${glyph.id}">
            <img src="${glyph.glyph_url}" alt="${glyph.filename}" class="glyph-image">
        </div>
    `).join('');

    document.querySelectorAll('.glyph-card').forEach(card => {
        card.onclick = () => toggleSelection(card.dataset.id, card);
    });
}

// ==================== SELECTION MANAGEMENT ====================

function toggleSelection(id, card) {
    if (selectedGlyphs.has(id)) {
        selectedGlyphs.delete(id);
        card.classList.remove('selected');
    } else {
        selectedGlyphs.add(id);
        card.classList.add('selected');
    }
    updateExportButton();
}

function updateExportButton() {
    const selectionLine = document.getElementById('selectionLine');
    const selectedCount = document.getElementById('selectedCount');
    
    if (selectedGlyphs.size > 0) {
        selectionLine.classList.add('active');
        selectedCount.textContent = selectedGlyphs.size;
    } else {
        selectionLine.classList.remove('active');
    }
}

function clearSelections() {
    selectedGlyphs.clear();
    document.querySelectorAll('.glyph-card').forEach(card => {
        card.classList.remove('selected');
    });
    updateExportButton();
}

document.getElementById('selectionTick').addEventListener('click', (e) => {
    e.stopPropagation();
    const selectionLine = document.getElementById('selectionLine');
    selectionLine.classList.add('clearing');
    
    setTimeout(() => {
        clearSelections();
        selectionLine.classList.remove('clearing');
    }, 300);
});

// ==================== EXPORT FUNCTIONALITY ====================

document.getElementById('downloadJSON').onclick = () => {
    const selected = allGlyphs.filter(g => selectedGlyphs.has(g.id));
    const json = JSON.stringify({ glyphs: selected }, null, 2);
    downloadFile(json, 'glyphs-export.json', 'application/json');
    closeExportDropdown();
    clearSelections();
};

document.getElementById('downloadCSV').onclick = () => {
    const selected = allGlyphs.filter(g => selectedGlyphs.has(g.id));
    
    // Flatten the nested structure for CSV
    const flattenedData = selected.map(g => ({
        id: g.id,
        filename: g.filename,
        glyph_url: g.glyph_url,
        dominant_hex: g.color.dominant.hex,
        dominant_rgb_r: g.color.dominant.rgb[0],
        dominant_rgb_g: g.color.dominant.rgb[1],
        dominant_rgb_b: g.color.dominant.rgb[2],
        dominant_lab_l: g.color.dominant.lab[0],
        dominant_lab_a: g.color.dominant.lab[1],
        dominant_lab_b: g.color.dominant.lab[2],
        secondary_hex: g.color.secondary.hex,
        secondary_rgb_r: g.color.secondary.rgb[0],
        secondary_rgb_g: g.color.secondary.rgb[1],
        secondary_rgb_b: g.color.secondary.rgb[2],
        secondary_lab_l: g.color.secondary.lab[0],
        secondary_lab_a: g.color.secondary.lab[1],
        secondary_lab_b: g.color.secondary.lab[2],
        palette_distance: g.color.palette_distance,
        edge_density: g.metrics.edge_density,
        entropy: g.metrics.entropy,
        texture: g.metrics.texture,
        contrast: g.metrics.contrast,
        circularity: g.metrics.circularity,
        aspect_ratio: g.metrics.aspect_ratio,
        edge_angle: g.metrics.edge_angle,
        color_harmony: g.color_harmony,
        mood: g.mood,
        created_date: g.created_at.date,
        created_time: g.created_at.time
    }));
    
    const headers = Object.keys(flattenedData[0]);
    const csv = [
        headers.join(','),
        ...flattenedData.map(row => 
            headers.map(header => {
                const value = row[header];
                // Escape values containing commas or quotes
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            }).join(',')
        )
    ].join('\n');
    
    downloadFile(csv, 'glyphs-export.csv', 'text/csv');
    closeExportDropdown();
    clearSelections();
};

document.getElementById('copyURLs').onclick = () => {
    const selected = allGlyphs.filter(g => selectedGlyphs.has(g.id));
    const urls = selected.map(g => g.glyph_url).join('\n');
    navigator.clipboard.writeText(urls);
    closeExportDropdown();
    clearSelections();
};

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ==================== INITIALIZE APPLICATION ====================

loadGlyphs();
