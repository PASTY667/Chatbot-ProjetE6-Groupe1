import utils.logger as logger
import logging as log
from pathlib import Path
from pypdf import PdfReader
import re

def return_path(file_path: str):
    return Path(file_path)



def extract_file_pdf(file_path):

    reader = PdfReader(str(file_path))

    headers = []
    footers = []
    body = []

    def visitor(text, cm, tm, font_dict, font_size):
        y = tm[5]

        if y > 750:
            headers.append(text)
        elif y < 100:
            footers.append(text)
        else:
            body.append(text)

    for page in reader.pages:
        page.extract_text(visitor_text=visitor)

    return {
        "headers": "".join(headers),
        "body": "".join(body),
        "footers": "".join(footers),
        "metadata": reader.metadata
    }

def extract_file_txt(file_path):
    file = open(file_path, "rt")
    text = file.read()
    file.close()
    return {
        "headers":"",
        "body": "".join(text),
        "footers": "",
        "metadata": ""

    }

def extract_file_md(file_path):
    with open(file_path, "rt", encoding="utf-8") as file:
        md_content = file.read()
        # Remove Markdown links/images
        text = re.sub(r'!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)', '', md_content)
        # Remove Markdown formatting symbols
        text = re.sub(r'[#*_>`-]', '', text)
        return {
            "headers": "",
            "body": "".join(text.strip),
            "footers": "",
            "metadata": ""

        }

def extract_text(file_path) :
    pass
