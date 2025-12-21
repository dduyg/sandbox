# 🗝 Getting Gemini API Key

## Step-by-Step:

1. **Go to Google AI Studio:**
   ```
   https://aistudio.google.com/app/apikey
   ```

2. **Sign in** with your Google account

3. **Click "Create API Key"** button

4. **Choose a Google Cloud project:**
   - If you don't have one, click "Create API key in new project"
   - This will automatically create a project for you

5. **Copy your API key** 🔑
   - It looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - Store it safely!

## Free Tier Limits:

✅ **Completely FREE** for:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

This is more than enough for personal font cataloging! 🎉

## Alternative Direct Link:

If the above doesn't work, try:
```
https://makersuite.google.com/app/apikey
```

## Important Notes:

⚠️ **Keep your API key secret** - don't share it publicly or commit it to GitHub

💡 **Tip:** You can store it in environment variables:
```bash
export GEMINI_API_KEY="your-key-here"
```

Then modify the script to read it:
```python
import os
gemini_key = os.getenv('GEMINI_API_KEY') or getpass("　ＧＥＭＩＮＩ　ＡＰＩ　ＫＥＹ (hidden)： ")
```

That's it! Super easy and completely free. 🌟
