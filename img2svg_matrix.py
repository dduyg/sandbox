!pip install -q vtracer pyperclip requests

import vtracer
import os
import pyperclip
import requests
import time

def get_path():
    try:
        from google.colab import files
        print("🌌 [SYSTEM]: INITIATING NEURAL UPLOAD...")
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
    print("｡☆━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━☆｡")
    print("    ＶＡＰＯＲＷＡＶＥ  ＳＶＧ  ＥＮＧＩＮＥ  ｖ１０．２    ")
    print("       > STATUS: READY_TO_VECTORIZE <        ")
    print("｡☆━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━☆｡")
    
    user_input = input("✨ [SIGNAL_INPUT] (URL / Local Path / 'p' for Upload): ").strip()

    source = get_path() if user_input.lower() == 'p' else user_input
    if not source: 
        print("🏮 [ERROR]: SIGNAL LOST. SHUTTING DOWN...")
        return

    is_url = source.startswith("http")
    local_img = "input_temp.png" if is_url else source
    
    if is_url:
        try:
            r = requests.get(source, timeout=10)
            with open(local_img, 'wb') as f: f.write(r.content)
        except Exception as e:
            print(f"🏮 [ERROR]: PACKET LOSS DURING DOWNLOAD: {e}"); return

    print("\n[1] ＬＯＧＯ (Smooth Spline) | [2] ＰＨＯＴＯ (Grid Polygon)")
    mode_choice = "spline" if input("🔮 [SELECT_AESTHETIC]: ") == "1" else "polygon"
    temp_svg = "output.svg"
    
    print(f"\n⚡ [COMPILING]: TRACING NEURAL PATHWAYS...")

    success = False
    # Cycle through parameter sets for maximum compatibility
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
            
            print("\n💎 [SUCCESS]: VECTOR STREAM STABILIZED!")
            
            # Clipboard Logic
            try:
                pyperclip.copy(svg_code)
                print("📋 [CLIPBOARD]: DATA COPIED TO LOCAL MEMORY.")
            except:
                pass
            
            # Google Colab Auto-Download
            try:
                from google.colab import files
                print("💾 [TRANSFER]: DOWNLOADING DATA-PACK TO USER...")
                files.download(temp_svg)
                time.sleep(2) # Handshake buffer for browser trigger
            except:
                print(f"📄 [STORAGE]: SAVED TO VIRTUAL DISK: {os.path.abspath(temp_svg)}")

            print("\n--- ＣＯＤＥ_ＰＲＥＶＩＥＷ ---")
            print(f"{svg_code[:250]}...")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        except Exception as e:
            print(f"🏮 [ERROR]: DATA CORRUPTION DETECTED: {e}")
    else:
        print("🏮 [ERROR]: CONVERSION SEQUENCE TERMINATED.")

    # Cleanup temp download files
    if is_url and os.path.exists(local_img):
        os.remove(local_img)
    
    print("\n🌌 [ENGINE_IDLE]: DISCONNECTING FROM GRID...")

# Execute the engine
img_2_svg_engine()
