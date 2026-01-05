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

import subprocess
import sys
import logging
import warnings
import os
import re
import json
import base64
import getpass
import tempfile
import struct
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
# DEPENDENCY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

class DependencyManager:
    """Handles installation of required packages"""
    
    DEPENDENCIES = {
        "cssutils": "cssutils",
        "torch": "torch",
        "open_clip": "open-clip-torch",
        "PIL": "Pillow",
        "freetype": "freetype-py",
        "requests": "requests",
        "numpy": "numpy"
    }
    
    @staticmethod
    def install(package_name: str, module_name: Optional[str] = None):
        if module_name is None:
            module_name = package_name
        try:
            __import__(module_name)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name, "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    
    @classmethod
    def install_all(cls):
        for module, pip_name in cls.DEPENDENCIES.items():
            cls.install(pip_name, module)

# Install dependencies
DependencyManager.install_all()

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("PIL").setLevel(logging.CRITICAL)
import cssutils
cssutils.log.setLevel(logging.CRITICAL)

# Import after installation
import requests
import torch
import open_clip
import freetype
import numpy as np
from PIL import Image

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Config:
    """Application configuration"""
    
    # Device settings
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Image rendering
    IMAGE_SIZE: int = 512
    FONT_SIZE: int = 96
    
    # CLIP model
    CLIP_MODEL: str = "ViT-B-32"
    CLIP_PRETRAIN: str = "openai"
    
    # Font categories
    CATEGORIES: List[str] = None
    
    # Available tags
    TAGS: List[str] = None
    
    # Sample texts for rendering
    SAMPLES: List[str] = None
    
    # Tag threshold
    TAG_THRESHOLD: float = 0.20
    
    # Script detection tests
    SCRIPT_TESTS: Dict[str, List[int]] = None
    
    def __post_init__(self):
        self.CATEGORIES = ["sans-serif", "serif", "monospace", "cursive", "fantasy"]
        
        self.TAGS = [
            "geometric", "formal", "handwritten", "fatface", "monospaced", "techno",
            "pixel", "medieval", "art nouveau", "blobby", "distressed", "wood",
            "wacky", "shaded", "marker", "futuristic", "vintage", "calm", "playful",
            "sophisticated", "business", "stiff", "childlike", "horror", "distorted",
            "clean", "warm", "aesthetic", "brutalist", "modular", "neutral",
            "contemporary", "rounded", "approachable", "humanist", "coding",
            "retro", "android", "condensed", "expanded", "display", "elegant",
            "bold", "light", "decorative", "minimal", "organic", "sharp"
        ]
        
        self.SAMPLES = [
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "abcdefghijklmnopqrstuvwxyz",
            "The quick brown fox jumps",
            "0123456789"
        ]
        
        self.SCRIPT_TESTS = {
            'latin-ext': [0x011E, 0x011F, 0x0130, 0x0131, 0x015E, 0x015F,
                          0x0104, 0x0105, 0x0141, 0x0142, 0x010C, 0x010D,
                          0x0158, 0x0159, 0x0152, 0x0153, 0x0100, 0x0101],
            'vietnamese': [0x1EA0, 0x1EA1, 0x1EB0, 0x1EB1, 0x1EE4, 0x1EE5,
                           0x01A0, 0x01A1, 0x01AF, 0x01B0],
            'cyrillic': [0x0410, 0x0411, 0x0412, 0x0430, 0x0431, 0x0432,
                         0x0401, 0x0451],
            'greek': [0x0391, 0x0392, 0x0393, 0x03B1, 0x03B2, 0x03B3,
                      0x03A9, 0x03C9],
            'arabic': [0x0628, 0x062A, 0x062B, 0x0639, 0x063A, 0x0644, 0x0647],
            'hebrew': [0x05D0, 0x05D1, 0x05D2, 0x05E9, 0x05EA],
            'chinese': [0x4E00, 0x4E8C, 0x4E09, 0x6C49, 0x5B57],
            'japanese': [0x3042, 0x3044, 0x3046, 0x30A2, 0x30A4, 0x30A6],
            'korean': [0xAC00, 0xAC01, 0xAC04, 0xD55C, 0xAE00]
        }

# ═══════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FontMetadata:
    """Font metadata information"""
    weights: List[int]
    is_variable: bool
    has_italic: bool
    scripts: List[str]
    is_monospace: bool = False

@dataclass
class FontEntry:
    """Complete font catalog entry"""
    name: str
    source: str
    url: str
    category: str
    tags: List[str]
    weights: List[int]
    variable: bool
    scripts: List[str]
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source": self.source,
            "url": self.url,
            "category": self.category,
            "tags": self.tags,
            "weights": self.weights,
            "variable": self.variable,
            "scripts": self.scripts
        }

# ═══════════════════════════════════════════════════════════════════
# FONT SOURCE DETECTION
# ═══════════════════════════════════════════════════════════════════

class FontSourceDetector:
    """Detects font source type from URL"""
    
    @staticmethod
    def detect(url: str) -> str:
        url_lower = url.lower()
        
        if "fonts.googleapis.com" in url_lower or "fonts.gstatic.com" in url_lower:
            return "google"
        elif "fonts.adobe.com" in url_lower or "typekit.net" in url_lower:
            return "adobe"
        elif url.endswith((".woff2", ".woff", ".ttf", ".otf")):
            return "custom"
        
        return "web"

# ═══════════════════════════════════════════════════════════════════
# FONT DOWNLOAD
# ═══════════════════════════════════════════════════════════════════

class FontDownloader:
    """Handles font file downloads"""
    
    @staticmethod
    def download_file(url: str) -> str:
        """Download font file and return temp path"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        suffix = os.path.splitext(url.split("?")[0])[1] or ".woff2"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(response.content)
        tmp.close()
        
        return tmp.name
    
    @staticmethod
    def download_from_css(css_url: str) -> Tuple[str, Optional[List[int]]]:
        """Download font from CSS URL and extract weights"""
        response = requests.get(css_url, timeout=30)
        response.raise_for_status()
        
        sheet = cssutils.parseString(response.text)
        font_urls = []
        font_weights = {}
        
        for rule in sheet:
            if rule.type == rule.FONT_FACE_RULE:
                src = rule.style.getPropertyValue("src")
                weight = rule.style.getPropertyValue("font-weight")
                
                matches = re.findall(r'url\((https?:[^)]+)\)', src)
                for font_url in matches:
                    font_url = font_url.strip('\'"')
                    font_urls.append(font_url)
                    if weight:
                        font_weights[font_url] = int(weight) if weight.isdigit() else 400
        
        if not font_urls:
            raise RuntimeError("No font URLs found in CSS")
        
        # Prefer woff2, then woff, then ttf
        font_url = next((u for u in font_urls if "woff2" in u),
                        next((u for u in font_urls if "woff" in u), font_urls[0]))
        
        weights = list(set(font_weights.values())) if font_weights else None
        return FontDownloader.download_file(font_url), weights
    
    @staticmethod
    def retrieve(url: str, source: str) -> Tuple[str, Optional[List[int]]]:
        """Main retrieval method"""
        if source in ["google", "adobe", "web"]:
            result = FontDownloader.download_from_css(url)
            if isinstance(result, tuple):
                return result
            return result, None
        else:
            return FontDownloader.download_file(url), None

# ═══════════════════════════════════════════════════════════════════
# GOOGLE FONTS ANALYZER
# ═══════════════════════════════════════════════════════════════════

class GoogleFontsAnalyzer:
    """Analyzes Google Fonts URLs and checks availability"""
    
    @staticmethod
    def check_availability(font_name: str) -> Tuple[List[int], bool, bool]:
        """Check available weights for a Google Font"""
        try:
            api_url = "https://fonts.googleapis.com/css2"
            test_url = f"{api_url}?family={font_name.replace(' ', '+')}:wght@100;200;300;400;500;600;700;800;900"
            
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                css_content = response.text
                available_weights = set()
                
                weight_matches = re.findall(r'font-weight:\s*(\d+)', css_content)
                available_weights.update(int(w) for w in weight_matches)
                
                has_italic = 'font-style: italic' in css_content or 'ital' in css_content
                is_variable = 'font-variation-settings' in css_content
                
                if available_weights:
                    return sorted(list(available_weights)), is_variable or len(available_weights) > 4, has_italic
            
            # Fallback
            minimal_url = f"{api_url}?family={font_name.replace(' ', '+')}"
            response = requests.get(minimal_url, timeout=10)
            if response.status_code == 200:
                return [400], False, False
        except:
            pass
        
        return [400], False, False
    
    @staticmethod
    def parse_url(url: str) -> Tuple[List[int], bool, bool, List[str]]:
        """Parse Google Fonts URL for metadata"""
        weights = []
        is_variable = False
        has_italic = False
        scripts = ["latin"]
        
        family_match = re.search(r'family=([^:&]+)', url)
        if family_match:
            family_name = family_match.group(1).replace('+', ' ')
            
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
            
            if not weights:
                print("      🌀  Checking available weights...")
                available_weights, available_variable, available_italic = GoogleFontsAnalyzer.check_availability(family_name)
                weights = available_weights
                is_variable = available_variable
                has_italic = has_italic or available_italic
        
        if 'subset=' in url:
            subset_match = re.search(r'subset=([^&]+)', url)
            if subset_match:
                scripts = subset_match.group(1).split(',')
        
        if not weights:
            weights = [400]
        
        return weights, is_variable, has_italic, scripts

# ═══════════════════════════════════════════════════════════════════
# FONT FILE ANALYZER
# ═══════════════════════════════════════════════════════════════════

class FontFileAnalyzer:
    """Deep analysis of font files"""
    
    WEIGHT_MAP = {
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
    
    def __init__(self, config: Config):
        self.config = config
    
    def analyze(self, font_path: str) -> FontMetadata:
        """Perform deep analysis of font file"""
        try:
            face = freetype.Face(font_path)
            
            # Basic info
            is_monospace = face.is_fixed_width
            is_variable = self._check_variable(face)
            
            # Style analysis
            style_name = self._get_style_name(face)
            has_italic = any(s in style_name.lower() for s in ['italic', 'oblique'])
            
            # Weight detection
            weights = self._detect_weight(style_name)
            
            # Script detection
            scripts = self._detect_scripts(face)
            
            return FontMetadata(
                weights=weights,
                is_variable=is_variable,
                has_italic=has_italic,
                scripts=scripts,
                is_monospace=is_monospace
            )
        except Exception as e:
            return FontMetadata(
                weights=[400],
                is_variable=False,
                has_italic=False,
                scripts=['latin'],
                is_monospace=False
            )
    
    @staticmethod
    def _check_variable(face) -> bool:
        try:
            return hasattr(face, 'is_variation') and face.is_variation
        except:
            return False
    
    @staticmethod
    def _get_style_name(face) -> str:
        style = face.style_name
        if isinstance(style, bytes):
            style = style.decode('utf-8')
        return style
    
    def _detect_weight(self, style_name: str) -> List[int]:
        style_lower = style_name.lower()
        for weight_name, weight_value in self.WEIGHT_MAP.items():
            if weight_name in style_lower:
                return [weight_value]
        return [400]
    
    def _detect_scripts(self, face) -> List[str]:
        detected = set(['latin'])
        
        for script, test_chars in self.config.SCRIPT_TESTS.items():
            found_count = 0
            for char_code in test_chars:
                try:
                    char_index = face.get_char_index(char_code)
                    if char_index != 0:
                        found_count += 1
                        if found_count >= 2:
                            detected.add(script)
                            break
                except:
                    pass
        
        return sorted(list(detected))

# ═══════════════════════════════════════════════════════════════════
# FONT RENDERER
# ═══════════════════════════════════════════════════════════════════

class FontRenderer:
    """Renders font samples as images"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def render(self, font_path: str) -> List[Image.Image]:
        """Render all sample texts"""
        face = freetype.Face(font_path)
        face.set_char_size(self.config.FONT_SIZE * 64)
        
        return [self._render_sample(face, sample) for sample in self.config.SAMPLES]
    
    def _render_sample(self, face, text: str) -> Image.Image:
        """Render single text sample"""
        img = Image.new("L", (self.config.IMAGE_SIZE, self.config.IMAGE_SIZE), 255)
        pixels = img.load()
        pen_x, pen_y = 40, self.config.IMAGE_SIZE // 2
        
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
                        if 0 <= px < self.config.IMAGE_SIZE and 0 <= py < self.config.IMAGE_SIZE:
                            pixels[px, py] = 0
            
            pen_x += face.glyph.advance.x >> 6
            if pen_x > self.config.IMAGE_SIZE - 40:
                break
        
        return img.convert('RGB')

# ═══════════════════════════════════════════════════════════════════
# CLIP TAGGER
# ═══════════════════════════════════════════════════════════════════

class CLIPTagger:
    """AI-powered font tagging using CLIP"""
    
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.preprocess = None
        self.tokenizer = None
    
    def load_model(self):
        """Load CLIP model (cached)"""
        if self.model is None:
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                self.config.CLIP_MODEL,
                pretrained=self.config.CLIP_PRETRAIN,
                device=self.config.DEVICE
            )
            self.tokenizer = open_clip.get_tokenizer(self.config.CLIP_MODEL)
            self.model.eval()
    
    def tag(self, images: List[Image.Image], category: str, metadata: FontMetadata) -> Dict[str, float]:
        """Generate tags for font"""
        self.load_model()
        
        # Encode images
        image_tensors = torch.stack([self.preprocess(img) for img in images]).to(self.config.DEVICE)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensors)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Encode text prompts
        prompts = self._build_prompts()
        all_texts = []
        tag_indices = []
        
        for tag, texts in prompts.items():
            tag_indices.append((tag, len(all_texts), len(all_texts) + len(texts)))
            all_texts.extend(texts)
        
        tokens = self.tokenizer(all_texts).to(self.config.DEVICE)
        
        with torch.no_grad():
            text_features = self.model.encode_text(tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        # Calculate similarities
        results = {}
        for tag, start_idx, end_idx in tag_indices:
            tag_features = text_features[start_idx:end_idx]
            similarities = (image_features @ tag_features.T).cpu().numpy()
            results[tag] = float(similarities.max(axis=1).mean())
        
        # Apply rule-based boosts
        results = self._apply_boosts(results, category, metadata)
        
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
    
    def _build_prompts(self) -> Dict[str, List[str]]:
        return {tag: [f"{tag} font", f"{tag} typeface"] for tag in self.config.TAGS}
    
    @staticmethod
    def _apply_boosts(results: Dict[str, float], category: str, metadata: FontMetadata) -> Dict[str, float]:
        """Apply rule-based boosts to CLIP scores"""
        # Monospace fonts
        if category == "monospace" or metadata.is_monospace:
            results["monospaced"] = max(results.get("monospaced", 0), 0.30)
            results["coding"] = max(results.get("coding", 0), 0.28)
            results["techno"] = max(results.get("techno", 0), 0.26)
        
        # Weight-based boosts
        if any(w >= 700 for w in metadata.weights):
            results["bold"] = max(results.get("bold", 0), 0.22)
        if any(w <= 300 for w in metadata.weights):
            results["light"] = max(results.get("light", 0), 0.22)
        
        return results

# ═══════════════════════════════════════════════════════════════════
# GITHUB CATALOG MANAGER
# ═══════════════════════════════════════════════════════════════════

class GitHubCatalogManager:
    """Manages font catalog on GitHub"""
    
    def __init__(self, repo: str, token: str, file_path: str = "catalog.fonts.json"):
        self.repo = repo
        self.token = token
        self.file_path = file_path
        self.headers = {"Authorization": f"token {token}"}
    
    def fetch(self) -> Tuple[List[dict], str]:
        """Fetch current catalog"""
        url = f"https://api.github.com/repos/{self.repo}/contents/{self.file_path}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        content = response.json()
        sha = content["sha"]
        data = base64.b64decode(content["content"]).decode("utf-8")
        
        return json.loads(data), sha
    
    def update(self, catalog: List[dict], sha: str):
        """Update catalog on GitHub"""
        url = f"https://api.github.com/repos/{self.repo}/contents/{self.file_path}"
        content_bytes = json.dumps(catalog, indent=2, ensure_ascii=False).encode("utf-8")
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")
        
        payload = {
            "message": f"Update font catalog ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "content": content_b64,
            "sha": sha
        }
        
        response = requests.put(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
    
    @staticmethod
    def save_local(catalog: List[dict], file_path: str = "catalog.fonts.json"):
        """Save catalog locally"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

# ═══════════════════════════════════════════════════════════════════
# MAIN FONT CATALOG MANAGER
# ═══════════════════════════════════════════════════════════════════

class FontCatalogManager:
    """Main application class for font cataloging"""
    
    def __init__(self):
        self.config = Config()
        self.analyzer = FontFileAnalyzer(self.config)
        self.renderer = FontRenderer(self.config)
        self.tagger = CLIPTagger(self.config)
        self.github = None
    
    def initialize(self, repo: str, token: str):
        """Initialize GitHub connection"""
        self.github = GitHubCatalogManager(repo, token)
        print("\n📡 Loading AI model...")
        self.tagger.load_model()
        print("✓ Ready!\n")
    
    def process_font(self, name: str, url: str, category: str, step: int, total: int) -> Optional[FontEntry]:
        """Process a single font"""
        print(f"\n📡 Processing {step}/{total}: {name}")
        
        try:
            # Detect source and download
            source = FontSourceDetector.detect(url)
            font_path, css_weights = FontDownloader.retrieve(url, source)
            
            # Analyze metadata
            if source == "google":
                weights, is_variable, has_italic, scripts = GoogleFontsAnalyzer.parse_url(url)
                # Check monospace for Google fonts
                try:
                    face = freetype.Face(font_path)
                    is_monospace = face.is_fixed_width
                except:
                    is_monospace = False
                
                metadata = FontMetadata(weights, is_variable, has_italic, scripts, is_monospace)
            else:
                metadata = self.analyzer.analyze(font_path)
                if css_weights:
                    metadata.weights = css_weights
            
            # Render and tag
            images = self.renderer.render(font_path)
            scores = self.tagger.tag(images, category, metadata)
            
            # Cleanup
            try:
                os.unlink(font_path)
            except:
                pass
            
            if not images:
                print("   ⊗ Failed to render")
                return None
            
            # Display results
            print(f"   ✓ Detected: {len(metadata.weights)} weight(s), {'Variable' if metadata.is_variable else 'Static'}, Scripts: {', '.join(metadata.scripts)}")
            
            suggested_tags = [k for k, v in scores.items() if v >= self.config.TAG_THRESHOLD][:6]
            
            print("\n━━━ ＳＵＧＧＥＳＴＥＤ　ＴＡＧＳ ━━━")
            for idx, tag in enumerate(suggested_tags, 1):
                score = scores[tag]
                bar = "█" * int(score * 20)
                print(f"   {idx}. {tag:15s} {bar} {score:.3f}")
            
            # User selection
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
            
            # Create entry
            entry = FontEntry(
                name=name,
                source=source,
                url=url,
                category=category,
                tags=final_tags,
                weights=metadata.weights,
                variable=metadata.is_variable,
                scripts=metadata.scripts
            )
            
            # Preview
            print("\n" + "═" * 60)
            print("░▒▓█  ＰＲＥＶＩＥＷ  █▓▒░")
            print("═" * 60)
            print(json.dumps(entry.to_dict(), indent=2, ensure_ascii=False))
            
            confirm = input("\n🔘 Add? (y/n): ").strip().lower()
            return entry if confirm == "y" else None
            
        except Exception as e:
            print(f"　　　🤷‍♀️ Oops, error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def collect_fonts(self) -> List[Dict[str, str]]:
        """Collect font information from user"""
        fonts = []
        
        while True:
            print(f"\n{'='*60}")
            print(f"░▒▓█  ＡＤＤＩＮＧ　ＦＯＮＴ　＃{len(fonts) + 1}  █▓▒░")
            print(f"{'='*60}")
            
            print("\n　━━━ ＦＯＮＴ ＮＡＭＥ ━━━")
            name = input("　　　＞ ").strip()
            if not name:
                if fonts:
                    break
                continue
            
            print("\n　━━━ ＵＲＬ ━━━")
            url = input("　　　＞ ").strip()
            
            print("\n　━━━ ＣＡＴＥＧＯＲＹ ━━━")
            print(f"　　　({' • '.join(self.config.CATEGORIES)}）")
            category = input("　　　＞ ").strip().lower()
            
            if category not in self.config.CATEGORIES:
                category = "sans-serif"
            
            fonts.append({"name": name, "url": url, "category": category})
            
            more = input("\n➕ Add another? (y/n): ").strip().lower()
            if more != "y":
                break
        
        return fonts
    
    def run(self):
        """Main application entry point"""
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║　　　　　　　　Ｆ Ｏ Ｎ Ｔ 　Ｃ Ａ Ｔ Ａ Ｌ Ｏ Ｇ Ｅ Ｒ　　　　　　　　║
╚═══════════════════════════════════════════════════════════════════╝
""")
        
        # Get repository info
        print("\n　━━━ ＳＯＵＲＣＥ ＲＥＰＯ ━━━")
        print(f"  　     (username/repo)  ")
        repo = input("　　　＞ ").strip()
        
        print("\n　━━━ ＴＯＫＥＮ ━━━")
        token = getpass.getpass("　　　＞ ").strip()
        
        # Initialize
        self.initialize(repo, token)
        
        # Fetch existing catalog
        try:
            catalog, sha = self.github.fetch()
            print(f"📡 Fetching current catalog with {len(catalog)} fonts\n")
        except Exception as e:
            print(f"⚠  Starting new catalog: {e}\n")
            catalog, sha = [], None
        
        # Collect fonts to process
        fonts_to_process = self.collect_fonts()
        
        if not fonts_to_process:
            print("⊗ No fonts to process.")
            return
        
        # Process fonts
        print(f"\n\n{'#'*60}")
        print(f"📡 Processing {len(fonts_to_process)} font(s)...")
        print(f"{'#'*60}")
        
        added_count = 0
        for i, font_data in enumerate(fonts_to_process, 1):
            entry = self.process_font(
                font_data["name"],
                font_data["url"],
                font_data["category"],
                i,
                len(fonts_to_process)
            )
            
            if entry:
                # Update or add to catalog
                found = False
                for j, existing in enumerate(catalog):
                    if existing["name"].lower() == entry.name.lower():
                        catalog[j] = entry.to_dict()
                        found = True
                        break
                
                if not found:
                    catalog.append(entry.to_dict())
                
                added_count += 1
        
        # Commit changes
        if added_count > 0 and sha:
            print(f"\n{'='*60}")
            print(f"🌀 Committing {added_count} font(s) to catalog...")
            try:
                self.github.update(catalog, sha)
                print("🎉 Catalog updated successfully!")
            except Exception as e:
                print(f"⊗ Commit failed: {e}")
                print("\n🌀 Saving locally...")
                GitHubCatalogManager.save_local(catalog)
                print("☑️ Saved to catalog.fonts.json")
        elif added_count > 0:
            print("\n🌀 Saving to local file...")
            GitHubCatalogManager.save_local(catalog)
            print("☑️ Saved to catalog.fonts.json")
        else:
            print("\n⚠  No changes made")
        
        print("\n╰┈➤ 🎊 ＡＬＬ ＤＯＮＥ！")

# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main():
    """Application entry point"""
    manager = FontCatalogManager()
    manager.run()

if __name__ == "__main__":
    main()
