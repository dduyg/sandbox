# ARCV — Complete Setup Guide
## Every step, every click, every URL

---

## WHAT YOU WILL BUILD
An image archive system where you:
1. Drop images into a folder on your computer
2. Run one Python command
3. Images appear automatically in your searchable web gallery

---

## PART 1 — SUPABASE (your database)
*Takes about 5 minutes*

### Step 1.1 — Create account
1. Go to → **https://supabase.com**
2. Click **"Start your project"** (top right)
3. Sign up with GitHub (easiest) or email

### Step 1.2 — Create a project
1. Click **"New project"**
2. Fill in:
   - **Name:** `arcv`
   - **Database Password:** choose something strong, save it
   - **Region:** pick the one closest to you
3. Click **"Create new project"**
4. Wait about 60 seconds for it to set up

### Step 1.3 — Create the images table
1. In the left sidebar, click **"SQL Editor"**
2. Click **"New query"**
3. Copy and paste this ENTIRE block:

```sql
create table images (
  id         bigserial primary key,
  filename   text unique not null,
  url        text not null,
  thumb_url  text,
  caption    text,
  tags       text[],
  dims       text,
  size       text,
  created_at timestamptz default now()
);

-- Allow public read access (so your UI can fetch images)
alter table images enable row level security;

create policy "Public read" on images
  for select using (true);

create policy "Service insert" on images
  for insert with check (true);
```

4. Click **"Run"** (or press Ctrl+Enter)
5. You should see: **"Success. No rows returned"**

### Step 1.4 — Get your credentials
1. In the left sidebar, click **"Project Settings"** (gear icon at bottom)
2. Click **"API"**
3. You will see:
   - **Project URL** → looks like `https://abcdefgh.supabase.co`
   - **anon public key** → long string starting with `eyJ...`
4. Copy BOTH — you need them in the next steps

---

## PART 2 — CLOUDFLARE R2 (your image storage)
*Takes about 10 minutes*

### Step 2.1 — Create account
1. Go to → **https://cloudflare.com**
2. Click **"Sign Up"** (top right)
3. Fill in email + password, verify email

### Step 2.2 — Enable R2
1. After login, in the left sidebar click **"R2 Object Storage"**
2. Click **"Purchase R2"** — it's free up to 10GB, no charge unless you go over
3. You may need to add a credit card (for identity verification only, not charged on free tier)

### Step 2.3 — Create a bucket
1. Click **"Create bucket"**
2. **Bucket name:** `arcv-images` (use lowercase, no spaces)
3. **Location:** leave as default
4. Click **"Create bucket"**

### Step 2.4 — Make the bucket public
1. Click on your new bucket **"arcv-images"**
2. Click the **"Settings"** tab
3. Scroll down to **"Public access"**
4. Click **"Allow Access"** → confirm
5. You will see a **"Public bucket URL"** — copy it. Looks like:
   `https://pub-abc123.r2.dev`

### Step 2.5 — Create API credentials
1. Go back to R2 main page (click "R2 Object Storage" in sidebar)
2. Click **"Manage R2 API Tokens"** (top right of the page)
3. Click **"Create API Token"**
4. Fill in:
   - **Token name:** `arcv-ingest`
   - **Permissions:** select **"Object Read & Write"**
   - **Bucket:** select **"arcv-images"**
5. Click **"Create API Token"**
6. **IMPORTANT:** Copy ALL THREE values shown (you won't see them again):
   - **Access Key ID**
   - **Secret Access Key**
   - **Account ID** (shown at the top of the page)

---

## PART 3 — ANTHROPIC API KEY (for AI labeling)
*Takes 2 minutes*

1. Go to → **https://console.anthropic.com**
2. Log in or create account
3. Click **"API Keys"** in the left sidebar
4. Click **"Create Key"**
5. **Name:** `arcv`
6. Copy the key — starts with `sk-ant-...`

---

## PART 4 — SET UP THE PYTHON INGESTION SCRIPT
*On your own computer*

### Step 4.1 — Install Python (if you don't have it)
- Go to **https://python.org/downloads**
- Download and install Python 3.10 or newer

### Step 4.2 — Set up the project folder
Open your Terminal (Mac/Linux) or Command Prompt (Windows) and run:

```bash
# Create project folder
mkdir arcv
cd arcv

# Create a folder to drop your images into
mkdir images_to_upload

# Copy ingest.py and requirements.txt into this folder
# (the files you downloaded from ARCV)
```

### Step 4.3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4.4 — Fill in your credentials
1. Open **`ingest.py`** in any text editor (VS Code, Notepad, TextEdit)
2. Find the section at the top that says `PASTE YOUR CREDENTIALS HERE`
3. Replace each placeholder with your real values:

```python
SUPABASE_URL      = "https://YOUR_PROJECT_ID.supabase.co"   # ← from Step 1.4
SUPABASE_KEY      = "eyJ..."                                  # ← from Step 1.4
R2_ACCOUNT_ID     = "abc123..."                               # ← from Step 2.5
R2_ACCESS_KEY_ID  = "abc..."                                  # ← from Step 2.5
R2_SECRET_KEY     = "xyz..."                                  # ← from Step 2.5
R2_BUCKET_NAME    = "arcv-images"                             # ← your bucket name
R2_PUBLIC_URL     = "https://pub-abc123.r2.dev"               # ← from Step 2.4
ANTHROPIC_API_KEY = "sk-ant-..."                              # ← from Part 3
```

4. Save the file

### Step 4.5 — Run your first ingestion
```bash
# Drop some images into the images_to_upload folder, then:
python ingest.py
```

You will see output like:
```
═══════════════════════════════════════════════════════
  ARCV Ingestion Pipeline
  Folder : /Users/you/arcv/images_to_upload
  Images : 3 found
═══════════════════════════════════════════════════════

[1/3] photo.jpg
    Uploading to R2 as 'images/photo.jpg'...
    Sending to Claude Vision for labeling...
    Saving to Supabase...
    ✅ Done — A laptop computer on a wooden desk with code visible on screen
    Tags: laptop, code, desk, programming, workspace, technology
```

---

## PART 5 — SET UP THE WEB INTERFACE
*Deploy to Vercel for free*

### Step 5.1 — Fill in credentials in App.jsx
1. Open **`src/App.jsx`**
2. Find this at the top:
```js
const SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co";
const SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";
```
3. Replace with your actual values from Step 1.4
4. Save the file

### Step 5.2 — Push to GitHub
1. Go to **https://github.com** → log in or create account
2. Click **"New repository"** (green button)
3. Name it `arcv`
4. Click **"Create repository"**
5. Follow the commands GitHub shows you to push your code:

```bash
# In your arcv folder:
git init
git add .
git commit -m "initial arcv setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/arcv.git
git push -u origin main
```

### Step 5.3 — Deploy on Vercel
1. Go to → **https://vercel.com**
2. Click **"Sign Up"** → choose **"Continue with GitHub"**
3. Click **"Add New Project"**
4. Find your `arcv` repository → click **"Import"**
5. Vercel auto-detects Vite. Leave all settings as default.
6. Click **"Deploy"**
7. Wait ~60 seconds
8. Click **"Visit"** — your live URL will look like `https://arcv-xxx.vercel.app`

---

## DAILY USAGE

Once everything is set up, adding images is just:

```bash
# Copy images into the folder
cp ~/Downloads/new_photo.jpg ./images_to_upload/

# Run the script
python ingest.py

# Refresh your browser — images appear instantly
```

---

## TROUBLESHOOTING

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `Invalid API Key` | Check your Supabase anon key in App.jsx |
| Images not showing in UI | Check R2 bucket is set to public (Step 2.4) |
| `Access Denied` on R2 | Check R2 Access Key and Secret Key in ingest.py |
| Claude returns bad JSON | Re-run the script, it's occasionally flaky |
| Vercel deploy fails | Make sure package.json is in the root folder |

---

## YOUR CREDENTIALS CHECKLIST

Before running anything, make sure you have all of these:

- [ ] Supabase Project URL
- [ ] Supabase Anon Key  
- [ ] Cloudflare Account ID
- [ ] R2 Access Key ID
- [ ] R2 Secret Access Key
- [ ] R2 Bucket Name
- [ ] R2 Public URL
- [ ] Anthropic API Key
