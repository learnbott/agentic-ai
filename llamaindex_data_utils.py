import json, os
from llama_parse import LlamaParse
from llama_index.core import Document

def extract_text_from_pdf(pdf_urls, llama_api_key, llamaparse_kwargs={}, save_json_path=None):
    
    parser = LlamaParse(api_key=llama_api_key, **llamaparse_kwargs)
    
    documents = []
    for pdf in pdf_urls:
        assert os.path.exists(pdf), f"pdf file not found: {pdf}"
        print('processing pdf:', pdf)
        documents += parser.load_data(pdf)

    if save_json_path:
        with open(save_json_path, "r") as f:
            result = json.load(f)
            documents.append(Document(text=result['text']))
    
    return documents