
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image, UnidentifiedImageError

from modules.qr_generator import (
    create_qr,
    LOGO_OPTIONS,
    ASSETS_FOLDER,
)
from modules.qr_customization import get_color_presets
from modules.qr_scanner import decode_qr_image


# ============================================================
# QR STUDIO 3.2
# Sidebar navigation | Responsive layout | No dashboard
# ============================================================

st.set_page_config(
    page_title="QR Studio",
    page_icon="🔳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "history": [],
    "generated_qr": None,
    "qr_input": "",
    "draft_shape": "Square",
    "draft_fill": "#000000",
    "draft_background": "#FFFFFF",
    "draft_preset": "Classic Black",
    "draft_logo": "No Logo",
    "current_page": "Create QR",
    "scanner_result": None,
    "foreground_picker": "#000000",
    "background_picker": "#FFFFFF",
    "preset_selector": "Classic Black",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


PRESETS = get_color_presets()

PAGES = {
    "Create QR": "＋",
    "Scan QR": "⌗",
    "My Designs": "▤",
    "Settings": "⚙",
}


# ============================================================
# CSS
# ============================================================

CSS_FILE = Path(__file__).parent / "styles" / "style.css"

if CSS_FILE.exists():
    st.markdown(
        f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def apply_preset():
    """Update the colour controls when a preset is selected."""

    preset_name = st.session_state.preset_selector

    if preset_name in PRESETS:
        foreground = PRESETS[preset_name]["foreground"]
        background = PRESETS[preset_name]["background"]

        st.session_state.draft_preset = preset_name
        st.session_state.draft_fill = foreground
        st.session_state.draft_background = background

        st.session_state.foreground_picker = foreground
        st.session_state.background_picker = background

    else:
        st.session_state.draft_preset = "Custom"


def update_foreground():
    """Save a manually selected foreground colour."""

    st.session_state.draft_fill = st.session_state.foreground_picker
    st.session_state.draft_preset = "Custom"
    st.session_state.preset_selector = "Custom"


def update_background():
    """Save a manually selected background colour."""

    st.session_state.draft_background = st.session_state.background_picker
    st.session_state.draft_preset = "Custom"
    st.session_state.preset_selector = "Custom"


def make_qr_record(data):
    """Generate a QR code and prepare its history record."""

    image, image_bytes = create_qr(
        data=data,
        fill_color=st.session_state.draft_fill,
        back_color=st.session_state.draft_background,
        box_size=10,
        border=4,
        error_correction="High",
        shape=st.session_state.draft_shape,
        logo_name=st.session_state.draft_logo,
    )

    image_bytes.seek(0)
    png_data = image_bytes.getvalue()

    return {
        "data": data,
        "fill": st.session_state.draft_fill,
        "background": st.session_state.draft_background,
        "shape": st.session_state.draft_shape,
        "logo_name": st.session_state.draft_logo,
        "png": png_data,
        "date": datetime.now().strftime("%d %b %Y"),
        "time": datetime.now().strftime("%H:%M"),
    }


def save_qr_record(record):
    """Save a generated QR code in session history."""

    st.session_state.generated_qr = record
    st.session_state.history.insert(0, record)
    st.session_state.history = st.session_state.history[:10]


def load_history_item(index):
    """Load a saved QR code back into the creation controls."""

    record = st.session_state.history[index]

    st.session_state.generated_qr = record
    st.session_state.qr_input = record["data"]

    st.session_state.draft_fill = record["fill"]
    st.session_state.draft_background = record["background"]
    st.session_state.draft_shape = record["shape"]
    st.session_state.draft_logo = record["logo_name"]

    st.session_state.foreground_picker = record["fill"]
    st.session_state.background_picker = record["background"]

    matching_preset = "Custom"

    for name, colors in PRESETS.items():
        if (
            colors["foreground"] == record["fill"]
            and colors["background"] == record["background"]
        ):
            matching_preset = name
            break

    st.session_state.draft_preset = matching_preset
    st.session_state.preset_selector = matching_preset


def get_logo_thumbnail(logo_name, size=64):
    """Create a safely sized thumbnail for a built-in logo."""

    filename = LOGO_OPTIONS.get(logo_name)

    if not filename:
        return None

    logo_path = ASSETS_FOLDER / filename

    if not logo_path.exists():
        return None

    with Image.open(logo_path) as original:
        logo = original.convert("RGBA")
        logo.thumbnail((size, size), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        x = (size - logo.width) // 2
        y = (size - logo.height) // 2

        canvas.alpha_composite(logo, (x, y))

    return canvas


def page_heading(eyebrow, title, description):
    """Display a consistent page heading."""

    st.markdown(
        f"""
        <div class="page-heading">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, description=None):
    """Display a compact section heading."""

    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )

    if description:
        st.caption(description)


def clear_scanner_result():
    """Clear an earlier scan result when a new file is uploaded."""

    st.session_state.scanner_result = None


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">▦</div>
            <div>
                <div class="brand-name">QR Studio</div>
                <div class="brand-caption">CREATE · SCAN · SHARE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-label">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    for name, icon in PAGES.items():

        active = st.session_state.current_page == name

        if st.button(
            f"{icon}   {name}",
            key=f"navigation_{name}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.current_page = name
            st.rerun()

    st.divider()

    st.markdown(
        """
        <div class="sidebar-footer">
            <div class="sidebar-footer-title">QR STUDIO 3.2</div>
            <div class="sidebar-footer-text">
                Your creative QR workspace.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


page = st.session_state.current_page


# ============================================================
# PAGE 1 — CREATE QR
# ============================================================

if page == "Create QR":

    page_heading(
        "QR CODE GENERATOR",
        "Create your QR code",
        "Enter your content, customize its appearance, and generate.",
    )

    controls_column, preview_column = st.columns(
        [1.05, 0.95],
        gap="large",
    )

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    with controls_column:

        with st.container(border=True):

            section_heading(
                "01 · Content",
                "What would you like your QR code to contain?",
            )

            st.text_area(
                "QR code content",
                key="qr_input",
                height=100,
                placeholder="https://example.com",
                label_visibility="collapsed",
            )

        with st.container(border=True):

            section_heading(
                "02 · Appearance",
                "Choose your pattern and colours.",
            )

            st.session_state.draft_shape = st.selectbox(
                "QR pattern",
                ["Square", "Rounded", "Dots"],
                index=["Square", "Rounded", "Dots"].index(
                    st.session_state.draft_shape
                ),
                key="shape_selector",
            )

            preset_options = list(PRESETS.keys()) + ["Custom"]

            if st.session_state.preset_selector not in preset_options:
                st.session_state.preset_selector = "Classic Black"

            st.selectbox(
                "Colour preset",
                preset_options,
                key="preset_selector",
                on_change=apply_preset,
            )

            color_columns = st.columns(2)

            with color_columns[0]:
                st.color_picker(
                    "QR colour",
                    key="foreground_picker",
                    on_change=update_foreground,
                )

            with color_columns[1]:
                st.color_picker(
                    "Background",
                    key="background_picker",
                    on_change=update_background,
                )

        with st.container(border=True):

            section_heading(
                "03 · Centre icon",
                "Choose an icon from the built-in gallery.",
            )

            logo_options = list(LOGO_OPTIONS.keys())

            st.selectbox(
                "Centre icon",
                logo_options,
                key="draft_logo",
            )

            selected_logo = st.session_state.draft_logo

            if selected_logo != "No Logo":
                thumbnail = get_logo_thumbnail(selected_logo)

                if thumbnail:
                    st.image(
                        thumbnail,
                        width=52,
                        caption=selected_logo,
                    )

        generate_clicked = st.button(
            "Generate QR Code",
            type="primary",
            use_container_width=True,
        )

        if generate_clicked:

            content = st.session_state.qr_input.strip()

            if not content:
                st.warning("Please enter some content first.")

            else:
                try:
                    record = make_qr_record(content)
                    save_qr_record(record)
                    st.success("QR code generated successfully.")

                except Exception as error:
                    st.error(f"Unable to generate QR code: {error}")

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    with preview_column:

        with st.container(border=True):

            section_heading(
                "LIVE RESULT",
                "Your generated QR code.",
            )

            record = st.session_state.generated_qr

            if record:

                st.image(
                    record["png"],
                    use_container_width=True,
                )

                st.markdown(
                    f"""
                    <div class="preview-meta">
                        <span>{record['shape']} pattern</span>
                        <span>{record['logo_name']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.download_button(
                    "Download PNG",
                    data=record["png"],
                    file_name="qr_studio_code.png",
                    mime="image/png",
                    use_container_width=True,
                    type="primary",
                )

                changed = (
                    record["data"] != st.session_state.qr_input.strip()
                    or record["fill"] != st.session_state.draft_fill
                    or record["background"] != st.session_state.draft_background
                    or record["shape"] != st.session_state.draft_shape
                    or record["logo_name"] != st.session_state.draft_logo
                )

                if changed:
                    st.info(
                        "Your settings have changed. Generate again "
                        "to update the QR code."
                    )

            else:

                st.markdown(
                    """
                    <div class="empty-preview">
                        <div class="empty-preview-icon">▦</div>
                        <div class="empty-preview-title">
                            Your QR code will appear here
                        </div>
                        <div class="empty-preview-text">
                            Enter your content and select Generate QR Code.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if st.session_state.history:
            st.caption(
                f"{len(st.session_state.history)} recent QR code(s) "
                "in this session."
            )


# ============================================================
# PAGE 2 — SCAN QR
# ============================================================

elif page == "Scan QR":

    page_heading(
        "QR CODE SCANNER",
        "Scan a QR code",
        "Upload an image containing a QR code to decode its content.",
    )

    upload_column, result_column = st.columns(
        [1, 1],
        gap="large",
    )

    with upload_column:

        with st.container(border=True):

            section_heading(
                "01 · Upload image",
                "Supported formats: PNG, JPG, and JPEG.",
            )

            uploaded_file = st.file_uploader(
                "Choose a QR code image",
                type=["png", "jpg", "jpeg"],
                key="qr_upload",
                on_change=clear_scanner_result,
            )

            if uploaded_file:

                try:
                    uploaded_image = Image.open(uploaded_file).convert("RGB")

                    st.image(
                        uploaded_image,
                        caption="Uploaded image",
                        use_container_width=True,
                    )

                    if st.button(
                        "Decode QR Code",
                        type="primary",
                        use_container_width=True,
                    ):

                        decoded_text = decode_qr_image(uploaded_image)

                        st.session_state.scanner_result = decoded_text

                        if decoded_text:
                            st.success("QR code decoded successfully.")
                        else:
                            st.warning("No QR code was detected.")

                except (UnidentifiedImageError, OSError):
                    st.error("The uploaded file is not a valid image.")

    with result_column:

        with st.container(border=True):

            section_heading(
                "02 · Scan result",
                "Your decoded content appears here.",
            )

            result = st.session_state.scanner_result

            if result:

                st.success("QR code successfully decoded.")

                st.text_area(
                    "Decoded content",
                    value=result,
                    height=150,
                    disabled=True,
                )

                st.caption(
                    "Select the text above and press Ctrl+C to copy it."
                )

            else:

                st.markdown(
                    """
                    <div class="empty-preview">
                        <div class="empty-preview-icon">⌗</div>
                        <div class="empty-preview-title">
                            Waiting for a scan
                        </div>
                        <div class="empty-preview-text">
                            Upload an image and select Decode QR Code.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# PAGE 3 — MY DESIGNS
# ============================================================

elif page == "My Designs":

    page_heading(
        "YOUR COLLECTION",
        "My designs",
        "View, download, and reuse your recently generated QR codes.",
    )

    history = st.session_state.history

    if not history:

        with st.container(border=True):

            st.markdown(
                """
                <div class="empty-preview">
                    <div class="empty-preview-icon">▤</div>
                    <div class="empty-preview-title">
                        No designs yet
                    </div>
                    <div class="empty-preview-text">
                        QR codes you generate will appear here.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Create your first QR code", type="primary"):
            st.session_state.current_page = "Create QR"
            st.rerun()

    else:

        st.caption(
            f"{len(history)} recent design(s). "
            "History is stored for the active session."
        )

        for index, record in enumerate(history):

            with st.container(border=True):

                image_column, details_column, actions_column = st.columns(
                    [0.8, 2.2, 1],
                    gap="medium",
                )

                with image_column:
                    st.image(
                        record["png"],
                        use_container_width=True,
                    )

                with details_column:

                    st.markdown(
                        f"**QR Code · {record['date']}**"
                    )

                    st.caption(record["data"][:100])

                    st.caption(
                        f"{record['shape']} · {record['logo_name']} "
                        f"· {record['time']}"
                    )

                with actions_column:

                    st.download_button(
                        "Download",
                        data=record["png"],
                        file_name=f"qr_design_{index + 1}.png",
                        mime="image/png",
                        key=f"download_design_{index}",
                        use_container_width=True,
                    )

                    if st.button(
                        "Edit / View",
                        key=f"load_design_{index}",
                        use_container_width=True,
                    ):
                        load_history_item(index)
                        st.session_state.current_page = "Create QR"
                        st.rerun()

        st.divider()

        if st.button(
            "Clear session history",
            use_container_width=True,
        ):
            st.session_state.history = []
            st.session_state.generated_qr = None
            st.rerun()


# ============================================================
# PAGE 4 — SETTINGS
# ============================================================

elif page == "Settings":

    page_heading(
        "APPLICATION SETTINGS",
        "Settings",
        "Information about your QR Studio workspace.",
    )

    with st.container(border=True):

        section_heading("Application")

        st.markdown("**QR Studio 3.2**")

        st.caption(
            "Generate, customize, download, and scan QR codes "
            "using your local workspace."
        )

    with st.container(border=True):

        section_heading("Current generation settings")

        st.markdown(
            f"**Pattern:** {st.session_state.draft_shape}"
        )

        st.markdown(
            f"**QR colour:** `{st.session_state.draft_fill}`"
        )

        st.markdown(
            f"**Background:** `{st.session_state.draft_background}`"
        )

        st.markdown(
            f"**Centre icon:** {st.session_state.draft_logo}"
        )

    with st.container(border=True):

        section_heading("Session information")

        metric_columns = st.columns(2)

        metric_columns[0].metric(
            "Saved designs",
            len(st.session_state.history),
        )

        metric_columns[1].metric(
            "History limit",
            10,
        )

        st.caption(
            "Session history is temporary and may reset "
            "when the Streamlit session restarts."
        )

    with st.container(border=True):

        section_heading("Technologies")

        st.markdown(
            """
            - Python
            - Streamlit
            - QR Code generation
            - Pillow image processing
            - OpenCV QR scanning
            """
        )
