
import io
from datetime import datetime

import qrcode
import streamlit as st
from qrcode.constants import ERROR_CORRECT_H


# Page configuration
st.set_page_config(
    page_title="QR Code Studio",
    page_icon="🔳",
    layout="wide",
)

# Session state keeps history while this app session is active.
if "history" not in st.session_state:
    st.session_state.history = []

if "generated_qr" not in st.session_state:
    st.session_state.generated_qr = None


# Helper function
def create_qr(data, fill_color, back_color):
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

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return image, buffer.getvalue()


# Styling
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #888888;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🔳 QR Code Studio</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Create, customize, preview and download QR codes.'
    '</div>',
    unsafe_allow_html=True,
)

# Main layout
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("Create your QR code")

    with st.form("qr_form"):
        data = st.text_area(
            "Enter text or URL",
            placeholder="https://github.com or Hello World",
            height=120,
        )

        fill_color = st.color_picker(
            "QR code color",
            "#000000",
        )

        back_color = st.color_picker(
            "Background color",
            "#FFFFFF",
        )

        submitted = st.form_submit_button(
            "✨ Generate QR Code",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not data.strip():
            st.error("Please enter some text or a URL.")
        elif fill_color.upper() == back_color.upper():
            st.error("Choose different colors for the QR code and background.")
        else:
            try:
                image, png_bytes = create_qr(
                    data.strip(),
                    fill_color,
                    back_color,
                )

                record = {
                    "data": data.strip(),
                    "fill": fill_color,
                    "background": back_color,
                    "png": png_bytes,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }

                st.session_state.generated_qr = record
                st.session_state.history.insert(0, record)
                st.session_state.history = (
                    st.session_state.history[:10]
                )

            except (ValueError, OSError) as error:
                st.error(f"Could not generate the QR code: {error}")

with right:
    st.subheader("QR code preview")

    current = st.session_state.generated_qr

    if current:
        st.image(
            current["png"],
            caption="Your QR code is ready!",
            width=300,
        )

        st.download_button(
            label="⬇️ Download QR Code (PNG)",
            data=current["png"],
            file_name="qr_code.png",
            mime="image/png",
            use_container_width=True,
        )

        st.caption(f"QR color: {current['fill']}")
        st.caption(f"Background: {current['background']}")
    else:
        st.info(
            "Enter your text or URL, choose your colors, "
            "and click Generate QR Code."
        )

# Generation history
st.divider()
st.subheader("🕘 Generation history")

history = st.session_state.history

if history:
    st.caption(
        "Your 10 most recent QR codes in this active app session."
    )

    for index, item in enumerate(history):
        with st.expander(
            f"{item['time']} — {item['data'][:50]}"
        ):
            st.image(item["png"], width=180)
            st.write(f"QR color: {item['fill']}")
            st.write(f"Background: {item['background']}")

            st.download_button(
                "Download this QR code",
                data=item["png"],
                file_name=f"qr_code_{index + 1}.png",
                mime="image/png",
                key=f"history_download_{index}",
            )

    if st.button("Clear history"):
        st.session_state.history = []
        st.rerun()
else:
    st.write("Your generated QR codes will appear here.")
