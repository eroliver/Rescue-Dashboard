A plug & play dashboard for animal shelters that use ShelterLuv to visualize their impact in real-time. No database or expensive hosting required.

## 🌟 Features
- **Real-Time API Sync**: Pulls data directly from Shelterluv (no manual exports).
- **Geographic Insights**: See which cities are supporting your rescue the most.
- **Medical Transparency**: Showcase the number of medical services (vaccines/spays) provided.
- **Fully Customizable**: Change the shelter name, colors and which stats to display via a config file.
- **Available Online for Free**: Using streamlit hosting, you can access the dashboard from any device that's online.
---
Steps below should get you up and running, but reach out to me if you have any trouble or would like help extending the dashboard. 
## 🚀 15-Minute Setup Guide
### Step 1: Create a GitHub Account
1. Go to [GitHub.com](https://github.com) and sign up for a free account.
2. Click the **+** icon in the top right and select **New repository**.
3. Name it `impact-dashboard` and click **Create repository**.

### Step 2: Upload the Files
1. In your new repository, click **Add file** -> **Create new file**.
2. Create `streamlit_app.py` and paste the script code.
3. Create `requirements.txt` and paste the dependency list.
4. Click **Commit changes** to save.

### Step 3: Host for Free on Streamlit
1. Go to [Streamlit Cloud](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **Create App** and select your `impact-dashboard` repository.
3. **CRITICAL**: Click **Advanced Settings** before deploying.
4. In the **Secrets** box, paste the following and fill in your details:

```toml
# --- REQUIRED ---
SHELTERLUV_API_KEY = "your-api-key-here"
# --- CUSTOMIZATION ---
SHELTER_DISPLAY_NAME = "Your Rescue Name"
PRIMARY_COLOR = "#2E7D32" # Your brand's hex color
# --- TOGGLES ---
SHOW_ADOPTED_COUNT = true
SHOW_SAVE_RATE = true
SHOW_ALTERED_COUNT = true
SHOW_VACCINES = true
SHOW_SPECIES = true
SHOW_GEODATA = true
