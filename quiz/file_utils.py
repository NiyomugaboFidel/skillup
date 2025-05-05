def process_uploaded_file(file_obj):
    """
    Process various file types and extract text content.
    Supports .txt, .docx, and .pdf files.
    
    Args:
        file_obj: The uploaded file object
        
    Returns:
        str: Extracted text content from the file
    """
    file_name = file_obj.name.lower()
    
    # Process TXT files
    if file_name.endswith('.txt'):
        return file_obj.read().decode('utf-8', errors='replace')
    
    # Process DOCX files
    elif file_name.endswith('.docx'):
        try:
            # Try mammoth first (better HTML conversion)
            import mammoth
            result = mammoth.convert_to_html(file_obj)
            return result.value
        except ImportError:
            try:
                # Fall back to python-docx
                from docx import Document
                document = Document(file_obj)
                return "\n".join([para.text for para in document.paragraphs])
            except ImportError:
                raise ImportError("Document processing libraries not available. Please install mammoth or python-docx.")
    
    # Process PDF files
    elif file_name.endswith('.pdf'):
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file_obj)
            content = []
            for page in pdf_reader.pages:
                content.append(page.extract_text())
            return "\n".join(content)
        except ImportError:
            raise ImportError("PDF processing library not available. Please install PyPDF2.")
    
    # Unsupported file type
    else:
        raise ValueError(f"Unsupported file type: {file_name}. Please upload .txt, .docx, or .pdf files.")