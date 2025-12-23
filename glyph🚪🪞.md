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
