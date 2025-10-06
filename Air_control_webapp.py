# streamlit run Air_control_webapp.py

import streamlit as st
import requests
import time


# ================== CONFIG ==================
FIREBASE_URL = "https://newfirebase-3741b-default-rtdb.asia-southeast1.firebasedatabase.app"
REFRESH_SEC = 2
SEND_INTERVAL = 5

st.set_page_config(page_title="Smart Room Management", layout="wide", page_icon="🏢")

# ================== SIDEBAR NAVIGATION ==================
st.sidebar.title("🏢 Smart Room System")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📍 Select Page",
    ["🌡️ AC Control System"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Use the navigation above to switch between pages")

# ================== SHARED CSS ==================
st.markdown("""
<style>
    /* Global Styles */
    .main-title {
        font-size: 48px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 28px;
        font-weight: bold;
        color: #1f2a44;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid #7b3fbf;
    }

    /* AC Control Styles */
    .room-frame {
        border: 3px solid #1f2a44;
        border-radius: 16px;
        background: linear-gradient(135deg, #f6f8ff 0%, #e8ecff 100%);
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .room-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 20px;
    }
    .ac-card {
        background: linear-gradient(135deg, rgba(123,63,191,.95), rgba(123,63,191,.80));
        color: #fff;
        border-radius: 12px;
        padding: 20px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 2px solid rgba(255,255,255,.2);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .ac-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    .ac-title { 
        font-size: 24px; 
        font-weight: bold; 
        margin-bottom: 12px;
        border-bottom: 2px solid rgba(255,255,255,0.3);
        padding-bottom: 8px;
    }
    .kv { 
        display: flex; 
        justify-content: space-between; 
        font-weight: 600;
        margin: 6px 0;
        font-size: 16px;
    }
    .status-on { color: #22c55e; font-weight: bold; text-shadow: 0 0 10px rgba(34,197,94,0.5); }
    .status-off { color: #ef4444; font-weight: bold; text-shadow: 0 0 10px rgba(239,68,68,0.5); }
    .person-count { 
        font-size: 32px; 
        font-weight: bold; 
        text-align: center;
        background: white;
        padding: 20px;
        border-radius: 12px;
        color: #1f2a44;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .person-count span {
        color: #7b3fbf;
        font-size: 40px;
    }
    .control-panel {
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 2px solid #e8ecff;
    }

    .ac-control-title {
        font-size: 26px;
        font-weight: bold;
        color: #7b3fbf;
        margin-bottom: 16px;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }

    /* Activity Detection Styles */

    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stats-number {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .stats-label {
        font-size: 18px;
        text-align: center;
        opacity: 0.9;
    }
    .activity-table {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .activity-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        font-weight: bold;
        text-align: center;
    }

    /* Common Styles */
    .time-display {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        padding: 15px;
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
        border-radius: 10px;
        margin-top: 20px;
    }
    div[data-testid="stButton"] button {
        height: 50px; 
        font-size: 16px; 
        font-weight: bold; 
        border-radius: 10px;
        transition: all 0.3s;
    }
    div[data-testid="stButton"] button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)


# ================== FIREBASE HELPERS ==================
def get_firebase_data(path):
    try:
        r = requests.get(f"{FIREBASE_URL}/{path}.json", timeout=3)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def set_firebase_data(path, value):
    try:
        r = requests.put(f"{FIREBASE_URL}/{path}.json", json=value, timeout=3)
        return r.status_code == 200
    except:
        return False


def send_to_firebase(data):
    try:
        res = requests.patch(FIREBASE_URL + "/activity.json", json=data)
        if res.status_code != 200:
            st.warning(f"Firebase error: {res.text}")
    except Exception as e:
        st.error(f"Firebase exception: {e}")


# ================== PAGE 1: AC CONTROL SYSTEM ==================

# ✅ ADD TEMP SETTING FEATURE FOR EACH AC
# Modify your page_ac_control() function

def page_ac_control():
    def ac_card_html(i, temp, hum, status, set_temp):
        temp_txt = f"{temp}°C" if temp is not None else "N/A"
        hum_txt = f"{hum}%" if hum is not None else "N/A"
        set_temp_txt = f"{set_temp}°C" if set_temp is not None else "-"
        s_cls = "status-on" if status == "ON" else "status-off"
        return f"""
          <div class="ac-card">
            <div class="ac-title">Air Conditioner {i}</div>
            <div class="kv"><span>🌡️ Temperature</span><strong>{temp_txt}</strong></div>
            <div class="kv"><span>💧 Humidity</span><strong>{hum_txt}</strong></div>
            <div class="kv"><span>Set Temp</span><strong>{set_temp_txt}</strong></div>
            <div class="kv"><span>⚡ Status</span><strong class="{s_cls}">{status}</strong></div>
          </div>
        """

    st.markdown('<div class="main-title">🏢 Room 1 - AC Control System</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div class="section-header">📍 Room Layout & Status</div>', unsafe_allow_html=True)
        room_ph = st.empty()
        people_ph = st.empty()

    with col_right:
        st.markdown('<div class="section-header">🎛️ Control Panel</div>', unsafe_allow_html=True)
        control_container = st.container()
        with control_container:
            for i in range(1, 5):
                st.markdown(f'<div class="ac-control-item">', unsafe_allow_html=True)
                st.markdown(f'<div class="ac-control-title">AIR CONDITIONER {i}</div>', unsafe_allow_html=True)

                # Input box and set button
                set_temp_value = st.number_input(f"Set Temp for AC{i}", min_value=16, max_value=30, value=25, key=f"input_temp_{i}")
                if st.button("Set Temp", key=f"set_temp_btn_{i}", use_container_width=True):
                    set_firebase_data(f"AC{i}/Set_temp", set_temp_value)

                # ON/OFF buttons
                c1, c2 = st.columns(2, gap="small")
                with c1:
                    if st.button(f"🟢 ON", key=f"on_{i}", use_container_width=True):
                        set_firebase_data(f"AC{i}/status", "ON")
                with c2:
                    if st.button(f"🔴 OFF", key=f"off_{i}", use_container_width=True):
                        set_firebase_data(f"AC{i}/status", "OFF")

                st.markdown('</div>', unsafe_allow_html=True)

    time_ph = st.empty()

    while True:
        temps = {
            1: get_firebase_data("latest/values/temp_node1"),
            2: get_firebase_data("latest/values/temp_node2"),
            3: get_firebase_data("latest/values/temp_node3"),
            4: get_firebase_data("latest/values/temp_node4"),
        }
        hums = {
            1: get_firebase_data("latest/values/humid_node1"),
            2: get_firebase_data("latest/values/humid_node2"),
            3: get_firebase_data("latest/values/humid_node3"),
            4: get_firebase_data("latest/values/humid_node4"),
        }
        total_people = get_firebase_data("activity/total_people") or 0

        ac_status = {}
        set_temps = {}
        for i in range(1, 5):
            raw = get_firebase_data(f"AC{i}/status")
            ac_status[i] = "ON" if raw in [True, "ON", "on", 1, "1"] else "OFF"
            set_temps[i] = get_firebase_data(f"AC{i}/Set_temp")

        html = f"""
        <div class="room-frame">
          <div class="room-grid">
            {ac_card_html(1, temps[1], hums[1], ac_status[1], set_temps[1])}
            {ac_card_html(2, temps[2], hums[2], ac_status[2], set_temps[2])}
            {ac_card_html(3, temps[3], hums[3], ac_status[3], set_temps[3])}
            {ac_card_html(4, temps[4], hums[4], ac_status[4], set_temps[4])}
          </div>
        </div>
        """
        room_ph.markdown(html, unsafe_allow_html=True)
        people_ph.markdown(f'<div class="person-count">👥 People in room: <span>{total_people}</span></div>', unsafe_allow_html=True)

        time_ph.markdown(
            f'<div class="time-display">🔄 Last Updated: {time.strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True
        )

        time.sleep(REFRESH_SEC)



# ================== MAIN ROUTING ==================
if page == "🌡️ AC Control System":
    page_ac_control()