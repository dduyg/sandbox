print(f"\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
print(f"██  ⟫⟫⟫ [COMPLETE] STREAM.SUCCESSFUL")
print(f"██  ")
print(f"      ├── total.input: (total inputted at first to process)")
print(f"      ├── status.success: (total processed glyphs)")
print(f"      ├── status.skipped: (total skipped)")
print(f"      ├── commit.type: (library_init or library_update)")
print(f"      │   ├── ((if existing_glyphs) `{len(existing_glyphs)} + {len(all_data)} = {len(all_glyphs)} glyphs in total` (else) `{len(all_data)} glyphs`)")
print(f"      │   └── ((if existing_glyphs) `2 catalogs updated` (else) `2 catalogs created`)")
print(f"      ├── input.mode: `SELECT.FROM.LOCAL.COMPUTER` ( if chosen 1) or `FETCH.FROM.REPOSITORY` (if 2)")
print(f"      └── location: (dest_repo)")
print(f"        └── [↗] https://github.com/link-to-dest-repo")
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
     if skipped:
            print(f"██  ")
            print(f"██⎯⎯⎯ [×] Skipped (n total skipped) files:")
            for msg in skipped:
                print(f"██        >> {msg}")
        
        
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
