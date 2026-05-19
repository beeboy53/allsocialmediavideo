# encode_session.py
import base64

try:
    with open("downloader_session.session", "rb") as session_file:
        session_bytes = session_file.read()
        encoded_string = base64.b64encode(session_bytes).decode('utf-8')

        print("\n✅ Your session string is ready. Copy the entire line below:\n")
        print(encoded_string)
        print("\n")

except FileNotFoundError:
    print("\n❌ Error: downloader_session.session not found.")
    print("Please run your main.py app locally one more time to generate it.\n")