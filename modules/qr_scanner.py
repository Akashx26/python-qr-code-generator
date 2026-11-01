
import cv2
import numpy as np


def decode_qr_image(image):
    """
    Decode a QR code from a PIL image.

    Args:
        image: PIL Image object.

    Returns:
        Decoded QR text if successful, otherwise None.
    """

    if image is None:
        return None

    # Convert the uploaded image to RGB.
    image = image.convert("RGB")

    # Convert the image into a NumPy array.
    image_array = np.array(image)

    # Convert RGB image to BGR for OpenCV.
    image_array = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2BGR
    )

    # Initialize the QR code detector.
    detector = cv2.QRCodeDetector()

    # Detect and decode the QR code.
    decoded_text, points, straight_qrcode = (
        detector.detectAndDecode(image_array)
    )

    # Return the decoded text.
    if decoded_text:
        return decoded_text

    return None
