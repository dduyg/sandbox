import { useState, useEffect, useRef } from "react";
import { createClient } from "@supabase/supabase-js";

// ── PASTE YOUR SUPABASE CREDENTIALS HERE ──────────────────────
const SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co";
const SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";
// ──────────────────────────────────────────────────────────────

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function aiSearch(query, images) {
  const imageList = images
    .map((img) => `ID:${img.id} | Caption: "${img.caption}" | Tags: ${(img.tags || []).join(", ")}`)
    .join("\n");

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      messages: [
        {
          role: "user",
          content: `You are an image search engine. Given a user query and a list of images with captions and tags, return the IDs of the most relevant images sorted by relevance.

User query: "${query}"

Available images:
${imageList}

Respond ONLY with a JSON object like: {"ids": [3, 7, 1], "reasoning": "short explanation"}
Match semantically. If no matches, return {"ids": [], "reasoning": "..."}`,
        },
      ],
    }),
  });

  const data = await response.json();
  const text = data.content?.[0]?.text || '{"ids":[]}';
  const clean = text.replace(/```json|```/g, "").trim();
  return JSON.parse(clean);
}

export default function App() {
  const [query, setQuery] = useState("");
  const [allImages, setAllImages] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [reasoning, setReasoning] = useState("");
  const [selected, setSelected] = useState(null);
  const [activeTag, setActiveTag] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  // Load all images from Supabase on mount
  useEffect(() => {
    async function fetchImages() {
      setFetching(true);
      const { data, error } = await supabase
        .from("images")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) {
        setError("Could not connect to Supabase. Check your credentials in App.jsx.");
        setFetching(false);
        return;
      }
      setAllImages(data || []);
      setResults(data || []);
      setFetching(false);
    }
    fetchImages();
  }, []);

  const allTags = [...new Set((allImages || []).flatMap((img) => img.tags || []))].sort();

  const handleSearch = async () => {
    if (!query.trim() && !activeTag) {
      setResults(allImages);
      setReasoning("");
      return;
    }
    setLoading(true);
    setReasoning("");
    try {
      if (activeTag) {
        setResults(allImages.filter((img) => (img.tags || []).includes(activeTag)));
      } else {
        const result = await aiSearch(query, allImages);
        if (result.ids.length === 0) {
          setResults([]);
        } else {
          const sorted = result.ids
            .map((id) => allImages.find((img) => img.id === id))
            .filter(Boolean);
          setResults(sorted);
        }
        setReasoning(result.reasoning || "");
      }
    } catch (e) {
      const q = query.toLowerCase();
      setResults(
        allImages.filter(
          (img) =>
            img.caption?.toLowerCase().includes(q) ||
            (img.tags || []).some((t) => t.includes(q))
        )
      );
      setReasoning("Keyword fallback used (AI search unavailable).");
    }
    setLoading(false);
  };

  const handleTagClick = (tag) => {
    const next = tag === activeTag ? null : tag;
    setActiveTag(next);
    setQuery("");
    setReasoning("");
    if (next) {
      setResults(allImages.filter((img) => (img.tags || []).includes(next)));
    } else {
      setResults(allImages);
    }
  };

  const handleReset = () => {
    setQuery("");
    setActiveTag(null);
    setResults(allImages);
    setReasoning("");
  };

  const handleDownload = (img) => {
    const a = document.createElement("a");
    a.href = img.url;
    a.download = img.filename || `image-${img.id}.jpg`;
    a.target = "_blank";
    a.click();
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0f", fontFamily: "'DM Mono', 'Fira Code', monospace", color: "#e8e4dc" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a0f; }
        ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 3px; }
        .card { transition: transform 0.25s ease, box-shadow 0.25s ease; cursor: pointer; }
        .card:hover { transform: translateY(-4px) scale(1.01); box-shadow: 0 16px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(180,140,255,0.2); }
        .card:hover .card-img { transform: scale(1.06); }
        .card-img { transition: transform 0.4s ease; }
        .tag-pill { cursor: pointer; transition: all 0.15s; }
        .tag-pill:hover { background: rgba(180,140,255,0.2) !important; color: #d4b8ff !important; }
        .search-input:focus { outline: none; border-color: #7c5cbf !important; box-shadow: 0 0 0 3px rgba(124,92,191,0.15); }
        .modal-overlay { animation: fadeIn 0.2s ease; }
        .modal-box { animation: slideUp 0.25s ease; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .dl-btn { transition: background 0.2s !important; }
        .dl-btn:hover { background: #7c5cbf !important; }
        .close-btn:hover { background: rgba(255,255,255,0.08) !important; }
        .grid-item { animation: fadeIn 0.35s ease both; }
        .open-btn:hover { border-color: #5c3d9e !important; color: #b09ad0 !important; }
        .search-btn:hover:not(:disabled) { background: #6d4ab8 !important; }
      `}</style>

      {/* Header */}
      <div style={{ borderBottom: "1px solid #1a1a28", padding: "24px 40px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontFamily: "'Syne', sans-serif", fontSize: "20px", fontWeight: 800, color: "#e8e4dc" }}>◈ ARCV</div>
          <div style={{ fontSize: "10px", color: "#3a3a4a", letterSpacing: "3px", marginTop: "3px" }}>IMAGE ARCHIVE SYSTEM</div>
        </div>
        <div style={{ fontSize: "10px", color: "#3a3a4a", letterSpacing: "1px" }}>
          {fetching ? "LOADING…" : `${allImages.length} IMAGES · SUPABASE + R2`}
        </div>
      </div>

      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "36px 40px" }}>

        {/* Error banner */}
        {error && (
          <div style={{ marginBottom: "24px", padding: "14px 18px", background: "rgba(220,60,60,0.1)", border: "1px solid rgba(220,60,60,0.3)", borderRadius: "10px", color: "#e88", fontSize: "12px" }}>
            ⚠ {error}
          </div>
        )}

        {/* Search bar */}
        <div style={{ marginBottom: "28px" }}>
          <div style={{ display: "flex", gap: "10px" }}>
            <div style={{ flex: 1, position: "relative" }}>
              <span style={{ position: "absolute", left: "16px", top: "50%", transform: "translateY(-50%)", color: "#444", fontSize: "16px", pointerEvents: "none" }}>⌕</span>
              <input
                ref={inputRef}
                className="search-input"
                value={query}
                onChange={(e) => { setQuery(e.target.value); setActiveTag(null); }}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Describe what you're looking for… e.g. 'charts about data' or 'space and satellites'"
                style={{ width: "100%", padding: "15px 16px 15px 44px", background: "#0f0f1a", border: "1px solid #2a2a3a", borderRadius: "10px", color: "#e8e4dc", fontSize: "13px", fontFamily: "inherit", transition: "border-color 0.2s, box-shadow 0.2s" }}
              />
            </div>
            <button
              className="search-btn"
              onClick={handleSearch}
              disabled={loading || fetching}
              style={{ padding: "15px 26px", background: loading || fetching ? "#2a2a3a" : "#5c3d9e", border: "none", borderRadius: "10px", color: "#e8e4dc", fontFamily: "inherit", fontSize: "12px", fontWeight: 500, cursor: loading || fetching ? "not-allowed" : "pointer", letterSpacing: "1.5px", whiteSpace: "nowrap", transition: "background 0.2s" }}
            >
              {loading ? "SEARCHING…" : "AI SEARCH"}
            </button>
            <button
              onClick={handleReset}
              style={{ padding: "15px 18px", background: "transparent", border: "1px solid #2a2a3a", borderRadius: "10px", color: "#555", fontFamily: "inherit", fontSize: "12px", cursor: "pointer", letterSpacing: "1px" }}
            >
              RESET
            </button>
          </div>
          {reasoning && (
            <div style={{ marginTop: "10px", padding: "10px 16px", background: "rgba(92,61,158,0.08)", borderLeft: "2px solid #5c3d9e", borderRadius: "0 6px 6px 0", fontSize: "11px", color: "#8a72b0", lineHeight: 1.6 }}>
              ✦ {reasoning}
            </div>
          )}
        </div>

        {/* Tag filter */}
        {allTags.length > 0 && (
          <div style={{ marginBottom: "28px" }}>
            <div style={{ fontSize: "10px", color: "#3a3a4a", letterSpacing: "2px", marginBottom: "10px" }}>FILTER BY TAG</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {allTags.map((tag) => (
                <span
                  key={tag}
                  className="tag-pill"
                  onClick={() => handleTagClick(tag)}
                  style={{ padding: "4px 12px", borderRadius: "100px", fontSize: "11px", background: activeTag === tag ? "rgba(180,140,255,0.15)" : "rgba(255,255,255,0.03)", color: activeTag === tag ? "#c4a8f0" : "#555", border: `1px solid ${activeTag === tag ? "rgba(180,140,255,0.35)" : "#1e1e2e"}` }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Count */}
        <div style={{ fontSize: "10px", color: "#3a3a4a", letterSpacing: "2px", marginBottom: "18px" }}>
          {fetching ? "LOADING IMAGES…" : `${results.length} RESULT${results.length !== 1 ? "S" : ""}${activeTag ? ` · TAG: ${activeTag.toUpperCase()}` : query ? ` · "${query.toUpperCase()}"` : " · ALL IMAGES"}`}
        </div>

        {/* Loading state */}
        {fetching && (
          <div style={{ textAlign: "center", padding: "80px 40px", color: "#333" }}>
            <div style={{ fontSize: "36px", marginBottom: "14px" }}>◌</div>
            <div style={{ fontFamily: "'Syne', sans-serif", fontSize: "16px", color: "#555" }}>Loading your archive…</div>
          </div>
        )}

        {/* Empty state */}
        {!fetching && results.length === 0 && (
          <div style={{ textAlign: "center", padding: "80px 40px", color: "#333" }}>
            <div style={{ fontSize: "36px", marginBottom: "14px" }}>◎</div>
            <div style={{ fontFamily: "'Syne', sans-serif", fontSize: "16px", marginBottom: "6px", color: "#555" }}>
              {allImages.length === 0 ? "No images yet — run the ingest script to add images" : "No images match your search"}
            </div>
            <div style={{ fontSize: "11px", color: "#3a3a4a" }}>
              {allImages.length === 0 ? "See SETUP_GUIDE.md for instructions" : "Try different keywords or browse by tag"}
            </div>
          </div>
        )}

        {/* Grid */}
        {!fetching && results.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "14px" }}>
            {results.map((img, i) => (
              <div
                key={img.id}
                className="card grid-item"
                onClick={() => setSelected(img)}
                style={{ background: "#0f0f1a", borderRadius: "12px", border: "1px solid #1a1a28", overflow: "hidden", animationDelay: `${i * 0.03}s` }}
              >
                <div style={{ position: "relative", paddingTop: "65%", background: "#080810", overflow: "hidden" }}>
                  <img
                    className="card-img"
                    src={img.thumb_url || img.url}
                    alt={img.caption}
                    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover" }}
                    onError={(e) => { e.target.style.display = "none"; }}
                  />
                  <div style={{ position: "absolute", top: "9px", right: "9px", background: "rgba(5,5,12,0.75)", borderRadius: "5px", padding: "2px 7px", fontSize: "10px", color: "#555", backdropFilter: "blur(4px)" }}>
                    #{img.id}
                  </div>
                </div>
                <div style={{ padding: "13px" }}>
                  <div style={{ fontSize: "11px", color: "#9a9088", lineHeight: 1.55, marginBottom: "9px" }}>{img.caption}</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginBottom: "9px" }}>
                    {(img.tags || []).slice(0, 3).map((t) => (
                      <span key={t} style={{ fontSize: "10px", padding: "2px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "100px", color: "#4a4a5a", border: "1px solid #1a1a28" }}>{t}</span>
                    ))}
                    {(img.tags || []).length > 3 && <span style={{ fontSize: "10px", color: "#3a3a4a" }}>+{img.tags.length - 3}</span>}
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px", color: "#2e2e3e" }}>
                    <span>{img.created_at ? new Date(img.created_at).toLocaleDateString() : ""}</span>
                    <span>{img.size || ""}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {selected && (
        <div
          className="modal-overlay"
          onClick={() => setSelected(null)}
          style={{ position: "fixed", inset: 0, background: "rgba(4,4,10,0.93)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: "20px", backdropFilter: "blur(10px)" }}
        >
          <div
            className="modal-box"
            onClick={(e) => e.stopPropagation()}
            style={{ background: "#0d0d1a", borderRadius: "16px", border: "1px solid #2a2a3a", maxWidth: "860px", width: "100%", maxHeight: "92vh", overflow: "auto" }}
          >
            <div style={{ padding: "18px 22px", borderBottom: "1px solid #1a1a28", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontFamily: "'Syne', sans-serif", fontSize: "15px", fontWeight: 700, color: "#e8e4dc" }}>{selected.filename || `Image #${selected.id}`}</div>
                <div style={{ fontSize: "10px", color: "#3a3a4a", marginTop: "3px" }}>{selected.dims || ""} · {selected.size || ""}</div>
              </div>
              <button className="close-btn" onClick={() => setSelected(null)} style={{ background: "transparent", border: "1px solid #2a2a3a", borderRadius: "8px", color: "#555", fontSize: "18px", cursor: "pointer", width: "34px", height: "34px", lineHeight: "34px", textAlign: "center", transition: "background 0.15s" }}>×</button>
            </div>
            <div style={{ background: "#06060f" }}>
              <img src={selected.url} alt={selected.caption} style={{ width: "100%", maxHeight: "480px", objectFit: "contain", display: "block" }} />
            </div>
            <div style={{ padding: "22px" }}>
              <div style={{ fontSize: "13px", color: "#a09888", lineHeight: 1.7, marginBottom: "18px" }}>{selected.caption}</div>
              <div style={{ fontSize: "10px", color: "#3a3a4a", letterSpacing: "2px", marginBottom: "9px" }}>ALL TAGS</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "22px" }}>
                {(selected.tags || []).map((t) => (
                  <span key={t} style={{ fontSize: "11px", padding: "4px 12px", background: "rgba(160,120,220,0.07)", borderRadius: "100px", color: "#8a72b0", border: "1px solid rgba(160,120,220,0.15)" }}>{t}</span>
                ))}
              </div>
              <div style={{ display: "flex", gap: "10px" }}>
                <button className="dl-btn" onClick={() => handleDownload(selected)} style={{ flex: 1, padding: "13px", background: "#5c3d9e", border: "none", borderRadius: "10px", color: "#e8e4dc", fontFamily: "inherit", fontSize: "12px", fontWeight: 500, cursor: "pointer", letterSpacing: "1.5px" }}>
                  ↓ DOWNLOAD IMAGE
                </button>
                <button className="open-btn" onClick={() => window.open(selected.url, "_blank")} style={{ padding: "13px 18px", background: "transparent", border: "1px solid #2a2a3a", borderRadius: "10px", color: "#555", fontFamily: "inherit", fontSize: "12px", cursor: "pointer", letterSpacing: "1px", transition: "border-color 0.15s, color 0.15s" }}>
                  ↗ FULL RES
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
