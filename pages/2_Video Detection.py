import streamlit as st
from glob import glob
import cv2
from ultralytics import YOLO
from PIL import Image
import os
from tempfile import NamedTemporaryFile
from numpy import random
import io

st.set_page_config(
        page_title="Video-based Detection",
        page_icon="🔥",
        initial_sidebar_state="expanded",
    )

#  page title
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
        [data-testid="stSidebarContent"]
        {
            
        }
        [data-testid= "stAppViewContainer"]{
            /* background: url('https://t4.ftcdn.net/jpg/02/82/46/67/360_F_282466772_lGY7jncjqt2Gjc9jbJYiCyIGmN1x5hgh.jpg');
            background-size: cover; */
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )


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

    <div class="styled-text">Automated Forest Fire Detection System</div>''', 
unsafe_allow_html=True)

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
        </style>
        """,
        unsafe_allow_html=True
    )

# side bar description
st.sidebar.write("Demo - how it works")
gif_url = "images/vdosidebar.gif"
st.sidebar.image(gif_url, use_column_width=True)

@st.cache_resource
def load_model(model_path):
    model = YOLO(model_path)
    return model


def predict_image(model, image, conf_threshold, iou_threshold):
    res = model.predict(
        image,
        conf=conf_threshold,
        iou=iou_threshold,
        device="cpu",
    )

    class_name = model.model.names
    classes = res[0].boxes.cls
    class_counts = {}

    for c in classes:
        c = int(c)
        class_counts[class_name[c]] = class_counts.get(class_name[c], 0) + 1

    prediction_text = "Predicted "
    for k, v in sorted(class_counts.items(), key=lambda item: item[1], reverse=True):
        prediction_text += f"{v} {k}"
        
        if v > 1:
            prediction_text += "s"
        
        prediction_text += ", "

    prediction_text = prediction_text[:-2]
    if len(class_counts) == 0:
        prediction_text = "No objects detected"

    latency = sum(res[0].speed.values())  
    latency = round(latency / 1000, 2)
    prediction_text += f" in {latency} seconds."

    res_image = res[0].plot()
    res_image = cv2.cvtColor(res_image, cv2.COLOR_BGR2RGB)
    
    return res_image, prediction_text


def process_video(model, video_path, output_path, conf_threshold, iou_threshold):
    cap = cv2.VideoCapture(video_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*"XVID") 
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        res_image, _ = predict_image(model, frame, conf_threshold, iou_threshold)
        
        out.write(cv2.cvtColor(res_image, cv2.COLOR_RGB2BGR))

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "mov", "avi", "mkv"])

if uploaded_video is not None:
    temp_video = NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_video.write(uploaded_video.read())  
    temp_video.close()  

    st.video(uploaded_video)

    model_path = "../model/best.pt"
    model = load_model(model_path)

    if st.button("Process Video"):
        with st.spinner("Processing video..."):
            output_video_path = "./uploads/processed_video.mp4" 
            conf_threshold = 0.5
            iou_threshold = 0.5

            process_video(model, temp_video.name, output_video_path, conf_threshold, iou_threshold)

            st.success("The video has been processed.")


            # Download button for the processed video
            with open(output_video_path, "rb") as file:
                st.download_button(
                    label="Download Processed Video",
                    data=file.read(),
                    file_name="processed_video.mp4",
                    mime="video/mp4",
                )

            os.unlink(temp_video.name) 
            os.unlink(output_video_path) 



# footer
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