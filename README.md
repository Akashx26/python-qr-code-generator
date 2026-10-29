# QR Code Studio

A Python QR code generator with both a command-line version and a Streamlit web app.

## Features

- Generate QR codes from text or URLs
- Preview QR codes in your browser
- Customize QR code and background colors
- Download generated QR codes as PNG images
- View and download recently generated QR codes

## Technologies Used

- Python
- Streamlit
- qrcode
- Pillow

## Installation

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Run the Web App

```bash
python -m streamlit run app.py
```

Streamlit will open QR Code Studio in your browser.

## Run the Command-Line Version

```bash
python qr_generator.py
```

Follow the terminal prompts to generate a QR code.

## Project Structure

```text
QR_generator/
├── app.py
├── qr_generator.py
├── requirements.txt
├── README.md
└── .gitignore
```

## What I Learned

- Working with Python libraries
- Creating QR codes and PNG images
- Building a web interface with Streamlit
- Managing Python project dependencies
- Preparing a project for GitHub deployment
