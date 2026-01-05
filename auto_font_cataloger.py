"""
═══════════════════════════════════════════════════════════════════
　　　　　　　　　Ｆ Ｏ Ｎ Ｔ 　Ｃ Ａ Ｔ Ａ Ｌ Ｏ Ｇ Ｅ Ｒ　　　　　　　　
═══════════════════════════════════════════════════════════════════

　░▒▓█  ＴＡＧ　ＰＡＬＥＴＴＥ  █▓▒░

　geometric • formal • handwritten • fatface • monospaced • techno
　pixel • medieval • art nouveau • blobby • distressed • wood
　wacky • shaded • marker • futuristic • vintage • calm • playful
　sophisticated • business • stiff • childlike • horror • distorted
　clean • warm • aesthetic • brutalist • modular • neutral
　contemporary • rounded • approachable • humanist • coding
　retro • android

═══════════════════════════════════════════════════════════════════
　Ａｕｔｈｏｒ：　Duygu Dağdelen
　Ｄａｔｅ：　　December 2024
═══════════════════════════════════════════════════════════════════
"""

import subprocess, sys, logging, warnings, os

def install(package_name, module_name=None):
    if module_name is None: module_name = package_name
    try: __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for module, pip_name in [("cssutils", "cssutils"), ("torch", "torch"), ("open_clip", "open-clip-torch"),
                          ("PIL", "Pillow"), ("freetype", "freetype-py"), ("requests", "requests"), ("numpy", "numpy")]:
    install(pip_name, module)

warnings.filterwarnings("ignore")
logging.getLogger("PIL").setLevel(logging.CRITICAL)
import cssutils
cssutils.log.setLevel(logging.CRITICAL)

import re, json, base64, getpass, tempfile, requests, time, struct
import torch, open_clip, freetype
import numpy as np
from PIL import Image
from datetime import datetime

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMAGE_SIZE = 512
FONT_SIZE = 96
CLIP_MODEL = "ViT-B-32"
CLIP_PRETRAIN = "openai"
CATEGORIES = ["sans-serif", "serif", "monospace", "cursive", "fantasy"]

TAGS = [
    "geometric", "formal", "handwritten", "fatface", "monospaced", "techno",
    "pixel", "medieval", "art nouveau", "blobby", "distressed", "wood",
    "wacky", "shaded", "marker", "futuristic", "vintage", "calm", "playful",
    "sophisticated", "business", "stiff", "childlike", "horror", "distorted",
    "clean", "warm", "aesthetic", "brutalist", "modular", "neutral",
    "contemporary", "rounded", "approachable", "humanist", "coding",
    "retro", "android", "condensed", "expanded", "display", "elegant",
    "bold", "light", "decorative", "minimal", "organic", "sharp"
]

SAMPLES = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", 
           "The quick brown fox jumps", "0123456789"]

_MODEL_CACHE = None

def progress_bar(current, total, width=20):
    filled = int(width * current / total)
    bar = "▓" * filled + "░" * (width - filled)
    percent = int(100 * current / total)
    return f"[{bar}] {percent}%"

def get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        model, _, preprocess = open_clip.create_model_and_transforms(
            CLIP_MODEL, pretrained=CLIP_PRETRAIN, device=DEVICE
        )
        tokenizer = open_clip.get_tokenizer(CLIP_MODEL)
        model.eval()
        _MODEL_CACHE = (model, preprocess, tokenizer)
    return _MODEL_CACHE

def build_prompts():
    return {tag: [f"{tag} font", f"{tag} typeface"] for tag in TAGS}

def detect_font_source(url: str) -> str:
    url = url.lower()
    if "fonts.googleapis.com" in url or "fonts.gstatic.com" in url:
        return "google"
    elif "fonts.adobe.com" in url or "typekit.net" in url:
        return "adobe"
    elif url.endswith((".woff2", ".woff", ".ttf", ".otf")):
        return "custom"
    return "web"

def check_google_font_availability(font_name):
    """Check what weights are actually available for a Google Font"""
    try:
        # Query Google Fonts API list
        api_url = "https://fonts.googleapis.com/css2"
        
        # Try to fetch with full weight range to see what's available
        test_url = f"{api_url}?family={font_name.replace(' ', '+')}:wght@100;200;300;400;500;600;700;800;900"
        
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            css_content = response.text
            
            # Parse CSS to find available weights
            available_weights = set()
            
            # Look for font-weight declarations
            weight_matches = re.findall(r'font-weight:\s*(\d+)', css_content)
            available_weights.update(int(w) for w in weight_matches)
            
            # Look for font-style and variation axes
            has_italic = 'font-style: italic' in css_content or 'ital' in css_content
            is_variable = 'font-variation-settings' in css_content or '..' in test_url
            
            if available_weights:
                weights = sorted(list(available_weights))
                return weights, is_variable or len(weights) > 4, has_italic
        
        # Fallback: fetch minimal to see if font exists
        minimal_url = f"{api_url}?family={font_name.replace(' ', '+')}"
        response = requests.get(minimal_url, timeout=10)
        if response.status_code == 200:
            return [400], False, False
            
    except:
        pass
    
    return [400], False, False

def parse_google_fonts_url(url):
    """Extract weights and variable status from Google Fonts URL"""
    weights = []
    is_variable = False
    has_italic = False
    scripts = ["latin"]
    
    # Extract family name
    family_match = re.search(r'family=([^:&]+)', url)
    if family_match:
        family_name = family_match.group(1).replace('+', ' ')
        
        # Check if URL specifies weights
        weight_match = re.search(r':wght@([\d;.]+)', url)
        ital_match = re.search(r':ital,wght@', url) or re.search(r'ital', url)
        
        if ital_match:
            has_italic = True
        
        if weight_match:
            weight_str = weight_match.group(1)
            if '..' in weight_str:
                is_variable = True
                parts = weight_str.split('..')
                if len(parts) == 2:
                    weights = [int(parts[0]), int(parts[1])]
            else:
                weights = sorted([int(w) for w in weight_str.split(';') if w.isdigit()])
        
        # If URL doesn't specify weights, check what's actually available
        if not weights:
            print("      🌀  Checking available weights...")
            available_weights, available_variable, available_italic = check_google_font_availability(family_name)
            weights = available_weights
            is_variable = available_variable
            has_italic = has_italic or available_italic
    
    # Parse subsets for scripts
    if 'subset=' in url:
        subset_match = re.search(r'subset=([^&]+)', url)
        if subset_match:
            scripts = subset_match.group(1).split(',')
    
    if not weights:
        weights = [400]
    
    return weights, is_variable, has_italic, scripts

def parse_woff2_tables(data):
    """Parse WOFF2 file to extract font metadata"""
    try:
        # WOFF2 signature
        if data[:4] != b'wOF2':
            return None
        
        # Read header
        flavor = struct.unpack('>I', data[4:8])[0]
        length = struct.unpack('>I', data[8:12])[0]
        num_tables = struct.unpack('>H', data[12:14])[0]
        
        # For WOFF2, we need to decompress and parse tables
        # This is complex, so we'll use a simpler heuristic
        return None
    except:
        return None

def parse_ttf_tables(data):
    """Parse TTF/OTF file to extract font metadata"""
    try:
        # Check signature
        if data[:4] not in [b'\x00\x01\x00\x00', b'OTTO', b'true']:
            return None
        
        info = {
            'weights': [],
            'is_variable': False,
            'scripts': set(['latin'])
        }
        
        # Read table directory
        num_tables = struct.unpack('>H', data[4:6])[0]
        
        # Find OS/2 table for weight
        for i in range(num_tables):
            offset = 12 + i * 16
            tag = data[offset:offset+4]
            
            if tag == b'OS/2':
                table_offset = struct.unpack('>I', data[offset+8:offset+12])[0]
                # Weight class is at offset 4 in OS/2 table
                weight = struct.unpack('>H', data[table_offset+4:table_offset+6])[0]
                info['weights'] = [weight]
            
            elif tag == b'fvar':
                # Variation table = variable font
                info['is_variable'] = True
            
            elif tag == b'cmap':
                # Character map for script detection
                table_offset = struct.unpack('>I', data[offset+8:offset+12])[0]
                # Parse cmap to detect character ranges
                # This is simplified - full parsing is complex
        
        return info if info['weights'] else None
    except:
        return None

def analyze_font_file(font_path):
    """Deep analysis of font file for weights, variable status, and scripts"""
    try:
        with open(font_path, 'rb') as f:
            data = f.read()
        
        info = {
            'weights': [400],
            'is_variable': False,
            'has_italic': False,
            'scripts': ['latin']
        }
        
        # Try parsing as TTF/OTF
        parsed = parse_ttf_tables(data)
        if parsed:
            info.update(parsed)
        
        # Use freetype for additional checks
        face = freetype.Face(font_path)
        
        # Check if variable font
        try:
            if hasattr(face, 'is_variation') and face.is_variation:
                info['is_variable'] = True
        except:
            pass
        
        # Detect style from name
        family_name = face.family_name.decode('utf-8') if isinstance(face.family_name, bytes) else face.family_name
        style_name = face.style_name.decode('utf-8') if isinstance(face.style_name, bytes) else face.style_name
        
        if any(s in style_name.lower() for s in ['italic', 'oblique']):
            info['has_italic'] = True
        
        # Extract weight from style name
        weight_map = {
            'thin': 100, 'hairline': 100,
            'extralight': 200, 'ultralight': 200,
            'light': 300,
            'regular': 400, 'normal': 400, 'book': 400,
            'medium': 500,
            'semibold': 600, 'demibold': 600,
            'bold': 700,
            'extrabold': 800, 'ultrabold': 800,
            'black': 900, 'heavy': 900
        }
        
        style_lower = style_name.lower()
        for weight_name, weight_value in weight_map.items():
            if weight_name in style_lower:
                info['weights'] = [weight_value]
                break
        
        # Detect scripts by testing character ranges
        script_ranges = {
            'latin-ext': [(0x0100, 0x017F)],
            'cyrillic': [(0x0400, 0x04FF)],
            'greek': [(0x0370, 0x03FF)],
            'arabic': [(0x0600, 0x06FF)],
            'hebrew': [(0x0590, 0x05FF)],
            'vietnamese': [(0x1EA0, 0x1EFF)],
            'chinese': [(0x4E00, 0x9FFF)],
            'japanese': [(0x3040, 0x309F), (0x30A0, 0x30FF)],
            'korean': [(0xAC00, 0xD7AF)]
        }
        
        detected_scripts = set(['latin'])
        for script, ranges in script_ranges.items():
            for start, end in ranges:
                found = False
                # Test a few characters from each range
                for char_code in range(start, min(start + 10, end)):
                    try:
                        char_index = face.get_char_index(char_code)
                        if char_index != 0:
                            found = True
                            break
                    except:
                        pass
                if found:
                    detected_scripts.add(script)
                    break
        
        info['scripts'] = sorted(list(detected_scripts))
        
        return info
    except Exception as e:
        return {
            'weights': [400],
            'is_variable': False,
            'has_italic': False,
            'scripts': ['latin']
        }

def download_font_file(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    suffix = os.path.splitext(url.split("?")[0])[1] or ".woff2"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.close()
    return tmp.name

def download_web_font(css_url):
    r = requests.get(css_url, timeout=30)
    r.raise_for_status()
    
    # Parse CSS to get font URLs
    sheet = cssutils.parseString(r.text)
    font_urls = []
    font_weights = {}
    
    for rule in sheet:
        if rule.type == rule.FONT_FACE_RULE:
            src = rule.style.getPropertyValue("src")
            weight = rule.style.getPropertyValue("font-weight")
            
            matches = re.findall(r'url\((https?:[^)]+)\)', src)
            for url in matches:
                url = url.strip('\'"')
                font_urls.append(url)
                if weight:
                    font_weights[url] = int(weight) if weight.isdigit() else 400
    
    if not font_urls:
        raise RuntimeError("No font URLs found")
    
    # Prefer woff2, then woff, then ttf
    font_url = next((u for u in font_urls if "woff2" in u), 
                    next((u for u in font_urls if "woff" in u), font_urls[0]))
    
    # Return the font URL and collected weight info
    return download_font_file(font_url), list(set(font_weights.values())) if font_weights else None

def retrieve_font(url, source):
    if source in ["google", "adobe", "web"]:
        result = download_web_font(url)
        if isinstance(result, tuple):
            return result
        return result, None
    else:
        return download_font_file(url), None

def render_sample(face, text):
    img = Image.new("L", (IMAGE_SIZE, IMAGE_SIZE), 255)
    pixels = img.load()
    pen_x, pen_y = 40, IMAGE_SIZE // 2
    
    for char in text:
        try:
            face.load_char(char, freetype.FT_LOAD_RENDER)
        except:
            continue
        bitmap = face.glyph.bitmap
        top, left = face.glyph.bitmap_top, face.glyph.bitmap_left
        y, x = pen_y - top, pen_x + left
        
        for row in range(bitmap.rows):
            for col in range(bitmap.width):
                if bitmap.buffer[row * bitmap.width + col] > 128:
                    px, py = x + col, y + row
                    if 0 <= px < IMAGE_SIZE and 0 <= py < IMAGE_SIZE:
                        pixels[px, py] = 0
        pen_x += face.glyph.advance.x >> 6
        if pen_x > IMAGE_SIZE - 40:
            break
    return img.convert('RGB')

def render_font_images(font_path):
    face = freetype.Face(font_path)
    face.set_char_size(FONT_SIZE * 64)
    return [render_sample(face, s) for s in SAMPLES]

@torch.no_grad()
def tag_font(images):
    model, preprocess, tokenizer = get_model()
    image_tensors = torch.stack([preprocess(img) for img in images]).to(DEVICE)
    image_features = model.encode_image(image_tensors)
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    
    prompts = build_prompts()
    all_texts = []
    tag_indices = []
    for tag, texts in prompts.items():
        tag_indices.append((tag, len(all_texts), len(all_texts) + len(texts)))
        all_texts.extend(texts)
    
    tokens = tokenizer(all_texts).to(DEVICE)
    text_features = model.encode_text(tokens)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    results = {}
    for tag, start_idx, end_idx in tag_indices:
        tag_features = text_features[start_idx:end_idx]
        similarities = (image_features @ tag_features.T).cpu().numpy()
        results[tag] = float(similarities.max(axis=1).mean())
    
    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

def fetch_catalog(repo, token, file_path="catalog.fonts.json"):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    content = r.json()
    sha = content["sha"]
    data = base64.b64decode(content["content"]).decode("utf-8")
    return json.loads(data), sha

def update_catalog(repo, token, catalog, sha, file_path="catalog.fonts.json"):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    content_bytes = json.dumps(catalog, indent=2, ensure_ascii=False).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
    payload = {
        "message": f"Update font catalog ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
        "content": content_b64,
        "sha": sha
    }
    r = requests.put(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()

def process_font_entry(font_entry, step, total):
    name = font_entry["name"]
    url = font_entry["url"]
    category = font_entry.get("category", "sans-serif").lower()
    if category not in CATEGORIES:
        category = "sans-serif"
    
    print(f"\n{'─'*60}")
    print(f"📡 Processing {step}/{total}: {name}")
    
    try:
        stages = 5
        current = 0
        
        # Detect source
        source = detect_font_source(url)
        
        # Stage 1: Download
        current += 1
        print(f"   {progress_bar(current, stages)} Downloading...")
        path, css_weights = retrieve_font(url, source)
        
        # Stage 2: Parse metadata
        current += 1
        print(f"   {progress_bar(current, stages)} Extracting info...")
        
        if source == "google":
            weights, is_variable, has_italic, scripts = parse_google_fonts_url(url)
        else:
            # For custom/web fonts, analyze the file deeply
            font_info = analyze_font_file(path)
            weights = css_weights if css_weights else font_info['weights']
            is_variable = font_info['is_variable']
            has_italic = font_info['has_italic']
            scripts = font_info['scripts']
        
        # Stage 3: Render
        current += 1
        print(f"   {progress_bar(current, stages)} Rendering...")
        images = render_font_images(path)
        
        # Stage 4: Analyze
        current += 1
        print(f"   {progress_bar(current, stages)} Analyzing style...")
        scores = tag_font(images)
        
        # Stage 5: Complete
        current += 1
        print(f"   {progress_bar(current, stages)} Done!")
        
        # Clean up
        try:
            os.unlink(path)
        except:
            pass
        
        if not images:
            print("   ⊗ Failed to render")
            return None
        
        # Show detected info
        print(f"\n   ✓ Detected: {len(weights)} weight(s), {'Variable' if is_variable else 'Static'}, Scripts: {', '.join(scripts)}")
        
        # Filter top tags
        threshold = 0.20
        suggested_tags = [k for k, v in scores.items() if v >= threshold][:6]
        
        print("\n━━━ ＳＵＧＧＥＳＴＥＤ　ＴＡＧＳ ━━━")
        for idx, tag in enumerate(suggested_tags, 1):
            score = scores[tag]
            bar = "█" * int(score * 20)
            print(f"   {idx}. {tag:15s} {bar} {score:.3f}")
        
        print("\n　　　ＯＰＴＩＯＮＳ：")
        print("　　　 • [Enter] = Accept all")
        print("　　　 • [1,3,5] = Select by number")
        print("　　　 • [tag1,tag2] = Custom tags")
        print("　　　 • [skip] = Skip")
        
        user_input = input("\n🎛 Choice: ").strip()
        
        if user_input.lower() == "skip":
            print("⏭️  Skipped")
            return None
        elif user_input == "":
            final_tags = suggested_tags
        elif all(c.isdigit() or c in ", " for c in user_input):
            numbers = [int(n) - 1 for n in user_input.split(",") if n.strip().isdigit()]
            final_tags = [suggested_tags[i] for i in numbers if 0 <= i < len(suggested_tags)]
        else:
            final_tags = [t.strip() for t in user_input.split(",") if t.strip()]
        
        entry = {
            "name": name,
            "source": source,
            "url": url,
            "category": category,
            "tags": final_tags,
            "weights": weights,
            "variable": is_variable,
            "scripts": scripts
        }
        
        print("\n" + "═" * 60)
        print("░▒▓█  ＰＲＥＶＩＥＷ  █▓▒░")
        print("═" * 60)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        
        confirm = input("\n🔘 Add? (y/n): ").strip().lower()
        return entry if confirm == "y" else None
        
    except Exception as e:
        print(f"　　　🤷‍♀️ Oops, error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║　　　　　　　　Ｆ Ｏ Ｎ Ｔ 　Ｃ Ａ Ｔ Ａ Ｌ Ｏ Ｇ Ｅ Ｒ　　　　　　　　║
╚═══════════════════════════════════════════════════════════════════╝
""")
    print("\n　━━━ ＳＯＵＲＣＥ ＲＥＰＯ ━━━")
    print(f"  　     (username/repo)  ")
    repo = input("　　　＞ ").strip()
    print("\n　━━━ ＴＯＫＥＮ ━━━")
    token = getpass.getpass("　　　＞ ").strip()
    
    # Load model once
    print("\n📡 Loading AI model...")
    get_model()
    print("✓ Ready!\n")
    
    # Fetch existing catalog
    try:
        catalog, sha = fetch_catalog(repo, token)
        print(f"📡 Fetching current catalog with {len(catalog)} fonts\n")
    except Exception as e:
        print(f"⚠  Starting new catalog: {e}\n")
        catalog, sha = [], None
    
    fonts_to_process = []
    
    # Collect fonts to process
    while True:
        print(f"\n{'='*60}")
        print(f"░▒▓█  ＡＤＤＩＮＧ　ＦＯＮＴ　＃{len(fonts_to_process) + 1}  █▓▒░")
        print(f"{'='*60}")
        
        print("\n　━━━ ＦＯＮＴ ＮＡＭＥ ━━━")
        name = input("　　　＞ ").strip()
        if not name:
            if fonts_to_process:
                break
            continue
        
        print("\n　━━━ ＵＲＬ ━━━")
        url = input("　　　＞ ").strip()
        print("\n　━━━ ＣＡＴＥＧＯＲＹ ━━━")
        print(f"　　　({' • '.join(CATEGORIES)}）")
        category = input("　　　＞ ").strip().lower()
        if category not in CATEGORIES:
            category = "sans-serif"
        
        fonts_to_process.append({"name": name, "url": url, "category": category})
        
        more = input("\n➕ Add another? (y/n): ").strip().lower()
        if more != "y":
            break
    
    if not fonts_to_process:
        print("⊗ No fonts to process.")
        return
    
    # Process all fonts
    print(f"\n\n{'─'*60}")
    print(f"📡 Processing {len(fonts_to_process)} font(s)...")
    print(f"{'─'*60}")
    
    added_count = 0
    for i, font_entry in enumerate(fonts_to_process, 1):
        processed = process_font_entry(font_entry, i, len(fonts_to_process))
        
        if processed:
            # Update or add
            found = False
            for j, existing in enumerate(catalog):
                if existing["name"].lower() == processed["name"].lower():
                    catalog[j] = processed
                    found = True
                    break
            if not found:
                catalog.append(processed)
            added_count += 1
    
    # Commit all changes at once
    if added_count > 0 and sha:
        print(f"\n{'='*60}")
        print(f"🌀 Committing {added_count} font(s) to catalog...")
        try:
            update_catalog(repo, token, catalog, sha)
            print("🎉 Catalog updated successfully!")
        except Exception as e:
            print(f"⊗ Commit failed: {e}")
            print("\n🌀 Saving locally...")
            with open("catalog.fonts.json", "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            print("☑️ Saved to catalog.fonts.json")
    elif added_count > 0:
        print("\n🌀 Saving to local file...")
        with open("catalog.fonts.json", "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        print("☑️ Saved to catalog.fonts.json")
    else:
        print("\n⚠  No changes made")
    
    print("\n╰┈➤ 🎊 ＡＬＬ ＤＯＮＥ！")

if __name__ == "__main__":
    main()
