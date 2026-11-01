
from datetime import datetime

import streamlit as st
from PIL import Image

from modules.qr_generator import (
    create_qr,
    ERROR_CORRECTION_LEVELS,
    LOGO_OPTIONS,
    ASSETS_FOLDER,
)

from modules.qr_customization import get_color_presets
from modules.qr_scanner import decode_qr_image


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="QR Code Studio 2.0",
    page_icon="🔳",
    layout="wide",
)


# --------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# --------------------------------------------------

DEFAULT_SETTINGS = {
    "history": [],
    "generated_qr": None,
    "qr_input": "",
    "draft_shape": "Square",
    "draft_fill": "#000000",
    "draft_background": "#FFFFFF",
    "draft_preset": "Classic Black",
    "draft_logo": "No Logo",
    "scanner_result": None,
}

for key, value in DEFAULT_SETTINGS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# 3. COLOR THEME MANAGEMENT
# --------------------------------------------------

def select_preset(theme_name):
    """Apply the selected preset's foreground and background."""

    presets = get_color_presets()

    if theme_name in presets:
        st.session_state.draft_preset = theme_name
        st.session_state.draft_fill = presets[theme_name]["foreground"]
        st.session_state.draft_background = presets[theme_name]["background"]


def mark_custom_colors():
    """Mark the theme as Custom after a manual color change."""

    st.session_state.draft_preset = "Custom"


# --------------------------------------------------
# 4. LOGO THUMBNAIL MANAGEMENT
# --------------------------------------------------

def load_logo_thumbnail(logo_name, size=64):
    """Return a square thumbnail so every logo occupies equal space."""

    logo_path = ASSETS_FOLDER / LOGO_OPTIONS[logo_name]

    if not logo_path.is_file():
        return None

    with Image.open(logo_path) as original:
        logo = original.convert("RGBA")
        logo.thumbnail((size, size), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        x = (size - logo.width) // 2
        y = (size - logo.height) // 2

        canvas.alpha_composite(logo, (x, y))

    return canvas


# --------------------------------------------------
# 5. QR CODE GENERATION
# --------------------------------------------------

def generate_qr_record(data, fill, background, shape, logo_name):
    """Generate a QR code and return its saved record."""

    image, png_bytes = create_qr(
        data=data,
        fill_color=fill,
        back_color=background,
        box_size=10,
        border=4,
        error_correction=ERROR_CORRECTION_LEVELS["High"],
        shape=shape,
        logo_name=logo_name,
    )

    return {
        "data": data,
        "fill": fill,
        "background": background,
        "shape": shape,
        "logo_name": logo_name,
        "png": png_bytes,
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "QR Code",
    }


# --------------------------------------------------
# 6. HISTORY MANAGEMENT
# --------------------------------------------------

def add_to_history(record):
    """Keep the ten most recent QR code versions."""

    st.session_state.history.insert(0, record)
    st.session_state.history = st.session_state.history[:10]


# --------------------------------------------------
# 7. APPLICATION STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #888888;
        margin-bottom: 2rem;
    }

    .theme-card {
        border: 1px solid rgba(128,128,128,0.3);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 5px;
    }

    .theme-swatches {
        display: flex;
        gap: 7px;
        margin-top: 8px;
    }

    .theme-swatch {
        height: 24px;
        width: 24px;
        border-radius: 6px;
        border: 1px solid rgba(128,128,128,0.4);
    }

    .color-value {
        font-size: 0.8rem;
        color: #999999;
        margin-top: -10px;
    }

    .logo-label {
        text-align: center;
        font-size: 0.85rem;
        font-weight: 600;
        line-height: 1.2rem;
        min-height: 1.2rem;
        white-space: nowrap;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 8. APPLICATION HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🔳 QR Code Studio 2.0</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Your all-in-one QR code and barcode workspace.'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 9. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a feature",
    [
        "QR Code Generator",
        "QR Code Scanner",
    ],
)


# --------------------------------------------------
# 10. QR CODE GENERATOR PAGE
# --------------------------------------------------

if page == "QR Code Generator":

    left, right = st.columns(
        [1.1, 0.9],
        gap="large",
    )

    # ==================================================
    # LEFT COLUMN: INPUT AND CUSTOMIZATION
    # ==================================================

    with left:

        st.subheader("Create your QR code")

        st.text_area(
            "Enter text or URL",
            placeholder="https://github.com or Hello World",
            height=110,
            key="qr_input",
        )

        st.divider()

        st.subheader("🎨 Customize your QR code")

        st.caption(
            "Personalize your QR code and see the preview "
            "update as you experiment."
        )

        with st.container(border=True):

            # ------------------------------------------
            # QR SHAPE
            # ------------------------------------------

            st.markdown("#### QR code shape")

            st.selectbox(
                "Choose your preferred shape",
                ["Square", "Rounded", "Dots"],
                key="draft_shape",
            )

            st.divider()

            # ------------------------------------------
            # COLOR THEMES
            # ------------------------------------------

            st.markdown("#### Color themes")

            presets = get_color_presets()

            st.caption(
                "Choose a ready-made combination or create your own."
            )

            theme_names = list(presets.keys())

            theme_columns = st.columns(3)

            for index, theme_name in enumerate(theme_names):

                colors = presets[theme_name]

                foreground = colors["foreground"]
                background = colors["background"]

                with theme_columns[index % 3]:

                    st.markdown(
                        f"""
                        <div class="theme-card">
                            <strong>{theme_name}</strong>
                            <div class="theme-swatches">
                                <div class="theme-swatch"
                                     style="background:{foreground}">
                                </div>
                                <div class="theme-swatch"
                                     style="background:{background}">
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    is_selected = (
                        st.session_state.draft_preset == theme_name
                    )

                    st.button(
                        "Selected" if is_selected else "Select",
                        key=f"theme_{index}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary",
                        on_click=select_preset,
                        args=(theme_name,),
                    )

            st.divider()

            # ------------------------------------------
            # CUSTOM COLOR SELECTION
            # ------------------------------------------

            st.markdown("#### Custom colors")

            foreground_column, background_column = st.columns(2)

            with foreground_column:

                st.color_picker(
                    "QR code color",
                    key="draft_fill",
                    on_change=mark_custom_colors,
                )

                st.markdown(
                    f"""
                    <div class="color-value">
                        {st.session_state.draft_fill}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with background_column:

                st.color_picker(
                    "Background color",
                    key="draft_background",
                    on_change=mark_custom_colors,
                )

                st.markdown(
                    f"""
                    <div class="color-value">
                        {st.session_state.draft_background}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.divider()

            # ------------------------------------------
            # BUILT-IN LOGO SELECTOR
            # ------------------------------------------

            st.markdown("#### ✨ Choose a centre logo")

            st.caption(
                "Select an icon to personalise the centre of your QR code."
            )

            logo_names = list(LOGO_OPTIONS.keys())

            logo_columns = st.columns(5)

            for index, logo_name in enumerate(logo_names):

                with logo_columns[index % 5]:

                    selected = (
                        st.session_state.draft_logo == logo_name
                    )

                    with st.container(height=225, border=True):

                        if logo_name == "No Logo":
                            thumbnail = Image.new(
                                "RGBA",
                                (64, 64),
                                (0, 0, 0, 0),
                            )
                        else:
                            thumbnail = load_logo_thumbnail(logo_name)

                        if thumbnail is not None:
                            st.image(thumbnail, width=55)
                        else:
                            st.image(
                                Image.new(
                                    "RGBA",
                                    (64, 64),
                                    (0, 0, 0, 0),
                                ),
                                width=55,
                            )

                        st.markdown(
                            f'<div class="logo-label">{logo_name}</div>',
                            unsafe_allow_html=True,
                        )

                        st.button(
                            "Selected" if selected else "Select",
                            key=f"logo_{index}",
                            use_container_width=True,
                            type="primary" if selected else "secondary",
                            on_click=lambda name=logo_name: (
                                st.session_state.update(
                                    {"draft_logo": name}
                                )
                            ),
                        )

        # ==================================================
        # GENERATE QR CODE
        # ==================================================

        st.write("")

        if st.button(
            "✨ Generate QR Code",
            use_container_width=True,
            type="primary",
        ):

            data = st.session_state.qr_input.strip()

            if not data:

                st.error("Please enter some text or a URL.")

            else:

                try:

                    record = generate_qr_record(
                        data,
                        st.session_state.draft_fill,
                        st.session_state.draft_background,
                        st.session_state.draft_shape,
                        st.session_state.draft_logo,
                    )

                    st.session_state.generated_qr = record

                    add_to_history(record)

                    st.success("QR code generated successfully!")

                except (ValueError, OSError) as error:

                    st.error(f"Could not generate QR code: {error}")

        # ==================================================
        # APPLY CHANGES TO EXISTING QR CODE
        # ==================================================

        current_qr = st.session_state.generated_qr

        if current_qr:

            st.divider()

            if st.button(
                "✓ Apply Changes",
                use_container_width=True,
            ):

                try:

                    record = generate_qr_record(
                        current_qr["data"],
                        st.session_state.draft_fill,
                        st.session_state.draft_background,
                        st.session_state.draft_shape,
                        st.session_state.draft_logo,
                    )

                    st.session_state.generated_qr = record

                    add_to_history(record)

                    st.success("Your QR code design has been updated!")

                    st.rerun()

                except (ValueError, OSError) as error:

                    st.error(f"Could not apply changes: {error}")

    # ==================================================
    # RIGHT COLUMN: LIVE PREVIEW
    # ==================================================

    with right:

        st.subheader("QR code preview")

        current_qr = st.session_state.generated_qr

        preview_data = st.session_state.qr_input.strip()

        if current_qr:
            preview_data = current_qr["data"]

        if preview_data:

            try:

                preview_image, preview_png = create_qr(
                    data=preview_data,
                    fill_color=st.session_state.draft_fill,
                    back_color=st.session_state.draft_background,
                    box_size=10,
                    border=4,
                    error_correction=ERROR_CORRECTION_LEVELS["High"],
                    shape=st.session_state.draft_shape,
                    logo_name=st.session_state.draft_logo,
                )

                st.image(
                    preview_png,
                    caption="Live preview",
                    width=300,
                )

                st.caption(
                    f"QR shape: {st.session_state.draft_shape}"
                )

                st.caption(
                    f"QR color: {st.session_state.draft_fill}"
                )

                st.caption(
                    f"Background: {st.session_state.draft_background}"
                )

                st.caption(
                    f"Centre logo: {st.session_state.draft_logo}"
                )

                if current_qr:

                    has_changes = (
                        current_qr["shape"] != st.session_state.draft_shape
                        or current_qr["fill"] != st.session_state.draft_fill
                        or current_qr["background"]
                        != st.session_state.draft_background
                        or current_qr.get("logo_name", "No Logo")
                        != st.session_state.draft_logo
                    )

                    if has_changes:

                        st.info(
                            "You have unapplied changes. "
                            "Click Apply Changes to save your design."
                        )

                    else:

                        st.success("Your current design is applied.")

                    st.download_button(
                        label="⬇️ Download Applied QR Code",
                        data=current_qr["png"],
                        file_name="qr_code.png",
                        mime="image/png",
                        use_container_width=True,
                    )

                else:

                    st.caption(
                        "Generate your QR code to enable downloading."
                    )

            except (ValueError, OSError) as error:

                st.error(f"Could not create QR preview: {error}")

        else:

            st.info(
                "Enter some text or a URL to see your live preview."
            )


# --------------------------------------------------
# 11. QR CODE SCANNER PAGE
# --------------------------------------------------

elif page == "QR Code Scanner":

    st.subheader("📷 QR Code Scanner")

    st.caption(
        "Upload an image containing a QR code to read its contents."
    )

    uploaded_file = st.file_uploader(
        "Upload QR code image",
        type=["png", "jpg", "jpeg"],
        help="Supported formats: PNG, JPG and JPEG.",
        key="qr_scanner_upload",
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        left, right = st.columns(2, gap="large")

        with left:

            st.markdown("#### Uploaded image")

            st.image(
                image,
                use_container_width=True,
            )

        with right:

            st.markdown("#### Scan result")

            if st.button(
                "🔍 Scan QR Code",
                use_container_width=True,
                type="primary",
            ):

                try:

                    decoded_text = decode_qr_image(image)

                    if decoded_text:

                        st.session_state.scanner_result = decoded_text

                    else:

                        st.session_state.scanner_result = ""

                except Exception as error:

                    st.session_state.scanner_result = None
                    st.error(f"Unable to scan this image: {error}")

            result = st.session_state.scanner_result

            if result is not None:

                if result:

                    st.success("QR code detected successfully!")

                    st.text_area(
                        "Decoded content",
                        value=result,
                        height=150,
                        disabled=True,
                    )

                    st.code(result, language=None)

                else:

                    st.warning(
                        "No QR code was detected in this image. "
                        "Try a clearer image with the QR code fully visible."
                    )

            else:

                st.info("Upload an image and click Scan QR Code.")


# --------------------------------------------------
# 12. GENERATION HISTORY
# --------------------------------------------------

st.divider()

st.subheader("🕘 Generation history")

history = st.session_state.history

if history:

    st.caption(
        "Your ten most recent generated or applied QR codes "
        "in this active app session."
    )

    for index, item in enumerate(history):

        with st.expander(
            f"{item['time']} — {item['shape']} — "
            f"{item['data'][:40]}"
        ):

            st.image(
                item["png"],
                width=180,
            )

            st.write(f"QR shape: {item['shape']}")
            st.write(f"QR color: {item['fill']}")
            st.write(f"Background: {item['background']}")

            st.write(
                f"Centre logo: {item.get('logo_name', 'No Logo')}"
            )

            st.download_button(
                "Download this QR code",
                data=item["png"],
                file_name=f"qr_code_{index + 1}.png",
                mime="image/png",
                key=f"history_download_{index}",
            )

    if st.button("Clear history"):

        st.session_state.history = []
        st.session_state.generated_qr = None

        st.rerun()

else:

    st.write("Your generated QR codes will appear here.")
