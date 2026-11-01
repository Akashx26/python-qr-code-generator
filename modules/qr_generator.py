
import io
from pathlib import Path

import qrcode
from PIL import Image, ImageColor, ImageDraw


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

ERROR_CORRECTION_LEVELS = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
    "Low": qrcode.constants.ERROR_CORRECT_L,
    "Medium": qrcode.constants.ERROR_CORRECT_M,
    "Quartile": qrcode.constants.ERROR_CORRECT_Q,
    "High": qrcode.constants.ERROR_CORRECT_H,
}

QR_SHAPES = {
    "Square": "square",
    "Rounded": "rounded",
    "Dots": "dots",
}

ASSETS_FOLDER = Path(__file__).resolve().parent.parent / "assets"

LOGO_OPTIONS = {
    "No Logo": None,
    "Contact": "contact.png",
    "Email": "email.png",
    "Facebook": "facebook.png",
    "Heart": "heart.png",
    "Instagram": "instagram.png",
    "LinkedIn": "linkedin.png",
    "Location": "location.png",
    "Message": "message.png",
    "Phone": "phone.png",
    "Star": "star.png",
    "Telegram": "telegram.png",
    "WhatsApp": "whatsapp.png",
    "X": "x.png",
    "YouTube": "youtube.png",
}


# --------------------------------------------------
# 2. LOGO PREPARATION
# --------------------------------------------------

def prepare_logo(logo_path, fill_color, target_size):
    """
    Remove transparent margins, recolour the logo,
    and fit it proportionally inside a standard area.
    """

    logo = Image.open(logo_path).convert("RGBA")

    # Find the visible artwork.
    alpha = logo.getchannel("A")
    bounding_box = alpha.getbbox()

    if bounding_box is None:
        raise ValueError(f"The logo image is empty: {logo_path.name}")

    # Remove unnecessary transparent margins.
    logo = logo.crop(bounding_box)

    # Preserve original transparency.
    original_alpha = logo.getchannel("A")

    # Apply the selected QR foreground colour.
    logo_color = ImageColor.getrgb(fill_color)

    recolored_logo = Image.new(
        "RGBA",
        logo.size,
        logo_color + (255,)
    )

    recolored_logo.putalpha(original_alpha)

    # Keep the original proportions while fitting
    # every logo inside the same maximum dimensions.
    recolored_logo.thumbnail(
        (target_size, target_size),
        Image.Resampling.LANCZOS
    )

    return recolored_logo


# --------------------------------------------------
# 3. CENTRE LOGO AND PROTECTED AREA
# --------------------------------------------------

def add_logo(image, logo_name, fill_color, back_color):
    """
    Add a centred logo inside a protected rounded-square area.

    QR modules are cleared from the complete rounded-square
    area, including the space around the logo.
    """

    if logo_name == "No Logo":
        return image

    logo_filename = LOGO_OPTIONS.get(logo_name)

    if not logo_filename:
        return image

    logo_path = ASSETS_FOLDER / logo_filename

    if not logo_path.is_file():
        raise FileNotFoundError(
            f"Logo asset not found: {logo_path}"
        )

    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)

    # ----------------------------------------------
    # BADGE DIMENSIONS
    # ----------------------------------------------

    # Badge occupies 22% of the QR width.
    badge_size = max(1, int(image.width * 0.22))

    # Logo now occupies 82% of the badge.
    # This reduces the empty space around the artwork.
    logo_size = max(1, int(badge_size * 0.82))

    # Smooth rounded-square corners.
    corner_radius = int(badge_size * 0.22)

    logo = prepare_logo(
        logo_path,
        fill_color,
        logo_size
    )

    # Centre the badge.
    badge_x = (image.width - badge_size) // 2
    badge_y = (image.height - badge_size) // 2

    badge_box = (
        badge_x,
        badge_y,
        badge_x + badge_size - 1,
        badge_y + badge_size - 1
    )

    background_color = ImageColor.getrgb(back_color)

    # ----------------------------------------------
    # CLEAR THE ROUNDED-SQUARE PROTECTED AREA
    # ----------------------------------------------

    # Draw the background only inside a rounded square.
    # This avoids the unwanted square cutout.
    draw.rounded_rectangle(
        badge_box,
        radius=corner_radius,
        fill=background_color
    )

    # ----------------------------------------------
    # CENTRE THE LOGO
    # ----------------------------------------------

    logo_x = badge_x + (badge_size - logo.width) // 2
    logo_y = badge_y + (badge_size - logo.height) // 2

    image.alpha_composite(
        logo,
        (logo_x, logo_y)
    )

    return image


# --------------------------------------------------
# 4. QR CODE GENERATION
# --------------------------------------------------

def create_qr(
    data,
    fill_color,
    back_color,
    box_size=10,
    border=4,
    error_correction="H",
    shape="Square",
    logo_name="No Logo"
):
    """
    Generate a customised QR code.

    Returns:
        image: Generated QR image.
        image_bytes: PNG image stored in memory.
    """

    # ----------------------------------------------
    # INPUT VALIDATION
    # ----------------------------------------------

    if not data or not data.strip():
        raise ValueError("Please enter some text or a URL.")

    if shape not in QR_SHAPES:
        raise ValueError("Invalid QR code shape selected.")

    if logo_name not in LOGO_OPTIONS:
        raise ValueError("Invalid logo selected.")

    if not isinstance(box_size, int) or box_size < 1:
        raise ValueError("Box size must be a positive integer.")

    if not isinstance(border, int) or border < 0:
        raise ValueError("Border must be a non-negative integer.")

    try:
        foreground = ImageColor.getrgb(fill_color)
        background = ImageColor.getrgb(back_color)
    except ValueError:
        raise ValueError("Please select valid QR code colours.")

    # Accept descriptive names or integer constants.
    if isinstance(error_correction, str):
        if error_correction not in ERROR_CORRECTION_LEVELS:
            raise ValueError("Invalid error correction level.")

        correction_value = ERROR_CORRECTION_LEVELS[error_correction]

    elif error_correction in ERROR_CORRECTION_LEVELS.values():
        correction_value = error_correction

    else:
        raise ValueError("Invalid error correction level.")

    # ----------------------------------------------
    # CREATE QR MATRIX
    # ----------------------------------------------

    qr = qrcode.QRCode(
        version=None,
        error_correction=correction_value,
        box_size=box_size,
        border=border,
    )

    qr.add_data(data)
    qr.make(fit=True)

    matrix = qr.get_matrix()

    rows = len(matrix)
    columns = len(matrix[0])

    image_width = columns * box_size
    image_height = rows * box_size

    image = Image.new(
        "RGB",
        (image_width, image_height),
        background
    )

    draw = ImageDraw.Draw(image)

    selected_shape = QR_SHAPES[shape]

    # ----------------------------------------------
    # FINDER PATTERN LOCATIONS
    # ----------------------------------------------

    finder_regions = [
        (border, border),
        (columns - border - 7, border),
        (border, rows - border - 7),
    ]

    def is_finder_module(row, column):
        """Identify the three QR finder patterns."""

        for finder_x, finder_y in finder_regions:
            if (
                finder_y <= row < finder_y + 7
                and finder_x <= column < finder_x + 7
            ):
                return True

        return False

    # ----------------------------------------------
    # DRAW QR MODULES
    # ----------------------------------------------

    for row in range(rows):
        for column in range(columns):

            if not matrix[row][column]:
                continue

            # Finder patterns are drawn separately.
            if is_finder_module(row, column):
                continue

            x1 = column * box_size
            y1 = row * box_size

            x2 = x1 + box_size - 1
            y2 = y1 + box_size - 1

            if selected_shape == "rounded":

                draw.rounded_rectangle(
                    (x1, y1, x2, y2),
                    radius=max(1, box_size // 3),
                    fill=foreground
                )

            elif selected_shape == "dots":

                draw.ellipse(
                    (x1, y1, x2, y2),
                    fill=foreground
                )

            else:

                draw.rectangle(
                    (x1, y1, x2, y2),
                    fill=foreground
                )

    # ----------------------------------------------
    # DRAW FINDER PATTERNS
    # ----------------------------------------------

    for finder_x, finder_y in finder_regions:

        x1 = finder_x * box_size
        y1 = finder_y * box_size

        x2 = x1 + 7 * box_size
        y2 = y1 + 7 * box_size

        # Outer square.
        draw.rectangle(
            (x1, y1, x2 - 1, y2 - 1),
            fill=foreground
        )

        # Middle background ring.
        draw.rectangle(
            (
                x1 + box_size,
                y1 + box_size,
                x2 - box_size - 1,
                y2 - box_size - 1,
            ),
            fill=background
        )

        # Inner square.
        draw.rectangle(
            (
                x1 + 2 * box_size,
                y1 + 2 * box_size,
                x2 - 2 * box_size - 1,
                y2 - 2 * box_size - 1,
            ),
            fill=foreground
        )

    # ----------------------------------------------
    # ADD CENTRE LOGO
    # ----------------------------------------------

    image = add_logo(
        image,
        logo_name,
        fill_color,
        back_color
    )

    # ----------------------------------------------
    # PREPARE PNG OUTPUT
    # ----------------------------------------------

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    return image, image_bytes
