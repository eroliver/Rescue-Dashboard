import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIG & THEME ---
SHELTER_NAME = st.secrets.get("SHELTER_DISPLAY_NAME", "Our Animal Rescue")
PRIMARY_COLOR = st.secrets.get("PRIMARY_COLOR", "#2E7D32")
SHOW_GEODATA = st.secrets.get("SHOW_GEODATA", True)
SHOW_VACCINES = st.secrets.get("SHOW_VACCINES", True)
SHOW_ADOPTED_COUNT = st.secrets.get("SHOW_ADOPTED_COUNT", True)
SHOW_SAVE_RATE = st.secrets.get("SHOW_SAVE_RATE", False)
SHOW_ALTERED_COUNT = st.secrets.get("SHOW_ALTERED_COUNT", True)
SHOW_SPECIES = st.secrets.get("SHOW_SPECIES", False)

st.set_page_config(page_title=f"{SHELTER_NAME} Impact", layout="wide")

st.markdown(f"""
    <style>
    .main {{ background-color: #f5f7f9; }}
    div[data-testid="stMetricValue"] {{ color: {PRIMARY_COLOR}; font-size: 42px; font-weight: 700; }}
    h1, h2, h3 {{ color: {PRIMARY_COLOR}; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_rescue_data():
    api_key = st.secrets["SHELTERLUV_API_KEY"]
    headers = {"X-Api-Key": api_key}
    endpoints = ["animals", "events", "people", "vaccines"]
    results = {}

    for ep in endpoints:
        all_records, has_more, offset = [], True, 0
        while has_more:
            url = f"https://new.shelterluv.com/api/v1/{ep}?offset={offset}"
            resp = requests.get(url, headers=headers).json()
            all_records.extend(resp.get(ep, []))
            has_more = resp.get('has_more', False)
            offset += 100
        results[ep] = pd.DataFrame(all_records)
    return results

# --- 3. PROCESSING & BRIDGING ---
data = fetch_rescue_data()
df_animals = data['animals']
df_events = data['events']
df_people = data['people']
df_vaccines = data['vaccines']


# Normalize People Data for the "Name Bridge"
# Note: peopleResponse.json uses 'Firstname' and 'Lastname'
df_people['join_name'] = (df_people['Firstname'].str.strip().str.lower() + 
                            df_people['Lastname'].str.strip().str.lower())

# Create Name -> City lookup
name_to_city = df_people.set_index('join_name')['City'].to_dict()

# --- METRICS ---
# 1. Foster Heroes (Using the Name Bridge)
foster_data = df_animals[df_animals['RelationshipType'] == 'foster'].copy() if 'RelationshipType' in df_animals.columns else df_animals[df_animals['InFoster'] == True].copy()

def get_foster_name(row):
    p = row.get('AssociatedPerson', {})
    if isinstance(p, dict):
        return f"{p.get('FirstName', '')} {p.get('LastName', '')}".strip()
    return None

foster_data['FullName'] = foster_data.apply(get_foster_name, axis=1)
unique_fosters = foster_data['FullName'].dropna().unique()
foster_count = len(unique_fosters)

# 2. Medical & Adoptions
total_adoptions = df_events[df_events['Type'] == 'Outcome.Adoption'].shape[0]
med_impact = len(df_vaccines)

# Spay/Neuter (Looking for 'Yes', 1, or True in 'Altered')
# Use .get() or check column existence to prevent crashes if API schema changes
altered_col = 'Altered' if 'Altered' in df_animals.columns else 'AlteredStatus'
altered_count = df_animals[df_animals[altered_col].isin(['Yes', 1, True])].shape[0]

# Save Rate
pos_types = ['Outcome.Adoption', 'Outcome.Transfer', 'Outcome.ReturnToOwner']
neg_types = ['Outcome.Euthanasia']
positive = df_events[df_events['Type'].isin(pos_types)].shape[0]
negative = df_events[df_events['Type'].isin(neg_types)].shape[0]
total_outcomes = positive + negative
save_rate = (positive / total_outcomes * 100) if total_outcomes > 0 else 0

# --- UI DISPLAY ---
st.title(f"🐾 {SHELTER_NAME} Impact Dashboard")
st.divider()

metrics_to_show = []
if SHOW_ADOPTED_COUNT:
    metrics_to_show.append({"label": "Lives Rehomed", "value": f"{total_adoptions:,}"})
if SHOW_SAVE_RATE:
    metrics_to_show.append({"label": "Save Rate", "value": f"{save_rate:.1f}%"})
if SHOW_ALTERED_COUNT:
    metrics_to_show.append({"label": "Spay/Neuter Procedures", "value": f"{altered_count:,}"})
if SHOW_VACCINES:
    metrics_to_show.append({"label": "Medical Services", "value": f"{med_impact:,}"})

# 2. Create the exact number of columns needed
if metrics_to_show:
    cols = st.columns(len(metrics_to_show))
    # 3. Iterate through both the columns and the metrics at the same time
    for col, metric in zip(cols, metrics_to_show):
        col.metric(label=metric["label"], value=metric["value"])

col_l, col_r = st.columns(2)

with col_l:
    if SHOW_SPECIES:
        st.write("### Rescue Species Breakdown")
        st.bar_chart(df_animals['Type'].value_counts(), color=PRIMARY_COLOR, horizontal=True)

with col_r:
    if SHOW_GEODATA:
        st.write("### Adoption Communities")
        # Join for Adopters (using Internal-ID from events)
        def extract_pid(records):
            return next((r['Id'] for r in records if r.get('Type') == 'Person'), None)
        
        adoptions = df_events[df_events['Type'] == 'Outcome.Adoption'].copy()
        adoptions['PID'] = adoptions['AssociatedRecords'].apply(extract_pid)
        
        # Map ID to City
        id_to_city = df_people.set_index('Internal-ID')['City'].to_dict()
        adoptions['City'] = adoptions['PID'].map(id_to_city)
        
        st.bar_chart(adoptions['City'].value_counts().head(10), color=PRIMARY_COLOR, horizontal=True)

st.write("### Impact Projection")
multiplier = st.slider("Estimated strays prevented per spay:", 5, 20, 12)
projected = altered_count * multiplier

st.markdown(f"""
    <div style="text-align: center; padding: 25px; border: 2px solid {PRIMARY_COLOR}; border-radius: 15px; background-color: white;">
        <p style="font-size: 18px; color: #555;">Predicted Future Strays Prevented</p>
        <h1 style="font-size: 72px; margin: 0; color: {PRIMARY_COLOR};">{projected:,}</h1>
    </div>
""", unsafe_allow_html=True)
