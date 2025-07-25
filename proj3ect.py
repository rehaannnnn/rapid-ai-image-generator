import streamlit as st
import requests
import io
from PIL import Image
import base64
import time

# Page configuration
st.set_page_config(
    page_title="⚡ Rapid AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Title and description
st.title("⚡ Rapid AI Image Generator")
st.markdown("Generate images in seconds using free APIs!")

# API Configuration
API_CONFIGS = {
    "Pollinations (Free)": {
        "url": "https://image.pollinations.ai/prompt/{prompt}",
        "method": "GET",
        "fast": True,
        "description": "Super fast, no API key needed"
    },
    "Hugging Face (Free)": {
        "url": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
        "method": "POST",
        "fast": True,
        "description": "High quality, requires free API key"
    },
    "Stability AI (Premium)": {
        "url": "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
        "method": "POST",
        "fast": True,
        "description": "Best quality, requires paid API key"
    }
}

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Quick Settings")
    
    # API selection
    selected_api = st.selectbox("Choose API:", list(API_CONFIGS.keys()))
    
    # API Key input (if needed)
    if selected_api != "Pollinations (Free)":
        api_key = st.text_input(
            "API Key:", 
            type="password",
            help="Get free key from Hugging Face or paid from Stability AI"
        )
    else:
        api_key = None
    
    # Quick settings
    st.subheader("Image Settings")
    image_size = st.selectbox("Size:", ["512x512", "768x768", "1024x1024"])
    width, height = map(int, image_size.split('x'))
    
    # Style presets
    style_preset = st.selectbox("Style:", [
        "None",
        "Photographic",
        "Digital Art",
        "Anime",
        "Fantasy",
        "Sci-Fi",
        "Oil Painting",
        "Watercolor"
    ])

# Fast generation functions
def generate_with_pollinations(prompt, width=512, height=512):
    """Super fast generation with Pollinations API"""
    try:
        # Clean prompt for URL
        clean_prompt = prompt.replace(" ", "%20").replace(",", "%2C")
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={width}&height={height}&nologo=true"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_with_huggingface(prompt, api_key, width=512, height=512):
    """Generate with Hugging Face API"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 20
            }
        }
        
        response = requests.post(
            API_CONFIGS["Hugging Face (Free)"]["url"],
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_with_stability(prompt, api_key, width=512, height=512):
    """Generate with Stability AI API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 20
        }
        
        response = requests.post(
            API_CONFIGS["Stability AI (Premium)"]["url"],
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            image_data = base64.b64decode(data["artifacts"][0]["base64"])
            return Image.open(io.BytesIO(image_data))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Quick Generation")
    
    # Enhanced prompt input
    prompt = st.text_area(
        "Describe your image:",
        placeholder="A majestic dragon flying over a castle at sunset",
        height=100,
        key="main_prompt"
    )
    
    # Add style to prompt
    if style_preset != "None":
        style_suffix = f", {style_preset.lower()} style"
    else:
        style_suffix = ""
    
    # Quick prompt examples
    st.markdown("**Quick Examples (click to use):**")
    example_prompts = [
        "Cute cat wearing sunglasses",
        "Futuristic city with flying cars",
        "Beautiful mountain landscape",
        "Abstract geometric art",
        "Vintage car in the rain"
    ]
    
    cols = st.columns(len(example_prompts))
    for i, example in enumerate(example_prompts):
        if cols[i].button(f"🎯", key=f"example_{i}", help=example):
            st.session_state.main_prompt = example
            st.rerun()
    
    # Generate button
    generate_button = st.button("⚡ Generate Fast", type="primary", use_container_width=True)

with col2:
    st.subheader("🖼️ Generated Image")
    
    if generate_button and prompt:
        full_prompt = prompt + style_suffix
        
        # Show generation info
        st.info(f"🚀 Using {selected_api} - Generating: {full_prompt[:50]}...")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        
        # Generate based on selected API
        image = None
        
        if selected_api == "Pollinations (Free)":
            status_text.text("Connecting to Pollinations API...")
            progress_bar.progress(25)
            image = generate_with_pollinations(full_prompt, width, height)
            
        elif selected_api == "Hugging Face (Free)":
            if api_key:
                status_text.text("Connecting to Hugging Face API...")
                progress_bar.progress(25)
                image = generate_with_huggingface(full_prompt, api_key, width, height)
            else:
                st.error("Please enter your Hugging Face API key!")
                
        elif selected_api == "Stability AI (Premium)":
            if api_key:
                status_text.text("Connecting to Stability AI...")
                progress_bar.progress(25)
                image = generate_with_stability(full_prompt, api_key, width, height)
            else:
                st.error("Please enter your Stability AI API key!")
        
        progress_bar.progress(100)
        generation_time = time.time() - start_time
        
        if image:
            status_text.success(f"✅ Generated in {generation_time:.1f} seconds!")
            st.image(image, caption=f"Generated: {full_prompt}")
            
            # Download button
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            st.download_button(
                label="💾 Download Image",
                data=img_buffer,
                file_name=f"fast_generated_{int(time.time())}.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            status_text.error("❌ Generation failed!")
        
        progress_bar.empty()
    
    elif generate_button and not prompt:
        st.warning("Please enter a text prompt first!")

# API Information
with st.expander("🔑 API Setup Instructions"):
    st.markdown("""
    **Pollinations (Recommended - Free & Fast):**
    - No API key needed
    - Instant generation
    - Good quality
    - Just click generate!
    
    **Hugging Face (Free):**
    1. Go to [huggingface.co](https://huggingface.co)
    2. Sign up (free)
    3. Go to Settings > Access Tokens
    4. Create new token
    5. Paste it above
    
    **Stability AI (Premium):**
    1. Go to [stability.ai](https://stability.ai)
    2. Sign up and add credits
    3. Get API key from dashboard
    4. Best quality but costs money
    """)

# Speed comparison
with st.expander("⚡ Speed Comparison"):
    st.markdown("""
    | API | Speed | Quality | Cost |
    |-----|-------|---------|------|
    | Pollinations | ⚡⚡⚡ 2-5 sec | 🌟🌟🌟 Good | 💰 Free |
    | Hugging Face | ⚡⚡ 10-20 sec | 🌟🌟🌟🌟 Great | 💰 Free |
    | Stability AI | ⚡⚡ 10-15 sec | 🌟🌟🌟🌟🌟 Excellent | 💰 Paid |
    | Local Models | ⚡ 60-300 sec | 🌟🌟🌟🌟 Great | 💰 Free |
    """)

# Tips for better prompts
with st.expander("💡 Tips for Better & Faster Results"):
    st.markdown("""
    **For Speed:**
    - Use Pollinations API (no setup needed)
    - Keep prompts under 200 characters
    - Use standard sizes (512x512, 768x768)
    
    **For Quality:**
    - Be specific: "red sports car" vs "car"
    - Add style: "digital art", "photorealistic"
    - Include lighting: "golden hour", "studio lighting"
    - Mention composition: "close-up", "wide shot"
    
    **Example Good Prompts:**
    - "A cyberpunk street at night, neon lights, rain, cinematic"
    - "Portrait of a wise old man, detailed, oil painting style"
    - "Modern minimalist kitchen, bright natural lighting, architectural"
    """)

# Footer
st.markdown("---")
st.markdown("⚡ **Rapid AI Image Generator** | Made with Streamlit | Multiple API Support")