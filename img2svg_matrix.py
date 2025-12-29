!pip install -q vtracer pyperclip requests

import vtracer
import os
import pyperclip
import requests
import time

def get_path():
    try:
        from google.colab import files
        print("💾 [SYSTEM] ACCESSING NEURAL UPLOAD GATEWAY...")
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
    # --- CYBERPUNK HEADER ---
    print("\n" + "％"*25)
    print("    💠 ɪᴍɢ_𝟸_sᴠɢ_ᴇɴɢɪɴᴇ // ᴠ.𝟷𝟶.𝟸 💠    ")
    print("    > STATUS: HYPER-VIRTUAL ONLINE <    ")
    print("％"*25)
    
    print("⚡ [INPUT] PROVIDE DATA STREAM (URL / LOCAL_PATH / 'p' for UPLOAD)")
    user_input = input(">> NETWORK_PATH: ").strip()

    source = get_path() if user_input.lower() == 'p' else user_input
    if not source: 
        print("❌ [CRITICAL] NO SOURCE DETECTED. TERMINATING...")
        return

    is_url = source.startswith("http")
    local_img = "buffer_img.png" if is_url else source
    
    if is_url:
        try:
            print("🌐 [FETCH] PULLING PIXELS FROM THE GRID...")
            r = requests.get(source, timeout=10)
            with open(local_img, 'wb') as f: f.write(r.content)
        except Exception as e:
            print(f"❌ [ERROR] STREAM INTERRUPTED: {e}"); return

    print("\n[1] LOGO.spline (Smooth/Minimal) | [2] PHOTO.poly (High-Detail)")
    mode_choice = "spline" if input(">> SELECT_ALGORITHM: ") == "1" else "polygon"
    temp_svg = "vector_matrix.svg"
    
    print(f"\n✨ [PROCESS] RECONSTRUCTING GEOMETRY...")

    success = False
    # Attempting matrix decomposition with adaptive parameter injection
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
            
            print("\n" + "─"*40)
            print("✅ [SUCCESS] SVG SYNTHESIS COMPLETE!")
            
            # Clipboard Uplink
            try:
                pyperclip.copy(svg_code)
                print("📋 [LINK] SVG_CODE PUSHED TO CLIPBOARD")
            except:
                pass
            
            # File Extraction
            try:
                from google.colab import files
                print("💾 [DOWNLOAD] EXTRUDING SVG TO LOCAL STORAGE...")
                files.download(temp_svg)
                time.sleep(2) # Handshake delay
            except:
                print(f"📄 [SAVE] VECTOR_MATRIX LOCATED AT: {os.path.abspath(temp_svg)}")

            print("\n--- DATA PREVIEW (NEURAL SCAN) ---")
            print(f"\033[95m{svg_code[:200]}...\033[0m")
            print("─"*40)

        except Exception as e:
            print(f"❌ [FATAL] OUTPUT BUFFER CORRUPTED: {e}")
    else:
        print("❌ [FAILED] ALGORITHM COLLAPSE.")

    # Final Grid Cleanup
    if is_url and os.path.exists(local_img):
        os.remove(local_img)
    
    print("\n✨ [SIGNAL] PROCESS FINISHED. LOGGING OFF...")

# --- INIT CORE ---
img_2_svg_engine()
