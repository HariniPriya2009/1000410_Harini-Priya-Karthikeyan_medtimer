import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta, time
import calendar
import json
import plotly.graph_objects as go

# ================= SESSION STATE INITIALIZATION =================
def init_session_state():
    """Initialize all session state variables for data persistence"""
    
    # Authentication state
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = None
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    # Calendar state
    if 'cal_year' not in st.session_state:
        today = date.today()
        st.session_state.cal_year = today.year
        st.session_state.cal_month = today.month
    
    # Medicine editing state
    if 'edit_medicine_id' not in st.session_state:
        st.session_state.edit_medicine_id = None
    
    # Shopping cart and orders
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    if 'orders' not in st.session_state:
        st.session_state.orders = []
    
    # DATABASE - Replace SQLite with session state
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    
    if 'medicines_db' not in st.session_state:
        st.session_state.medicines_db = {}  # {user_id: {med_id: med_data}}
    
    if 'tracking_db' not in st.session_state:
        st.session_state.tracking_db = {}  # {(medicine_id, date, time_slot): tracking_data}
    
    if 'settings_db' not in st.session_state:
        st.session_state.settings_db = {}  # {user_id: settings_data}
    
    # ID counters
    if 'next_user_id' not in st.session_state:
        st.session_state.next_user_id = 1
    
    if 'next_medicine_id' not in st.session_state:
        st.session_state.next_medicine_id = 1
    
    # Calendar view state
    if 'view_day_details' not in st.session_state:
        st.session_state.view_day_details = False
    
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None

# ================= DATABASE FUNCTIONS (Session State Version) =================

def create_user(name, email, password, age, conditions="", phone="", email_address=""):
    """Create a new user in session state"""
    if email in st.session_state.users_db:
        return False
    
    user_id = st.session_state.next_user_id
    st.session_state.users_db[email] = {
        'id': user_id,
        'name': name,
        'email': email,
        'password': password,
        'age': age,
        'conditions': conditions,
        'phone': phone,
        'email_address': email_address
    }
    
    # Initialize settings for new user
    st.session_state.settings_db[user_id] = {
        'user_id': user_id,
        'reminders_enabled': True,
        'reminder_advance_minutes': 30
    }
    
    st.session_state.next_user_id += 1
    return True

def login_user(email, password):
    """Authenticate user and return user data"""
    if email in st.session_state.users_db:
        user = st.session_state.users_db[email]
        if user['password'] == password:
            return (user['id'], user['name'], user['email'], user['password'],
                   user['age'], user['conditions'], user['phone'], user['email_address'])
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    for email, user in st.session_state.users_db.items():
        if user['id'] == user_id:
            return (user['id'], user['name'], user['email'], user['password'],
                   user['age'], user['conditions'], user['phone'], user['email_address'])
    return None

def update_user(user_id, name, age, conditions, phone, email_address):
    """Update user information"""
    for email, user in st.session_state.users_db.items():
        if user['id'] == user_id:
            user['name'] = name
            user['age'] = age
            user['conditions'] = conditions
            user['phone'] = phone
            user['email_address'] = email_address
            return True
    return False

def save_medicine(user_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, color):
    """Save a new medicine for a user"""
    med_id = st.session_state.next_medicine_id
    
    if user_id not in st.session_state.medicines_db:
        st.session_state.medicines_db[user_id] = {}
    
    st.session_state.medicines_db[user_id][med_id] = {
        'id': med_id,
        'user_id': user_id,
        'name': name,
        'dosage': dosage,
        'med_type': med_type,
        'times': times,
        'time_labels': time_labels,
        'notes': notes,
        'start_date': start_date,
        'end_date': end_date,
        'paused': False,
        'color': color
    }
    
    st.session_state.next_medicine_id += 1
    return med_id

def get_user_medicines(user_id):
    """Get all medicines for a user"""
    if user_id in st.session_state.medicines_db:
        medicines = st.session_state.medicines_db[user_id].values()
        result = []
        for med in medicines:
            result.append((
                med['id'], med['user_id'], med['name'], med['dosage'],
                med['med_type'], med['times'], med['time_labels'], med['notes'],
                med['start_date'], med['end_date'], med['paused'], med['color']
            ))
        return result
    return []

def get_medicine_by_id(med_id):
    """Get medicine by ID"""
    for user_id, medicines in st.session_state.medicines_db.items():
        if med_id in medicines:
            med = medicines[med_id]
            return (
                med['id'], med['user_id'], med['name'], med['dosage'],
                med['med_type'], med['times'], med['time_labels'], med['notes'],
                med['start_date'], med['end_date'], med['paused'], med['color']
            )
    return None

def update_medicine(med_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, color):
    """Update medicine information"""
    for user_id, medicines in st.session_state.medicines_db.items():
        if med_id in medicines:
            medicines[med_id]['name'] = name
            medicines[med_id]['dosage'] = dosage
            medicines[med_id]['med_type'] = med_type
            medicines[med_id]['times'] = times
            medicines[med_id]['time_labels'] = time_labels
            medicines[med_id]['notes'] = notes
            medicines[med_id]['start_date'] = start_date
            medicines[med_id]['end_date'] = end_date
            medicines[med_id]['color'] = color
            return True
    return False

def delete_medicine(med_id):
    """Delete a medicine and its tracking records"""
    for user_id, medicines in st.session_state.medicines_db.items():
        if med_id in medicines:
            del medicines[med_id]
            # Delete related tracking records
            keys_to_delete = [k for k in st.session_state.tracking_db.keys() if k[0] == med_id]
            for key in keys_to_delete:
                del st.session_state.tracking_db[key]
            return True
    return False

def toggle_medicine_pause(med_id):
    """Toggle pause status of a medicine"""
    for user_id, medicines in st.session_state.medicines_db.items():
        if med_id in medicines:
            medicines[med_id]['paused'] = not medicines[med_id]['paused']
            return True
    return False

def get_medicines_for_date(user_id, target_date):
    """Get all medicines scheduled for a specific date"""
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

def mark_as_taken(medicine_id, target_date, time_slot):
    """Mark a medicine dose as taken"""
    key = (medicine_id, target_date, time_slot)
    
    if key in st.session_state.tracking_db:
        st.session_state.tracking_db[key]['taken'] = True
        st.session_state.tracking_db[key]['timestamp'] = datetime.now()
    else:
        st.session_state.tracking_db[key] = {
            'id': len(st.session_state.tracking_db) + 1,
            'medicine_id': medicine_id,
            'date': target_date,
            'time_slot': time_slot,
            'taken': True,
            'timestamp': datetime.now()
        }

def toggle_intake(medicine_id, target_date, time_slot):
    """Toggle intake status of a medicine dose"""
    key = (medicine_id, target_date, time_slot)
    
    if key in st.session_state.tracking_db:
        tracking = st.session_state.tracking_db[key]
        tracking['taken'] = not tracking['taken']
        tracking['timestamp'] = datetime.now() if tracking['taken'] else None
    else:
        st.session_state.tracking_db[key] = {
            'id': len(st.session_state.tracking_db) + 1,
            'medicine_id': medicine_id,
            'date': target_date,
            'time_slot': time_slot,
            'taken': True,
            'timestamp': datetime.now()
        }

def get_intake_status(medicine_id, target_date, time_slot):
    """Check if a medicine dose has been taken"""
    key = (medicine_id, target_date, time_slot)
    if key in st.session_state.tracking_db:
        return st.session_state.tracking_db[key]['taken']
    return False

def calculate_adherence(user_id, target_date):
    """Calculate adherence percentage for a specific date"""
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
    """Calculate adherence for the last 7 days"""
    weekly_data = {}
    for i in range(7):
        d = date.today()
        target_date = (d - timedelta(days=6-i)).strftime('%Y-%m-%d')
        day_name = (d - timedelta(days=6-i)).strftime('%a')
        adherence = calculate_adherence(user_id, target_date)
        weekly_data[day_name] = adherence
    
    return weekly_data

def get_adherence_stats(user_id):
    """Get comprehensive adherence statistics"""
    today = date.today().strftime("%Y-%m-%d")
    today_adherence = calculate_adherence(user_id, today)
    medicines = get_user_medicines(user_id)
    total_meds = len(medicines)
    active_meds = len([m for m in medicines if not m[10]])  # m[10] is paused
    
    # Get adherence for last 7 days
    last_7_days = []
    for i in range(7):
        d = date.today()
        target_date = (d - timedelta(days=i)).strftime("%Y-%m-%d")
        adherence = calculate_adherence(user_id, target_date)
        last_7_days.append(adherence)
    
    avg_adherence = sum(last_7_days) / len(last_7_days) if last_7_days else 100
    
    # Get 30-day adherence
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
    if user_id in st.session_state.settings_db:
        settings = st.session_state.settings_db[user_id]
        return {
            'reminders_enabled': settings['reminders_enabled'],
            'reminder_advance_minutes': settings['reminder_advance_minutes']
        }
    else:
        # Create default settings
        st.session_state.settings_db[user_id] = {
            'user_id': user_id,
            'reminders_enabled': True,
            'reminder_advance_minutes': 30
        }
        return {'reminders_enabled': True, 'reminder_advance_minutes': 30}

def update_settings(user_id, reminders_enabled, reminder_advance_minutes):
    """Update user settings"""
    if user_id in st.session_state.settings_db:
        st.session_state.settings_db[user_id]['reminders_enabled'] = reminders_enabled
        st.session_state.settings_db[user_id]['reminder_advance_minutes'] = reminder_advance_minutes

def get_upcoming_reminders(user_id):
    """Get upcoming medicine reminders"""
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

def export_user_data(user_id):
    """Export all user data as JSON"""
    user = get_user_by_id(user_id)
    medicines = get_user_medicines(user_id)
    
    # Get tracking data
    tracking_data = []
    for med in medicines:
        med_id = med[0]
        for key, tracking in st.session_state.tracking_db.items():
            if key[0] == med_id:
                tracking_data.append({
                    'medicine_id': tracking['medicine_id'],
                    'date': tracking['date'],
                    'time_slot': tracking['time_slot'],
                    'taken': tracking['taken'],
                    'timestamp': tracking['timestamp']
                })
    
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
        'tracking': tracking_data
    }
    return json.dumps(data, indent=2)

# ================= MIGRATION HELPERS =================

def migrate_from_sqlite(conn, cursor):
    """
    Migrate existing SQLite data to session state
    Call this once to transfer your existing data
    """
    try:
        # Migrate users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            if user[2] not in st.session_state.users_db:  # Check by email
                st.session_state.users_db[user[2]] = {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'password': user[3],
                    'age': user[4],
                    'conditions': user[5],
                    'phone': user[6],
                    'email_address': user[7]
                }
        
        # Migrate medicines
        cursor.execute("SELECT * FROM medicines")
        medicines = cursor.fetchall()
        for med in medicines:
            med_id, user_id, name, dosage, med_type, times, time_labels, notes, start_date, end_date, paused, color = med
            if user_id not in st.session_state.medicines_db:
                st.session_state.medicines_db[user_id] = {}
            st.session_state.medicines_db[user_id][med_id] = {
                'id': med_id,
                'user_id': user_id,
                'name': name,
                'dosage': dosage,
                'med_type': med_type,
                'times': times,
                'time_labels': time_labels,
                'notes': notes,
                'start_date': start_date,
                'end_date': end_date,
                'paused': paused,
                'color': color
            }
        
        # Migrate tracking
        cursor.execute("SELECT * FROM tracking")
        tracking_records = cursor.fetchall()
        for track in tracking_records:
            track_id, medicine_id, track_date, time_slot, taken, timestamp = track
            key = (medicine_id, track_date, time_slot)
            st.session_state.tracking_db[key] = {
                'id': track_id,
                'medicine_id': medicine_id,
                'date': track_date,
                'time_slot': time_slot,
                'taken': taken,
                'timestamp': timestamp
            }
        
        # Update ID counters
        if medicines:
            st.session_state.next_medicine_id = max(m[0] for m in medicines) + 1
        if users:
            st.session_state.next_user_id = max(u[0] for u in users) + 1
        
        return True, "Migration successful!"
    except Exception as e:
        return False, f"Migration failed: {str(e)}"

# ================= MASCOT CONFIGURATION =================
def get_mascot_path(emotion):
    """Get the path to mascot image based on emotion"""
    mascot_paths = {
        'happy': 'mascots/waving pill.png',
        'sad': 'mascots/sad pill.png',
        'urgent': 'mascots/Angry pill.png',
        'sleepy': 'mascots/Doubt pill.png'
    }
    
    path = mascot_paths.get(emotion, mascot_paths['happy'])
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(script_dir, path)
    
    if not os.path.exists(abs_path):
        return None
    
    return abs_path

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
    """Render the pill mascot with different emotions"""
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
            'happy': '😊',
            'sad': '😢',
            'urgent': '😰',
            'sleepy': '😴'
        }
        fallback_emoji = emoji_map.get(emotion, '💊')
        
        st.markdown(f"""
        <div class="mascot-container">
            <div class="{css_class}" style="font-size: 8rem;">
                {fallback_emoji}
            </div>
            <h2 style="color: #9c27b0; margin-top: 1rem;">{message}</h2>
            <p style="color: #666;">(Mascot image not loaded - using emoji fallback)</p>
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

# ================= HELPER FUNCTIONS =================
def get_medicine_status(medicine, time_slot, current_time, user_id):
    """Determine the status of a medicine at a specific time"""
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

# ================= STYLES (Same as original) =================
# Add your existing styles here

