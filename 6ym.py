▸▸▸ source.repo [username/repo-name]:

dest_input = input("  >> DEST.REPO (username/repo-name): ").strip()
branch = input("  >> DEST.BRANCH [main]: ").strip() or "main"
token = getpass("  >> AUTH.TOKEN: ").strip()
source_input = input("  >> SOURCE.REPO (username/repo-name): ").strip()


▸▸▸ DEST_REPO [username/repo-name]:
▸▸▸ ACCESS_TOKEN:
▸▸▸ SOURCE_PATH [e.g. raw_glyphs]:
▸▸▸ SOURCE_BRANCH [default=main]:

print("\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
print("█ ⟪⟪⟪ INPUT SOURCE CONFIGURATION ⟫⟫⟫                                      █")
print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
print("█  [1] LOCAL_UPLOAD → Select from computer                                 █")
print("█  [2] GITHUB_FETCH → Pull from repository                                 █")
print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")


>> GITHUB CONFIG :: 

  >> LOCAL UPLOAD :: Select files to process")

>> INPUT SOURCE :: Select data origin")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  [1] Local upload from computer")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ▓▓▓ SOURCE REPOSITORY CONFIGURATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Choose input method
print("\n╔══════════════════════════════════════════════════════════════════════════════╗")
print("║  ⟨⟨ INPUT SOURCE SELECTION ⟩⟩                                                ║")
print("╠══════════════════════════════════════════════════════════════════════════════╣")
print("║  [1] → LOCAL.UPLOAD    ⟨Upload from computer⟩                                ║")
print("║  [2] → REMOTE.FETCH    ⟨Fetch from GitHub repo⟩                              ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝")
