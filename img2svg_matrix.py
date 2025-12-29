!pip install -q vtracer pyperclip requests

import vtracer
import os
import pyperclip
import requests
import time

def get_path():
    try:
        from google.colab import files
        print(" [SYSTEM] INITIALIZING UPLOAD_VORTEX...")
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
    print("""
    ░█▀▀█ █░░█ █▀▀█ █▀▀ █▀▀█ 　 ▀▀█ 　 █▀▀ █░░█ █▀▀█ 
    ░█░░░ █▄▄█ █▀▀▄ █▀▀ █▄▄▀ 　 ▄▀░ 　 ▀▀█ ▀▄▄█ █░░█ 
    ░█▄▄█ ▄▄▄█ █▄▄█ ▀▀▀ ▀░▀▀ 　 ▀▀▀ 　 ▀▀▀ ▄▄▄█ ▀▀▀█
    
    >> VIRTUAL_TRACER :: VERSION_10.2_NEON
    >> STATUS: READY_TO_CODE
    """)
    print("═" * 60)
    print(" [LINK_INPUT] URL / LOCAL_PATH / 'P' (UPLOAD_SIGNAL)")
    print("═" * 60)
    
    user_input = input(" 🖥️  SYS_ENTRY >> ").strip()

    source = get_path() if user_input.lower() == 'p' else user_input
    if not source: 
        print(" [!] NULL_SOURCE_DETECTED. TERMINATING_THREAD.")
        return

    is_url = source.startswith("http")
    local_img = "buffer_source.png" if is_url else source
    
    if is_url:
        try:
            print(" [NET] PULLING_DATA_FROM_GRID...")
            r = requests.get(source, timeout=10)
            with open(local_img, 'wb') as f: f.write(r.content)
        except Exception as e:
            print(f" [!] NET_ERROR: {e}"); return

    print("\n [SELECT_ALGORITHM]")
    print(" 1: LOGO_SMOOTH (SPLINE_FLOW)")
    print(" 2: PHOTO_REAL (POLY_CRUSH)")
    
    mode_choice = "spline" if input(" >> MODE_ID: ") == "1" else "polygon"
    temp_svg = "vector_export.svg"
    
    print(f"\n [⚡] PARSING_PIXELS... PLEASE_WAIT...")

    success = False
    # Attempting various kernels for maximum compatibility
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
            
            print("\n" + "─" * 60)
            print(" ██████╗ ██╗  ██╗")
            print(" ██╔══██╗██║ ██╔╝")
            print(" ██║  ██║█████╔╝ ")
            print(" ██║  ██║██╔═██╗ ")
            print(" ██████╔╝██║  ██╗")
            print(" ╚═════╝ ╚═╝  ╚═╝ VECTOR_SYNTHESIS_COMPLETE")
            
            # Clipboard Sync
            try:
                pyperclip.copy(svg_code)
                print(" [CLIPBOARD] SVG_STRING_CACHED")
            except:
                pass
            
            # Grid Download (Colab)
            try:
                from google.colab import files
                print(" [EXPORT] TRANSMITTING_FILE_TO_USER...")
                files.download(temp_svg)
                time.sleep(2) 
            except:
                print(f" [FILE] LOCAL_STORAGE: {os.path.abspath(temp_svg)}")

            print("\n--- HEX_PREVIEW ---")
            print(f"{svg_code[:180]}...")
            print("─" * 60)

        except Exception as e:
            print(f" [!] OUTPUT_FAILURE: {e}")
    else:
        print(" [!] CORE_DUMP: CONVERSION_FAILED")

    # Final Grid Cleanup
    if is_url and os.path.exists(local_img):
        os.remove(local_img)
    
    print("\n [SYSTEM] THREAD_CLOSED. GOODBYE_USER.")

# BOOT SYSTEM
img_2_svg_engine()
