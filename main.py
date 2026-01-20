import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta
from utils import (
    get_users, get_vehicles, create_log, get_logs_as_dataframe,
    create_vehicle, update_vehicle, get_last_km, check_alerts
)

# Helper for time slots
def get_time_slots():
    slots = []
    current = datetime.strptime("07:00", "%H:%M")
    end = datetime.strptime("18:30", "%H:%M")
    while current <= end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)
    return slots

TIME_SLOTS = get_time_slots()

# Page Configuration
st.set_page_config(page_title="車両運行管理システム", layout="wide")

# Custom CSS for Accessibility
st.markdown("""
<style>
    /* Increase base font size */
    html, body, [class*="css"]  {
        font-size: 18px;
    }
    /* Increase button size and contrast */
    .stButton > button {
        width: 100%;
        height: 3em;
        font-size: 20px;
        font-weight: bold;
        background-color: #0068C9;
        color: white;
        border-radius: 10px;
    }
    .stButton > button:hover {
        background-color: #004B91;
        color: white;
    }
    /* Improve input visibility */
    .stSelectbox label, .stNumberInput label, .stDateInput label, .stTimeInput label, .stCheckbox label {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }
    /* Increase checkbox size */
    .stCheckbox {
        transform: scale(1.2);
        margin-top: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'user' not in st.session_state:
    st.session_state['user'] = None

def login_page():
    st.title("ログイン")
    users = get_users()
    user_names = {u.name: u for u in users}
    
    selected_name = st.selectbox("ユーザーを選択してください", list(user_names.keys()))
    
    if st.button("ログイン"):
        st.session_state['user'] = user_names[selected_name]
        st.rerun()

def input_page():
    st.title("運行記録入力")
    
    user = st.session_state['user']
    st.write(f"ログイン中: {user.name}")

    # Alerts
    alerts = check_alerts()
    if alerts:
        with st.expander("⚠️ アラートがあります", expanded=True):
            for alert in alerts:
                st.error(alert)

    # Input Form
    st.markdown("### 📝 運行情報を入力してください")
    with st.form("log_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            log_date = st.date_input("日付", date.today(), help="運行した日付を選択してください。")
            vehicles = get_vehicles()
            vehicle_names = {v.name: v for v in vehicles}
            selected_vehicle_name = st.selectbox("車両を選択", list(vehicle_names.keys()), help="使用する車両を選択してください。")
            selected_vehicle = vehicle_names[selected_vehicle_name]
            
            # Auto-fill start_km
            last_km = get_last_km(selected_vehicle.id)
            st.info(f"ℹ️ 前回の走行距離: {last_km} km")

        with col2:
            st.subheader("詳細情報")
            
            tab1, tab2 = st.tabs(["🛫 出発時", "🛬 帰社時"])
            
            with tab1:
                start_time_str = st.selectbox("出発時間", TIME_SLOTS, index=TIME_SLOTS.index("09:00") if "09:00" in TIME_SLOTS else 0, help="出発した時間を選択してください。")
                start_km = st.number_input("出発時メーター (km)", value=last_km, step=0.1, format="%.1f", help="出発時のオドメーター数値を入力してください。前回の距離が自動入力されています。")
                st.markdown("---")
                alcohol_check = st.checkbox("✅ アルコールチェック (出発)", help="出発前のアルコールチェックを行ったらチェックを入れてください。")
                tire_check = st.checkbox("✅ タイヤ点検", help="タイヤの空気圧や溝の確認を行ったらチェックを入れてください。")

            with tab2:
                end_time_str = st.selectbox("帰社時間", TIME_SLOTS, index=TIME_SLOTS.index("18:00") if "18:00" in TIME_SLOTS else len(TIME_SLOTS)-1, help="帰社した時間を選択してください。")
                end_km = st.number_input("帰社時メーター (km)", value=last_km, step=0.1, format="%.1f", help="帰社時のオドメーター数値を入力してください。")
                st.markdown("---")
                refuel_check = st.checkbox("⛽️ 給油しましたか？", help="給油を行った場合はチェックを入れてください。")

        submitted = st.form_submit_button("登録する")
        
        if submitted:
            # Convert time strings back to time objects
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

            if end_km < start_km:
                st.error("帰社時メーターが出発時メーターより小さいです。")
            else:
                log_data = {
                    "user_id": user.id,
                    "vehicle_id": selected_vehicle.id,
                    "date": log_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "start_km": start_km,
                    "end_km": end_km,
                    "alcohol_check": alcohol_check,
                    "tire_check": tire_check,
                    "refuel_check": refuel_check
                }
                create_log(log_data)
                
                # Update vehicle last_oil_change_km logic could be here if we tracked oil changes in logs,
                # but currently it's manual in management.
                # However, we should probably update the vehicle's mileage implicitly? 
                # The requirement says "Alert: current km > last_oil_change_km + 5000".
                # So we rely on the latest log for "current km".
                
                st.success("運行記録を保存しました。")

def dashboard_page():
    st.title("管理者ダッシュボード")
    
    st.subheader("運行記録一覧")
    df = get_logs_as_dataframe()
    
    # Filters
    st.sidebar.subheader("フィルター")
    # (Simple implementation for now, can be expanded)
    
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "CSVダウンロード",
        csv,
        "logs.csv",
        "text/csv",
        key='download-csv'
    )

def management_page():
    st.title("車両管理")
    
    vehicles = get_vehicles()
    
    # List Vehicles
    for v in vehicles:
        with st.expander(f"{v.name} ({v.plate_number})"):
            with st.form(f"edit_vehicle_{v.id}"):
                new_name = st.text_input("車両名", v.name)
                new_plate = st.text_input("ナンバー", v.plate_number)
                new_inspection = st.date_input("次回車検日", v.next_inspection_date)
                new_oil_km = st.number_input("前回オイル交換時距離 (km)", v.last_oil_change_km)
                
                if st.form_submit_button("更新"):
                    update_data = {
                        "name": new_name,
                        "plate_number": new_plate,
                        "next_inspection_date": new_inspection,
                        "last_oil_change_km": new_oil_km
                    }
                    update_vehicle(v.id, update_data)
                    st.success("更新しました。")
                    st.rerun()

    st.divider()
    st.subheader("➕ 新規車両追加")
    st.write("新しい車両をシステムに登録します。")
    with st.form("add_vehicle"):
        name = st.text_input("車両名", placeholder="例: プリウス", help="車両の名称を入力してください。")
        plate = st.text_input("ナンバー", placeholder="例: 品川 500 あ 1234", help="車両のナンバープレート情報を入力してください。")
        inspection = st.date_input("次回車検日", help="車検証に記載されている次回の車検満了日を選択してください。")
        oil_km = st.number_input("前回オイル交換時距離 (km)", value=0.0, help="最後にオイル交換をした時の走行距離を入力してください。不明な場合は0でも構いません。")
        
        if st.form_submit_button("追加する"):
            if name and plate:
                create_vehicle({
                    "name": name,
                    "plate_number": plate,
                    "next_inspection_date": inspection,
                    "last_oil_change_km": oil_km
                })
                st.success("追加しました。")
                st.rerun()
            else:
                st.error("車両名とナンバーは必須です。")

def main():
    if st.session_state['user'] is None:
        login_page()
    else:
        user = st.session_state['user']
        
        # Sidebar Navigation
        st.sidebar.title("メニュー")
        st.sidebar.write(f"ユーザー: {user.name}")
        
        page = st.sidebar.radio("画面切替", ["運行記録入力", "ダッシュボード", "車両管理"])
        
        if st.sidebar.button("ログアウト"):
            st.session_state['user'] = None
            st.rerun()

        if page == "運行記録入力":
            input_page()
        elif page == "ダッシュボード":
            if user.role == 'admin':
                dashboard_page()
            else:
                st.warning("このページは管理者専用です。")
        elif page == "車両管理":
            if user.role == 'admin':
                management_page()
            else:
                st.warning("このページは管理者専用です。")

if __name__ == "__main__":
    main()
