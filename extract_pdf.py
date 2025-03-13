import fitz  # PyMuPDF
import json

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    paragraphs = []

    for page in doc:
        text = page.get_text("text").strip()  # Extract and clean text
        if text:
            paragraphs.append(text)  # Store full page as a paragraph

    return paragraphs

# Extract text and save it
pdf_text = extract_text_from_pdf("amity_handbook.pdf")

# Save extracted text as JSON for easy searching
with open("amity_handbook.json", "w", encoding="utf-8") as file:
    json.dump({"content": pdf_text}, file, indent=4)

print("✅ Handbook text extracted and saved!")
