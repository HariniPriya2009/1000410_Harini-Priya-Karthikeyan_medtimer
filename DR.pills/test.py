import streamlit as st
import os

st.set_page_config(page_title="Mascot Debug", page_icon="🔍", layout="wide")

st.markdown("# 🔍 Mascot Image Debug Tool")
st.markdown("This tool helps diagnose why mascot images aren't loading")

# Show current working directory
st.markdown("---")
st.markdown("## 📁 Directory Information")
st.markdown(f"**Current Working Directory:** `{os.getcwd()}`")

# Show script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
st.markdown(f"**Script Directory:** `{script_dir}`")

# List files in current directory
st.markdown("---")
st.markdown("## 📂 Files in Current Directory")
current_files = os.listdir('.')
if current_files:
    for file in sorted(current_files):
        file_path = os.path.join('.', file)
        if os.path.isdir(file_path):
            st.markdown(f"📁 **{file}** (directory)")
        else:
            st.markdown(f"📄 {file}")
else:
    st.markdown("No files found")

# List files in script directory if different
if script_dir != os.getcwd():
    st.markdown("---")
    st.markdown("## 📂 Files in Script Directory")
    script_files = os.listdir(script_dir)
    if script_files:
        for file in sorted(script_files):
            file_path = os.path.join(script_dir, file)
            if os.path.isdir(file_path):
                st.markdown(f"📁 **{file}** (directory)")
            else:
                st.markdown(f"📄 {file}")
    else:
        st.markdown("No files found")

# Check for mascot folder
st.markdown("---")
st.markdown("## 🎨 Mascot Folder Check")

mascot_locations = [
    'mascots',
    'mascot',
    'Mascots',
    'Mascot',
    '../mascots',
    '../mascot',
]

found_mascot_folder = None
for location in mascot_locations:
    full_path = os.path.join(script_dir, location)
    if os.path.exists(full_path) and os.path.isdir(full_path):
        found_mascot_folder = full_path
        st.success(f"✅ Found mascot folder at: `{location}`")
        st.markdown(f"Full path: `{full_path}`")
        
        # List files in mascot folder
        mascot_files = os.listdir(full_path)
        if mascot_files:
            st.markdown("**Files in mascot folder:**")
            for file in sorted(mascot_files):
                st.markdown(f"  - {file}")
        else:
            st.warning("  (folder is empty)")
        break

if not found_mascot_folder:
    st.error("❌ No mascot folder found in expected locations!")
    st.info("Searched locations:")
    for location in mascot_locations:
        st.markdown(f"- `{location}`")

# Test loading images
st.markdown("---")
st.markdown("## 🖼️ Image Loading Test")

mascot_images = [
    ('happy', 'waving pill.png'),
    ('sad', 'sad pill.png'),
    ('urgent', 'Angry pill.png'),
    ('sleepy', 'Doubt pill.png')
]

if found_mascot_folder:
    for emotion, filename in mascot_images:
        image_path = os.path.join(found_mascot_folder, filename)
        st.markdown(f"### {emotion.capitalize()} Mascot")
        st.markdown(f"Looking for: `{filename}`")
        st.markdown(f"Full path: `{image_path}`")
        
        if os.path.exists(image_path):
            st.success("✅ File exists!")
            
            # Try to display using different methods
            col1, col2, col3 = st.columns(3)
            
            # Method 1: Using st.image()
            try:
                with col1:
                    st.markdown("**Method 1: st.image()**")
                    st.image(image_path, width=150, caption="Using st.image()")
                    st.success("✅ Works!")
            except Exception as e:
                with col1:
                    st.markdown("**Method 1: st.image()**")
                    st.error(f"❌ Failed: {e}")
            
            # Method 2: Using file:// protocol in HTML
            try:
                with col2:
                    st.markdown("**Method 2: HTML img**")
                    st.markdown(f'<img src="file:///{image_path}" width="150">', unsafe_allow_html=True)
                    st.success("✅ Works!")
            except Exception as e:
                with col2:
                    st.markdown("**Method 2: HTML img**")
                    st.error(f"❌ Failed: {e}")
            
            # Method 3: Using data URI
            try:
                with col3:
                    st.markdown("**Method 3: Data URI**")
                    import base64
                    with open(image_path, "rb") as image_file:
                        encoded = base64.b64encode(image_file.read()).decode()
                        img_tag = f'<img src="data:image/png;base64,{encoded}" width="150">'
                    st.markdown(img_tag, unsafe_allow_html=True)
                    st.success("✅ Works!")
            except Exception as e:
                with col3:
                    st.markdown("**Method 3: Data URI**")
                    st.error(f"❌ Failed: {e}")
            
        else:
            st.error(f"❌ File not found: `{filename}`")
        
        st.markdown("---")

# Interactive path configuration
st.markdown("---")
st.markdown("## ⚙️ Path Configuration")

st.markdown("### Find your mascot images")
st.info("Use the file browser below to locate your mascot images and then update the paths in the main app.")

uploaded_files = st.file_uploader(
    "Or upload your mascot images here to test",
    accept_multiple_files=True,
    type=['png', 'jpg', 'jpeg', 'gif']
)

if uploaded_files:
    st.markdown("### Uploaded Images:")
    for uploaded_file in uploaded_files:
        st.markdown(f"**{uploaded_file.name}**")
        st.image(uploaded_file, width=150)
        
        # Save the uploaded file
        save_path = os.path.join('mascots', uploaded_file.name)
        os.makedirs('mascots', exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Saved to: `{save_path}`")

# Recommendations
st.markdown("---")
st.markdown("## 💡 Recommendations")

if not found_mascot_folder:
    st.markdown("""
    ### To fix the mascot loading:
    
    1. **Create a mascot folder** next to your Python script:
       ```bash
       mkdir mascots
       ```
    
    2. **Move your mascot images** into the `mascots` folder:
       - `waving pill.png`
       - `sad pill.png`
       - `Angry pill.png`
       - `Doubt pill.png`
    
    3. **Ensure the images are in PNG format** and have readable filenames
    
    4. **Run the debug tool again** to verify the images are found
    """)
else:
    st.markdown(f"""
    ### Mascot folder found at: `{found_mascot_folder}`
    
    Your folder structure looks good! If images still aren't loading in the main app:
    
    1. **Check that image files are not corrupted**
    2. **Try renaming files** to remove spaces (e.g., `waving_pill.png`)
    3. **Verify file permissions** - the app should be able to read the files
    4. **Use Method 3 (Data URI)** from the test above in your main app
    """)

# Generate corrected code snippet
st.markdown("---")
st.markdown("## 📝 Updated Code for Main App")

st.markdown("### Use this in your `get_mascot_path()` function:")

code_snippet = '''
```python
def get_mascot_path(emotion):
    """Get the path to mascot image based on emotion"""
    mascot_paths = {
        'happy': 'mascots/waving pill.png',
        'sad': 'mascots/sad pill.png',
        'urgent': 'mascots/Angry pill.png',
        'sleepy': 'mascots/Doubt pill.png'
    }
    
    path = mascot_paths.get(emotion, mascot_paths['happy'])
    
    # Get absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(script_dir, path)
    
    return abs_path

def render_mascot_with_data_uri(emotion, message, missed_list=None):
    """Render mascot using data URI method (most reliable)"""
    img_path = get_mascot_path(emotion)
    
    if img_path and os.path.exists(img_path):
        import base64
        with open(img_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            img_tag = f'<img src="data:image/png;base64,{encoded}" width="160" style="border-radius: 10px;">'
    else:
        img_tag = '<div style="font-size: 8rem;">😊</div>'
    
    st.markdown(f"""
    <div class="mascot-container">
        <div style="text-align: center;">
            {img_tag}
        </div>
        <h2 style="color: #9c27b0; margin-top: 1rem;">{message}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if missed_list:
        # ... rest of the function
```
'''

st.markdown(code_snippet, unsafe_allow_html=True)

# Create mascot folder button
st.markdown("---")
st.markdown("## 🔧 Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📁 Create 'mascots' folder"):
        os.makedirs('mascots', exist_ok=True)
        st.success("✅ Created 'mascots' folder!")
        st.rerun()

with col2:
    if st.button("🔄 Refresh Debug Info"):
        st.rerun()

st.markdown("---")
st.markdown("### 📋 Summary")
if found_mascot_folder:
    st.success("✅ Mascot folder found! Check the Image Loading Test section above to see if images are loading correctly.")
    st.info(f"✨ Update the mascot paths in your main app to use: `{found_mascot_folder}`")
else:
    st.warning("⚠️ Mascot folder not found. Create a 'mascots' folder and add your images there.")
