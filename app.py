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

# Dicționarul de traducere
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

# Alăturați-vă conversației de grup cu botul-telegram: https://t.me/+2MRoAgxZpdxmZmRi

language = st.sidebar.selectbox("Select language:", ["Romanian", "English", "Russian"], index=1, key="Translation")

st.sidebar.write(f"Selected language: {language}")

trequest = HTTPXRequest(connection_pool_size=20)
bot = telegram.Bot(token='6962273873:AAFMmSB9Tk9W2jkpOJn69XMQnVjGLQLUn1U', request=trequest)

# Atașăm modelul customizat YOLO în cod
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

path = 'C:/Users/Cristi/Downloads/AI_project/streamlit/best_model.pt'

model = torch.hub.load('ultralytics/yolov5', 'custom', path, force_reload=True)

# Poza de background
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

# Funcția pentru a fi trimisă o poză de botul-telegram
async def send_photo_to_telegram(chat_id, photo):
    try:
        await bot.send_photo(chat_id=chat_id, photo=photo)
        print("Photo sent successfully to Telegram")
    except Exception as e:
        print("Error sending photo to Telegram:", e)
        
# Funcția pentru a porni o circulație de date pentru telegram
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

# Rularea funcției de a trimit foto
def send_photo(chat_id, photo):
     asyncio.run(send_photo_to_telegram(chat_id, photo))

# Funcția pentru a detecta armele respective
def detect_objects(frame, knife_confidence_threshold=0.75, knife_precision_threshold=0.75, pistol_confidence_threshold=0.85, pistol_precision_threshold=0.85):
    # Detectați obiectele din cadru
    results = model(frame)
    
    
    # Verificați dacă sunt detectate careva obiecte
    if results.xyxy[0] is not None:
        # Iterați prin obiectele detectate
        for obj in results.xyxy[0]:
            class_id = int(obj[5])  # ID-ul clasei de obiecte
            confidence = obj[4]    # Scorul de încredere(Confidence)
            precision = obj[4]    # Scorul de precizie(Precision)
            
            
            # Verificați dacă obiectul detectat este un cuțit
            if class_id == 0:
                if confidence >= knife_confidence_threshold and precision >= knife_precision_threshold :
                    return True
            
            # Verificați dacă obiectul detectat este un pistol
            elif class_id == 1:
                if confidence >= pistol_confidence_threshold and precision >= pistol_precision_threshold:
                    return True
    
   
# Nu au fost detectate obiecte care să îndeplinească cerințele specificate
    return False



# Configurarea aplicației Streamlit
st.sidebar.title(translation_dict[language]["Choose input type:"])
pages = [translation_dict[language]["Photo"], translation_dict[language]["Video"], translation_dict[language]["Live-Video (webcam)"]]
choice = st.sidebar.selectbox(translation_dict[language]["Select one of the pages"], pages)

#Pentru rubrica photo
if choice == translation_dict[language]["Photo"]:
    st.title(translation_dict[language]["Photo"])
    uploaded_file = st.sidebar.file_uploader(translation_dict[language]["Choose a photo from your PC (sweet-spot: 1920x1080 [Full HD]): "], type="jpg")
    
    if uploaded_file:
       
        # Atașați imaginea încărcată
        original_image = Image.open(uploaded_file)
        
        # Redimensionați imaginea originală la rezoluția dorită
        original_image = original_image.resize((1920, 1080))
        
        # Procesați imaginea pentru a detecta obiecte
        processed_image = model(original_image)
        
        # Afișați imaginile originale și procesate una lângă alta
        col1, col2 = st.columns(2)
        with col1:
            st.image(original_image, caption=(translation_dict[language]["Original Image"]), use_column_width=True)
        with col2:
            st.image(processed_image.render()[0], caption=(translation_dict[language]["Processed Image"]), use_column_width=True)
# Pentru rubrica video
if choice == translation_dict[language]["Video"]:
    st.title(translation_dict[language]["Video"])
    run = st.sidebar.checkbox(translation_dict[language]["Run"])
    
    st.write(translation_dict[language]["Original Video"])
    
    # Atașați videoul încărcat
    video_file = st.sidebar.file_uploader(translation_dict[language]["Upload a video file (MP4)"], type=["mp4"])
    
    if video_file:
        
        # Salvați fișierul video încărcat pe disc
        video_path = "uploaded_video.mp4"
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        
        # Afișează videoclipul original ca fundal principal
        st.video(video_file)
        
        FRAME_WINDOW = st.image([])
        video_capture = cv2.VideoCapture(video_path)
        replay_button_clicked = False
        replay_button_key = "replay_button"
        
        # Creați butonul de reluare în afara buclei
        st.write(translation_dict[language]["Processed Video"])

        replay_button_clicked = st.button(translation_dict[language]["Replay Processed Video"], key=replay_button_key)
        
        
        # Procesați cadrele video
        
        while run:
            ret, frame = video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = model(frame)  # Efectuați inferența direct pe cadru
                
                # Redarea cadrelor video procesate
                processed_frame = results.render()[0]
                processed_image = Image.fromarray(processed_frame)
                FRAME_WINDOW.image(processed_image, use_column_width=True)
                
                # Verificați dacă butonul de reluare a fost apăsat
                if replay_button_clicked:
                    replay_button_clicked = False
                    video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Redați din nou videoclipul
                
            else:
                # Eliberați captura video când videoclipul se termină
                video_capture.release()
                break


# Pentru rubrica web-cam
if choice == translation_dict[language]["Live-Video (webcam)"]:
    st.title(translation_dict[language]["Live-Video (webcam)"])
    run = st.sidebar.checkbox(translation_dict[language]["Run"])
    FRAME_WINDOW = st.image([])
    camera = cv2.VideoCapture(0)
    # Setarea rezoluției camerei
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    
    # Adăugați o casetă de selectare pentru interacțiunea utilizatorului
    types = [translation_dict[language]["Multiple Frames"], translation_dict[language]["Single Frame"]]
    telegram_option = st.sidebar.selectbox(translation_dict[language]["Select Telegram Notification Option"], types, key="telegram_option_message")

    while run:
        ret, frame = camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame)  # Efectuați inferența direct pe cadru
            processed_frame = results.render()[0]
            FRAME_WINDOW.image(processed_frame, use_column_width=True)
            if detect_objects(processed_frame):
                # Trimiteți multiple cadre 
                if telegram_option == translation_dict[language]["Multiple Frames"]:
                    # Convertiți cadrul procesat în octeți(bytes)
                    img_byte_array = BytesIO()
                    Image.fromarray(processed_frame).save(img_byte_array, format='JPEG')
                    img_byte_array.seek(0)
                    # Trimite fotografia la Telegram într-un fir separat
                    threading.Thread(target=send_photo, args=('-1002095049360', img_byte_array)).start() 
                    

                else:  # Trimiteți un singur cadru
                    if not st.session_state.object_detected:  # Verificați dacă un obiect nu a fost detectat anterior
                        st.session_state.object_detected = True
                        img_byte_array = BytesIO()
                        Image.fromarray(processed_frame).save(img_byte_array, format='JPEG')
                        img_byte_array.seek(0)
                        # Trimite fotografia la Telegram într-un fir separat
                        threading.Thread(target=send_photo, args=('-1002095049360', img_byte_array)).start() 
                        

                       # Setați object_detected la True pentru a evita trimiterea mai multor cadre
                    st.session_state.object_detected = True
else:
    # Resetați starea sesiunii dacă nu sunt detectate obiecte
    st.session_state.object_detected = False


                



