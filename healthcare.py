from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from cerina import Completion

# Load environment variables
load_dotenv()
completions = Completion()

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

    analyze_nutrition = st.button("Analyze Nutrition")

# --- Report Analysis Card ---
with col2:
    st.markdown('<div class="card">Report Analysis</div>', unsafe_allow_html=True)
    uploaded_report = st.file_uploader("Upload Medical Report...", type=["pdf", "docx", "jpg", "png"])
    
    if uploaded_report is not None:
        # Process report file (assumed to be handled in another function)
        st.write("Report uploaded successfully!")
    
    analyze_report = st.button("Analyze Report")
    calculate_risk = st.button("Calculate Risk Factors")

# Results section (full width)
if analyze_nutrition and uploaded_file is not None:
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
    AI can make mistakes, the analysis might not be correct.
    """
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    st.subheader("Nutrition Analysis")
    st.write(response)

if analyze_report and uploaded_report is not None:
    report_prompt = """
    You are a healthcare expert analyzing a medical report.
    Extract key information such as patient report biomarkers, treatment plan, and observation.
    """
    image_data1 = input_image_setup(uploaded_report)
    report_response = get_gemini_response(report_prompt, image_data1, input)
    st.subheader("Report Summary")
    st.write(report_response)

if calculate_risk and uploaded_report is not None:
    risk_factor_prompt = """
    Based on the patient's report, identify and calculate the risk factors.
    Don't estimate any risk that is not associated with the report. Make the risk factors clear, small and concise.
    Include risks related to heart disease, diabetes, and any other conditions found in the report.
    """
    image_data2 = input_image_setup(uploaded_report)
    risk_response = get_gemini_response(risk_factor_prompt, image_data2, input)
    st.subheader("Risk Factor Analysis")
    st.write(risk_response)

# --- Virtual Healthcare Assistant ---
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Virtual Healthcare Assistant")

# Initialize session state for virtual assistant
if 'virtual_assistant_data' not in st.session_state:
    st.session_state.virtual_assistant_data = {
        'age': "",
        'family_history': "",
        'diabetic_status': "",
        'initial_problem': "",
        'chat_history': []
    }

# Initial form for user details
if not st.session_state.virtual_assistant_data['initial_problem']:
    with st.form("user_details_form"):
        age = st.text_input("Enter your age")
        family_history = st.text_input("Any family history (Father, Mother, Blood Relation, no)?")
        diabetic_status = st.radio("Do you have diabetes?", ("Yes", "No"))
        initial_problem = st.text_area("Describe your health concern or question")
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            st.session_state.virtual_assistant_data.update({
                'age': age,
                'family_history': family_history,
                'diabetic_status': diabetic_status,
                'initial_problem': initial_problem
            })
            
            # Generate initial response
            initial_prompt = f"""
            You are a virtual healthcare assistant.
            Age: {age}
            Family History: {family_history}
            Diabetes Status: {diabetic_status}
            User's health concern: {initial_problem}

            Analyze the user's concern and provide appropriate health-related guidance. 
            If the concern is not clear, ask follow-up questions only.
            Or if the concern is not related to health, say "It's not related to health concern, please visit a doctor for further assistance."
            Or if the concern is emergency, say "It's an emergency, please visit a doctor immediately."
            """
            initial_response = completions.create(initial_prompt)
            st.session_state.virtual_assistant_data['chat_history'].append(("Initial Problem", initial_problem))
            st.session_state.virtual_assistant_data['chat_history'].append(("Assistant", initial_response))
            st.rerun()

# Display chat history
for role, message in st.session_state.virtual_assistant_data['chat_history']:
    if role == "Initial Problem":
        st.text(f"You: {message}")
    elif role == "You":
        st.text(f"You: {message}")
    else:
        st.markdown(f"**Assistant:** {message}")

# Chat input for follow-up questions
if st.session_state.virtual_assistant_data['initial_problem']:
    user_input = st.text_input("Your response or follow-up question:")
    if st.button("Send"):
        if user_input:
            st.session_state.virtual_assistant_data['chat_history'].append(("You", user_input))
            
            chat_prompt = f"""
            Previous conversation:
            {' '.join([f'{role}: {msg}' for role, msg in st.session_state.virtual_assistant_data['chat_history']])}
            
            User's new input: {user_input}
            
            Provide a response based on the previous context and the new input. 
            Ask follow-up questions if needed for more clarity.
            Or if the concern is not related to health, say "It's not related to health concern, I can only assist with health related concerns."
            Or if the concern is vital or serious, say "It could be a serious concern, please visit a doctor immediately."
            If there is no follow-up questions, just say "Thank you for using Tecosys Virtual Healthcare Assistant!"
            """
            
            chat_response = completions.create(chat_prompt)
            st.session_state.virtual_assistant_data['chat_history'].append(("Assistant", chat_response))
            st.rerun()

# Footer
st.write("Made with ❤️ Tecosys by Avishek")
