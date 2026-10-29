import argparse
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H


def generate_qr(data, output, fill_color, back_color):
    if not data.strip():
        raise ValueError("Input text or URL cannot be empty.")

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color=fill_color,
        back_color=back_color,
    )

    output_path = Path(output)

    if output_path.suffix.lower() != ".png":
        output_path = output_path.with_suffix(".png")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    print(f"QR code created successfully: {output_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a QR code from text or a URL."
    )

    parser.add_argument("data", nargs="?", help="Text or URL to encode")
    parser.add_argument("-o", "--output", default="qrcode.png")
    parser.add_argument("--fill", default="black")
    parser.add_argument("--background", default="white")

    args = parser.parse_args()

    data = args.data
    if data is None:
        data = input("Enter text or URL for your QR code: ")

    try:
        generate_qr(data, args.output, args.fill, args.background)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()