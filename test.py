from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from cerina import Completion

# Load environment variables
load_dotenv()
completion = Completion()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page configuration with title and favicon
st.set_page_config(
    page_title="Report Analysis",
    page_icon="tecosys.jpg",
    layout="centered"
)

# Function to load Google Gemini Pro Vision API and get a response
def get_gemini_response(image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash-exp-0827')
    response = model.generate_content([image[0], prompt])
    return response.text

# Function to prepare uploaded image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Define available pages
def show_main_page():
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

    col1, col2, col3 = st.columns(3)

    # --- Nutrition Analysis Card ---
    with col1:
        st.markdown('<div class="card">Nutrition Analysis</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Food Image...", type=["jpg", "jpeg", "png"], key="nutrition_upload")

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Nutrition", key="nutrition_analyze"):
            st.experimental_set_query_params(page="nutrition_analysis", uploaded_file=True)

    # --- Report Analysis Card ---
    with col2:
        st.markdown('<div class="card">Report Analysis</div>', unsafe_allow_html=True)
        uploaded_report = st.file_uploader("Upload Medical Report...", type=["pdf", "docx", "jpg", "png"], key="report_upload")

        if uploaded_report is not None:
            st.write("Report uploaded successfully!")

        if st.button("Analyze Report", key="report_analyze"):
            st.experimental_set_query_params(page="report_analysis", uploaded_report=True)

        if st.button("Calculate Risk Factors", key="risk_factors"):
            st.experimental_set_query_params(page="risk_factors", uploaded_report=True)

    # --- Chat with Prescription Bot Card ---
    with col3:
        st.markdown('<div class="card">Chat with Prescription Bot</div>', unsafe_allow_html=True)
        user_question = st.text_area("Ask the bot about your health or prescription", key="chat_input")

        if st.button("Get Prescription Advice", key="prescription_advice"):
            st.experimental_set_query_params(page="prescription_advice", question=user_question)


def show_nutrition_analysis_page():
    st.header("Nutrition Analysis Results")
    # Get the uploaded image from session state or query param
    uploaded_file = st.session_state.get("nutrition_upload")

    if uploaded_file:
        input_prompt = """
        You are an expert nutritionist tasked with analyzing food items in an image.
        Calculate the calories, proteins, fat, and others. Provide a detailed report.
        """
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data)
        st.write(response)
    else:
        st.write("No image uploaded. Go back to the main page.")

    if st.button("Back to main page"):
        st.experimental_set_query_params(page="main")


def show_report_analysis_page():
    st.header("Report Analysis Results")
    uploaded_report = st.session_state.get("report_upload")

    if uploaded_report:
        report_prompt = """
        You are a healthcare expert analyzing a medical report.
        Extract key information such as patient biomarkers, treatment plans, and observations.
        """
        report_data = input_image_setup(uploaded_report)
        report_response = get_gemini_response(report_prompt, report_data)
        st.write(report_response)
    else:
        st.write("No report uploaded. Go back to the main page.")

    if st.button("Back to main page"):
        st.experimental_set_query_params(page="main")


def show_risk_factors_page():
    st.header("Risk Factor Analysis")
    uploaded_report = st.session_state.get("report_upload")

    if uploaded_report:
        risk_factor_prompt = """
        Based on the patient's report, identify and calculate the risk factors.
        Include risks related to heart disease, diabetes, and other conditions found in the report.
        """
        risk_data = input_image_setup(uploaded_report)
        risk_response = get_gemini_response(risk_factor_prompt, risk_data)
        st.write(risk_response)
    else:
        st.write("No report uploaded. Go back to the main page.")

    if st.button("Back to main page"):
        st.experimental_set_query_params(page="main")


def show_prescription_advice_page():
    st.header("Prescription Advice")
    user_question = st.session_state.get("chat_input")

    if user_question:
        chat_prompt = f"""
        You are a virtual healthcare assistant. Answer the user's question based on their symptoms and prescriptions.
        Question: {user_question}
        """
        chat_response = completion.create(chat_prompt)
        st.write(chat_response)
    else:
        st.write("No question asked. Go back to the main page.")

    if st.button("Back to main page"):
        st.experimental_set_query_params(page="main")


# Main logic for handling page navigation
query_params = st.query_params()
page = query_params.get("page", ["main"])[0]

if page == "main":
    show_main_page()
elif page == "nutrition_analysis":
    show_nutrition_analysis_page()
elif page == "report_analysis":
    show_report_analysis_page()
elif page == "risk_factors":
    show_risk_factors_page()
elif page == "prescription_advice":
    show_prescription_advice_page()
else:
    show_main_page()
