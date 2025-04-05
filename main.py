import streamlit as st
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, storage
import os

# Initialize Firebase (only once)
if 'firebase_initialized' not in st.session_state:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'my-stegano-project.appspot.com'
    })
    st.session_state['firebase_initialized'] = True

# Encode message into the image
def encode_message(image, message):
    d = {chr(i): i for i in range(255)}  # char to int map
    img = np.array(image)
    m, n, z = 0, 0, 0

    for char in message:
        img[n, m, z] = d[char]
        n = (n + 1) % img.shape[0]
        m = (m + 1) % img.shape[1]
        z = (z + 1) % 3

    return img

# Decode message from image
def decode_message(image, message_length, passcode, stored_passcode):
    if passcode != stored_passcode:
        return "Incorrect passcode. Decryption failed."

    c = {i: chr(i) for i in range(255)}  # int to char map
    img = np.array(image)
    m, n, z = 0, 0, 0
    message = ""

    try:
        for _ in range(message_length):
            message += c[img[n, m, z]]
            n = (n + 1) % img.shape[0]
            m = (m + 1) % img.shape[1]
            z = (z + 1) % 3
    except KeyError:
        return "Message extraction error."

    return message

st.title("🔐 Secure Data Hiding in Image Using Steganography")

stored_passcode = st.session_state.get('stored_passcode', None)

option = st.radio("Choose an option:", ("Encrypt Message", "Decrypt Message"))

if option == "Encrypt Message":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(image, caption="Original Image", use_column_width=True, channels="BGR")

        message = st.text_input("Enter your secret message:")
        passcode = st.text_input("Enter a passcode for encryption:", type="password")

        if st.button("Encrypt and Save Image"):
            st.session_state['stored_passcode'] = passcode
            encrypted_img = encode_message(image, message)

            # Save locally
            local_path = "encrypted_image.png"
            cv2.imwrite(local_path, encrypted_img)
            st.success(f"✅ Encrypted image saved locally at {local_path}")

            # Save to Firebase Cloud
            img_bytes = cv2.imencode(".png", encrypted_img)[1].tobytes()
            bucket = storage.bucket()
            blob = bucket.blob("encrypted_image.png")
            blob.upload_from_string(img_bytes, content_type="image/png")
            st.success("☁️ Encrypted image uploaded to Firebase Cloud Storage.")

            # Store message length in session
            st.session_state['message_length'] = len(message)

            st.image(encrypted_img, caption="Encrypted Image", use_column_width=True, channels="BGR")

elif option == "Decrypt Message":
    uploaded_file = st.file_uploader("Upload an encrypted image", type=["jpg", "png"])
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(image, caption="Encrypted Image", use_column_width=True, channels="BGR")
        message_length = st.number_input("Enter the length of the hidden message:", min_value=1, value=10)
        passcode = st.text_input("Enter the passcode to decrypt:", type="password")

        if st.button("Decrypt Message"):
            if stored_passcode is None:
                st.warning("⚠️ Passcode was not set during encryption.")
            else:
                decrypted_message = decode_message(image, message_length, passcode, stored_passcode)
                if decrypted_message:
                    st.success(f"🔓 Decrypted Message: {decrypted_message}")
                else:
                    st.error("❌ Incorrect passcode or message extraction failed.")
