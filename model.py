#!/usr/bin/env python3
import torch
from transformers import pipeline
from dotenv import load_dotenv
import argparse
from PyPDF2 import PdfReader
import os

load_dotenv()
hf_name = os.environ.get("HF_NAME")
source_documents = os.environ.get("SOURCE_DOCUMENTS")
output_dir = os.environ.get("OUTPUT_DIR")

min_length=8
max_length=512
no_repeat_ngram_size=3 
encoder_no_repeat_ngram_size=3
repetition_penalty=3.5
num_beams=4
do_sample=False
early_stopping=True

writePerPage = True # default: True, writing summaries per page
starting_page = 0 # 0 as starting index
ending_page = 0 # if 0 then whole pdf

def return_full_path(folder: str):
    return os.getcwd()+"/"+folder


def summarize_text_chunks(text:str, summarizer, chunk_size=16384):
    # Split the text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    #? summarizer = pipeline("summarization", model="stevhliu/my_awesome_billsum_model")

    # Processing summaries
    summaries = [summarize(chunk, summarizer) for chunk in chunks]

    return summaries

def summarize(text:str, summarizer):
    result = summarizer(
            text,
            min_length=min_length, 
            max_length=max_length,
            no_repeat_ngram_size=no_repeat_ngram_size, 
            encoder_no_repeat_ngram_size=encoder_no_repeat_ngram_size,
            repetition_penalty=repetition_penalty,
            num_beams=num_beams,
            do_sample=do_sample,
            early_stopping=early_stopping,
    )

    return result[0]["summary_text"]


def main():
    # init summarizer
    summarizer = pipeline(
        "summarization",
        hf_name,
        device=0 if torch.cuda.is_available() else -1,
    )

    args = parse_arguments()
    if args.select_documents:
        file_name = ""
        file_names = os.listdir(return_full_path(source_documents))

        # selecting file
        while not file_name in file_names:
            file_names = os.listdir(return_full_path(source_documents))
            print(f"Choose a file by index (1,2,3,4): \n {file_names} \n\n")
            file_name_index = input(">")
            file_name = file_names[file_name_index]

        with open(return_full_path(source_documents+"/"+file_name), "r") as file:
            text = file.read()
            summaries = summarize_text_chunks(text, summarizer)
            

    else:
        if args.file:
            if os.path.isfile(args.file):
                match args.file[-4:]: # last 4 chars
                    case ".txt":
                        # summary by text chunks (one chunk -> 16384)
                        with open(args.file, "r") as file:
                            text = file.read()
                        summaries = summarize_text_chunks(text, summarizer)

                    case ".pdf":
                        # summary each page
                        reader = PdfReader(args.file)
                        ending_page = len(reader.pages) if not ending_page else ending_page
                        summaries = []
                        for page_number in range(starting_page, ending_page):
                            text = reader.pages[page_number].extract_text()
                            summary = summarize(text, summarizer)
                            summaries.append(summary)
                            if writePerPage:
                                # write summary of each page in summary folder
                                with open(return_full_path(output_dir+"/summary_"
                                                           +str(page_number)+".txt"), "w") as file:
                                    file.write(summary)
                    case _default:
                        print("Suffix not supported.")
                        exit()

            else:
                print("Invalid file.")
                exit()
        else:
            print("You must specify at least '-SD' or '-f' flag.")
            exit()


    # 32 -> 16384 // 512
    ending_chunk = 16384 // max_length
    # summarize until only one summary remains
    while len(summaries) > 1:
        # compile chunks into one string
        summaries = [''.join(summaries[i:i+ending_chunk-1]) for i in 
                     range(0, len(summaries), ending_chunk-1)]
        # summarize all strings
        summaries = [summarize(compiled_summary) for compiled_summary in summaries]

    with open(return_full_path(output_dir+"/summary_final.txt")) as file:
        file.write(summaries[0])

    print("**FINISHED**")

def parse_arguments():
    parser = argparse.ArgumentParser(description='PdfSummarizer: summary your pdf filesusing the power of LLMs.')

    parser.add_argument("--select-documents", "-SD",
                        action='store_true',
                        help='Use this flag to select document from source_documents folder.')
    parser.add_argument("--file", "-f", 
                        action='store', 
                        help='Specifify a file to use')
    return parser.parse_args()


if __name__ == "__main__":
    main()