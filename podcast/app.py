import streamlit as st
import os
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid
import qrcode
from io import BytesIO

# App title and description
st.title("Simple Podcast RSS Generator")
st.write("Upload your podcast episodes and generate an RSS feed")

# Set your feed URL here
FEED_URL = "https://static.rjuro.com/podcast/podcast/feed.xml"

# Initialize session state variables
if 'rss_initialized' not in st.session_state:
    st.session_state.rss_initialized = False

# Function to create QR code
def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buffered = BytesIO()
    img.save(buffered)
    return buffered.getvalue()

# Function to create initial RSS structure
def initialize_rss():
    # Create podcast directory if it doesn't exist
    if not os.path.exists("podcast"):
        os.makedirs("podcast")
    
    # Check if RSS file exists
    if not os.path.exists("podcast/feed.xml"):
        # Create a new RSS feed
        rss = ET.Element("rss", version="2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
        
        channel = ET.SubElement(rss, "channel")
        
        # Add basic podcast info (these can be made configurable)
        title = ET.SubElement(channel, "title")
        title.text = "My Private Podcast"
        
        description = ET.SubElement(channel, "description")
        description.text = "A private podcast created with Streamlit"
        
        language = ET.SubElement(channel, "language")
        language.text = "en-us"
        
        link = ET.SubElement(channel, "link")
        link.text = "https://example.com/podcast"
        
        # Save the empty feed
        xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
        with open("podcast/feed.xml", "w") as f:
            f.write(xml_str)
        
        st.success("Initialized new RSS feed")
        
        # Also create a subscription page
        create_subscription_page()
    else:
        st.success("Using existing RSS feed")
    
    st.session_state.rss_initialized = True
    return True

# Function to create subscription page
def create_subscription_page():
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscribe to My Podcast</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .subscribe-buttons {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        .subscribe-button {{
            display: block;
            background-color: #4a86e8;
            color: white;
            padding: 14px 20px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 8px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .subscribe-button:hover {{
            background-color: #3a76d8;
        }}
        .subscribe-button.apple {{
            background-color: #8c2df4;
        }}
        .subscribe-button.apple:hover {{
            background-color: #7b1bd3;
        }}
        .subscribe-button.overcast {{
            background-color: #fc7e0f;
        }}
        .subscribe-button.overcast:hover {{
            background-color: #e67109;
        }}
        .subscribe-button.pocketcasts {{
            background-color: #f43e37;
        }}
        .subscribe-button.pocketcasts:hover {{
            background-color: #e62d26;
        }}
        .direct-link {{
            margin-top: 30px;
            text-align: center;
        }}
        .qr-section {{
            margin-top: 40px;
            text-align: center;
        }}
        .qr-code {{
            max-width: 200px;
            margin: 0 auto;
            display: block;
        }}
    </style>
</head>
<body>
    <h1>Subscribe to My Podcast</h1>
    
    <div class="subscribe-buttons">
        <a href="pcast://{FEED_URL.replace('https://', '')}" class="subscribe-button apple">
            Subscribe with Apple Podcasts
        </a>
        
        <a href="overcast://x-callback-url/add?url={FEED_URL}" class="subscribe-button overcast">
            Subscribe with Overcast
        </a>
        
        <a href="pktc://subscribe/{FEED_URL}" class="subscribe-button pocketcasts">
            Subscribe with Pocket Casts
        </a>
        
        <a href="castro://subscribe/{FEED_URL}" class="subscribe-button">
            Subscribe with Castro
        </a>
        
        <a href="{FEED_URL}" class="subscribe-button">
            Subscribe with Other Podcast Apps
        </a>
    </div>
    
    <div class="direct-link">
        <p>Or copy this RSS feed URL:</p>
        <code>{FEED_URL}</code>
    </div>
    
    <div class="qr-section">
        <p>Scan this QR code with your phone:</p>
        <img src="qrcode.png" alt="QR Code for Podcast Feed" class="qr-code">
    </div>
    
    <script>
        // Detect platform and highlight appropriate button
        document.addEventListener('DOMContentLoaded', function() {{
            const platform = navigator.platform.toLowerCase();
            if (platform.includes('mac') || platform.includes('iphone') || platform.includes('ipad')) {{
                document.querySelector('.subscribe-button.apple').style.boxShadow = '0 0 10px #8c2df4';
            }}
        }});
    </script>
</body>
</html>
"""
    # Save the HTML file
    with open("podcast/subscribe.html", "w") as f:
        f.write(html_content)
    
    # Generate and save QR code
    qr_data = generate_qr_code(FEED_URL)
    with open("podcast/qrcode.png", "wb") as f:
        f.write(qr_data)
    
    st.success("Created subscription page")

# Function to add an episode to the RSS feed
def add_episode(title, audio_file, description="", file_path=""):
    try:
        # Parse the existing RSS feed
        tree = ET.parse("podcast/feed.xml")
        root = tree.getroot()
        channel = root.find("channel")
        
        # Get the current date and time
        now = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Create the new item element
        item = ET.SubElement(channel, "item")
        
        # Add item details
        item_title = ET.SubElement(item, "title")
        item_title.text = title
        
        item_description = ET.SubElement(item, "description")
        item_description.text = description if description else title
        
        item_pubDate = ET.SubElement(item, "pubDate")
        item_pubDate.text = now
        
        item_guid = ET.SubElement(item, "guid", isPermaLink="false")
        item_guid.text = str(uuid.uuid4())
        
        # Construct file URL based on your domain
        file_url = f"{FEED_URL.replace('feed.xml', '')}{file_path}"
        
        item_enclosure = ET.SubElement(item, "enclosure", 
                                       url=file_url,
                                       length=str(os.path.getsize(f"podcast/{file_path}")),
                                       type="audio/mpeg")
        
        # Save the updated feed
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open("podcast/feed.xml", "w") as f:
            f.write(xml_str)
        
        return True
    except Exception as e:
        st.error(f"Error adding episode: {e}")
        return False

# Initialize RSS feed button
if not st.session_state.rss_initialized:
    if st.button("Initialize RSS Feed"):
        initialize_rss()

# Only show the episode upload form if RSS is initialized
if st.session_state.rss_initialized or os.path.exists("podcast/feed.xml"):
    st.session_state.rss_initialized = True
    
    # Episode upload form
    with st.form("episode_form"):
        st.subheader("Add New Episode")
        
        episode_title = st.text_input("Episode Title", key="title")
        episode_description = st.text_area("Episode Description (optional)", key="description")
        audio_file = st.file_uploader("Upload Audio File (MP3)", type=["mp3"])
        
        submit_button = st.form_submit_button("Add Episode")
        
        if submit_button and audio_file is not None and episode_title:
            # Create a safe filename
            safe_filename = audio_file.name.replace(" ", "_")
            
            # Save the audio file
            with open(f"podcast/{safe_filename}", "wb") as f:
                f.write(audio_file.getbuffer())
            
            # Add the episode to the RSS feed
            if add_episode(episode_title, audio_file, episode_description, safe_filename):
                st.success(f"Added episode: {episode_title}")
            else:
                st.error("Failed to add episode")

# Display the current RSS feed
if st.session_state.rss_initialized or os.path.exists("podcast/feed.xml"):
    st.subheader("Current RSS Feed")
    
    if os.path.exists("podcast/feed.xml"):
        with open("podcast/feed.xml", "r") as f:
            rss_content = f.read()
        st.code(rss_content, language="xml")
        
        # Option to download the feed
        st.download_button(
            label="Download RSS Feed",
            data=rss_content,
            file_name="feed.xml",
            mime="application/xml"
        )

# Subscription information
st.divider()
st.subheader("Podcast Subscription Links")

if os.path.exists("podcast/subscribe.html"):
    st.success("Subscription page created at podcast/subscribe.html")
    
    # Display QR code if available
    if os.path.exists("podcast/qrcode.png"):
        st.image("podcast/qrcode.png", width=200, caption="Scan this QR code to subscribe")
else:
    if st.button("Create Subscription Page"):
        create_subscription_page()

st.markdown(f"""
### Direct Subscription Links

- **Apple Podcasts**: `pcast://{FEED_URL.replace('https://', '')}`
- **Overcast**: `overcast://x-callback-url/add?url={FEED_URL}`
- **Pocket Casts**: `pktc://subscribe/{FEED_URL}`
- **Castro**: `castro://subscribe/{FEED_URL}`
- **Direct RSS URL**: `{FEED_URL}`
""")

# GitHub setup instructions
st.divider()
st.subheader("GitHub Deployment Instructions")
st.markdown("""
1. Create a new GitHub repository
2. Push the 'podcast' directory to your repository:
```bash
git init
git add podcast/
git commit -m "Add podcast files"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```
3. Enable GitHub Pages in your repository settings to serve the files
4. Share the subscription page URL with your listeners
""")