import gradio as gr
from emotion_detector import EmotionDetector
from encryptor import encrypt_message, decrypt_message

det = EmotionDetector()

def process_text(message):
    try:
        # Step 1 – Detect emotion
        emotions = det.detect_emotion(message)
        print(f"Detected emotions: {emotions}")

        # Step 2 – Encrypt text
        encrypted_text, encrypted_key = encrypt_message(message)
        print(f"Encrypted text: {encrypted_text}")

        # Step 3 – Decrypt text
        decrypted_text = decrypt_message(encrypted_text, encrypted_key)
        print(f"Decrypted text: {decrypted_text}")

        return encrypted_text, encrypted_key, ", ".join(emotions), decrypted_text, ", ".join(emotions)

    except Exception as e:
        print("⚠️ ERROR OCCURRED:", e)
        return "Error", "Error", "Error", "Error", "Error"

# Gradio UI
iface = gr.Interface(
    fn=process_text,
    inputs=gr.Textbox(lines=4, label="Enter your message"),
    outputs=[
        gr.Textbox(label="Encrypted Text"),
        gr.Textbox(label="Encrypted Signature"),
        gr.Textbox(label="Detected Emotion (client)"),
        gr.Textbox(label="Decrypted Text"),
        gr.Textbox(label="Detected Emotion (server)"),
    ],
    title="🧠 Emotion Cipher – Decode Feelings through Code",
    description="Encrypt messages while preserving emotional tone using AI + Encryption Logic",
)

if __name__ == "__main__":
    iface.launch()
