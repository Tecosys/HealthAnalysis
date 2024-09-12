from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from cerina import Completion

# Load environment variables
load_dotenv()
completions=Completion()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page configuration with title and favicon
st.set_page_config(
    page_title="Report Analysis",
    page_icon="tecosys.jpg",  # Ensure 'your_logo.png' is in the same directory or provide a full path
    layout="centered"
)

# Function to load Google Gemini Pro Vision API and get a response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash-exp-0827')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to prepare uploaded image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
def navigate_to_new_page(title, content):
    st.title(title)
    st.write(content)

# CSS for card styling
st.markdown("""
    <style>
    .card {
        background-color: #f9f9f9;
        padding: 20px;
        margin: 10px;
        border-radius: 10px;
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Create three cards for different features using columns
st.header("Report Management App")

col1, col2 = st.columns(2)


if 'page' not in st.session_state:
    st.session_state.page = 'main'

# Render cards on the main page
if st.session_state.page == 'main':
    st.text("AI can make mistakes! Reverify all the info's before taking any actions.")

# --- Nutrition Analysis Card ---
with col1:
    st.markdown('<div class="card">Nutrition Analysis</div>', unsafe_allow_html=True)
    input = ""
    uploaded_file = st.file_uploader("Upload Food Image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Analyze Nutrition"):
        input_prompt = """
        You are an expert nutritionist tasked with analyzing food items in an image.
        Calculate the calories, proteins, fat and Others provide a detailed report like this format:

        Always start with **Ingredients**
        
        Here is one format format -

        **Ingredients**
        [List of estimated ingredients]

        **Calories**
        [Name of the ingredients] - [Number of Total Calories]
 
        **Protein**
        [Name of the ingredients] - [Number of Total Proteins]

        **Fat**
        [Name of the ingredients] - [Number of Total Fat]

        **Others**
        [List of others ingredients]

        \n**Total Calories**  - 
        \n**Total Proteins** -   
        \n**Fat Estimated** -

        **Important Notes**
        [Two small paragraph of the total food analysis]

        **Disclaimer**
        ...
        For an example to understand better:

        **Ingradients**
        1. Basmati Rice - 200gm (estimated)
        2. Mutton - 150gm (estimated)

        **Calories**
        - Basmati Rice - 300-350gm calcories (estimated)
 
        **Protein**
        - Basmati Rice - 50gm proteins (estimated)

        **Fat**
        - Basmati Rice - 123gm fat (estimated)

        **Others**
        - Food Colour Noticed

        \n**Total Calories**  - 350gm (High Calories)
        \n**Total Proteins** -  50gm (Average)
        \n**Fat Estimated** -   123gm (High Fat)
        
        **Important Notes**

        According to the analysis, it is observed that user is taking huge calories and biriyani is often considered
        as un-helathy food.

        Before taking such food, make sure to take plenty of water and Don't take such food regularly

        **Disclaimer**
        AI can make mistakes, the analysis might not be correct.
        """
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input)
        st.subheader("Neutrition Analysis")
        st.write(response)

# --- Report Analysis Card ---
with col2:
    st.markdown('<div class="card">Report Analysis</div>', unsafe_allow_html=True)
    uploaded_report = st.file_uploader("Upload Medical Report...", type=["pdf", "docx", "jpg", "png"])
    
    if uploaded_report is not None:
        # Process report file (assumed to be handled in another function)
        st.write("Report uploaded successfully!")
    
    if st.button("Analyze Report"):
        report_prompt = """
        You are a healthcare expert analyzing a medical report.
        Extract key information such as patient report biomarkers, treatment plan, and observation.
        """
        # Simulate report analysis (integration with the Gemini API or another module)
        image_data1 = input_image_setup(uploaded_report)
        report_response = get_gemini_response(report_prompt, image_data1, input)
        st.subheader("Report Summary")
        st.write(report_response)

    # Risk Factor Calculator
    if st.button("Calculate Risk Factors"):
        risk_factor_prompt = """
        Based on the patient's report, identify and calculate the risk factors.
        Don't estimate any risk that is not associated with the report. Make the risk factors clear, small and concise.
        Include risks related to heart disease, diabetes, and any other conditions found in the report.
        """
        image_data2 = input_image_setup(uploaded_report)
        risk_response = get_gemini_response(risk_factor_prompt, image_data2, input)
        st.subheader("Risk Factor Analysis")
        st.write(risk_response)

# --- Chat with Prescription Bot Card ---
# Second Row: Virtual Healthcare Assistant

# Second Row: Virtual Healthcare Assistant
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Virtual Healthcare Assistant")

# Form for Virtual Healthcare Assistant input
with st.form(key="virtual_assistant_form"):
    user_age = st.text_input("Enter your age")
    family_history = st.text_input("Any family history (heart, diabetes, no)?")
    diabetic_status = st.radio("Do you have diabetes?", ("Yes", "No"))
    user_question = st.text_area("Ask a health-related question")
    
    submit_button = st.form_submit_button(label="Chat")
    
if submit_button:
    chat_prompt = f"""
    You are a virtual healthcare assistant.
    Age: {user_age}
    Family History: {family_history}
    Diabetes Status: {diabetic_status}
    User Question: {user_question}

    Analyze the user's question and provide appropriate health-related guidance with some common risk alerts.
    """
    chat_response = completions.create(chat_prompt)
    navigate_to_new_page("Virtual Healthcare Assistant", chat_response)

# Footer
st.write("Made with ❤️ Tecosys by Avishek")
