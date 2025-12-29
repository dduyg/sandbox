!pip install -q vtracer pyperclip requests

import vtracer
import os
import pyperclip
import requests
import time

def get_path():
    try:
        from google.colab import files
        print("\n[SYSTEM] 🟢 INITIALIZING UPLOAD_UPLINK...")
        uploaded = files.upload()
        if not uploaded: return None
        return list(uploaded.keys())[0]
    except:
        from tkinter import Tk, filedialog
        root = Tk(); root.withdraw(); root.attributes("-topmost", True)
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        root.destroy()
        return path

def img_2_svg_engine():
    print(" " + "═"*60)
    print("   ░▒▓█ ERROR_404: IMG_2_SVG_ENGINE // V.10.2 █▓▒░   ")
    print("   > STATUS: NEON_LINK_ESTABLISHED...")
    print(" " + "═"*60)
    
    user_input = input("\n[SYNTAX] 🔗 INPUT_STREAM (URL / PATH / 'p' for UPLINK): ").strip()

    source = get_path() if user_input.lower() == 'p' else user_input
    if not source: 
        print("\n[TERMINAL] 🔴 ABORT: NO_SOURCE_DETECTED.")
        return

    is_url = source.startswith("http")
    local_img = "buffer_input.png" if is_url else source
    
    if is_url:
        try:
            print("[NETWORK] 🌐 DOWNLOADING_REMOTE_ASSET...")
            r = requests.get(source, timeout=10)
            with open(local_img, 'wb') as f: f.write(r.content)
        except Exception as e:
            print(f"\n[CRITICAL] ❌ PROTOCOL_FAILURE: {e}"); return

    print("\n--- SELECT_VECTOR_MODE ---")
    print("[1] 💠 LOGO_SPLINE (Ultra-Smooth)")
    print("[2] 🌌 PHOTO_POLYGON (High-Detail)")
    mode_choice = "spline" if input("\n[USER_INPUT] > ").strip() == "1" else "polygon"
    
    temp_svg = "cyber_render.svg"
    print(f"\n[ENGINE] ⚙️ TRACING_PIXELS_INTO_VECTORS...")

    success = False
    # Attempting conversion with adaptive fallback logic
    for params in [{"mode": mode_choice, "precision": 2}, {"mode": mode_choice}, {}]:
        try:
            vtracer.convert_image_to_svg_py(local_img, temp_svg, **params)
            success = True
            break
        except: continue

    if success:
        try:
            with open(temp_svg, "r", encoding="utf-8") as f:
                content = f.read()
                svg_start = content.find("<svg")
                svg_code = content[svg_start:] if svg_start != -1 else content
            
            print("\n" + "─"*60)
            print("✨ RENDER_COMPLETE: ASSET_VIRTUALIZED!")
            
            # Clipboard Deployment
            try:
                pyperclip.copy(svg_code)
                print("📋 CODE_DEPLOYED: Copied to Neural_Link (Clipboard)")
            except:
                pass
            
            # Colab Downlink
            try:
                from google.colab import files
                print("💾 DOWNLOAD_STREAM: Initializing local save...")
                files.download(temp_svg)
                time.sleep(2) # Buffer for Colab's JavaScript to trigger
            except:
                print(f"📄 LOCAL_SAVE: {os.path.abspath(temp_svg)}")

            print("\n--- HEX_PREVIEW ---")
            print(f"\033[95m{svg_code[:250]}...\033[0m")
            print("─"*60)

        except Exception as e:
            print(f"\n[ERROR] ❌ OUTPUT_CORRUPTED: {e}")
    else:
        print("\n[CRITICAL] ❌ ENGINE_STALL: Conversion Failed.")

    # Garbage Collection
    if is_url and os.path.exists(local_img):
        os.remove(local_img)
    
    print("\n[SYSTEM] 💤 ENGINE_SLEEP. SESSION_CLOSED.")

# Start the Engine
img_2_svg_engine()
