import streamlit as st
from datetime import date, datetime, timedelta, time
import calendar
import json
import os
import plotly.graph_objects as go
import sqlite3

st.set_page_config(
    page_title="Dr.Pill - Medicine Tracker",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 50%, #e1f5fe 100%); }
    
    .main {
        background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 50%, #e1f5fe 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #9c27b0;
    }
    
    h1 {
        font-size: 3rem !important;
        text-align: center;
        color: #e91e63;
    }
    
    h2 {
        font-size: 2.5rem !important;
    }
    
    h3 {
        font-size: 2rem !important;
    }
    
    p, div, label, span {
        font-size: 1.3rem !important;
    }
    
    .stButton > button {
        font-size: 1.5rem !important;
        padding: 1rem 2rem !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        background: linear-gradient(90deg, #ff9acb, #c7a6ff, #9bc6ff);
        color: white;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stTimeInput > div > div > input {
        font-size: 1.3rem !important;
        padding: 0.8rem !important;
        border-radius: 15px !important;
    }
    
    input, textarea {
        border-radius: 15px !important;
    }
    
    .medicine-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 4px solid;
    }
    
    .card-taken {
        border-color: #81c784;
        background-color: #e8f5e9;
    }
    
    .card-missed {
        border-color: #e57373;
        background-color: #ffebee;
    }
    
    .card-upcoming {
        border-color: #ffd54f;
        background-color: #fff9e1;
    }
    
    .card-scheduled {
        border-color: #64b5f6;
        background-color: #e3f2fd;
    }
    
    .mascot-container {
        text-align: center;
        padding: 2rem;
        background: white;
        border-radius: 30px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 4px solid #f48fb1;
        margin: 2rem 0;
    }
    
    .mascot {
        font-size: 8rem;
        animation: bounce 2s infinite;
    }
    
    .mascot-sad {
        font-size: 8rem;
        animation: sway 2s infinite;
    }
    
    .mascot-urgent {
        font-size: 8rem;
        animation: shake 0.5s infinite;
    }
    
    .mascot-sleepy {
        font-size: 8rem;
        animation: rotate 3s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes sway {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-5deg); }
        75% { transform: rotate(5deg); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    @keyframes rotate {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(10deg); }
    }
    
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
    
    .stat-card {
        background: linear-gradient(135deg, #b144ff 0%, #9b59b6 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(177, 68, 255, 0.3);
    }
    
    .shop-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 3px solid #e1bee7;
        text-align: center;
    }
    
    .shop-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    
    .notification-badge {
        background: #f44336;
        color: white;
        border-radius: 50%;
        padding: 0.3rem 0.6rem;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    .calendar-day {
        background: white;
        border-radius: 15px;
        padding: 12px 8px;
        text-align: center;
        margin: 5px;
        min-height: 120px;
        border: 2px solid #e9ecef;
        transition: all 0.2s;
    }
    
    .calendar-day:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .calendar-day.today {
        border: 4px solid #b144ff;
        box-shadow: 0 0 10px rgba(177, 68, 255, 0.3);
    }
    
    .day-number {
        font-size: 1.3rem;
        font-weight: bold;
        color: #b144ff;
        margin-bottom: 5px;
    }
    
    .adherence-badge {
        font-size: 0.9rem;
        padding: 4px 8px;
        border-radius: 10px;
        margin: 5px 0;
        font-weight: bold;
    }
    
    .medicine-list {
        font-size: 0.8rem;
        text-align: left;
        margin-top: 8px;
    }
    
    .medicine-item {
        background: rgba(255,255,255,0.9);
        border-radius: 5px;
        padding: 3px 6px;
        margin: 2px 0;
        border-left: 3px solid #b144ff;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "drpill.db"

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        age INTEGER,
        conditions TEXT,
        phone TEXT,
        email_address TEXT
    )
    """)
    
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        dosage TEXT,
        med_type TEXT,
        times TEXT,
        time_labels TEXT,
        notes TEXT,
        start_date TEXT,
        end_date TEXT,
        paused BOOLEAN DEFAULT 0,
        color TEXT DEFAULT '#9c27b0',
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    
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
    
   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        reminders_enabled BOOLEAN DEFAULT 1,
        reminder_advance_minutes INTEGER DEFAULT 30,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()


init_database()


def create_user(name, email, password, age, conditions="", phone="", email_address=""):
    """Create a new user in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, age, conditions, phone, email_address) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, password, age, conditions, phone, email_address)
        )
        
        user_id = cursor.lastrowid
        
        # Create default settings for new user
        cursor.execute(
            "INSERT INTO settings (user_id, reminders_enabled, reminder_advance_minutes) VALUES (?, 1, 30)",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(email, password):
    """Authenticate user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return (user['id'], user['name'], user['email'], user['password'],
               user['age'], user['conditions'], user['phone'], user['email_address'])
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return (user['id'], user['name'], user['email'], user['password'],
               user['age'], user['conditions'], user['phone'], user['email_address'])
    return None

def update_user(user_id, name, age, conditions, phone, email_address):
    """Update user information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET name=?, age=?, conditions=?, phone=?, email_address=? WHERE id=?",
        (name, age, conditions, phone, email_address, user_id)
    )
    
    conn.commit()
    conn.close()

def save_medicine(user_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, color):
    """Save a new medicine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO medicines (user_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, color) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, color)
    )
    
    med_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return med_id

def get_user_medicines(user_id):
    """Get all medicines for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM medicines WHERE user_id=?", (user_id,))
    medicines = cursor.fetchall()
    conn.close()
    
    result = []
    for med in medicines:
        result.append((
            med['id'], med['user_id'], med['name'], med['dosage'],
            med['med_type'], med['times'], med['time_labels'], med['notes'],
            med['start_date'], med['end_date'], med['paused'], med['color']
        ))
    return result

def get_medicine_by_id(med_id):
    """Get medicine by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM medicines WHERE id=?", (med_id,))
    med = cursor.fetchone()
    conn.close()
    
    if med:
        return (
            med['id'], med['user_id'], med['name'], med['dosage'],
            med['med_type'], med['times'], med['time_labels'], med['notes'],
            med['start_date'], med['end_date'], med['paused'], med['color']
        )
    return None

def update_medicine(med_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, color):
    """Update medicine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE medicines SET name=?, dosage=?, med_type=?, times=?, time_labels=?, notes=?, start_date=?, end_date=?, color=? WHERE id=?",
        (name, dosage, med_type, times, time_labels, notes, start_date, end_date, color, med_id)
    )
    
    conn.commit()
    conn.close()

def delete_medicine(med_id):
    """Delete medicine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    cursor.execute("DELETE FROM tracking WHERE medicine_id=?", (med_id,))
    
    conn.commit()
    conn.close()

def toggle_medicine_pause(med_id):
    """Toggle medicine pause status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE medicines SET paused = NOT paused WHERE id=?", (med_id,))
    
    conn.commit()
    conn.close()

def get_medicines_for_date(user_id, target_date):
    """Get medicines scheduled for a specific date"""
    medicines = get_user_medicines(user_id)
    scheduled_meds = []
    
    for med in medicines:
        med_id, user_id_val, name, dosage, med_type, times_str, time_labels_str, notes, start_date, end_date, paused, color = med
        time_slots = [t.strip() for t in times_str.split(",") if t.strip()]
        time_labels = [l.strip() for l in time_labels_str.split(",") if l.strip()] if time_labels_str else [""] * len(time_slots)
        
        if paused:
            continue
        
        if med_type == 'Daily (Ongoing)' or (med_type == 'Date Range' and start_date and end_date and start_date <= target_date <= end_date):
            if time_slots:
                scheduled_meds.append({
                    'id': med_id,
                    'name': name,
                    'dosage': dosage,
                    'times': time_slots,
                    'time_labels': time_labels,
                    'notes': notes,
                    'paused': paused,
                    'color': color
                })
    
    return scheduled_meds

def toggle_intake(medicine_id, target_date, time_slot):
    """Toggle medicine intake"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, taken FROM tracking WHERE medicine_id=? AND date=? AND time_slot=?",
        (medicine_id, target_date, time_slot)
    )
    result = cursor.fetchone()
    
    if result:
        track_id = result['id']
        taken = result['taken']
        cursor.execute(
            "UPDATE tracking SET taken=?, timestamp=? WHERE id=?",
            (not taken, datetime.now() if not taken else None, track_id)
        )
    else:
        cursor.execute(
            "INSERT INTO tracking (medicine_id, date, time_slot, taken, timestamp) VALUES (?, ?, ?, ?, ?)",
            (medicine_id, target_date, time_slot, True, datetime.now())
        )
    
    conn.commit()
    conn.close()

def get_intake_status(medicine_id, target_date, time_slot):
    """Check if medicine was taken"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT taken FROM tracking WHERE medicine_id=? AND date=? AND time_slot=?",
        (medicine_id, target_date, time_slot)
    )
    result = cursor.fetchone()
    conn.close()
    
    return result['taken'] if result else False

def get_tracking_records_for_medicine(med_id):
    """Get all tracking records for a specific medicine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tracking WHERE medicine_id=?", (med_id,))
    records = cursor.fetchall()
    conn.close()
    
    return records

def get_total_taken_count(med_id):
    """Get total number of times a medicine was taken"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM tracking WHERE medicine_id=? AND taken=1", (med_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['count'] if result else 0

def calculate_adherence(user_id, target_date):
    """Calculate adherence percentage"""
    scheduled_meds = get_medicines_for_date(user_id, target_date)
    if not scheduled_meds:
        return 100
    
    total_slots = 0
    taken_slots = 0
    
    for med in scheduled_meds:
        for time_slot in med['times']:
            total_slots += 1
            if get_intake_status(med['id'], target_date, time_slot):
                taken_slots += 1
    
    if total_slots == 0:
        return 100
    
    return int((taken_slots / total_slots) * 100)

def calculate_weekly_adherence(user_id):
    """Calculate weekly adherence"""
    weekly_data = {}
    for i in range(7):
        d = date.today()
        target_date = (d - timedelta(days=6-i)).strftime('%Y-%m-%d')
        day_name = (d - timedelta(days=6-i)).strftime('%a')
        adherence = calculate_adherence(user_id, target_date)
        weekly_data[day_name] = adherence
    
    return weekly_data

def get_adherence_stats(user_id):
    """Get adherence statistics"""
    today = date.today().strftime("%Y-%m-%d")
    today_adherence = calculate_adherence(user_id, today)
    medicines = get_user_medicines(user_id)
    total_meds = len(medicines)
    active_meds = len([m for m in medicines if not m[10]])
    
    
    last_7_days = []
    for i in range(7):
        d = date.today()
        target_date = (d - timedelta(days=i)).strftime("%Y-%m-%d")
        adherence = calculate_adherence(user_id, target_date)
        last_7_days.append(adherence)
    
    avg_adherence = sum(last_7_days) / len(last_7_days) if last_7_days else 100
    
    
    total_scheduled_30d = 0
    total_taken_30d = 0
    for i in range(30):
        check_date = (date.today() - timedelta(days=i)).strftime('%Y-%m-%d')
        meds_for_date = get_medicines_for_date(user_id, check_date)
        for med in meds_for_date:
            for time_slot in med['times']:
                total_scheduled_30d += 1
                if get_intake_status(med['id'], check_date, time_slot):
                    total_taken_30d += 1
    
    overall_adherence = int((total_taken_30d / total_scheduled_30d * 100)) if total_scheduled_30d > 0 else 0
    
    return {
        'today_adherence': today_adherence,
        'total_medicines': total_meds,
        'active_medicines': active_meds,
        'avg_adherence': int(avg_adherence),
        'last_7_days': last_7_days,
        'overall_adherence': overall_adherence
    }

def get_settings(user_id):
    """Get user settings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM settings WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'reminders_enabled': result['reminders_enabled'],
            'reminder_advance_minutes': result['reminder_advance_minutes']
        }
    else:
        # Create default settings
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO settings (user_id, reminders_enabled, reminder_advance_minutes) VALUES (?, 1, 30)",
            (user_id,)
        )
        conn.commit()
        conn.close()
        return {'reminders_enabled': True, 'reminder_advance_minutes': 30}

def update_settings(user_id, reminders_enabled, reminder_advance_minutes):
    """Update user settings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE settings SET reminders_enabled=?, reminder_advance_minutes=? WHERE user_id=?",
        (reminders_enabled, reminder_advance_minutes, user_id)
    )
    
    conn.commit()
    conn.close()

def get_upcoming_reminders(user_id):
    """Get upcoming reminders"""
    current_time = datetime.now()
    today = current_time.strftime('%Y-%m-%d')
    today_medicines = get_medicines_for_date(user_id, today)
    settings = get_settings(user_id)
    
    upcoming = []
    for medicine in today_medicines:
        for time_slot in medicine['times']:
            is_taken = get_intake_status(medicine['id'], today, time_slot)
            
            if not is_taken:
                time_parts = time_slot.split(':')
                medicine_time = current_time.replace(
                    hour=int(time_parts[0]), 
                    minute=int(time_parts[1]), 
                    second=0, 
                    microsecond=0
                )
                
                if medicine_time > current_time:
                    time_diff = (medicine_time - current_time).total_seconds() / 60
                    upcoming.append({
                        'medicine': medicine,
                        'time': time_slot,
                        'minutes_until': int(time_diff)
                    })
    
    return sorted(upcoming, key=lambda x: x['minutes_until'])

def get_all_tracking_records(user_id):
    """Get all tracking records for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.* FROM tracking t
        JOIN medicines m ON t.medicine_id = m.id
        WHERE m.user_id = ?
    """, (user_id,))
    
    records = cursor.fetchall()
    conn.close()
    
    return records

def clear_tracking_for_medicines(user_id):
    """Clear all tracking records for user's medicines"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM tracking
        WHERE medicine_id IN (SELECT id FROM medicines WHERE user_id = ?)
    """, (user_id,))
    
    conn.commit()
    conn.close()

def export_user_data(user_id):
    """Export user data as JSON"""
    user = get_user_by_id(user_id)
    medicines = get_user_medicines(user_id)
    
    tracking_records = get_all_tracking_records(user_id)
    
    data = {
        'user': {
            'name': user[1],
            'email': user[2],
            'age': user[4],
            'conditions': user[5],
            'phone': user[6],
            'email_address': user[7]
        },
        'medicines': [
            {
                'id': m[0],
                'name': m[2],
                'dosage': m[3],
                'med_type': m[4],
                'times': m[5],
                'time_labels': m[6],
                'notes': m[7],
                'start_date': m[8],
                'end_date': m[9],
                'paused': m[10],
                'color': m[11]
            }
            for m in medicines
        ],
        'tracking': [
            {
                'id': t['id'],
                'medicine_id': t['medicine_id'],
                'date': t['date'],
                'time_slot': t['time_slot'],
                'taken': t['taken'],
                'timestamp': t['timestamp']
            }
            for t in tracking_records
        ]
    }
    return json.dumps(data, indent=2)

def delete_user_account(user_id):
    """Delete user account and all associated data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    cursor.execute("DELETE FROM tracking WHERE medicine_id IN (SELECT id FROM medicines WHERE user_id=?)", (user_id,))
    
    
    cursor.execute("DELETE FROM medicines WHERE user_id=?", (user_id,))
    
  
    cursor.execute("DELETE FROM settings WHERE user_id=?", (user_id,))
    

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    
    conn.commit()
    conn.close()


def get_mascot_path(emotion):
    """Get mascot image path with fallback"""
    
    emotion_file_map = {
        'happy': 'waving pill',
        'sad': 'sad pill',
        'urgent': 'Angry pill',
        'sleepy': 'Doubt pill'
    }
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_paths = [
        f'DR.pills/mascots/{emotion_file_map[emotion]}.png',
        f'mascots/{emotion_file_map[emotion]}.png',
        f'dr.pill/mascots/{emotion_file_map[emotion]}.png',
    ]
    
    for path in possible_paths:
        abs_path = os.path.join(script_dir, path)
        if os.path.exists(abs_path):
            return abs_path
    
    return None

def get_mascot_css_class(emotion):
    """Get CSS class for mascot animation"""
    css_classes = {
        'happy': 'mascot',
        'sad': 'mascot-sad',
        'urgent': 'mascot-urgent',
        'sleepy': 'mascot-sleepy'
    }
    return css_classes.get(emotion, 'mascot')

def render_pill_mascot(emotion, message, missed_list=None):
    """Render mascot with emoji fallback"""
    
    img_path = get_mascot_path(emotion)
    css_class = get_mascot_css_class(emotion)
    
    if img_path and os.path.exists(img_path):
        st.markdown(f"""
        <div class="mascot-container">
            <div class="{css_class}">
                <img src="file://{img_path}" style="width:160px; border-radius: 10px;">
            </div>
            <h2 style="color: #9c27b0; margin-top: 1rem;">{message}</h2>
        </div>
        """, unsafe_allow_html=True)
    else:
        emoji_map = {
            'happy': '💊😊',
            'sad': '💊😢',
            'urgent': '💊😰',
            'sleepy': '💊😴'
        }
        fallback_emoji = emoji_map.get(emotion, '💊')
        
        st.markdown(f"""
        <div class="mascot-container">
            <div class="{css_class}" style="font-size: 8rem;">
                {fallback_emoji}
            </div>
            <h2 style="color: #9c27b0; margin-top: 1rem;">{message}</h2>
        </div>
        """, unsafe_allow_html=True)

    if missed_list:
        st.markdown("### 📋 Missed Today:")
        for med in missed_list:
            st.markdown(f"""
            <div class="medicine-card card-missed">
                <p>💊 <strong>{med['name']}</strong></p>
                <p>🕐 Scheduled for {med['time']}</p>
            </div>
            """, unsafe_allow_html=True)


def get_medicine_status(medicine, time_slot, current_time, user_id):
    """Get medicine status"""
    today = datetime.now().strftime('%Y-%m-%d')
    settings = get_settings(user_id)
    
    if get_intake_status(medicine['id'], today, time_slot):
        return 'taken'
    
    current_minutes = current_time.hour * 60 + current_time.minute
    time_parts = time_slot.split(':')
    medicine_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
    
    if current_minutes > medicine_minutes:
        return 'missed'
    elif current_minutes >= medicine_minutes - settings['reminder_advance_minutes']:
        return 'upcoming'
    
    return 'scheduled'


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

if "edit_medicine_id" not in st.session_state:
    st.session_state.edit_medicine_id = None

if "cart" not in st.session_state:
    st.session_state.cart = []

if "orders" not in st.session_state:
    st.session_state.orders = []

if "view_day_details" not in st.session_state:
    st.session_state.view_day_details = False

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None


st.markdown(
    "<h2 style='text-align:center;color:#9b59b6;'>Dr.Pill – Your health journey begins here 🌸</h2>",
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)


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

elif st.session_state.auth_mode == "signup":
    st.markdown("### Create your account 💜")
    with st.form("signup"):
        name = st.text_input("Name 👤")
        email = st.text_input("Email 📧")
        password = st.text_input("Password 🔒", type="password")
        age = st.number_input("Age 🎂", min_value=1, max_value=120, value=25)
        conditions = st.text_input("Health Conditions (Optional) 🏥", placeholder="e.g., High BP, Diabetes")
        phone = st.text_input("Phone Number (Optional) 📱", placeholder="+1 (555) 123-4567")
        email_address = st.text_input("Email Address (Optional) 📧", placeholder="your.email@example.com")
        
        submit = st.form_submit_button("Sign Up 🚀")

        if submit:
            if name and email and password and age:
                if create_user(name, email, password, age, conditions, phone, email_address):
                    st.success("Account created! Please log in 😊")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("Email already exists ❌")
            else:
                st.warning("Fill all required fields")

    if st.button("⬅ Back"):
        st.session_state.auth_mode = None
        st.rerun()

elif st.session_state.auth_mode == "login":
    st.markdown("### Welcome back 👋")
    with st.form("login"):
        email = st.text_input("Email 📧")
        password = st.text_input("Password 🔒", type="password")
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


elif st.session_state.user and st.session_state.page == "home":
    user = st.session_state.user
    user_id = user[0]
    today_date = date.today()
    current_time = datetime.now()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    
    date_str = f"{days[today_date.weekday()]}, {months[today_date.month-1]} {today_date.day}, {today_date.year}"
    time_str = current_time.strftime("%I:%M %p")
    today_str = today_date.strftime("%Y-%m-%d")
    
    stats = get_adherence_stats(user_id)
    today_medicines = get_medicines_for_date(user_id, today_str)
    settings = get_settings(user_id)
    
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"# Hi {user[1]}! 👋")
        st.markdown(f"### {date_str}")
        st.markdown(f"#### 🕐 {time_str}")
    with col2:
        st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{stats['today_adherence']}%</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Today's Progress</p>", unsafe_allow_html=True)
    with col3:
        upcoming = get_upcoming_reminders(user_id)
        upcoming_count = len([r for r in upcoming if r['minutes_until'] <= settings['reminder_advance_minutes']])
        st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{upcoming_count}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>⏰ Upcoming</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get mascot state
    def get_mascot_state():
        current_hour = current_time.hour
        is_evening = current_hour >= 20
        
        missed_count = 0
        upcoming_count = 0
        total_scheduled = 0
        taken_count = 0
        missed_medicines = []
        
        for medicine in today_medicines:
            for time_slot in medicine['times']:
                total_scheduled += 1
                status = get_medicine_status(medicine, time_slot, current_time, user_id)
                
                if status == 'taken':
                    taken_count += 1
                elif status == 'missed':
                    missed_count += 1
                    missed_medicines.append({'name': medicine['name'], 'time': time_slot})
                elif status == 'upcoming':
                    upcoming_count += 1
        
       
        if is_evening:
            if taken_count == total_scheduled and total_scheduled > 0:
                return {
                    'emotion': 'happy',
                    'message': "Perfect day! You took all your medicines! Sweet dreams! 🌙✨",
                    'missed_list': None
                }
            else:
                return {
                    'emotion': 'sleepy',
                    'message': f"Time for bed! You missed {missed_count} medicine{'s' if missed_count != 1 else ''} today. Let's do better tomorrow! Good night! 💤",
                    'missed_list': missed_medicines if missed_medicines else None
                }
        
        
        if missed_count > 0:
            return {
                'emotion': 'sad',
                'message': f"Oh no! You have {missed_count} missed medicine{'s' if missed_count != 1 else ''}. Please check if you can still take them! 😢",
                'missed_list': None
            }
        
        if upcoming_count > 0:
            return {
                'emotion': 'urgent',
                'message': f"⚡ Time to take your medicine NOW! You have {upcoming_count} upcoming dose{'s' if upcoming_count != 1 else ''}! ⚡",
                'missed_list': None
            }
        
        if taken_count == total_scheduled and total_scheduled > 0:
            return {
                'emotion': 'happy',
                'message': "Yay! All medicines taken so far! Keep up the great work! 🎉💪",
                'missed_list': None
            }
        
        return None
    
    mascot_state = get_mascot_state()
    
   
    if mascot_state and today_medicines:
        render_pill_mascot(
            mascot_state['emotion'],
            mascot_state['message'],
            mascot_state['missed_list']
        )
        st.markdown("---")
    
    
    if settings['reminders_enabled']:
        upcoming = get_upcoming_reminders(user_id)
        if upcoming and upcoming[0]['minutes_until'] <= settings['reminder_advance_minutes']:
            st.markdown("## 🔔 Upcoming Reminders")
            for reminder in upcoming[:3]:  # Show next 3
                if reminder['minutes_until'] <= settings['reminder_advance_minutes']:
                    hours = reminder['minutes_until'] // 60
                    minutes = reminder['minutes_until'] % 60
                    time_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    
                    st.markdown(f"""
                    <div class="medicine-card card-upcoming">
                        <h3>⏰ {reminder['medicine']['name']}</h3>
                        <p>💊 {reminder['medicine']['dosage']} • 🕐 {reminder['time']}</p>
                        <p>📍 In {time_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
    
   
    st.markdown("## 📅 Today's Medicines")
    
    if not today_medicines:
        st.info("No medicines scheduled for today! Add your first medicine to get started 💜")
        if st.button("➕ Add Medicine", use_container_width=True):
            st.session_state.page = "add_medicine"
            st.rerun()
    else:
        for medicine in today_medicines:
            for idx, time_slot in enumerate(medicine['times']):
                status = get_medicine_status(medicine, time_slot, current_time, user_id)
                
                status_colors = {
                    'taken': ('✅', 'card-taken'),
                    'missed': ('❌', 'card-missed'),
                    'upcoming': ('⏰', 'card-upcoming'),
                    'scheduled': ('📋', 'card-scheduled')
                }
                
                emoji, card_class = status_colors[status]
                time_label = medicine['time_labels'][idx] if idx < len(medicine['time_labels']) else ''
                
                is_taken = get_intake_status(medicine['id'], today_str, time_slot)
                
                col1, col2 = st.columns([8, 2])
                
                with col1:
                    notes_html = f"<p>📝 {medicine['notes']}</p>" if medicine['notes'] else ''
                    st.markdown(f"""
                    <div class="medicine-card {card_class}">
                        <h3>{emoji} {medicine['name']}</h3>
                        <p>💊 {medicine['dosage']} • 🕐 {time_slot} • {time_label}</p>
                        {notes_html}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✓ Taken" if not is_taken else "↶ Undo", 
                               key=f"toggle_{medicine['id']}_{time_slot}",
                               use_container_width=True):
                        toggle_intake(medicine['id'], today_str, time_slot)
                        st.rerun()
    
    
    if stats['today_adherence'] >= 80:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff9c4 0%, #ffcc80 100%); 
                    border-radius: 30px; padding: 2rem; text-align: center; 
                    border: 4px solid #ffd54f; margin-top: 2rem;">
            <h2>🏆 Amazing Work! 🎉</h2>
            <p style="font-size: 1.5rem;">You're doing fantastic! Keep it up! 💪✨</p>
        </div>
        """, unsafe_allow_html=True)


elif st.session_state.user and st.session_state.page == "profile":
    user = st.session_state.user
    user_id = user[0]
    
    st.markdown("# 👤 Profile Settings")
    st.markdown("### Edit your profile information")
    st.markdown("---")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Your Name 👤", value=user[1])
            age = st.number_input("Your Age 🎂", min_value=1, max_value=120, value=user[4])
            phone = st.text_input("Phone Number 📱", value=user[6] if user[6] else "")
        
        with col2:
            email_address = st.text_input("Email Address 📧", value=user[7] if user[7] else "")
            conditions = st.text_input("Health Conditions (Optional) 🏥", 
                                      value=user[5] if user[5] else "",
                                      placeholder="e.g., High BP, Diabetes, etc.")
        
        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
        
        if submitted:
            if name:
                update_user(user_id, name, age, conditions, phone, email_address)
                st.session_state.user = get_user_by_id(user_id)
                st.success(f"✅ Profile saved! 💕")
                st.balloons()
            else:
                st.error("Please enter your name! 😊")
    
    st.markdown("---")
    st.markdown("## 📊 Your Profile Summary")
    
    stats = get_adherence_stats(user_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Age", f"{user[4]} years")
    with col2:
        st.metric("Total Medicines", stats['total_medicines'])
    with col3:
        st.metric("Active Medicines", stats['active_medicines'])



elif st.session_state.user and st.session_state.page == "add_medicine":
    user_id = st.session_state.user[0]
    
    st.markdown("# ➕ Add New Medicine")
    st.markdown("---")
    
    with st.form("add_medicine_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_name = st.text_input("Medicine Name 💊", placeholder="e.g., Aspirin, Metformin")
            dosage = st.text_input("Dosage 💉", placeholder="e.g., 50mg, 2 tablets")
            medicine_type = st.radio("Medicine Type 📋", ["Daily (Ongoing)", "Date Range"])
        
        with col2:
            color = st.color_picker("Medicine Color 🎨", "#9c27b0")
            notes = st.text_area("Notes (Optional) 📝", placeholder="Any special instructions...", height=100)
        
        start_date = None
        end_date = None
        if medicine_type == "Date Range":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date 📅", value=date.today())
            with col2:
                end_date = st.date_input("End Date 📅", value=date.today() + timedelta(days=7))
        
        st.markdown("### ⏰ When do you take this medicine?")
        num_times = st.number_input("How many times per day?", min_value=1, max_value=10, value=2)
        
        times = []
        time_labels = []
        
        cols = st.columns(2)
        for i in range(int(num_times)):
            with cols[i % 2]:
                st.markdown(f"**Dose {i+1}**")
                time_val = st.time_input(f"Time", key=f"time_{i}", value=time(8 + i*6, 0))
                times.append(time_val.strftime("%H:%M"))
                label = st.text_input(f"Label", placeholder="e.g., After breakfast", key=f"label_{i}")
                time_labels.append(label)
                st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Add Medicine", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            if medicine_name and dosage:
                save_medicine(
                    user_id,
                    medicine_name,
                    dosage,
                    medicine_type,
                    ", ".join(times),
                    ", ".join(time_labels),
                    notes,
                    start_date.strftime('%Y-%m-%d') if start_date else None,
                    end_date.strftime('%Y-%m-%d') if end_date else None,
                    color
                )
                st.success(f"✅ {medicine_name} added successfully! 🎉")
                st.balloons()
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Please fill in medicine name and dosage! 😊")
        
        if cancel:
            st.session_state.page = "home"
            st.rerun()


elif st.session_state.user and st.session_state.page == "medicines_list":
    user_id = st.session_state.user[0]
    
    st.markdown("# 💊 All Medicines")
    st.markdown("### Manage your medications")
    st.markdown("---")
    
   
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Filter by Type", ["All", "Daily (Ongoing)", "Date Range"])
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All", "Active", "Paused"])
    with col3:
        search = st.text_input("🔍 Search", placeholder="Search medicine name...")
    
   
    medicines = get_user_medicines(user_id)
    filtered_meds = medicines
    
    if filter_type == "Daily (Ongoing)":
        filtered_meds = [m for m in filtered_meds if m[4] == 'Daily (Ongoing)']
    elif filter_type == "Date Range":
        filtered_meds = [m for m in filtered_meds if m[4] == 'Date Range']
    
    if filter_status == "Active":
        filtered_meds = [m for m in filtered_meds if not m[10]]
    elif filter_status == "Paused":
        filtered_meds = [m for m in filtered_meds if m[10]]
    
    if search:
        filtered_meds = [m for m in filtered_meds if search.lower() in m[2].lower()]
    
    st.markdown(f"**Showing {len(filtered_meds)} medicine(s)**")
    st.markdown("---")
    
    if not filtered_meds:
        st.info("No medicines found! Adjust your filters or add a new medicine 💜")
        if st.button("➕ Add New Medicine", use_container_width=True):
            st.session_state.page = "add_medicine"
            st.rerun()
    else:
        for med in filtered_meds:
            med_id, user_id_val, name, dosage, med_type, times_str, time_labels_str, notes, start_date, end_date, paused, color = med
            
            status_text = "⏸️ Paused" if paused else "✅ Active"
            type_text = f"📅 {med_type}"
            if med_type == "Date Range":
                type_text = f"📆 {start_date} to {end_date}"
            
            time_slots = [t.strip() for t in times_str.split(",") if t.strip()]
            time_labels_list = [l.strip() for l in time_labels_str.split(",") if l.strip()] if time_labels_str else [""] * len(time_slots)
            times_display = ", ".join([f"{t} ({l})" for t, l in zip(time_slots, time_labels_list)])
            
            with st.expander(f"💊 {name} - {status_text}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Dosage:** {dosage}")
                    st.markdown(f"**Type:** {type_text}")
                    st.markdown(f"**Times:** {times_display}")
                    if notes:
                        st.markdown(f"**Notes:** {notes}")
                    st.markdown(f"**Color:** <span style='display:inline-block; width:30px; height:30px; background-color:{color}; border-radius:50%; vertical-align:middle;'></span>", unsafe_allow_html=True)
                
                with col2:
                
                    total_intakes = get_total_taken_count(med_id)
                    st.metric("Total Taken", total_intakes)
                
               
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("⏸️ Pause" if not paused else "▶️ Resume", 
                               key=f"pause_{med_id}",
                               use_container_width=True):
                        toggle_medicine_pause(med_id)
                        st.success(f"{'Paused' if not paused else 'Resumed'} {name}")
                        st.rerun()
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_btn_{med_id}", use_container_width=True):
                        st.session_state.edit_medicine_id = med_id
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{med_id}", use_container_width=True):
                        delete_medicine(med_id)
                        st.success(f"Deleted {name}")
                        st.rerun()
    
   
    if st.session_state.edit_medicine_id:
        med = get_medicine_by_id(st.session_state.edit_medicine_id)
        
        if med:
            med_id, user_id_val, name, dosage, med_type, times_str, time_labels_str, notes, start_date, end_date, paused, color = med
            
            st.markdown("---")
            st.markdown(f"## ✏️ Editing: {name}")
            
            with st.form("edit_medicine_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Medicine Name 💊", value=name)
                    new_dosage = st.text_input("Dosage 💉", value=dosage)
                    new_type = st.radio("Medicine Type 📋", 
                                       ["Daily (Ongoing)", "Date Range"],
                                       index=0 if med_type == 'Daily (Ongoing)' else 1)
                
                with col2:
                    new_color = st.color_picker("Medicine Color 🎨", value=color)
                    new_notes = st.text_area("Notes 📝", value=notes, height=100)
                
                new_start_date = None
                new_end_date = None
                if new_type == "Date Range":
                    col1, col2 = st.columns(2)
                    with col1:
                        new_start_date = st.date_input("Start Date 📅", 
                                                      value=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else date.today())
                    with col2:
                        new_end_date = st.date_input("End Date 📅",
                                                    value=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.today() + timedelta(days=7))
                
                st.markdown("### ⏰ Times")
                num_times = st.number_input("How many times per day?", min_value=1, max_value=10, value=len(times_str.split(",")))
                
                new_times = []
                new_time_labels = []
                existing_times = [t.strip() for t in times_str.split(",") if t.strip()]
                existing_labels = [l.strip() for l in time_labels_str.split(",") if l.strip()] if time_labels_str else []
                
                cols = st.columns(2)
                for i in range(int(num_times)):
                    with cols[i % 2]:
                        st.markdown(f"**Dose {i+1}**")
                        
                        if i < len(existing_times):
                            existing_time = datetime.strptime(existing_times[i], "%H:%M").time()
                            existing_label = existing_labels[i] if i < len(existing_labels) else ""
                        else:
                            existing_time = time(8 + i*6, 0)
                            existing_label = ""
                        
                        time_val = st.time_input(f"Time", key=f"edit_time_{i}", value=existing_time)
                        new_times.append(time_val.strftime("%H:%M"))
                        label = st.text_input(f"Label", key=f"edit_label_{i}", value=existing_label)
                        new_time_labels.append(label)
                        st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        update_medicine(
                            med_id,
                            new_name,
                            new_dosage,
                            new_type,
                            ", ".join(new_times),
                            ", ".join(new_time_labels),
                            new_notes,
                            new_start_date.strftime('%Y-%m-%d') if new_start_date else None,
                            new_end_date.strftime('%Y-%m-%d') if new_end_date else None,
                            new_color
                        )
                        st.session_state.edit_medicine_id = None
                        st.success(f"✅ {new_name} updated successfully!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.edit_medicine_id = None
                        st.rerun()


elif st.session_state.user and st.session_state.page == "calendar":
    user = st.session_state.user
    user_id = user[0]
    year = st.session_state.cal_year
    month = st.session_state.cal_month
    today_date = date.today()
    
    st.markdown("# 📅 Medicine Calendar")
    st.markdown("### View your medicine intake history")
    st.markdown("---")
    
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous Month", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    
    with col2:
        st.markdown(
            f"<h2 style='text-align:center;color:#b144ff;'>"
            f"{calendar.month_name[month]} {year}</h2>",
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("Next Month ➡️", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    st.markdown("---")

   
    st.markdown("""
    <div style="text-align:center; padding: 10px;">
    <span style="background:#d4edda;padding:5px 10px;border-radius:5px;border:2px solid #28a745;">🟩 100%</span>
    <span style="background:#e8f5e9;padding:5px 10px;border-radius:5px;border:2px solid #66bb6a;">🟢 80-99%</span>
    <span style="background:#fff3cd;padding:5px 10px;border-radius:5px;border:2px solid #ffc107;">🟡 60-79%</span>
    <span style="background:#f8d7da;padding:5px 10px;border-radius:5px;border:2px solid #dc3545;">🔴 &lt;60%</span>
    <span style="background:#e9ecef;padding:5px 10px;border-radius:5px;border:2px solid #ced4da;">⬜ Future/No Meds</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Week headers
    week_cols = st.columns(7)
    for i, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        week_cols[i].markdown(f"<p style='text-align:center;color:#b144ff;font-weight:bold;font-size:1.1rem;'>{day}</p>", unsafe_allow_html=True)

    # Calendar grid
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            if day_num == 0:
                cols[i].markdown(" ")
            else:
                target_date = f"{year:04d}-{month:02d}-{day_num:02d}"
                adherence = calculate_adherence(user_id, target_date)
                
                # Determine color based on adherence
                if adherence >= 100:
                    color_bg = "#d4edda"
                    color_border = "#28a745"
                    badge_color = "#28a745"
                elif adherence >= 80:
                    color_bg = "#e8f5e9"
                    color_border = "#66bb6a"
                    badge_color = "#66bb6a"
                elif adherence >= 60:
                    color_bg = "#fff3cd"
                    color_border = "#ffc107"
                    badge_color = "#ffc107"
                else:
                    color_bg = "#f8d7da"
                    color_border = "#dc3545"
                    badge_color = "#dc3545"
                
                is_today = (
                    day_num == today_date.day
                    and month == today_date.month
                    and year == today_date.year
                )
                
                today_border = "4px solid #b144ff" if is_today else "2px solid #e9ecef"
                today_class = "today" if is_today else ""
                
                
                day_meds = get_medicines_for_date(user_id, target_date)
                
               
                date_obj = date(year, month, day_num)
                is_future = date_obj > today_date
                
                if is_future or not day_meds:
                    color_bg = "#f8f9fa"
                    color_border = "#e9ecef"
                    badge_color = "#6c757d"
                    adherence_text = "Upcoming" if is_future else "No meds"
                    adherence_value = 0
                else:
                    adherence_text = f"{adherence}%"
                    adherence_value = adherence
                
                med_list_html = ""
                if day_meds:
                    med_list_html = "<div class='medicine-list'>"
                    for med in day_meds:
                        med_list_html += f"<div class='medicine-item'>💊 {med['name']}</div>"
                    med_list_html += "</div>"
                
               
                total_doses = sum(len(med['times']) for med in day_meds) if day_meds else 0
                
                cols[i].markdown(
                    f"""
                    <div class="calendar-day {today_class}" style="background:{color_bg};border:{today_border};">
                        <div class="day-number">{day_num}</div>
                        <div class="adherence-badge" style="background:{badge_color};color:white;">
                            {adherence_text}
                        </div>
                        {med_list_html}
                        <div style="font-size:0.75rem;color:#666;margin-top:5px;">
                            {total_doses} dose{'s' if total_doses != 1 else ''}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            
                if not is_future and day_meds:
                    if cols[i].button("📋 Details", key=f"view_{target_date}", use_container_width=True):
                        st.session_state.selected_date = target_date
                        st.session_state.view_day_details = True

   
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Go to Today", use_container_width=True):
            today = date.today()
            st.session_state.cal_year = today.year
            st.session_state.cal_month = today.month
            st.rerun()
    
    with col2:
        if st.button("⏮️ Last Month", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    
    with col3:
        if st.button("Next Month ⏭️", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
                st.rerun()

    
    if st.session_state.get('view_day_details', False):
        st.markdown("---")
        st.markdown(f"## 📋 Details for {st.session_state.selected_date}")
        
        selected_date = st.session_state.selected_date
        day_meds = get_medicines_for_date(user_id, selected_date)
        
        if day_meds:
            total = 0
            taken = 0
            
            for med in day_meds:
                for time_slot in med['times']:
                    total += 1
                    
                    # Check if taken using SQLite
                    is_taken = get_intake_status(med['id'], selected_date, time_slot)
                    taken_at = None
                    
                    if is_taken:
                        taken += 1
                        # Get timestamp from database
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT timestamp FROM tracking WHERE medicine_id=? AND date=? AND time_slot=?",
                            (med['id'], selected_date, time_slot)
                        )
                        result = cursor.fetchone()
                        conn.close()
                        if result and result['timestamp']:
                            taken_at = datetime.fromisoformat(result['timestamp']).strftime('%I:%M %p')
                    
                    status = "✅ Taken" if is_taken else "⭕ Not Taken"
                    bg_color = "#d4edda" if is_taken else "#f8d7da"
                    border_color = "#28a745" if is_taken else "#dc3545"
                    taken_time_html = f"<p>✅ Taken at: {taken_at}</p>" if taken_at else ""
                    
                    st.markdown(f"""
                    <div style="background:{bg_color};border-radius:15px;padding:1rem;margin:0.5rem 0;border:3px solid {border_color};">
                        <h3>{status} - {med['name']}</h3>
                        <p>💊 {med['dosage']} • ⏰ {time_slot}</p>
                        {taken_time_html}
                    </div>
                    """, unsafe_allow_html=True)
            
            
            adherence_rate = int((taken / total * 100)) if total > 0 else 0
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Scheduled", total)
            with col2:
                st.metric("Total Taken", taken)
            with col3:
                st.metric("Adherence Rate", f"{adherence_rate}%")
            
            st.progress(adherence_rate / 100)
        else:
            st.info(f"No medicines scheduled for this date")
        
        if st.button("Close Details", use_container_width=True):
            st.session_state.view_day_details = False
            st.rerun()

    
    st.markdown("---")
    st.markdown("## 📊 Weekly Adherence Overview")
    
    weekly_data = calculate_weekly_adherence(user_id)
    
    
    weekly_values = list(weekly_data.values())
    marker_colors = ['#81c784' if v >= 80 else '#ffd54f' if v >= 50 else '#e57373' for v in weekly_values]
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(weekly_data.keys()),
            y=weekly_values,
            marker_color=marker_colors,
            text=weekly_values,
            texttemplate='%{text}%',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Last 7 Days Adherence",
        xaxis_title="Day",
        yaxis_title="Adherence %",
        yaxis_range=[0, 105],
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


elif st.session_state.user and st.session_state.page == "settings":
    user_id = st.session_state.user[0]
    
    st.markdown("# ⚙️ Settings")
    st.markdown("### Customize your Dr.Pill experience")
    st.markdown("---")
    
    # Reminder Settings
    st.markdown("## 🔔 Reminder Settings")
    
    settings = get_settings(user_id)
    
    col1, col2 = st.columns(2)
    with col1:
        reminders_enabled = st.toggle("Enable Reminders", value=settings['reminders_enabled'])
        update_settings(user_id, reminders_enabled, settings['reminder_advance_minutes'])
        settings = get_settings(user_id)
    
    with col2:
        advance_minutes = st.number_input(
            "Reminder advance time (minutes)",
            min_value=5,
            max_value=120,
            value=settings['reminder_advance_minutes'],
            step=5
        )
        update_settings(user_id, settings['reminders_enabled'], advance_minutes)
        settings = get_settings(user_id)
    
    if settings['reminders_enabled']:
        st.success(f"✅ You'll be reminded {settings['reminder_advance_minutes']} minutes before each medicine time")
    else:
        st.info("⏸️ Reminders are currently disabled")
    
    st.markdown("---")
    
    
    st.markdown("## 📊 Your Statistics")
    
    stats = get_adherence_stats(user_id)
    tracking_records = get_all_tracking_records(user_id)
    total_intakes = sum(1 for t in tracking_records if t['taken'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Medicines Taken", total_intakes)
    
    with col2:
        total_daily = len([m for m in get_user_medicines(user_id) if m[4] == 'Daily (Ongoing)'])
        st.metric("Daily Medicines", total_daily)
    
    with col3:
        total_date_range = len([m for m in get_user_medicines(user_id) if m[4] == 'Date Range'])
        st.metric("Date Range Medicines", total_date_range)
    
    with col4:
        st.metric("Active Medicines", stats['active_medicines'])
    
    # Overall adherence
    st.markdown("---")
    st.markdown("### 🎯 30-Day Adherence Rate")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h1 style='text-align: center; font-size: 5rem; color: #9c27b0;'>{stats['overall_adherence']}%</h1>", unsafe_allow_html=True)
    with col2:
        st.progress(stats['overall_adherence'] / 100)
        if stats['overall_adherence'] >= 90:
            st.success("🏆 Excellent! You're doing amazing!")
        elif stats['overall_adherence'] >= 75:
            st.info("👍 Good work! Keep it up!")
        elif stats['overall_adherence'] >= 50:
            st.warning("⚠️ You can do better! Stay consistent!")
        else:
            st.error("❗ Need improvement. Don't give up!")
    
    st.markdown("---")
    
    # Data Management
    st.markdown("## 💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Export Data")
        if st.button("📥 Download Backup (JSON)", use_container_width=True):
            json_data = export_user_data(user_id)
            st.download_button(
                label="💾 Download",
                data=json_data,
                file_name=f"dr_pill_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            st.success("✅ Backup ready for download!")
    
    with col2:
        st.markdown("### Danger Zone")
        st.warning("⚠️ These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Intake History", type="secondary", use_container_width=True):
                if st.checkbox("I understand this will delete all intake records"):
                    clear_tracking_for_medicines(user_id)
                    st.success("All intake history cleared!")
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Account", type="secondary", use_container_width=True):
                if st.checkbox("I understand this will delete ALL my data"):
                    delete_user_account(user_id)
                    st.session_state.user = None
                    st.session_state.auth_mode = None
                    st.session_state.page = "home"
                    st.success("Account deleted!")
                    st.rerun()

elif st.session_state.user and st.session_state.page == "shop":
    user_id = st.session_state.user[0]
    
    st.markdown("# 🛒 Medicine Shop")
    st.markdown("### Order your medicines online")
    st.markdown("---")
    
    
    st.markdown("""
    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
        <p style="font-size: 1.2rem; margin: 0; color: #856404; font-weight: bold;">
            ⚠️ Important Note
        </p>
        <p style="font-size: 1.1rem; margin: 0.5rem 0 0 0; color: #856404;">
            This is a demo shopping feature. For actual medicine purchases, please visit the linked pharmacy websites. Always consult with your doctor before purchasing any medication! 💙
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
   
    cart_count = len(st.session_state.cart)
    cart_total = sum(item['price'] * item['quantity'] for item in st.session_state.cart)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### Browse Medicines")
    with col2:
        st.metric("Cart Items", cart_count)
    with col3:
        st.metric("Cart Total", f"${cart_total:.2f}")
    
   
    categories = ["All", "Pain Relief", "Vitamins", "Supplements", "Digestive", "Minerals", "Sleep", "Joint Care", "Heart Health"]
    selected_category = st.selectbox("Filter by Category", categories)
    
    st.markdown("---")
    
  
    shop_items = [
        {"id": "1", "name": "Aspirin 100mg", "price": 5.99, "description": "Pain relief and fever reduction", "emoji": "💊", "category": "Pain Relief"},
        {"id": "2", "name": "Vitamin D3", "price": 12.99, "description": "Supports bone health", "emoji": "☀️", "category": "Vitamins"},
        {"id": "3", "name": "Omega-3 Fish Oil", "price": 18.99, "description": "Heart and brain health", "emoji": "🐟", "category": "Supplements"},
        {"id": "4", "name": "Multivitamin", "price": 15.99, "description": "Daily nutritional support", "emoji": "🌈", "category": "Vitamins"},
        {"id": "5", "name": "Calcium + Vitamin K", "price": 14.99, "description": "Bone strength formula", "emoji": "🦴", "category": "Supplements"},
        {"id": "6", "name": "Probiotic Complex", "price": 22.99, "description": "Digestive health support", "emoji": "🦠", "category": "Digestive"},
        {"id": "7", "name": "Magnesium 400mg", "price": 11.99, "description": "Muscle and nerve support", "emoji": "💪", "category": "Minerals"},
        {"id": "8", "name": "Vitamin C 1000mg", "price": 9.99, "description": "Immune system boost", "emoji": "🍊", "category": "Vitamins"},
        {"id": "9", "name": "Melatonin 5mg", "price": 13.99, "description": "Sleep support supplement", "emoji": "😴", "category": "Sleep"},
        {"id": "10", "name": "Glucosamine", "price": 19.99, "description": "Joint health support", "emoji": "🦵", "category": "Joint Care"},
        {"id": "11", "name": "B-Complex Vitamins", "price": 16.99, "description": "Energy and metabolism", "emoji": "⚡", "category": "Vitamins"},
        {"id": "12", "name": "CoQ10 200mg", "price": 24.99, "description": "Heart health antioxidant", "emoji": "❤️", "category": "Heart Health"},
    ]
    
   
    if selected_category != "All":
        shop_items = [item for item in shop_items if item["category"] == selected_category]
    
  
    cols_per_row = 3
    for i in range(0, len(shop_items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(shop_items):
                item = shop_items[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div class="shop-card">
                        <div style="font-size: 4rem;">{item['emoji']}</div>
                        <h3>{item['name']}</h3>
                        <p>{item['description']}</p>
                        <p style="color: #9c27b0;"><strong>${item['price']}</strong></p>
                        <p style="font-size: 1rem; color: #666;">Category: {item['category']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        max_value=10,
                        value=1,
                        key=f"qty_{item['id']}"
                    )
                    
                    if st.button(f"🛒 Add to Cart", key=f"add_{item['id']}", use_container_width=True):
                        # Check if item already in cart
                        existing_item = next((x for x in st.session_state.cart if x['id'] == item['id']), None)
                        if existing_item:
                            existing_item['quantity'] += quantity
                        else:
                            st.session_state.cart.append({
                                'id': item['id'],
                                'name': item['name'],
                                'price': item['price'],
                                'quantity': quantity,
                                'emoji': item['emoji']
                            })
                        st.success(f"Added {quantity}x {item['name']} to cart!")
                        st.rerun()
    
    
    if st.session_state.cart:
        st.markdown("---")
        st.markdown("## 🛒 Your Shopping Cart")
        
        for item in st.session_state.cart:
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            
            with col1:
                st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{item['emoji']}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"${item['price']} each")
            
            with col3:
                st.markdown(f"Quantity: {item['quantity']}")
                st.markdown(f"**Subtotal: ${item['price'] * item['quantity']:.2f}**")
            
            with col4:
                if st.button("🗑️", key=f"remove_{item['id']}", use_container_width=True):
                    st.session_state.cart.remove(item)
                    st.rerun()
        
        
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            st.markdown(f"### Total: ${cart_total:.2f}")
        
        with col3:
            if st.button("💳 Checkout", use_container_width=True, type="primary"):
                order_id = f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_order = {
                    'id': order_id,
                    'items': st.session_state.cart.copy(),
                    'total': cart_total,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': "Processing"
                }
                st.session_state.orders.append(new_order)
                st.session_state.cart = []
                st.success(f"✅ Order placed! Order ID: {order_id}")
                st.balloons()
                st.rerun()
    
   
    if st.session_state.orders:
        st.markdown("---")
        st.markdown("## 📦 Order History")
        
        for order in reversed(st.session_state.orders):
            with st.expander(f"Order {order['id']} - ${order['total']:.2f} - {order['status']}"):
                st.markdown(f"**Date:** {order['date']}")
                st.markdown(f"**Status:** {order['status']}")
                st.markdown("**Items:**")
                for item in order['items']:
                    st.markdown(f"- {item['emoji']} {item['name']} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}")
                st.markdown(f"**Total: ${order['total']:.2f}**")



if st.session_state.user:
    st.sidebar.markdown("# 💊 Dr.Pill")
    st.sidebar.markdown("---")
    
   
    settings = get_settings(st.session_state.user[0])
    upcoming = get_upcoming_reminders(st.session_state.user[0])
    urgent_count = len([r for r in upcoming if r['minutes_until'] <= settings['reminder_advance_minutes']])
    
    pages = {
        '🏠 Home': 'home',
        '👤 Profile': 'profile',
        '➕ Add Medicine': 'add_medicine',
        '💊 All Medicines': 'medicines_list',
        '📅 Calendar': 'calendar',
        '⚙️ Settings': 'settings',
        '🛒 Shop': 'shop'
    }
    
    for label, page in pages.items():
       
        display_label = label
        if page == 'home' and urgent_count > 0 and settings['reminders_enabled']:
            display_label = f"{label} 🔴"
        
        if st.sidebar.button(display_label, use_container_width=True, 
                            type="primary" if st.session_state.page == page else "secondary"):
            st.session_state.page = page
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("💕 Taking care of you, one reminder at a time!")
    
    
    stats = get_adherence_stats(st.session_state.user[0])
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.progress(stats['today_adherence'] / 100)
    st.sidebar.markdown(f"Today's Adherence: **{stats['today_adherence']}%**")
    st.sidebar.markdown(f"Active Medicines: **{stats['active_medicines']}/{stats['total_medicines']}**")
    
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_mode = None
        st.session_state.page = "home"
        st.rerun()

st.markdown("---")

