import streamlit as st
import streamlit.components.v1 as components 
import cv2 
import numpy as np 
from ultralytics import YOLO
import streamlit_option_menu as option_menu
from PIL import Image, ImageDraw
import io
import tempfile
import imageio.v2 as imageio
from moviepy.editor import ImageSequenceClip
import os
import shutil
from ultralytics.yolo.utils.plotting import Annotator
from cv2 import cvtColor
import os
import time

#Importing the model

model = YOLO('best.pt')
def bgr2rgb(image):
    return image[:, :, ::-1]


    
def process_video(video_path):
    # Load the video
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None:
        fps = 30  # Set a default value for fps if it is 0 or None

    # Create a list to store the processed frames
    processed_frames = []

    # Process each frame in the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform the prediction on the frame
        prediction = model.predict(frame)
        frame_with_bbox = prediction[0].plot()

        # Convert the frame to PIL Image and store in the list
        processed_frames.append(Image.fromarray(frame_with_bbox))

    cap.release()

    # Create the output video file path
    video_path_output = "output.mp4"

    # Save the processed frames as individual images
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, frame in enumerate(processed_frames):
            frame.save(f"{temp_dir}/frame_{i}.png")

        # Create a video clip from the processed frames
        video_clip_path = f"{temp_dir}/clip.mp4"
        os.system(f"ffmpeg -framerate {fps} -i {temp_dir}/frame_%d.png -c:v libx264 -pix_fmt yuv420p {video_clip_path}")

        # Rename the video clip with the desired output path
        shutil.copy2(video_clip_path, video_path_output)

    return video_path_output


def main():

    with open("styles.css", "r") as source_style:
        st.markdown(f"<style>{source_style.read()}</style>", 
             unsafe_allow_html = True)
        
    st.title("AI Road Inspection System")
    Header = st.container()
    js_code = """
        const elements = window.parent.document.getElementsByTagName('footer');
        elements[0].innerHTML = "Siddaganga Institute of Technology " + new Date().getFullYear();
        """
    st.markdown(f"<script>{js_code}</script>", unsafe_allow_html=True)
            
    
    ##MainMenu
    
    with st.sidebar:
        selected = option_menu.option_menu(
            "Main Menu",
            options=[
                "Project Information",
                "Model Information",           
                "Predict Defects",
            ],
        )
    
    st.sidebar.markdown('---')
        
    ##HOME page 
    
    if selected == "Project Information":
        
        st.subheader("Problem Statement")
        problem_statement = """
        Current practices of performing road inspections are time-consuming and labour-intensive. Road surfaces degrade on a 
        daily basis as a result of the heavy traffic on them.This will not only impact the driver’s comfort but will also
        impact economic efficiency. To maintain roads as efficiently as possible, municipalities perform regular
        inspections. The aim of the project is to use machine learning to study and analyze different types of road defects
        and to automatically detect any road abnormalities.
        """
        
        st.write(problem_statement)
        
        with st.expander("Read More"): 
            text = """
        The goal of this project is to design, build and test an inspection system for detecting road abnormalities, defects, and damages
        using machine learning. The proposed system aims to improve the efficiency of road inspections and reduce
        the time and labor required for the process. The system will be equipped with a camera to capture video streams
        from different roads, and the data will be analyzed using the Matlab machine learning toolbox to train and test the network.
        The output of the system will be recommended actions for the municipality to fix/correct any identified road defects. 
        The approach will involve three main tasks: data acquisition, data training/testing, and dashboard building and testing. 
        Ultimately, the proposed system will help to maintain roads more efficiently, enhance driver comfort, and improve economic 
        efficiency. Additionally, the system will provide insights into the causes of road abnormalities in Indian roads, 
        including pitfalls, sinks, flooding, and traffic congestion due to insufficient lanes in cities and towns."""
            
            st.write(text)
        
        st.subheader("Our Solution")
        Project_goal = """
        Our Team developed a Machine Learning ( ML ) model based on the YOLOv8 Architecture, which was trained on a comprehensive
        dataset of road images and manuallyannotated them to highlight the various types of road defects. Once the model was trained,
        we proceeded to test its performance on new and unseen data. This testing phase was vital to ensure that our model could
        generalize well and accurately identify road defects in real-world scenarios.In addition to the model,
        we developed a web application using the Streamlit API which serves as a user friendly interface for others to test the 
        trained model on their own videos and images
        """
        st.write(Project_goal)
        
    elif selected == "Predict Defects": 
        st.sidebar.subheader('Settings')
        
        options = st.sidebar.radio(
            'Options:', ('Image', 'Video'), index=1)
    
        st.sidebar.markdown("---")
    
        # Image
        if options == 'Image':
            upload_img_file = st.sidebar.file_uploader(
                'Upload Image', type=['jpg', 'jpeg', 'png'])
            if upload_img_file is not None:
                # Start timing
                start_time = time.time()
            
                file_bytes = np.asarray(bytearray(upload_img_file.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)

                prediction = model.predict(img)
                res_plotted = prediction[0].plot()
            
                # End timing
                end_time = time.time()
                elapsed_time = end_time - start_time

                # Display timing information
                st.write(f"Processing time: {elapsed_time:.2f} seconds")

                image_pil = Image.fromarray(res_plotted)
                image_bytes = io.BytesIO()
                image_pil.save(image_bytes, format='PNG')

                st.image(image_bytes, caption='Predicted Image', use_container_width=True)
            
        # Video
        if options == 'Video':
            upload_vid_file = st.sidebar.file_uploader(
                'Upload Video', type=['mp4', 'avi', 'mkv']
            )
            if upload_vid_file is not None:
                # Save the uploaded video file temporarily
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(upload_vid_file.read())

                # Start timing
                start_time = time.time()

                # Process the video
                video_path_output = process_video(temp_file.name)
            
                # End timing
                end_time = time.time()
                elapsed_time = end_time - start_time

                # Calculate frame rate
                cap = cv2.VideoCapture(temp_file.name)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                frame_rate = frame_count / elapsed_time if elapsed_time > 0 else 0

                # Display timing information
                st.write(f"Processing time: {elapsed_time:.2f} seconds")
                st.write(f"Total frames: {frame_count:.2f} frames")
                st.write(f"Processed frame rate: {frame_rate:.2f} FPS")

                # Display the processed video
                st.video(video_path_output)

                # Remove the temporary files
                temp_file.close()
                os.remove(video_path_output)

    elif selected == "Model Information":
        st.subheader('Introduction')
        Introduction = """
        The Ai road Inspection system , is an innovatiove solution that leverages computer vision and deep learning techniques
        to improve the road inspection and analysis. Traditional road Inspection methods often rely on manual labour 
        which is time consuming  and prone to human error. The AI road inspection system aims to address these limitations by enabling 
        real time detection, classification and analysis of various objects and anomalies on roads including potholes, cracks and 
        alligator cracks. 
        """
        st.write(Introduction)
        st.subheader('Architecture')
        Architecture = """
        The architecture of YOLO consists of a convolutional neural network i.e CNN which is inspired by GoogleNet 
        and is composed of several convolutional layers followed by fully connected layers: This means that the YOLO 
        architecture is made up of two types of layers - convolutional and fully connected layers. Convolutional
        layers are used to extract features from the input image, while fully connected layers are used to predict the
        class probabilities and bounding boxes for each object detected in the image.YOLO also uses various other techniques
        like anchor boxes, class prediction objectness score etc.., Which makes it efficient and accurate object detection
        algorithm that can process images in real-time, making it well-suited for applications such as self-driving cars,
        surveillance systems, and robotics.

        """
        st.write(Architecture)
        st.image('architecture.jpg')
        st.subheader('Training')
        Training = """
        The YOLOv8 model used in the AI Road Inspection System is trained on a large dataset of road images which were
        annotated with bounding boxes and class labels on Roboflow.Roboflow offers a range of datasets and annotation 
        tools specifically designed for computer vision and also provides a user-friendly interface and annotation 
        capabilities that stremline the process of labeling and preparing datasets for training machine learning models. 
        The training data includes diverse road conditions, different types of objects, and various environmental factors
        to ensure the model's generalization capability.
        
        """
        st.write(Training)
        st.subheader("Conclusion")
        conclusion = """
        The model is hence a cutting -edge solution that offers significant advancements over traditional manual inspection methods. 
        With its real time capabilities, the Ai Road Inspection System provides timely and accurate identification of road anomalies 
        such as potholes , cracks and alligator crakcs.This enables road maintenance teams to prioritize repairs efficiently, leading
        to improved road safety and optimized maintenance operations. 

        """
        st.write(conclusion)   
if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    