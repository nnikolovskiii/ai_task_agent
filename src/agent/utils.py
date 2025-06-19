import base64
import binascii


def bytes_to_wav(data_url_string: str):
    header, encoded_data = data_url_string.split(",", 1)
    print(f"Received audio with header: {header}")

    try:
        # Step 3: Use a library like base64 to decode the data part into bytes.
        audio_bytes = base64.b64decode(encoded_data)
        print(f"Successfully decoded {len(audio_bytes)} bytes of audio data.")

    except (binascii.Error, TypeError):
       pass
        # --- Step 4: Use the bytes with other libraries ---
        # Now that we have `audio_bytes`, we can do anything with them.

        # Example 4a: Save the bytes to a file.
        # We open the file in "write binary" ('wb') mode.
    file_path = "received_audio.wav"
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    return file_path