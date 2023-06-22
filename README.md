## PDFSumarrizer
AI-powered summarizer for PDF files (powered by huggingface model)

Used model: [led-base-book-summary](https://huggingface.co/pszemraj/led-base-book-summary)https://huggingface.co/pszemraj/led-base-book-summary

Extracting text from PDF by **extract_text.py**

### Setup
**pip install -r requirements.txt**
rename **example.env** to **.env**

### Usage

You can use range of pages, if you want to summary only few pages you can change **starting_page** and **ending_page** variables in **model.py** file.
**python model.py -f file.pdf**


## Explanation of results
Output will be in folder **summary** pages will be in this format **summary_{page_number}.txt**.
The final output will summary all sumaries into one named: **summary_final.txt**.
