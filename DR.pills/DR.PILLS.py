import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta
import calendar

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Dr.Pill",
    page_icon="💊",
    layout="wide"
)

# ================= DATABASE ====================
@st.cache_resource
def init_db():
    conn = sqlite3.connect("drpill.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        age INTEGER
    )
    """)
    
    # Create medicines table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        dosage TEXT,
        med_type TEXT,
        times TEXT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        date TEXT,
        time_slot TEXT,
        taken BOOLEAN DEFAULT 0,
        timestamp DATETIME,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )
    """)
    
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# ================= DB FUNCTIONS =================
def create_user(name, email, password, age):
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, age) VALUES (?, ?, ?, ?)",
            (name, email, password, age)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(email, password):
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )
    return cursor.fetchone()


def save_medicine(user_id, name, dosage, med_type, times, notes):
    cursor.execute(
        "INSERT INTO medicines (user_id, name, dosage, med_type, times, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, dosage, med_type, times, notes)
    )
    conn.commit()


def get_user_medicines(user_id):
    cursor.execute("SELECT * FROM medicines WHERE user_id=?", (user_id,))
    return cursor.fetchall()


def get_medicines_for_date(user_id, target_date):
    cursor.execute("SELECT * FROM medicines WHERE user_id=?", (user_id,))
    medicines = cursor.fetchall()
    scheduled_meds = []
    
    for med in medicines:
        med_id, user_id_val, name, dosage, med_type, times, notes = med
        time_slots = [t.strip() for t in times.split(",") if t.strip()]
        
        if time_slots:
            scheduled_meds.append({
                'id': med_id,
                'name': name,
                'dosage': dosage,
                'times': time_slots
            })
    
    return scheduled_meds


def calculate_adherence(user_id, target_date):
    scheduled_meds = get_medicines_for_date(user_id, target_date)
    if not scheduled_meds:
        return 100
    
    total_slots = 0
    taken_slots = 0
    
    for med in scheduled_meds:
        for time_slot in med['times']:
            total_slots += 1
            cursor.execute(
                "SELECT taken FROM tracking WHERE medicine_id=? AND date=? AND time_slot=?",
                (med['id'], target_date, time_slot)
            )
            result = cursor.fetchone()
            if result and result[0]:
                taken_slots += 1
    
    if total_slots == 0:
        return 100
    
    return int((taken_slots / total_slots) * 100)


def mark_as_taken(medicine_id, target_date, time_slot):
    cursor.execute(
        "SELECT id FROM tracking WHERE medicine_id=? AND date=? AND time_slot=?",
        (medicine_id, target_date, time_slot)
    )
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute(
            "UPDATE tracking SET taken=?, timestamp=? WHERE medicine_id=? AND date=? AND time_slot=?",
            (True, datetime.now(), medicine_id, target_date, time_slot)
        )
    else:
        cursor.execute(
            "INSERT INTO tracking (medicine_id, date, time_slot, taken, timestamp) VALUES (?, ?, ?, ?, ?)",
            (medicine_id, target_date, time_slot, True, datetime.now())
        )
    conn.commit()


def get_adherence_stats(user_id):
    today = date.today().strftime("%Y-%m-%d")
    today_adherence = calculate_adherence(user_id, today)
    medicines = get_user_medicines(user_id)
    total_meds = len(medicines)
    
    # Get adherence for last 7 days
    last_7_days = []
    for i in range(7):
        d = date.today()
        target_date = (d - timedelta(days=i)).strftime("%Y-%m-%d")
        adherence = calculate_adherence(user_id, target_date)
        last_7_days.append(adherence)
    
    avg_adherence = sum(last_7_days) / len(last_7_days) if last_7_days else 100
    
    return {
        'today_adherence': today_adherence,
        'total_medicines': total_meds,
        'avg_adherence': int(avg_adherence),
        'last_7_days': last_7_days
    }

# ================= SESSION ======================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if "cal_year" not in st.session_state:
    today = date.today()
    st.session_state.cal_year = today.year
    st.session_state.cal_month = today.month

# ================= STYLES ======================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
body { background-color: #f9f4fc; }
.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}
.gradient {
    background: linear-gradient(90deg,#ff9acb,#c7a6ff,#9bc6ff);
    color: white;
}
.nav {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:14px 25px;
    border-radius:16px;
    background:white;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
}
.nav span {
    margin-left:18px;
    color:#b144ff;
    font-weight:500;
    cursor: pointer;
}
.stButton>button {
    border-radius:12px;
    padding:10px 24px;
    font-size:16px;
    background: linear-gradient(90deg, #ff9acb, #c7a6ff);
    color: white;
    border: none;
}
.stButton>button:hover {
    transform: scale(1.05);
}
input, textarea {
    border-radius:12px !important;
}
.medicine-card {
    background: linear-gradient(145deg, #ffffff, #f0f0f0);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    border-left: 5px solid #b144ff;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}
.stat-card {
    background: linear-gradient(135deg, #b144ff 0%, #9b59b6 100%);
    color: white;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(177, 68, 255, 0.3);
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE ========================
st.markdown(
    "<h2 style='text-align:center;color:#9b59b6;'>Dr.Pill – Your health journey begins here 🌸</h2>",
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# ================= FIRST SCREEN =================
if st.session_state.user is None and st.session_state.auth_mode is None:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign Up ✨", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.rerun()
    with c2:
        if st.button("Log In 🔐", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()

# ================= SIGN UP ======================
elif st.session_state.auth_mode == "signup":
    st.markdown("### Create your account 💜")
    with st.form("signup"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        age = st.text_input("Age")
        submit = st.form_submit_button("Sign Up 🚀")

        if submit:
            if name and email and password and age:
                if create_user(name, email, password, age):
                    st.success("Account created! Please log in 😊")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("Email already exists ❌")
            else:
                st.warning("Fill all fields")

    if st.button("⬅ Back"):
        st.session_state.auth_mode = None
        st.rerun()

# ================= LOGIN ========================
elif st.session_state.auth_mode == "login":
    st.markdown("### Welcome back 👋")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log In 🚀")

        if submit:
            user = login_user(email, password)
            if user:
                st.session_state.user = user
                st.session_state.page = "home"
                st.session_state.auth_mode = None
                st.rerun()
            else:
                st.error("Wrong email or password ❌")

    if st.button("⬅ Back"):
        st.session_state.auth_mode = None
        st.rerun()

# ================= HOME =========================
elif st.session_state.user and st.session_state.page == "home":

    user = st.session_state.user
    today = date.today().strftime("%A, %B %d, %Y")
    stats = get_adherence_stats(user[0])

    st.markdown("""
    <div class="nav">
        <b>💊 Dr.Pill</b>
        
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card gradient">
        <div style="display:flex;justify-content:space-between;">
            <div>
                <h3>Hi {user[1]} 👋</h3>
                <p>{today}</p>
            </div>
            <div style="text-align:right;">
                <h1>{stats['today_adherence']}%</h1>
                <small>Today's Progress</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['today_adherence']}%</h2>
            <small>Today</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['total_medicines']}</h2>
            <small>Active Meds</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['avg_adherence']}%</h2>
            <small>Weekly Avg</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button("➕ Add Medicine", use_container_width=True):
        st.session_state.page = "add_medicine"
        st.rerun()

    if c2.button("📅 View Calendar", use_container_width=True):
        st.session_state.page = "calendar"
        st.rerun()
    
    if c3.button("💊 My Medicines", use_container_width=True):
        st.session_state.page = "medicines_list"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Today's medicines
    st.markdown("### 📋 Today's Medicines")
    
    today_date = date.today().strftime("%Y-%m-%d")
    today_meds = get_medicines_for_date(user[0], today_date)
    
    if today_meds:
        for med in today_meds:
            st.markdown(f"""
            <div class="medicine-card">
                <h3>💊 {med['name']} - {med['dosage']}</h3>
                <p><strong>Times:</strong> {', '.join(med['times'])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Time slot buttons
            for time_slot in med['times']:
                cursor.execute(
                    "SELECT taken FROM tracking WHERE medicine_id=? AND date=? AND time_slot=?",
                    (med['id'], today_date, time_slot)
                )
                result = cursor.fetchone()
                taken = result[0] if result else False
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{time_slot}**")
                with col2:
                    if taken:
                        st.success("✅ Taken")
                    else:
                        if st.button(f"Take", key=f"take_{med['id']}_{time_slot}"):
                            mark_as_taken(med['id'], today_date, time_slot)
                            st.rerun()
            
            st.markdown("---")
    else:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <p style="font-size:18px;color:#a855f7;">
                No medicines scheduled for today 💜
            </p>
            <p>Add your first medicine to get started</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Log Out 🚪"):
        st.session_state.user = None
        st.session_state.auth_mode = None
        st.session_state.page = "home"
        st.rerun()

# ================= ADD MEDICINE =================
elif st.session_state.user and st.session_state.page == "add_medicine":

    st.markdown("## ➕ Add New Medicine")

    with st.form("add_medicine"):
        name = st.text_input("💊 Medicine Name")
        dosage = st.text_input("💉 Dosage")

        med_type = st.radio(
            "🏷 Medicine Type",
            ["Daily (Ongoing)", "Date Range"],
            horizontal=True
        )

        st.markdown("### ⏰ When to take?")
        times = []

        col1, col2 = st.columns(2)
        with col1:
            if st.checkbox("Morning – 08:00", key="chk_morning"):
                times.append("08:00")
            if st.checkbox("Evening – 18:00", key="chk_evening"):
                times.append("18:00")
        with col2:
            if st.checkbox("Afternoon – 12:00", key="chk_afternoon"):
                times.append("12:00")
            if st.checkbox("Night – 22:00", key="chk_night"):
                times.append("22:00")

        custom_time = st.text_input("➕ Custom Time (HH:MM)")
        if custom_time:
            times.append(custom_time)

        notes = st.text_area("📝 Notes (Optional)")

        colA, colB = st.columns(2)
        save = colA.form_submit_button("💾 Save Medicine")
        cancel = colB.form_submit_button("❌ Cancel")

        if save:
            save_medicine(
                st.session_state.user[0],
                name,
                dosage,
                med_type,
                ", ".join(times),
                notes
            )
            st.success("Medicine saved successfully 💜")
            st.session_state.page = "home"
            st.rerun()

        if cancel:
            st.session_state.page = "home"
            st.rerun()

# ================= CALENDAR =================
elif st.session_state.user and st.session_state.page == "calendar":

    user = st.session_state.user
    year = st.session_state.cal_year
    month = st.session_state.cal_month
    today_date = date.today()

    st.markdown("## 📅 Medicine Calendar")

    # Navigation
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("◀", key="cal_prev"):
            st.session_state.cal_month -= 1
            if st.session_state.cal_month == 0:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"<h2 style='text-align:center;color:#b144ff;'>"
            f"{calendar.month_name[month]} {year}</h2>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button("▶", key="cal_next"):
            st.session_state.cal_month += 1
            if st.session_state.cal_month == 13:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            st.rerun()

    # Legend
    st.markdown("""
    <div style="text-align:center; padding: 10px;">
    <span style="background:#d4edda;padding:5px 10px;border-radius:5px;border:2px solid #28a745;">🟩 100%</span>
    <span style="background:#e8f5e9;padding:5px 10px;border-radius:5px;border:2px solid #66bb6a;">🟢 80-99%</span>
    <span style="background:#fff3cd;padding:5px 10px;border-radius:5px;border:2px solid #ffc107;">🟡 60-79%</span>
    <span style="background:#f8d7da;padding:5px 10px;border-radius:5px;border:2px solid #dc3545;">🔴 &lt;60%</span>
    </div>
    """, unsafe_allow_html=True)

    # Week headers
    week_cols = st.columns(7)
    for i, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        week_cols[i].markdown(f"<p style='text-align:center;color:#b144ff;font-weight:bold;'>{day}</p>", unsafe_allow_html=True)

    # Calendar grid
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            if day_num == 0:
                cols[i].markdown(" ")
            else:
                target_date = f"{year:04d}-{month:02d}-{day_num:02d}"
                adherence = calculate_adherence(user[0], target_date)
                
                # Determine color based on adherence
                if adherence >= 100:
                    color_bg = "#d4edda"
                    color_border = "#28a745"
                elif adherence >= 80:
                    color_bg = "#e8f5e9"
                    color_border = "#66bb6a"
                elif adherence >= 60:
                    color_bg = "#fff3cd"
                    color_border = "#ffc107"
                else:
                    color_bg = "#f8d7da"
                    color_border = "#dc3545"
                
                is_today = (
                    day_num == today_date.day
                    and month == today_date.month
                    and year == today_date.year
                )
                
                today_border = "4px solid #b144ff" if is_today else "2px solid #e9ecef"
                
                # Get medicines for this day
                day_meds = get_medicines_for_date(user[0], target_date)
                
                # Build medicine list HTML
                med_list_html = ""
                if day_meds:
                    med_list_html = "<div style='font-size:11px;text-align:left;margin-top:8px;'>"
                    for med in day_meds:
                        med_list_html += f"<div style='background:rgba(255,255,255,0.8);border-radius:5px;padding:3px 6px;margin:2px 0;border-left:3px solid #b144ff;'>💊 {med['name']}</div>"
                    med_list_html += "</div>"
                
                # Check if it's a future date
                date_obj = date(year, month, day_num)
                is_future = date_obj > today_date
                
                adherence_text = f"{adherence}%" if not is_future else "Upcoming"
                
                cols[i].markdown(
                    f"""
                    <div style="background:{color_bg};border-radius:15px;padding:12px 8px;text-align:center;margin:5px;min-height:100px;border:{today_border};">
                        <strong>{day_num}</strong>
                        <div style="font-size:12px;color:#666;margin:4px 0;">{adherence_text}</div>
                        {med_list_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# ================= MEDICINES LIST =================
elif st.session_state.user and st.session_state.page == "medicines_list":

    user = st.session_state.user

    st.markdown("## 💊 My Medicines")

    medicines = get_user_medicines(user[0])

    if medicines:
        for med in medicines:
            med_id, user_id_val, name, dosage, med_type, times, notes = med
            st.markdown(f"""
            <div class="medicine-card">
                <h3>💊 {name}</h3>
                <p><strong>Dosage:</strong> {dosage}</p>
                <p><strong>Type:</strong> {med_type}</p>
                <p><strong>Times:</strong> {times}</p>
                {f"<p><strong>Notes:</strong> {notes}</p>" if notes else ""}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete", key=f"delete_{med_id}"):
                    cursor.execute("DELETE FROM medicines WHERE id=?", (med_id,))
                    cursor.execute("DELETE FROM tracking WHERE medicine_id=?", (med_id,))
                    conn.commit()
                    st.success("Medicine deleted!")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                st.markdown(" ")
            
            st.markdown("---")
    else:
        st.info("No medicines added yet. Add your first medicine to get started!")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()
