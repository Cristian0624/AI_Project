import streamlit as st
from PIL import Image
import cv2
import numpy as np
import torch
import telegram
from io import BytesIO
import pathlib
import threading
import asyncio
from telegram.request import HTTPXRequest

translation_dict = {
    
    "Romanian": {
        "Choose input type:": "Alegeți tipul de intrare:",
        "Select one of the pages": "Selectați una dintre pagini",
        "Choose a photo from your PC (sweet-spot: 1920x1080 [Full HD]): ": "Alegeți o fotografie de pe PC (rezoluția ideală: 1920x1080 [Full HD]):",
        "Upload a video file (MP4)": "Încărcați un fișier video (MP4)",
        "Live-Video (webcam)": "Video live (webcam)",
        "Run": "Rulează",
        "Photo": "Imagine", 
        "Video": "Videou",
        "Live-Video (webcam)": "Camera Web",
        "Original Image": "Imaginea Originală",
        "Processed Image": "Imaginea  Procesată",
        "Original Video": "Videoul Original",
        "Processed Video": "Videoul Procesat",
        "Select Telegram Notification Option": "Selectați opțiunea de notificare Telegram",
        "Multiple Frames": "Cadre multiple(mesaje spam)",
        "Single Frame": "Cadru singur(un singur mesaj)",
        "Selected language:": "Limba selectată:",
        "Replay Processed Video": "Reluează Videoul Procesat"
        
    },
    "English": {
        "Choose input type:": "Choose input type:",
        "Select one of the pages": "Select one of the pages",
        "Choose a photo from your PC (sweet-spot: 1920x1080 [Full HD]): ": "Choose a photo from your PC (sweet-spot: 1920x1080 [Full HD]):",
        "Upload a video file (MP4)": "Upload a video file (MP4)",
        "Live-Video (webcam)": "Live-Video (webcam)",
        "Run": "Run",
        "Photo": "Photo", 
        "Video": "Video",
        "Live-Video (webcam)": "Live-Video (webcam)",
        "Original Image": "Original Image",
        "Processed Image": "Processed Image",
        "Original Video": "Original Video",
        "Processed Video": "Processed Video",
        "Select Telegram Notification Option": "Select Telegram Notification Option",
        "Multiple Frames": "Multiple Frames",
        "Single Frame": "Single Frame",
        "Selected language:": "Selected language:",
        "Replay Processed Video": "Replay Processed Video"
       

    },
    "Russian": {
        "Choose input type:": "Выберите тип ввода:",
        "Select one of the pages": "Выберите одну из страниц:",    
        "Choose a photo from your PC (sweet-spot: 1920x1080 [Full HD]): ": "Выберите фотографию с вашего ПК (оптимальный размер: 1920x1080 [Full HD]):",   
        "Upload a video file (MP4)": "Загрузите видеофайл (MP4):",     
        "Live-Video (webcam)": "Видео в режиме реального времени (веб-камера):",         
        "Run": "Запустить",
        "Photo": "Фото", 
        "Video": "видео",
        "Live-Video (webcam)": "Живое видео (веб-камера)",
        "Original Image": "Исходное изображение",
        "Processed Image": "Обработанное изображение", 
        "Original Video": "Оригинальное видео",
        "Processed Video": "Обработанное видео",    
        "Select Telegram Notification Option": "Выберите опцию уведомлений Telegram:",         
        "Multiple Frames": "Несколько кадров", 
        "Single Frame": "Одиночный кадр",      
        "Selected language:": "Выбранный язык:",      
        "Replay Processed Video": "Переиграть обработанное видео"
       
    }
}


language = st.sidebar.selectbox("Select language:", ["Romanian", "English", "Russian"], index=1, key="Translation")

st.sidebar.write(f"Selected language: {language}")

trequest = HTTPXRequest(connection_pool_size=20)
bot = telegram.Bot(token='6962273873:AAFMmSB9Tk9W2jkpOJn69XMQnVjGLQLUn1U', request=trequest)

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

path = 'C:/Users/Cristi/Downloads/AI_project/streamlit/best_model.pt'

model = torch.hub.load('ultralytics/yolov5', 'custom', path, force_reload=True)


page_element="""
<style>
[data-testid="stAppViewContainer"]{
  background-image: url("https://wallpapers.com/images/hd/gun-background-3djkqt0gqs71w2n6.jpg");
  background-size: cover;
}
[data-testid="stHeader"]{
  background-color: rgba(0,0,0,0);
}
</style>
"""

st.markdown(page_element, unsafe_allow_html=True)


async def send_photo_to_telegram(chat_id, photo):
    try:
        await bot.send_photo(chat_id=chat_id, photo=photo)
        print("Photo sent successfully to Telegram")
    except Exception as e:
        print("Error sending photo to Telegram:", e)

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
asyncio.set_event_loop(st.session_state.loop)


def send_photo(chat_id, photo):
     asyncio.run(send_photo_to_telegram(chat_id, photo))

def detect_objects(frame, knife_confidence_threshold=0.75, knife_precision_threshold=0.75, pistol_confidence_threshold=0.85, pistol_precision_threshold=0.85):
    # Detect objects in the frame
    results = model(frame)
    
    
    # Check if any objects are detected
    if results.xyxy[0] is not None:
        # Iterate through detected objects
        for obj in results.xyxy[0]:
            class_id = int(obj[5])  # Class ID
            confidence = obj[4]     # Confidence score
            precision = obj[4]
            
            # Check if the detected object is a knife
            if class_id == 0:
                if confidence >= knife_confidence_threshold and precision >= knife_precision_threshold :
                    return True
            # Check if the detected object is a pistol
            elif class_id == 1:
                if confidence >= pistol_confidence_threshold and precision >= pistol_precision_threshold:
                    return True
    
    # No objects meeting the specified thresholds were detected
    return False



# Streamlit app setup
st.sidebar.title(translation_dict[language]["Choose input type:"])
pages = [translation_dict[language]["Photo"], translation_dict[language]["Video"], translation_dict[language]["Live-Video (webcam)"]]
choice = st.sidebar.selectbox(translation_dict[language]["Select one of the pages"], pages)

if choice == translation_dict[language]["Photo"]:
    st.title(translation_dict[language]["Photo"])
    uploaded_file = st.sidebar.file_uploader(translation_dict[language]["Choose a photo from your PC (sweet-spot: 1920x1080 [Full HD]): "], type="jpg")
    
    if uploaded_file:
        # Load the uploaded image
        original_image = Image.open(uploaded_file)
        
        # Resize the original image to the desired resolution
        original_image = original_image.resize((1920, 1080))
        
        # Process the image to detect objects
        processed_image = model(original_image)
        
        # Display the original and processed images side by side
        col1, col2 = st.columns(2)
        with col1:
            st.image(original_image, caption=(translation_dict[language]["Original Image"]), use_column_width=True)
        with col2:
            st.image(processed_image.render()[0], caption=(translation_dict[language]["Processed Image"]), use_column_width=True)

if choice == translation_dict[language]["Video"]:
    st.title(translation_dict[language]["Video"])
    run = st.sidebar.checkbox(translation_dict[language]["Run"])
    
    st.write(translation_dict[language]["Original Video"])
    # Add another option for video input
    video_file = st.sidebar.file_uploader(translation_dict[language]["Upload a video file (MP4)"], type=["mp4"])
    
    if video_file:
        # Save the uploaded video file to disk
        video_path = "uploaded_video.mp4"
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        
        # Display the original video as the main background
        st.video(video_file)
        
        FRAME_WINDOW = st.image([])
        video_capture = cv2.VideoCapture(video_path)
        replay_button_clicked = False
        replay_button_key = "replay_button"
        
        # Create the replay button outside the loop
        st.write(translation_dict[language]["Processed Video"])

        replay_button_clicked = st.button(translation_dict[language]["Replay Processed Video"], key=replay_button_key)
        
        # Process the video frames
        
        while run:
            ret, frame = video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = model(frame)  # Perform inference directly on the frame
                
                # Processed video frames rendering
                processed_frame = results.render()[0]
                processed_image = Image.fromarray(processed_frame)
                FRAME_WINDOW.image(processed_image, use_column_width=True)
                
                # Check if the replay button is clicked
                if replay_button_clicked:
                    replay_button_clicked = False
                    video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Rewind the video
                
            else:
                # Release video capture when the video ends
                video_capture.release()
                break



if choice == translation_dict[language]["Live-Video (webcam)"]:
    st.title(translation_dict[language]["Live-Video (webcam)"])
    run = st.sidebar.checkbox(translation_dict[language]["Run"])
    FRAME_WINDOW = st.image([])
    camera = cv2.VideoCapture(0)
    #Setting the camera resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Add a selectbox for user interaction
    types = [translation_dict[language]["Multiple Frames"], translation_dict[language]["Single Frame"]]
    telegram_option = st.sidebar.selectbox(translation_dict[language]["Select Telegram Notification Option"], types, key="telegram_option_message")

    while run:
        ret, frame = camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame)  # Perform inference directly on the frame
            processed_frame = results.render()[0]
            FRAME_WINDOW.image(processed_frame, use_column_width=True)
            if detect_objects(processed_frame):
                if telegram_option == translation_dict[language]["Multiple Frames"]:
                    # Convert the processed frame to bytes
                    img_byte_array = BytesIO()
                    Image.fromarray(processed_frame).save(img_byte_array, format='JPEG')
                    img_byte_array.seek(0)
                    # Send the photo to Telegram in a separate thread
                    threading.Thread(target=send_photo, args=('-1002095049360', img_byte_array)).start() 
                    

                else:  # Send only one frame
                    if not st.session_state.object_detected:  # Check if an object was not previously detected
                        st.session_state.object_detected = True
                        img_byte_array = BytesIO()
                        Image.fromarray(processed_frame).save(img_byte_array, format='JPEG')
                        img_byte_array.seek(0)
                        # Send the photo to Telegram in a separate thread
                        threading.Thread(target=send_photo, args=('-1002095049360', img_byte_array)).start() 
                        

                        # Set object_detected to True to avoid sending multiple frames
                    st.session_state.object_detected = True
else:
    # Reset the session state if no objects are detected
    st.session_state.object_detected = False


                



