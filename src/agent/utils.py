import base64
import binascii
import re
import uuid


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

def bytes_to_image(data_url_string: str) -> str | None:
    """
    Decodes a 'data:image/[type];base64,...' Data URL string into an image file.

    Args:
        data_url_string: The full Data URL string.

    Returns:
        The file path of the saved image file, or None if an error occurs.
    """
    # 1. Split the header from the encoded data
    try:
        header, encoded_data = data_url_string.split(",", 1)
        print(f"Received image with header: {header}")
    except ValueError:
        print("Error: Invalid Data URL format. Could not find ','.")
        return None

    # 2. Determine the file extension from the header's MIME type
    # e.g., 'data:image/png;base64' -> 'png'
    match = re.search(r'image/(\w+)', header)
    if match:
        file_extension = match.group(1)
    else:
        # Fallback if the MIME type is not found or is unusual
        print("Warning: Could not determine image type from header. Defaulting to .png")
        file_extension = "png"

    # 3. Decode the Base64 data into bytes
    try:
        image_bytes = base64.b64decode(encoded_data)
        print(f"Successfully decoded {len(image_bytes)} bytes of image data.")
    except (binascii.Error, TypeError) as e:
        print(f"Error decoding Base64 data: {e}")
        return None

    # 4. Save the bytes to a file with the correct extension
    file_path = f"received_image_{uuid.uuid4()}.{file_extension}"
    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Image saved successfully to: {file_path}")
        return file_path
    except IOError as e:
        print(f"Error writing file to disk: {e}")
        return None