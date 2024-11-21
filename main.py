import streamlit as st
import csv
from io import StringIO, BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import qrcode
import os

# Function to generate QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    return img

# Function to create PDF with QR code and dynamic text for each row
def create_pdf_with_qr_from_csv(csv_file, label_width, label_height, selected_fields):
    output = BytesIO()

    # Define custom label size
    page_width = label_width
    page_height = label_height

    # Initialize canvas for single label per page
    c = canvas.Canvas(output, pagesize=(page_width, page_height))

    # Read CSV file
    csv_file.seek(0)
    csv_content = csv_file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(csv_content))

    qr_size = 1 * cm  # QR code size
    padding = 0.07 * cm  # Padding between elements

    # Process each row
    for row in csv_reader:
        # Draw label border
        c.rect(0, 0, label_width, label_height)

        # Generate QR code
        qr_img = generate_qr_code(row["lid"])
        qr_img_path = f"{row['lid']}_temp_qr.png"
        qr_img.save(qr_img_path)

        # Place QR code on label
        qr_x = padding
        qr_y = (label_height - qr_size) / 2  # Center QR vertically
        c.drawImage(qr_img_path, qr_x, qr_y, width=qr_size, height=qr_size)

        # Remove temporary QR image
        os.remove(qr_img_path)

        # Add selected fields as text
        text_x = qr_x + qr_size + padding
        text_y = label_height - padding - 0.35 * cm  # Start below the top margin text up and down

        c.setFont("Helvetica-Bold", 5.5)  # Adjust font size for label fit
        for idx, field in enumerate(selected_fields):
            field_value = row.get(field, "N/A")
            c.drawString(text_x, text_y - idx * 0.6 * cm, f"{field}: {field_value}")

        # Start a new page for each label
        c.showPage()

    # Save the PDF
    c.save()
    output.seek(0)
    return output

# Streamlit app
st.title("QR Label Generator")

# Set default label dimensions (3.8 cm x 1.9 cm)
label_width = 3.8 * cm
label_height = 1.9 * cm

# Upload CSV file
uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_csv is not None:
    try:
        st.success("CSV uploaded successfully.")

        # Read CSV to show field options dynamically
        csv_content = uploaded_csv.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_content))
        fieldnames = csv_reader.fieldnames

        # Allow user to select which fields to display in the label
        selected_fields = st.multiselect("Select fields to display", fieldnames, default=fieldnames)

        # Generate PDF with QR codes
        pdf_output = create_pdf_with_qr_from_csv(uploaded_csv, label_width, label_height, selected_fields)

        # Add download button
        st.download_button(
            label="Download QR Code PDF",
            data=pdf_output,
            file_name="QR_Labels.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
