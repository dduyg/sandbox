"""
═══════════════════════════════════════════════════════════════════
                        FONT CATALOGER PIPELINE
═══════════════════════════════════════════════════════════════════
Author: Duygu Dağdelen
Date: January 2026

Features:
- High-resolution rendering for CLIP
- Always produces suggested tags
- Silent warnings
- Interactive tag selection
- Single/multiple fonts support
- Google, Web, or Custom font support
═══════════════════════════════════════════════════════════════════
"""

import subprocess, sys, logging, warnings

# ------------------ Dependency installation ------------------
def install(package_name, module_name=None):
    if module_name is None: module_name = package_name
    try: __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

dependencies = {
    "cssutils": "cssutils",
    "torch": "torch",
    "open_clip": "open-clip-torch",
    "PIL": "Pillow",
    "freetype": "freetype-py",
    "requests": "requests"
}
for module, pip_name in dependencies.items():
    install(pip_name, module)

# ------------------ Suppress warnings ------------------
warnings.filterwarnings("ignore")
logging.getLogger("PIL").setLevel(logging.CRITICAL)
import cssutils
cssutils.log.setLevel(logging.CRITICAL)

# ------------------ Imports ------------------
import os, re, json, base64, getpass, tempfile, requests
import torch, open_clip, freetype
from PIL import Image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMAGE_SIZE = 1024
FONT_SIZE = 128
CLIP_MODEL = "ViT-L-14"
CLIP_PRETRAIN = "openai"
CATEGORIES = ["sans-serif", "serif", "monospace", "cursive", "fantasy"]

TAGS = [
    "geometric", "formal", "handwritten", "fatface", "monospaced", "techno",
    "pixel", "medieval", "art nouveau", "blobby", "distressed", "wood",
    "wacky", "shaded", "marker", "futuristic", "vintage", "calm", "playful",
    "sophisticated", "business", "stiff", "childlike", "horror", "distorted",
    "clean", "warm", "aesthetic", "brutalist", "modular", "neutral",
    "contemporary", "rounded", "approachable", "humanist", "coding",
    "retro", "android"
]

# ------------------ Font samples ------------------
SAMPLES = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789 !@#$%^&*()",
    "Il1O0",
    "The quick brown fox jumps over the lazy dog",
    "function renderFont(x) { return x + 1; }",
    "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"
]

def build_prompts():
    prompts = {}
    for tag in TAGS:
        prompts[tag] = [
            f"a {tag} font",
            f"a {tag} typeface",
            f"{tag} style font"
        ]
    return prompts

# ------------------ Font source detection ------------------
def detect_font_source(url: str) -> str:
    url = url.lower()
    if "fonts.googleapis.com" in url:
        return "google"
    elif url.endswith((".woff2", ".woff", ".ttf", ".otf")):
        return "custom"
    else:
        return "web"

def download_font_file(url):
    r = requests.get(url); r.raise_for_status()
    suffix = os.path.splitext(url.split("?")[0])[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content); tmp.close()
    return tmp.name

def download_web_font(css_url):
    r = requests.get(css_url); r.raise_for_status()
    sheet = cssutils.parseString(r.text)
    font_urls = []
    for rule in sheet:
        if rule.type == rule.FONT_FACE_RULE:
            src = rule.style.getPropertyValue("src")
            matches = re.findall(r'url\((https:[^)]+)\)', src)
            font_urls.extend(matches)
    if not font_urls: raise RuntimeError("No font URLs found in CSS")
    font_url = next((u for u in font_urls if "woff2" in u), font_urls[0])
    return download_font_file(font_url)

def retrieve_font(url):
    source = detect_font_source(url)
    if source in ["google", "web"]:
        path = download_web_font(url)
    else:
        path = download_font_file(url)
    return path, source

# ------------------ Font rendering ------------------
def render_sample(face, text):
    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), "white")
    pen_x, pen_y = 40, IMAGE_SIZE // 2
    for char in text:
        face.load_char(char)
        bitmap = face.glyph.bitmap
        top, left = face.glyph.bitmap_top, face.glyph.bitmap_left
        y = pen_y - top; x = pen_x + left
        for row in range(bitmap.rows):
            for col in range(bitmap.width):
                val = bitmap.buffer[row * bitmap.width + col]
                if val > 0:
                    px, py = x+col, y+row
                    if 0 <= px < IMAGE_SIZE and 0 <= py < IMAGE_SIZE:
                        img.putpixel((px, py), (0,0,0))
        pen_x += face.glyph.advance.x >> 6
        if pen_x > IMAGE_SIZE - 40: break
    return img

def render_font_images(font_path):
    face = freetype.Face(font_path); face.set_char_size(FONT_SIZE*64)
    return [render_sample(face, s) for s in SAMPLES]

# ------------------ CLIP tagging ------------------
def cosine(a,b):
    return (a @ b).item() if a.ndim==1 and b.ndim==1 else (a @ b.mT).item()

def tag_font(images):
    model, _, preprocess = open_clip.create_model_and_transforms(
        CLIP_MODEL, pretrained=CLIP_PRETRAIN, device=DEVICE
    )
    tokenizer = open_clip.get_tokenizer(CLIP_MODEL)
    model.eval()
    image_tensors = torch.stack([preprocess(img) for img in images]).to(DEVICE)
    with torch.no_grad():
        image_features = model.encode_image(image_tensors)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    prompts = build_prompts()
    results = {}
    for tag, texts in prompts.items():
        tokens = tokenizer(texts).to(DEVICE)
        with torch.no_grad():
            text_features = model.encode_text(tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        score = 0.0
        for img_feat in image_features:
            sims = [cosine(img_feat, txt_feat) for txt_feat in text_features]
            score += sum(sorted(sims, reverse=True)[:2])/2  # Top-2 similarity
        results[tag] = score/len(image_features)
    return dict(sorted(results.items(), key=lambda x:x[1], reverse=True))

# ------------------ Catalog fetch/update ------------------
def fetch_catalog(repo, token, file_path="catalog.fonts.json"):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers); r.raise_for_status()
    content = r.json()
    sha = content["sha"]
    data = base64.b64decode(content["content"]).decode("utf-8")
    return json.loads(data), sha

def update_catalog(repo, token, catalog, sha, file_path="catalog.fonts.json", commit_message="Update catalog"):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    content_bytes = json.dumps(catalog, indent=2, ensure_ascii=False).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
    payload = {"message": commit_message, "content": content_b64, "sha": sha}
    r = requests.put(url, headers=headers, json=payload); r.raise_for_status()

# ------------------ Processing font entry ------------------
def process_font_entry(font_entry):
    name, url = font_entry["name"], font_entry["url"]
    category = font_entry.get("category", "sans-serif").lower()
    if category not in CATEGORIES: category = "sans-serif"
    path, source = retrieve_font(url)
    images = render_font_images(path)
    scores = tag_font(images)
    suggested_tags = [k for k,v in scores.items() if v >= 0.12]  # Lower threshold for always suggestions

    print(f"\nProcessing font: {name}")
    print(f"　　　ＳＵＧＧＥＳＴＥＤ  ＴＡＧＳ: {', '.join(suggested_tags)}")
    print("\n　　　ＯＰＴＩＯＮＳ：")
    print("　　　 • Press Enter to accept ALL")
    print("　　　 • Type tag numbers to keep (e.g., 1,3,5)")
    print("　　　 • Type your own tags (comma-separated)")

    for idx, tag in enumerate(suggested_tags):
        print(f"　　　 {idx+1}. {tag}")
    user_input = input("Your choice: ").strip()
    if user_input == "":
        final_tags = suggested_tags
    elif all(c.isdigit() or c in ", " for c in user_input):
        numbers = [int(n)-1 for n in user_input.split(",") if n.strip().isdigit()]
        final_tags = [suggested_tags[i] for i in numbers if 0<=i<len(suggested_tags)]
    else:
        final_tags = [t.strip() for t in user_input.split(",")]

    preview = {"name": name, "source": source, "url": url, "category": category, "tags": final_tags}
    print("\nPreview entry:")
    print(json.dumps(preview, indent=2, ensure_ascii=False))
    confirm = input("\nAdd/update this font in catalog? (y/n): ").strip().lower()
    return preview if confirm=="y" else None

# ------------------ Main update function ------------------
def analyze_and_update_fonts(repo, token, font_entries):
    catalog, sha = fetch_catalog(repo, token)
    updated = False
    for font_entry in font_entries:
        processed = process_font_entry(font_entry)
        if processed:
            for i, existing in enumerate(catalog):
                if existing["name"].lower() == processed["name"].lower():
                    catalog[i] = processed
                    updated = True
                    break
            else:
                catalog.append(processed)
                updated = True
    if updated:
        update_catalog(repo, token, catalog, sha, commit_message="Add/update fonts")
        print("\nCatalog updated successfully!")
    else:
        print("\nNo changes made to catalog.")

# ------------------ CLI ------------------
if __name__ == "__main__":
    repo = input("Enter repo (username/repo-name): ").strip()
    token = getpass.getpass("Enter your Personal Access Token (hidden): ").strip()
    mode = input("Add single font or multiple? (single/multiple): ").strip().lower()
    fonts_to_process = []

    if mode=="single":
        name = input("Enter font name: ").strip()
        url = input("Enter font URL: ").strip()
        while True:
            category = input(f"Enter category ({', '.join(CATEGORIES)}): ").strip().lower()
            if category in CATEGORIES: break
        fonts_to_process.append({"name": name, "url": url, "category": category})
    else:
        n = int(input("How many fonts to add/update? "))
        for _ in range(n):
            name = input("Font name: ").strip()
            url = input("Font URL: ").strip()
            while True:
                category = input(f"Category ({', '.join(CATEGORIES)}): ").strip().lower()
                if category in CATEGORIES: break
            fonts_to_process.append({"name": name, "url": url, "category": category})

    analyze_and_update_fonts(repo, token, fonts_to_process)
