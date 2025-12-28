import fitz  # PyMuPDF
import pymupdf4llm

def pdf_to_markdown(input_pdf, output_md):
    # Open the PDF
    doc = fitz.open(input_pdf)
    
    # Convert entire document to Markdown
    md_text = pymupdf4llm.to_markdown(doc)
    
    # Save to .md file
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_text)

if __name__ == "__main__":
    pdf_to_markdown("pdf/Resumen módulos profesionales SMR_DAM_DAW.pdf", "input/resumen.md")

