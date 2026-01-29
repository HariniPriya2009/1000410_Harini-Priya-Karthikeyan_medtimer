Dr.Pill – Smart Medicine Reminder & Adherence Tracker

A user-friendly medicine reminder and adherence tracking web application built using Python and Streamlit, designed to help users manage medications, reduce missed doses, and build consistent health routines.

 Project Overview

Medication non-adherence is a widespread issue, especially among students, elderly individuals, and patients taking multiple medicines daily. Forgetting or delaying doses can reduce treatment effectiveness and impact health.

Live Demo:https://1000410-harini-priya-karthikeyan-drpill.streamlit.app/

App Flow Drive Link:https://drive.google.com/drive/u/1/folders/1jRahU_nIZ-5ZSnem9_K-4MHKtuYlzoWL?q=sharedwith:public%20parent:1jRahU_nIZ-5ZSnem9_K-4MHKtuYlzoWL

Features:

Dashboard:

Real-time medicine tracking with visual status indicators

Interactive mascot that reacts to your medication adherence

Today's progress display with adherence percentage

Upcoming reminders countdown

Motivational messages and achievements

User Management:

Secure user authentication (signup/login)

Personalized profile settings

Health condition tracking

Contact information management

**Medicine Management:**

Add unlimited medicines with custom dosages

Set multiple daily intake times

Color-coded medicine cards for easy identification

Date range or ongoing medication support

Edit, pause, resume, and delete medicines

Custom notes for each medication

Interactive Calendar:

Monthly calendar view with adherence visualization

Color-coded days (green for good, yellow for moderate, red for poor)

Click any day to view detailed intake history

Weekly adherence statistics chart

30-day overall adherence tracking

Smart Reminders:

Configurable reminder advance time (5-120 minutes)

Visual notification badges

Upcoming medicine countdown

Real-time status updates (taken, missed, upcoming, scheduled)

Statistics & Analytics:

Daily adherence percentage

Weekly adherence trends with visual charts

30-day overall adherence rate

Total medicines taken counter

Active vs paused medicine tracking

Medicine Shop (Demo Feature):

Browse medicine categories

Add items to shopping cart

Order history tracking

Price comparison and quantity selection

Data Management:

Export all data as JSON backup

Clear intake history option

Account deletion with full data cleanup

APP FLOW:

First Time Setup:

1.Create an Account:

Click "Sign Up ✨"

Fill in your name, email, password, and age

Add optional health conditions and contact info

Click "Sign Up 🚀"

2.Log In:

Use your email and password to access your account


Adding Your First Medicine:

1.Click "➕ Add Medicine" in the sidebar

2.Enter medicine details:

Name: e.g., "Aspirin"

Dosage: e.g., "50mg" or "2 tablets"

Type: Choose "Daily (Ongoing)" or "Date Range"

Color: Pick a color for visual identification

Notes: Add any special instructions

3.Set intake times:

Specify how many times per day


Set the time for each dose

Add labels (e.g., "After breakfast", "Before bed")

Click "💾 Add Medicine"

Tracking Your Medicines:

Home Dashboard: View today's medicines with status indicators

Mark as Taken: Click "✓ Taken" button when you take a medicine

Undo: Click "↶ Undo" if you made a mistake

Viewing History:

1.Navigate to "📅 Calendar"

2.Browse months using the navigation buttons

3.Click "📅 Go to Today" to jump to current date

4.Click on any day to view detailed intake history

5.Check color-coded adherence percentages

Managing Medicines:

1.Go to "💊 All Medicines"

2.Use filters to find specific medicines

3.Expand any medicine card to see details

4.Available actions:
    -⏸️ Pause/▶️ Resume: Temporarily stop reminders
    -✏️ Edit: Modify medicine details
    -🗑️ Delete: Remove medicine permanently


Customizing Settings:

1.Navigate to "⚙️ Settings"

2.Reminder Settings:

  -Enable/disable reminders
  
  -Set advance reminder time

3.View Statistics:
  
  -Check 30-day adherence rate
  
  
  -View total medicines taken

4.Data Management:

  -Download JSON backup
  
  -Clear history or delete account

Mascot System:

The app features an adorable pill mascot that reacts to your medication habits:

😊 Happy

  -Shown when you're doing great
  
  -Perfect adherence or all medicines taken
  
  -Encouraging messages

😢 Sad

  -Appears when you've missed medicines
    
  -Gentle reminder to check your schedule

  -Lists missed medications

😰 Urgent

  -Alerts when it's time to take medicine NOW

 -Animated shaking effect

 -Shows upcoming doses

😴 Sleepy

  -Evening time greeting

  -Summary of the day's performance
  
  -Good night message

Adherence Scoring:

Your adherence is calculated based on the percentage of scheduled doses taken:

🟩 100%: Perfect adherence

🟢 80-99%: Excellent adherence

🟡 60-79%: Good (needs improvement)

🔴 <60%: Poor (needs attention)

Streamlit Cloud (Recommended)

Prerequisites

GitHub account

Streamlit Cloud account (free)

Step-by-Step Deployment

1. Prepare Your Repository

# Create .streamlit directory
mkdir .streamlit

# Create .streamlit/config.toml
cat > .streamlit/config.toml << EOF

[server]

port = 8501

headless = true

enableCORS = false

enableXsrfProtection = false



[browser]

gatherUsageStats = false

EOF

2. Create requirements.txt



streamlit>=1.28.0

plotly>=5.17.0

3. Push to GitHub




git add .


git commit -m "Initial commit"

git branch -M main

git remote add origin https://github.com/yourusername/dr-pill-medicine-tracker.git

git push -u origin main

4. Deploy to Streamlit Cloud

Go to share.streamlit.io

Click "New app"

Connect your GitHub repository

Select your repository and branch

Set Main file path: DR_PILLS_Fixed.py

Click "Deploy"


APP REVIEW:

Friend:

really liked using Dr. Pills. It’s a simple and helpful app that makes medicine tracking easy. The pill mascots with different emotions clearly show whether a medicine is taken, missed, or pending, which makes the app engaging and easy to understand. The interface is clean and user-friendly, so anyone can use it without confusion. Overall, it’s a smart and practical app with great real-life usefulness.

Sister:

As her sister, I’m really proud of Dr. Pills. She got the idea for this app after seeing our grandma struggle to remember her medicines, and she turned that problem into a simple and meaningful solution. The app is easy to use, practical, and clearly made with care. It’s not just a project, but something created with real love and purpose.


Credits

Created by: Harini Priya Karthikeyan (ID: 1000410)

Course: Artificial Intelligence: Real-World Applications and Implications

Mentor: Syed Ali Beema.S

School: Jain Vidyalaya IB world school, Madurai
