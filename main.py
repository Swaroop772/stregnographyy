import streamlit as st
import numpy as np
import cv2

# Function to encode the message into the image
def encode_message(image, message):
    d = {chr(i): i for i in range(255)}  # Mapping characters to pixel values
    img = np.array(image)
    m, n, z = 0, 0, 0
    
    for char in message:
        img[n, m, z] = d[char]  # Embed the message into the pixel values
        n = (n + 1) % img.shape[0]
        m = (m + 1) % img.shape[1]
        z = (z + 1) % 3
    
    return img

# Function to decode the message from the image
def decode_message(image, message_length, passcode, stored_passcode):
    if passcode != stored_passcode:  # Check for correct passcode
        return "Incorrect passcode. Decryption failed."
    
    c = {i: chr(i) for i in range(255)}  # Mapping pixel values to characters
    img = np.array(image)
    m, n, z = 0, 0, 0
    message = ""
    
    try:
        for _ in range(message_length):  # Extract the message based on length
            message += c[img[n, m, z]]
            n = (n + 1) % img.shape[0]
            m = (m + 1) % img.shape[1]
            z = (z + 1) % 3
    except KeyError:
        return "Message extraction error."
    
    return message

# Streamlit interface
st.title("Secure Data Hiding in Image Using Steganography")

# Define a simple passcode for encryption and decryption (This is for demonstration purposes)
# In a real application, the passcode should be securely stored and retrieved
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
            # Store the passcode in session state
            st.session_state['stored_passcode'] = passcode

            encrypted_img = encode_message(image, message)
            cv2.imwrite("encrypted_image.png", encrypted_img)
            st.success("Message encrypted and saved as encrypted_image.png")
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
                st.warning("Passcode was not set during encryption.")
            else:
                decrypted_message = decode_message(image, message_length, passcode, stored_passcode)
                if decrypted_message:
                    st.success(f"Decrypted Message: {decrypted_message}")
                else:
                    st.warning("Incorrect passcode or no hidden message found.")
