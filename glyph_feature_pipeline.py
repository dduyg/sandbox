"""
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
█  💠 𝐆𝐋𝐘𝐏𝐇 𝐅𝐄𝐀𝐓𝐔𝐑𝐄 𝐏𝐈𝐏𝐄𝐋𝐈𝐍𝐄 ⟫⟫⟫
█     [Automated extraction, analysis & storage of glyphs with detailed data features]
█ ─────────────────────────────────────────────────────────────────────────────
█ M.01 > K-MEANS.COLOR.CLUSTERING
█        Dominant/secondary palette extraction
█ M.02 > QUANTITATIVE.VISUAL.METRICS
█        Edge density | Entropy | Texture | Contrast | Shape analysis
█ M.03 > MOOD.CLASSIFICATION
█        Color harmony evaluation & aesthetic profiling
█ M.04 > LIBRARY.EXPANDED
█        Incremental updates stored in JSON and CSV for continuous library expansion
█ M.05 > AUTO.STORAGE
█        Direct commit to GH via API (images → glyphs/, data → data/)
█ ─────────────────────────────────────────────────────────────────────────────
█  >> SYS.AUTHOR: Duygu Dağdelen  [INIT 2025-12-14] 
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
"""

!pip install -q opencv-python-headless scikit-learn scikit-image PyGithub

import os, json, uuid, csv
from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass
from base64 import b64encode, b64decode
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO, StringIO

import numpy as np
import cv2
from PIL import Image
from sklearn.cluster import KMeans
from skimage.measure import shannon_entropy
from skimage.feature import local_binary_pattern
from skimage.color import rgb2gray
from github import Github as GH, Auth, GithubException as GhException, InputGitTreeElement
import colorsys

# ---------------------- COLOR DETECTION ----------------------

def rgb_to_hex(rgb):
    return "{:02x}{:02x}{:02x}".format(*rgb)

def rgb_to_lab(rgb):
    r, g, b = [x / 255 for x in rgb]
    r = ((r + 0.055)/1.055)**2.4 if r > 0.04045 else r/12.92
    g = ((g + 0.055)/1.055)**2.4 if g > 0.04045 else g/12.92
    b = ((b + 0.055)/1.055)**2.4 if b > 0.04045 else b/12.92
    x = r*0.4124 + g*0.3576 + b*0.1805
    y = r*0.2126 + g*0.7152 + b*0.0722
    z = r*0.0193 + g*0.1192 + b*0.9505
    x /= 0.95047
    z /= 1.08883
    f = lambda t: t**(1/3) if t > 0.008856 else 7.787*t + 16/116
    L = 116*f(y) - 16
    a = 500 * (f(x) - f(y))
    b = 200 * (f(y) - f(z))
    return (L, a, b)

def compute_hue(rgb):
    r, g, b = rgb
    return colorsys.rgb_to_hsv(r/255, g/255, b/255)[0] * 360

def compute_palette_contrast(rgb1, rgb2):
    """Compute perceptual distance between two colors in LAB space"""
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    delta = np.sqrt(
        (lab1[0] - lab2[0])**2 + 
        (lab1[1] - lab2[1])**2 + 
        (lab1[2] - lab2[2])**2
    )
    return round(float(delta / 100), 4)  # Normalize to 0-1 range

def masked_pixels(rgb, mask):
    pts = rgb[mask]
    if len(pts) == 0:
        return np.zeros((1, 3), dtype=np.uint8)
    return pts

def compute_dominant_color(rgb, mask, k=5):
    pts = masked_pixels(rgb, mask)
    if len(pts) < k:
        return (200, 200, 200)
    r, g, b = pts[:, 0]/255.0, pts[:, 1]/255.0, pts[:, 2]/255.0
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    sat = (max_c - min_c)/(max_c + 1e-6)
    weights = sat + 0.5
    kmeans = KMeans(n_clusters=k, n_init="auto").fit(pts, sample_weight=weights)
    centers = kmeans.cluster_centers_
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    return tuple(int(x) for x in centers[np.argmax(counts)])

def compute_secondary_color(rgb, mask, k=5):
    pts = masked_pixels(rgb, mask)
    if len(pts) < k:
        return (200, 200, 200)
    r, g, b = pts[:, 0]/255.0, pts[:, 1]/255.0, pts[:, 2]/255.0
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    sat = (max_c - min_c)/(max_c + 1e-6)
    weights = sat + 0.5
    kmeans = KMeans(n_clusters=k, n_init="auto").fit(pts, sample_weight=weights)
    centers = kmeans.cluster_centers_
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    if len(counts) == 1:
        return tuple(int(x) for x in centers[0])
    order = np.argsort(counts)[::-1]
    return tuple(int(x) for x in centers[order[1]])

def compute_color_group(rgb):
    r, g, b = rgb
    r_f, g_f, b_f = r/255, g/255, b/255
    h, s, v = colorsys.rgb_to_hsv(r_f, g_f, b_f)
    h *= 360
    brightness = 0.2126*r + 0.7152*g + 0.0722*b
    sat = s
    if brightness < 40: return "black"
    if brightness > 230 and sat < 0.20: return "white"
    if sat < 0.12 and 40 <= brightness <= 230: return "gray"
    if 35 < h < 65 and 120 < brightness < 220 and 0.20 < sat < 0.55: return "gold"
    if brightness > 180 and sat < 0.18: return "silver"
    if brightness < 140 and sat > 0.25 and 15 < h < 65: return "brown"
    if h <= 20 or h >= 345: return "red"
    if 20 < h <= 45: return "orange"
    if 45 < h <= 75: return "yellow"
    if 75 < h <= 165: return "green"
    if 165 < h <= 250: return "blue"
    if 250 < h <= 295: return "purple"
    if 295 < h <= 345: return "pink"
    return "gray"

def compute_color_harmony(c1, c2):
    h1 = compute_hue(c1)
    h2 = compute_hue(c2)
    d = abs(h1 - h2)
    if d < 30: return "analogous"
    if abs(d - 180) < 30: return "complementary"
    return "none"

# ---------------------- PROCESSING GLYPHS ----------------------

def compute_edge_density(rgb, mask):
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    return round(float(np.mean(edges[mask] > 0)), 4)

def compute_entropy(rgb, mask):
    gray = rgb2gray(rgb)
    return round(float(shannon_entropy(gray[mask])), 4)

def compute_texture_complexity(rgb, mask):
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    lbp = local_binary_pattern(gray, 8, 1, "uniform")
    vals = lbp[mask].ravel()
    hist, _ = np.histogram(vals, bins=np.arange(0, 11), density=True)
    ent = -np.sum(hist * np.log2(hist + 1e-10))
    return round(float(ent), 4)

def compute_contrast(image_rgba):
    arr = np.array(image_rgba)
    alpha = arr[..., 3]
    mask = alpha > 10
    if mask.sum() == 0: return 0.0
    rgb = arr[..., :3][mask]
    lum = 0.2126*rgb[:,0] + 0.7152*rgb[:,1] + 0.0722*rgb[:,2]
    I_max, I_min = lum.max(), lum.min()
    if I_max + I_min == 0: return 0.0
    return float(round((I_max - I_min)/(I_max + I_min),4))

def compute_shape_metrics(alpha):
    mask = (alpha > 10).astype("uint8")*255
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return 0.5, 1.0
    c = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(c)
    peri = cv2.arcLength(c, True)
    circularity = 4*np.pi*area/(peri*peri + 1e-6)
    x, y, w, h = cv2.boundingRect(c)
    aspect = w/(h + 1e-6)
    return round(float(circularity),4), round(float(aspect),4)

def compute_edge_angle(rgb, mask):
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    sx = cv2.Sobel(gray, cv2.CV_64F,1,0,3)
    sy = cv2.Sobel(gray, cv2.CV_64F,0,1,3)
    mag = np.sqrt(sx*sx + sy*sy)
    ang = np.degrees(np.arctan2(sy, sx))
    strong = mag[mask] > np.percentile(mag[mask],75)
    if strong.sum() == 0: return 0.0
    return round(float(abs(np.median(ang[mask][strong]))%180),4)

def compute_mood(dom_rgb, entropy, edge, tex, contrast, circ, aspect, angle, harmony):
    r, g, b = dom_rgb
    brightness = 0.2126*r + 0.7152*g + 0.0722*b
    h = compute_hue(dom_rgb)
    sat = (max(dom_rgb) - min(dom_rgb)) / (max(dom_rgb) + 1e-6)

    is_warm = (h <= 60) or (h >= 330)
    is_cool = (165 <= h <= 295)

    scores = {
        "serene": 0,
        "calm": 0,
        "playful": 0,
        "energetic": 0,
        "futuristic": 0,
        "mysterious": 0,
        "dramatic": 0,
        "chaotic": 0
    }

    if entropy < 2.2:
        scores["serene"] += (2.2 - entropy)/2.2
    elif entropy <= 2.8:
        scores["calm"] += (entropy - 2.2)/(2.8 - 2.2)
    elif entropy <= 3.8:
        scores["playful"] += (entropy - 2.8)/(3.8 - 2.8)
    elif entropy <= 5.3:
        scores["energetic"] += (entropy - 3.8)/(5.3 - 3.8)
    else:
        chaos_strength = min((entropy - 5.3)/2.5, 1) * 0.4
        scores["chaotic"] += chaos_strength

    if edge < 0.01:
        scores["serene"] += 0.3
    elif edge < 0.03:
        scores["calm"] += 0.15
    elif edge < 0.06:
        scores["playful"] += 0.3
    elif edge < 0.10:
        scores["energetic"] += 0.3
    else:
        scores["chaotic"] += 0.1

    if brightness > 180:
        scores["playful"] += 0.5
    if brightness < 80:
        scores["mysterious"] += 0.6
    if contrast > 0.5:
        scores["dramatic"] += (contrast - 0.5)/0.5 * 0.8
    if sat > 0.6:
        scores["energetic"] += 0.6
    if sat < 0.2:
        scores["calm"] += 0.2
    if harmony == "analogous":
        scores["calm"] += 0.2
    elif harmony == "complementary":
        scores["energetic"] += 0.3
    if circ > 0.8:
        scores["serene"] += 0.4
    if circ < 0.55:
        scores["playful"] += 0.4
    if 0.4 < aspect < 0.7 or 1.3 < aspect < 1.6:
        scores["futuristic"] += 0.6

    if is_warm and sat > 0.45:
        scores["energetic"] += 0.3
        scores["playful"] += 0.2
    if is_cool and brightness < 120:
        scores["mysterious"] += 0.3
        scores["calm"] += 0.1
    if 2.8 < entropy <= 3.8:
        scores["playful"] += 0.3
    if sat > 0.5 and brightness > 120:
        scores["energetic"] += 0.3

    return max(scores, key=scores.get)

def process_glyph_from_bytes(image_bytes, filename, gh_user, gh_repo, branch="main"):
    """Process a single glyph directly from bytes"""
    try:
        pil = Image.open(BytesIO(image_bytes)).convert("RGBA")
    except Exception as e:
        return None, f"SKIP.INVALID_IMAGE :: {filename}"
    
    arr = np.array(pil)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]
    mask = alpha > 10
    
    coords = np.column_stack(np.where(mask))
    if len(coords) > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        rgb_crop = rgb[y0:y1, x0:x1]
        alpha_crop = alpha[y0:y1, x0:x1]
        mask_crop = mask[y0:y1, x0:x1]
    else:
        rgb_crop, alpha_crop, mask_crop = rgb, alpha, mask

    dom = compute_dominant_color(rgb_crop, mask_crop)
    sec = compute_secondary_color(rgb_crop, mask_crop)
    dom_hex = rgb_to_hex(dom)
    sec_hex = rgb_to_hex(sec)
    dom_lab = rgb_to_lab(dom)
    sec_lab = rgb_to_lab(sec)
    dom_group = compute_color_group(dom)
    sec_group = compute_color_group(sec)
    palette_contrast = compute_palette_contrast(dom, sec)
    edge = compute_edge_density(rgb_crop, mask_crop)
    ent = compute_entropy(rgb_crop, mask_crop)
    tex = compute_texture_complexity(rgb_crop, mask_crop)
    con = compute_contrast(pil)
    circ, ar = compute_shape_metrics(alpha_crop)
    ang = compute_edge_angle(rgb_crop, mask_crop)
    harmony = compute_color_harmony(dom, sec)
    mood = compute_mood(dom, ent, edge, tex, con, circ, ar, ang, harmony)
    uid = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    newname = f"{dom_hex}_{sec_hex}_{uid}.png"
    
    # Save to bytes for streaming
    output_buffer = BytesIO()
    pil.save(output_buffer, format='PNG')
    output_bytes = output_buffer.getvalue()
    
    url = f"https://cdn.jsdelivr.net/gh/{gh_user}/{gh_repo}@{branch}/glyphs/{newname}"
    
    glyph_data = {
        "id": uid,
        "filename": newname,
        "glyph_url": url,
        "color": {
            "dominant": {
                "hex": dom_hex,
                "group": dom_group,
                "rgb": list(dom),
                "lab": [round(x, 2) for x in dom_lab]
            },
            "secondary": {
                "hex": sec_hex,
                "group": sec_group,
                "rgb": list(sec),
                "lab": [round(x, 2) for x in sec_lab]
            },
            "palette_contrast": palette_contrast
        },
        "metrics": {
            "edge_density": edge,
            "entropy": ent,
            "texture": tex,
            "contrast": con,
            "circularity": circ,
            "aspect_ratio": ar,
            "edge_angle": ang
        },
        "color_harmony": harmony,
        "mood": mood,
        "created_at": {
            "date": date_str,
            "time": time_str
        }
    }
    
    return (newname, output_bytes, glyph_data), None

# ---------------------- DATA PIPELINE ----------------------

def execute_glyph_pipeline(glyph_stream, gh_user, gh_repo, token, branch="main", max_workers=10, fetch_skipped=None, input_mode=None, original_input_count=None):
    """Process and stream to storage in one operation"""
    g = GH(auth=Auth.Token(token))
    user = g.get_user()
    
    repo_created = False
    try:
        repo = user.get_repo(gh_repo)
        print(f"\n  ◆ REPO.FOUND: {gh_repo}\n")
    except:
        print(f"\n   ⟨⚠⟩  REPO.NOT_FOUND → creating '{gh_repo}'...")
        repo = user.create_repo(gh_repo)
        repo.create_file("glyphs/.gitkeep", "init", "")
        repo.create_file("data/.gitkeep", "init", "")
        print("  ▲  BASE.FOLDERS_INIT ('glyphs/' and 'data/')\n")
        repo_created = True
    
    # Get existing catalog
    existing_glyphs = []
    if not repo_created:  # Only check for existing catalog if repo already existed
        try:
            file_content = repo.get_contents("data/glyphs.catalog.json", ref=branch)
            existing = json.loads(file_content.decoded_content.decode())
            existing_glyphs = existing.get("glyphs", [])
        except:
            pass
    
    print(f"\n⟨██⟩ Processing {len(glyph_stream)} glyphs...\n")
    
    # Process all files
    all_data = []
    elements = []
    skipped = fetch_skipped if fetch_skipped else []
    total_input = original_input_count if original_input_count is not None else len(glyph_stream)
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_glyph_from_bytes, data, fname, gh_user, gh_repo, branch): fname 
                for fname, data in glyph_stream.items() if fname.lower().endswith('.png')
            }
            
            for future in as_completed(futures):
                result, skip_msg = future.result()
                if skip_msg:
                    skipped.append(skip_msg)
                    continue
                    
                newname, image_bytes, glyph_data = result
                all_data.append(glyph_data)
                
                # Create blob directly
                blob_b64 = b64encode(image_bytes).decode("utf-8")
                blob = repo.create_git_blob(blob_b64, "base64")
                
                elements.append(InputGitTreeElement(
                    path=f"glyphs/{newname}",
                    mode='100644',
                    type="blob",
                    sha=blob.sha
                ))
        
        if not all_data:
            print("\n  [✖] FATAL :: No valid glyphs to process")
            return
        
        # Create catalog files
        all_glyphs = existing_glyphs + all_data
        catalog = {"total": len(all_glyphs), "glyphs": all_glyphs}
        
        # Add JSON
        elements.append(InputGitTreeElement(
            path="data/glyphs.catalog.json",
            mode='100644',
            type="blob",
            content=json.dumps(catalog, indent=2)
        ))
        
        # Add CSV
        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerow([
            "id", "filename", "glyph_url",
            "dominant_hex", "dominant_group", "dominant_rgb", "dominant_lab",
            "secondary_hex", "secondary_group", "secondary_rgb", "secondary_lab",
            "palette_contrast",
            "edge_density", "entropy", "texture", "contrast", "circularity", "aspect_ratio",
            "edge_angle", "color_harmony", "mood", "created_date", "created_time"
        ])
        for g in all_glyphs:
            csv_writer.writerow([
                g["id"], g["filename"], g["glyph_url"],
                g["color"]["dominant"]["hex"], g["color"]["dominant"]["group"],
                str(g["color"]["dominant"]["rgb"]), str(g["color"]["dominant"]["lab"]),
                g["color"]["secondary"]["hex"], g["color"]["secondary"]["group"],
                str(g["color"]["secondary"]["rgb"]), str(g["color"]["secondary"]["lab"]),
                g["color"]["palette_contrast"],
                g["metrics"]["edge_density"], g["metrics"]["entropy"], g["metrics"]["texture"],
                g["metrics"]["contrast"], g["metrics"]["circularity"], g["metrics"]["aspect_ratio"],
                g["metrics"]["edge_angle"], g["color_harmony"], g["mood"],
                g["created_at"]["date"], g["created_at"]["time"]
            ])
        
        elements.append(InputGitTreeElement(
            path="data/glyphs.catalog.csv",
            mode='100644',
            type="blob",
            content=csv_output.getvalue()
        ))
        
        # Determine commit type and message
        if existing_glyphs:
            commit_type = "LIBRARY.EXPANDED"
            commit_msg = f"[LIBRARY.EXPANDED]   +{len(all_data)} glyphs, 2 catalogs updated"
            catalog_status = "2 catalogs updated [CSV + JSON]"
            library_info = f"{len(existing_glyphs)} + {len(all_data)} = {len(all_glyphs)} glyphs in total"
        else:
            commit_type = "LIBRARY.INIT"
            commit_msg = f"[LIBRARY.INIT]   {len(all_data)} glyphs + 2 catalogs generated"
            catalog_status = "2 catalogs generated [CSV + JSON]"
            library_info = f"{len(all_data)} glyphs"
        
        # Commit everything
        sb = repo.get_branch(branch)
        base_tree = repo.get_git_tree(sb.commit.sha)
        tree = repo.create_git_tree(elements, base_tree)
        parent = repo.get_git_commit(sb.commit.sha)
        commit = repo.create_git_commit(commit_msg, tree, [parent])
        ref = repo.get_git_ref(f"heads/{branch}")
        ref.edit(commit.sha)
        
        # Determine input mode display
        input_mode_display = "SELECT.FROM.LOCAL.COMPUTER" if input_mode == "1" else "FETCH.FROM.REPOSITORY"
        
        # Final summary output
        print(f"\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
        print(f"██  ")
        print(f"██  ⟫⟫⟫ [COMPLETE] STREAM.SUCCESSFUL")
        print(f"██  ")
        print(f"██      ├── total.input: {total_input}")
        print(f"██      ├── status.success: {len(all_data)}")
        print(f"██      ├── status.skipped: {len(skipped)}")
        print(f"██      ├── commit.type: {commit_type}")
        print(f"██      │   ├── {library_info}")
        print(f"██      │   └── {catalog_status}")
        print(f"██      ├── input.mode: {input_mode_display}")
        print(f"██      └── storage.location: {gh_user}/{gh_repo}")
        print(f"██        └── [⫘] https://github.com/{gh_user}/{gh_repo}")
        print(f"██  ")
        
        if skipped:
            print(f"▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
            print(f"██  ")
            print(f"██      [◢◣]⎯⎯⎯⎯ SKIPPED {len(skipped)} FILE(S):")
            print(f"██  ")
            for msg in skipped:
                print(f"██                >>   {msg}")

        print(f"██  ")
        print(f"▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
            
    except GhException as e:
        print(f"\n  ⟨XX⟩ 🤷Oops, ERROR.GITHUB_API: {e.status} - {e.data.get('message', 'Unknown error')}")
        print(" >> Operation failed, retry again")
    except Exception as e:
        print(f"\n  ⟨XX⟩ 🤷Oops, UNEXPECTED_ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(" >> Operation failed, retry again")

def fetch_from_source(source_user, source_repo, source_path, token, branch="main"):
    """Fetch files from a source repository folder or root"""
    g = GH(auth=Auth.Token(token))
    
    try:
        repo = g.get_user(source_user).get_repo(source_repo)
        
        # Handle empty path (root directory)
        if source_path == "":
            contents = repo.get_contents("", ref=branch)
            location_display = f"{source_user}/{source_repo} (root)"
        else:
            contents = repo.get_contents(source_path, ref=branch)
            location_display = f"{source_user}/{source_repo}/{source_path}"
        
        if not isinstance(contents, list):
            contents = [contents]
        
        files_dict = {}
        skipped = []
        png_files = [item for item in contents if item.name.lower().endswith('.png') and item.type == "file"]
        
        # Store original count before any processing
        original_count = len(png_files)
        
        print(f"\n◢◤ [FETCHING.DATA] {original_count} files FROM {location_display}...\n")
        
        for item in png_files:
            try:
                file_content = repo.get_contents(item.path, ref=branch)
                image_bytes = b64decode(file_content.content)
                try:
                    Image.open(BytesIO(image_bytes))
                    files_dict[item.name] = image_bytes
                except:
                    skipped.append(f"SKIP.INVALID_IMAGE :: {item.name}")
            except Exception as e:
                skipped.append(f"SKIP.FETCH_ERROR :: {item.name}")
        
        return files_dict, skipped, original_count
        
    except Exception as e:
        print(f"  ⊗ ERR :: FETCH_FAILED: {e}")
        return {}, [], 0

def parse_repo_input(repo_input):
    """Parse username/repo format"""
    parts = repo_input.strip().split('/')
    if len(parts) != 2:
        raise ValueError("Format must be: username/repo-name")
    return parts[0].strip(), parts[1].strip()

print("\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
print("     ├─ ⌬ 𝐆𝐋𝐘𝐏𝐇 𝐅𝐄𝐀𝐓𝐔𝐑𝐄 𝐏𝐈𝐏𝐄𝐋𝐈𝐍𝐄    ⟩⟩⟩      SYS.ACTIVE")
print("     └──── [extract] → [analyze] → [classify] → [commit]")
print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n")

# Choose input method
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  ▓▓▓ INPUT.SOURCE.CONFIG ⟫⟫⟫")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("▓▓▓▓▓▓▓▓▓ [1] →  SELECT.FROM.LOCAL.COMPUTER")
print("▓▓▓▓▓▓▓▓▓ [2] →  FETCH.FROM.REPOSITORY")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
input_method = input("  [>] Select mode [1 or 2] >> ").strip()
print(f"   \n")

# Handle based on input method
if input_method == "1":
    # Mode 1: Local files - pick files first
    print("\n>>   SELECT.LOCAL images to start processing   ▓")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        from google.colab import files
        streamed = files.upload()
    except:
        input_dir = Path("./input_glyphs")
        streamed = {f.name: f.read_bytes() for f in input_dir.glob("*.png")}
    
    if not streamed:
        print("  [✖] FATAL :: No glyphs detected to process")
        exit(1)
    
    # Store original count for mode 1
    original_input_count = len(streamed)
    
    # Then get storage config and token
    print("\n  ▓▓▓ STORAGE.CONFIG ⟫⟫⟫")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("━━━STORAGE_REPO  (username/repo-name)━━━")
    storage_input = input("　　　＞ ").strip()
    try:
        gh_user, gh_repo = parse_repo_input(storage_input)
    except ValueError as e:
        print(f"  ⊗ [ERR] {e}")
        exit(1)

    print("━━━STORAGE_BRANCH  [default=main]━━━")
    branch = input("　　　＞ ").strip() or "main"
    print("\n━━━ACCESS_TOKEN  [✦]")
    token = getpass("　　　＞ ").strip()
    
    # No fetch skips for local mode
    fetch_skipped = None

else:
    # Mode 2: Repository - get source config first
    print("\n>>   FETCH.FROM.SOURCE.REPOSITORY to start processing   ▓")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print("━━━SOURCE_REPO  (username/repo-name)━━━")
    source_input = input("　　　＞ ").strip()
    try:
        source_user, source_repo = parse_repo_input(source_input)
    except ValueError as e:
        print(f"  ⊗ [ERR] {e}")
        exit(1)

    print("━━━SOURCE_BRANCH  [default=main]━━━")
    source_branch = input("　　　＞ ").strip() or "main"
    print("━━━SOURCE_FOLDER  (e.g., 'raw_glyphs' or press ENTER for repo root)━━━")
    source_path = input("　　　＞ ").strip() or ""
    
    # Then get storage config
    print("\n  ▓▓▓ STORAGE.CONFIG ⟫⟫⟫")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("━━━STORAGE_REPO  (username/repo-name)━━━")
    storage_input = input("　　　＞ ").strip()
    try:
        gh_user, gh_repo = parse_repo_input(storage_input)
    except ValueError as e:
        print(f"  ⊗ [ERR] {e}")
        exit(1)

    print("━━━STORAGE_BRANCH  [default=main]━━━")
    branch = input("　　　＞ ").strip() or "main"
    
    # Ask for token once (used for both source fetch and storage push)
    print("\n━━━ACCESS_TOKEN  [✦]")
    token = getpass("　　　＞ ").strip()
    
    # Now fetch files from repository using the token
    streamed, fetch_skipped, original_input_count = fetch_from_source(source_user, source_repo, source_path, token, source_branch)
    
    if not streamed:
        print("  [✖] FATAL :: No valid glyphs detected to process")
        exit(1)

# Process the files
execute_glyph_pipeline(streamed, gh_user, gh_repo, token, branch, max_workers=10, fetch_skipped=fetch_skipped, input_mode=input_method, original_input_count=original_input_count)
