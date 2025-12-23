# 💠glyphPipeline

An advanced image processing pipeline that transforms visual assets into a rich, queryable dataset with comprehensive color, texture, and aesthetic metrics.

### An intelligent pipeline
This pipeline transforms simple PNG images into richly annotated visual data assets by:

- **Color Intelligence**: K-means clustering extracts dominant/secondary colors with hex, RGB, and LAB color space representations
- **Computing Visual Metrics**: Quantifies edge density, Shannon entropy, texture complexity, contrast, shape properties, and edge angles
- **Aesthetic Profiling**: Evaluates color harmony and classifies mood (serene, playful, energetic, mysterious, dramatic, etc.)
- **Automated Storage**: Commits processed glyphs + structured data (JSON/CSV) directly to GitHub via API
- **Incremental Updates**: Preserves existing library and appends new glyphs without overwriting

## 💠
Each glyph is analyzed for 15+ features and cataloged with a unique identifier, timestamped filename, and CDN url.

---
---

## 🪢 Example workflow
```
Destination: myusername/myrepo
Branch: main
Token: ghp_xxxxxxxxxxxx
Input: Select 150 PNG glyphs from local computer

→ Pipeline processes all images in parallel
→ Commits to myusername/myrepo:
   - glyphs/ff5733_20251220_143022_a8f3e1b9.png
   - glyphs/3498db_20251220_143023_c2d4e5f6.png
   - data/glyphs.catalog.json
   - data/glyphs.catalog.csv
```

### 🎭 Example Queries

### Fetch from another repository
```python
# Fetch 1000+ glyphs from another repo
Source repo: sourceuser/source-repo
Folder path: pending_glyphs
Source branch: develop

→ Pipeline streams directly to destination repo
→ No local storage needed
```

> __🔧 Advanced Features__
> 
> <samp>Adjust worker threads for faster parallel processing:</samp>
> ```python
> stream_process_to_github(streamed, user, repo, token, max_workers=20)
> ```
> 
> <samp>Custom K-means Clustering, modify color extraction precision:</samp>
> ```python
> compute_dominant_color(rgb, mask, k=8)  # Default: 5
> ```

## ⚠️ Note
**Colors seem off** → Ensure PNGs have transparent backgrounds; opaque backgrounds skew color detection

**Image format:** PNG with transparency (alpha channel required for accurate masking)
