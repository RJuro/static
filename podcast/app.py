import streamlit as st
import os
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid
import shutil

# App title and description
st.title("Simple Podcast RSS Generator")
st.write("Upload your podcast episodes and generate an RSS feed")

# Initialize session state variables
if 'rss_initialized' not in st.session_state:
    st.session_state.rss_initialized = False

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
    else:
        st.success("Using existing RSS feed")
    
    st.session_state.rss_initialized = True
    return True

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
        
        # Updated URL to use your static deployment
        item_enclosure = ET.SubElement(item, "enclosure", 
                                       url=f"https://static.rjuro.com/podcast/podcast/{file_path}",
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

# GitHub setup instructions
st.divider()
st.subheader("Static Deployment Information")
st.markdown("""
Your podcast files are being deployed to a static site:

1. Audio files are uploaded to: `https://static.rjuro.com/podcast/podcast/`
2. Your podcast RSS feed will be available at: `https://static.rjuro.com/podcast/podcast/feed.xml`
3. You can use this RSS feed URL in podcast apps that support private RSS feeds
""")

# Optional: Automatic deployment section
st.subheader("Advanced: Automatic Deployment")
st.markdown("""
To automatically deploy changes to your static site, you could:
1. Set up a CI/CD pipeline with your hosting provider
2. Configure automatic file syncing to your static hosting
3. Add webhooks to trigger deployments after updates

This is left as an enhancement for simplicity, but can be added if needed.
""")

# Optional: GitHub authentication and auto-push
st.subheader("Advanced: Automatic GitHub Push")
st.markdown("""
To automatically push changes to GitHub, you would need to:
1. Set up GitHub credentials
2. Install the `gitpython` package
3. Add code to push changes after each update

This is left as an enhancement for simplicity, but can be added if needed.
""")