#!/usr/bin/env python3
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os

load_dotenv()

pdf_documents = os.environ.get("PDF_DOCUMENTS")
source_documents = os.environ.get("SOURCE_DOCUMENTS")


def main():
    '''Extract all text from pdf file'''
    file_names = os.listdir(os.getcwd()+"/"+pdf_documents)
    for file_name in file_names:
        pdf_full_path = os.getcwd()+"/"+pdf_documents+"/"+file_name
        reader = PdfReader(pdf_full_path)
        
        source_full_path = os.getcwd()+"/"+source_documents+"/"+file_name
        if os.path.isfile(source_full_path):
            continue

        with open(source_full_path[:-3]+"txt", "a") as file:
            print(f"Extracting text from {file_name}")
            for page in reader.pages:
                text = page.extract_text()
                file.write(text)
            print(f"Saved in {source_full_path}")


if __name__ == "__main__":
    main()