from gensim.corpora.wikicorpus import extract_pages, filter_wiki
from opencc import OpenCC

import bz2file
import re
import json

wiki_dump_file_path = "../download/zhwiki-20250201-pages-articles-multistream.xml.bz2"   
output_path = "./cleaned.json"

# custom filter
def wiki_replace(text):
    s = text
    s = re.sub(r':*{\|[\s\S]*?\|}', '', s)
    s = re.sub(r'<gallery>[\s\S]*?</gallery>', '', s)
    s = re.sub(r'(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
    s = filter_wiki(s)
    s = re.sub(r'\* *\n|\'{2,}', '', s)
    s = re.sub(r'\n+', '\n', s)
    s = re.sub(r'\n[:;]|\n +', '\n', s)
    s = re.sub(r'\n==', '\n\n==', s)
    return s


# extract

wiki = extract_pages(bz2file.open(wiki_dump_file_path))

with open(output_path, "w", encoding="utf-8") as out:
    count = 0
    for title, text, page_id in wiki:
        if count >= 1000: 
            break

        # skip special pages like edit histories
        if page_id in ["2"]:
            continue
        # skip help pages
        if re.findall('^[a-zA-Z]+:', text):
            continue

        # skip redirect pages
        if re.findall('^#', text):
            continue

        # special token replacement
        cleaned_text = filter_wiki(text)
        text = wiki_replace(text)


        # convert from traditional chinese to simplified chinese
        cc = OpenCC('t2s')
        cleaned_text = cc.convert(cleaned_text).strip()

        metadata = {
            "title": title,
            "page_id": page_id
        }
        entry = {
            "text": cleaned_text,
            "meta": metadata
        }

        out.write(json.dumps(entry, ensure_ascii=False) + '\n')
        count += 1
