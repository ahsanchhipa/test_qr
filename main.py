
import streamlit as st
import csv
from io import StringIO, BytesIO
import qrcode
import base64
import svgwrite

# Conversion factor for centimeters to pixels
CM_TO_PIXELS = 37.795275590551

# Function to generate QR code as base64
def generate_qr_code_base64(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    
    # Convert QR code to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to create SVG labels with QR code and text
def create_svg_with_qr(csv_file, selected_fields):
    # Determine file type (BytesIO or StringIO)
    if isinstance(csv_file, BytesIO):  # Handle binary input
        csv_content = csv_file.getvalue().decode("utf-8")
    elif isinstance(csv_file, StringIO):  # Handle text input
        csv_content = csv_file.read()
    else:
        raise ValueError("Unsupported file type")
    
    # Parse CSV
    csv_reader = csv.DictReader(StringIO(csv_content))
    labels = []  # Store individual SVG labels
    
    # Iterate over rows and create SVG for each label
    for row in csv_reader:
        # Create a new SVG canvas for each label
        dwg = svgwrite.Drawing(size=(3.8 * CM_TO_PIXELS, 1.9 * CM_TO_PIXELS))
        
        # Generate QR code as base64
        qr_base64 = generate_qr_code_base64(row["lid"])
        
        # Add QR code image to SVG
        qr_x = 5  # Padding from left
        qr_y = 5  # Padding from top
        qr_size = 1 * CM_TO_PIXELS  # Size of QR code
        dwg.add(dwg.image(href=f"data:image/png;base64,{qr_base64}", insert=(qr_x, qr_y), size=(qr_size, qr_size)))
        
        # Add text fields to SVG
        text_x = qr_x + qr_size + 10  # Position text to the right of the QR code
        text_y = qr_y + 10  # Initial text position
        font_size = 12  # Font size for text
        
        for idx, field in enumerate(selected_fields):
            field_value = row.get(field, "N/A")
            dwg.add(dwg.text(
                f"{field}: {field_value}",
                insert=(text_x, text_y + idx * (font_size + 2)),  # Add spacing between lines
                font_size=f"{font_size}px",
                fill="black"
            ))
        
        # Add SVG content to labels
        labels.append(dwg.tostring())
    
    # Combine all SVG labels into one document
    return "\n".join(labels)

# Streamlit app
st.title("QR Label Generator (SVG Output)")

# Upload CSV file
uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_csv is not None:
    try:
        st.success("CSV uploaded successfully.")
        
        # Read CSV to show field options dynamically
        csv_file_content = uploaded_csv.getvalue().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_file_content))
        fieldnames = csv_reader.fieldnames
        
        # Allow user to select which fields to display on the label
        selected_fields = st.multiselect("Select fields to display", fieldnames, default=fieldnames)
        
        # Generate SVG with QR codes
        svg_content = create_svg_with_qr(uploaded_csv, selected_fields)
        
        # Provide download button for the SVG
        st.download_button(
            label="Download SVG Labels",
            data=svg_content,
            file_name="labels.svg",
            mime="image/svg+xml"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
