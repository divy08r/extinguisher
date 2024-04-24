import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, db, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(
        page_title="Emergency Alert",
        page_icon="🔥",
        initial_sidebar_state="expanded",
    )
    
gif_url = "images/alertgif.gif"
st.sidebar.image(gif_url, use_column_width=True)


# Set custom CSS styles
st.markdown(
        """
        <style>
        .container {
            max-width: 800px;
        }
        .title {
            text-align: center;
            font-size: 35px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .description {
            margin-bottom: 30px;
        }
        .instructions {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        [data-testid="stHeader"]
        {
            background-color: #2a7c2a;
        }
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        [data-testid= "stAppViewContainer"]{
            /* background: url('https://t4.ftcdn.net/jpg/02/82/46/67/360_F_282466772_lGY7jncjqt2Gjc9jbJYiCyIGmN1x5hgh.jpg');
            background-size: cover; 
            */
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )

    # App title
st.markdown('''
        <style>
        .styled-text {
            font-family: 'Arial', sans-serif;
            font-size: 36px;
            color: darkred; 
            text-align: center;
            text-transform: uppercase; 
            text-shadow: 2px 2px 4px #000000;
            padding: 10px; 
            margin: 20px;  
            background-color: #f5f5f5;  
            border: 1px solid #333;  
            border-radius: 10px;
        }
    </style>

    <div class="styled-text">Send Emergency Alert</div>''', 
    unsafe_allow_html=True)


# Function to send an email alert
def send_email(to_email, subject, message):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "2021ugcs049@nitjsr.ac.in" 
    smtp_password = "lpqmchwljzvvppis"  

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password) 
        server.send_message(msg) 
        server.quit()

        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Function to get all documents from a collection
def fetch_all_documents(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()

    doc_list = [doc.to_dict() for doc in docs]
    return doc_list


st.subheader("Send Alert to all")

subject = st.text_input("Subject", "❗Alert there is a fire❗")
message = st.text_area("Message", """A forest fire has been detected near your area.
Please stay safe and take necessary precautions.""")

if st.button("Send"):
    collection_name = "users"
    data = fetch_all_documents(collection_name)
    result = ""
    if data:
        for i in data:
            user_email = i["email"]
            result = send_email(user_email, subject, message)

    else:
        st.write("No data found in the specified collection.")

    st.write(result)

st.subheader("Add New User")

# Add new user
name = st.text_input("Name:")
email = st.text_input("Email:")
user_data = {"name": name, "email": email}

# Adding a document to Firestore
if st.button("Add User"):
    result = db.collection("users").add(user_data)
    st.write("Added user data to Firestore")



# Include Font Awesome CSS for the icons
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
    /* Custom footer style */
    .footer {
        /* Keeps the footer at the bottom */
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2a7c2a; /* Dark background for contrast */
        color: white;
        text-align: center;
        padding: 10px;
        padding-bottom: 1rem; 
    }

    .footer a {
        color: white;
        margin: 0 10px;
        text-decoration: none;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="footer">
        <a href="https://github.com/divy08r" target="_blank" title="GitHub">
            <i class="fab fa-github"></i>
        </a>
        <a href="https://www.linkedin.com/in/divya-rani-95a55522b/" target="_blank" title="LinkedIn">
            <i class="fab fa-linkedin"></i>
        </a>
        <a href="https://www.facebook.com/profile.php?id=61550635601613&sfnsn=wiwspwa&mibextid=RUbZ1f" target="_blank" title="Facebook">
            <i class="fab fa-facebook"></i>
        </a>
        <a href="mailto:div8032003@gmail.com" title="Email">
            <i class="fas fa-envelope"></i>
        </a>
        <a href="https://www.instagram.com/divya.rani.08" target="_blank" title="Instagram">
            <i class="fab fa-instagram"></i>
        </a>
        <br> 
        <br>
        <p>© 2024 Copyright --
        <a href="https://github.com/divy08r/extinguisher" target="_blank" title="Repo">
        Extinguisher
        </a>
        </p> 
    </div>
    """,
    unsafe_allow_html=True,
)
