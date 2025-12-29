!pip install -q vtracer pyperclip requests

import vtracer
import os
import pyperclip
import requests
import time

def get_path():
    try:
        from google.colab import files
        print("\n[SYSTEM] 🟢 NEURAL_UPLINK INITIATED... Select File.")
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
    print("\n" + "═"*60)
    print("    🌌  ＩＭＧ_２_ＳＶＧ  //  ＥＮＧＩＮＥ  Ｖ１０.２  🌌    ")
    print("    [ STATUS: READY_TO_VECTORIZE ]  [ CONNECTION: ENCRYPTED ]    ")
    print("═"*60 + "\n")
    
    print(">>> 📥 INPUT_STREAM (URL / Local Path / 'p' to Upload)")
    user_input = input(">>> SOURCE: ").strip()

    source = get_path() if user_input.lower() == 'p' else user_input
    if not source: 
        print("\n[!] ERROR: NO_SOURCE_DETECTED. ABORTING.")
        return

    is_url = source.startswith("http")
    local_img = "input_temp.png" if is_url else source
    
    if is_url:
        try:
            print("🛰️ [FETCH] PULLING PIXELS FROM THE GRID...")
            r = requests.get(source, timeout=10)
            with open(local_img, 'wb') as f: f.write(r.content)
        except Exception as e:
            print(f"\n[!] DATA_TRANSFER_FAILURE: {e}"); return

    # --- MODE SELECTION ---
    print("\n" + "─"*60)  
    print("💠 [1] LOGO_SPLINE (Smooth/Minimal)  |  🌌 [2] PHOTO_POLYGON (High-Detail)")
    print("─"*60)
    mode_choice = "spline" if input(">>> SELECT RENDERING_MODE: ") == "1" else "polygon"
    
    temp_svg = "matrix_output.svg"
    
    print(f"\n [🏮] PARSING_PIXELS... PLEASE_WAIT...")

    success = False
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
            
            print("\n" + "💎" + "─"*58 + "💎")
            print(" ██████╗ ██╗  ██╗")
            print(" ██╔══██╗██║ ██╔╝")
            print(" ██║  ██║█████╔╝ ")
            print(" ██║  ██║██╔═██╗ ")
            print(" ██████╔╝██║  ██╗")
            print(" ╚═════╝ ╚═╝  ╚═╝ VECTOR_SYNTHESIS_COMPLETE")          
            print("      [CONVERSION SUCCESS] VECTOR_GRID_STABILIZED      ")
            print("💎" + "─"*58 + "💎")
            
            # Clipboard Deployment
            try:
                pyperclip.copy(svg_code)
                print("📋 [CLIPBOARD]: SVG COPIED TO LOCAL MEMORY.")
            except:
                pass
            
            # Browser Handshake
            try:
                from google.colab import files
                print("💾 TERMINAL_EXPORT: Downloading SVG file...")
                files.download(temp_svg)
                time.sleep(2) 
            except:
                print(f"📄 LOCAL_SAVE: Data stored at {os.path.abspath(temp_svg)}")

            # Visual Preview
            print("\n>>> 🖥️ DATA_PREVIEW_STREAM:")
            print(f"      {svg_code[:180]}...")
            print("\n" + "━"*60)

        except Exception as e:
            print(f"\n[!] OUTPUT_ERROR: {e}")
    else:
        print("\n[!] CORE_CRITICAL_FAILURE: Reconstruction failed.")

    # Cleanup Protocol
    if is_url and os.path.exists(local_img):
        os.remove(local_img)
    
    print("\n[ENGINE_IDLE] SESSION_TERMINATED. 💤 ENGINE_SLEEP.")

# Execute Engine
img_2_svg_engine()
