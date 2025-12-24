▸▸▸ access.token: ").strip()
▸▸▸ source.repo [username/repo-name]:


dest_input = input("  >> DEST.REPO (username/repo-name): ").strip()
branch = input("  >> DEST.BRANCH [main]: ").strip() or "main"
token = getpass("  >> AUTH.TOKEN: ").strip()
source_input = input("  >> SOURCE.REPO (username/repo-name): ").strip()


▸▸▸ DEST_REPO [username/repo-name]:
▸▸▸ ACCESS_TOKEN:

▸▸▸ SOURCE_PATH [e.g. raw_glyphs]:
▸▸▸ SOURCE_BRANCH [default=main]:


print(f"  ⊗ ERR :: {e}")


print("\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
print("█ ⟪⟪⟪ INPUT SOURCE CONFIGURATION ⟫⟫⟫                                      █")
print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
print("█  [1] LOCAL_UPLOAD → Select from computer                                 █")
print("█  [2] GITHUB_FETCH → Pull from repository                                 █")
print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")

if input_method == "2":
    print("\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
    print("█ ⌬ SOURCE REPOSITORY CONFIGURATION ⌬                                     █")
    print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
       

COMPLETE ::
 
>> GITHUB CONFIG :: 

print(f"  [X] ERROR :: {e}")

  >> LOCAL UPLOAD :: Select files to process")

  ⊙ WARN :: REPO_NOT_FOUND → CREATING '{github_repo}'...")


        print(f"\n  ⌬ FETCHING_DATA :: {len(png_files)} files from {source_user}/{source_repo}/{source_path}")

>> INPUT SOURCE :: Select data origin")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("  [1] Local upload from computer")

input_method = input("\n  [>] Select mode [1 or 2] >> ").strip()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ▓▓▓ OPERATION COMPLETE ▓▓▓")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Choose input method
print("\n╔══════════════════════════════════════════════════════════════════════════════╗")
print("║  ⟨⟨ INPUT SOURCE SELECTION ⟩⟩                                                ║")
print("╠══════════════════════════════════════════════════════════════════════════════╣")
print("║  [1] → LOCAL.UPLOAD    ⟨Upload from computer⟩                                ║")
print("║  [2] → REMOTE.FETCH    ⟨Fetch from GitHub repo⟩                              ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝")
