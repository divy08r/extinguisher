import streamlit as st
import cv2
from ultralytics import YOLO
import requests
from PIL import Image
import os
from glob import glob
from numpy import random
import io

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

@st.cache_resource
def load_model(model_path):
    model = YOLO(model_path)
    return model

def predict_image(model, image, conf_threshold, iou_threshold):
    res = model.predict(
        image,
        conf=conf_threshold,
        iou=iou_threshold,
        device='cpu',
    )
    
    class_name = model.model.names
    classes = res[0].boxes.cls
    class_counts = {}
    
    for c in classes:
        c = int(c)
        class_counts[class_name[c]] = class_counts.get(class_name[c], 0) + 1

    # Generate prediction text
    prediction_text = 'Predicted '
    for k, v in sorted(class_counts.items(), key=lambda item: item[1], reverse=True):
        prediction_text += f'{v} {k}'
        
        if v > 1:
            prediction_text += 's'
        
        prediction_text += ', '

    prediction_text = prediction_text[:-2]
    if len(class_counts) == 0:
        prediction_text = "No objects detected"

    # Calculate inference latency
    latency = sum(res[0].speed.values())  # in ms, need to convert to seconds
    latency = round(latency / 1000, 2)
    prediction_text += f' in {latency} seconds.'

    # Convert the result image to RGB
    res_image = res[0].plot()
    res_image = cv2.cvtColor(res_image, cv2.COLOR_BGR2RGB)
    
    return res_image, prediction_text

def main():
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="Wildfire Detection",
        page_icon="🔥",
        initial_sidebar_state="expanded",
    )
    

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

    <div class="styled-text">Forest Fire Detection</div>''', 
    unsafe_allow_html=True)

    # Display an image from a URL
    image_url = "images/introgif.gif"  # Online image
    st.image(image_url, use_column_width=True)

    # side bar description
    gif_url = "images/sidebargif.gif"
    st.sidebar.image(gif_url, use_column_width=True)

    st.sidebar.markdown("The website uses an innovative method to detect forest fires. It can find out if there's a fire in an image. Plus, drones are often used to watch forests. You can upload drone videos to the website, and it will detect if there's a fire in them. The website also has a database with the email addresses of local people. If there's an emergency, you can send an alert to everyone with just one click.")


  
    # Description
    st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    <div style='text-align: center;'>
        
    </div>
    """,
    unsafe_allow_html=True
)

    # Add a separator
    st.markdown("---")
    
    col1, col2 = st.columns(2)  # This creates a two-column layout

    # Insert image in the left column
    with col1:
        st.image("https://static.vecteezy.com/system/resources/previews/040/289/596/non_2x/ai-generated-deer-forest-fire-trees-in-smoke-flames-photo.jpg", use_column_width=True)

    # Insert text in the right column
    with col2:
        st.write(
            """
            Forest fires are intense fires that engulf forests, grasslands, or wooded areas. They can be caused by lightning strikes, campfires, or carelessly discarded cigarettes. These fires can spread rapidly, damaging trees, wildlife, and homes. The smoke makes it difficult to breathe and can force people to evacuate. Preventing forest fires is crucial for protecting nature and ensuring community safety.
            """
        )

    # Load the selected model
    model_path = "./model/best.pt"
    model = load_model(model_path)

    # Add a section divider
    st.markdown("---")

    
    # Image selection
    image = None
    image_source = st.radio("Select image source:", ("Enter URL", "Upload from Computer"))
    if image_source == "Upload from Computer":
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
        else:
            image = None

    else:
        url = st.text_input("Enter the image URL:")
        if url:
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    image = Image.open(response.raw)
                else:
                    st.error("Error loading image from URL.")
                    image = None
            except requests.exceptions.RequestException as e:
                st.error(f"Error loading image from URL: {e}")
                image = None

    if image:
        with st.spinner("Detecting"):
            iou_threshold = 0.5
            conf_threshold = 0.5
            prediction, text = predict_image(model, image, conf_threshold, iou_threshold)
            st.image(prediction, caption="Prediction", use_column_width=True)
            st.success(text)
        
        prediction = Image.fromarray(prediction)

        image_buffer = io.BytesIO()

        prediction.save(image_buffer, format='PNG')

        st.download_button(
            label='Download Prediction',
            data=image_buffer.getvalue(),
            file_name='prediciton.png',
            mime='image/png'
        )

    # Add a section divider
    st.markdown("---")

    # News card
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://i.guim.co.uk/img/static/sys-images/Guardian/Pix/pictures/2009/2/7/1234009239322/Australian-firefighters-t-001.jpg?width=465&dpr=1&s=none")
        st.subheader("Australia in 2009")
        st.write("On February 7, 2009, 'Black Saturday' bushfires in Victoria, Australia, killed 173 people, making it the country's deadliest bushfire. Whole towns and over 2,000 homes were destroyed during extreme weather, resulting in Australia's highest loss of human life from a bushfire.")

    with col2:
        st.image("https://c.files.bbci.co.uk/11C74/production/_130502827_gettyimages-1551690680.jpg")
        st.subheader("Algeria in 2021 and 2022")
        st.write("In August 2021, over 90 people, including 33 soldiers, died in Algeria due to multiple wildfires. A year later, in August 2022, massive blazes in northeastern El Tarf province, near Tunisia's border, claimed 37 lives over several days. ")

    with col3:
        st.image("https://media.cnn.com/api/v1/images/stellar/prod/170618083543-03-portugal-wirldfire-0618.jpg?q=w_4000,h_2250,x_0,y_0,c_fill")
        st.subheader("Portugal in 2017")
        st.write("In June 2017, Portugal's wildfires broke out in Leiria, killing 63 people as they burned through pine and eucalyptus forests for five days. Many were trapped in cars while trying to escape. In October, new fires erupted in northern Portugal, killing 45 people and four in neighboring Spain.")

    # Add a section divider
    st.markdown("---")
    

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


        
if __name__ == "__main__":
    main()