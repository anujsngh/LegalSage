from utils import *
from functions import *
from data import *
import json
from flask import jsonify
from sectionData import rel_statutes_search1
import re
import pandas as pd


def rel_search(query, doc_type):
    if doc_type == "Statute":
        documents = load_txt_docs(doc_type=doc_type)
    print("preprocessing: starts")
    try:
        preprocessed_docs = load_preprocessed_docs(doc_type=doc_type)
    except Exception as e:
        print(e)
        if doc_type == "Case":
            print("Loading all pdf's text: start")
            documents = load_pdf_docs(doc_type=doc_type)
            print("Loading all pdf's text: ends")
        preprocessed_docs = store_preprocessed_docs(
            documents=documents, doc_type=doc_type)
    print("preprocessing: ends")
    preprocessed_query = preprocess_text(text=query)
    print("tfidf vector creation: starts")
    try:
        query_tfidf_matrix, doc_tfidf_matrix = load_doc_tfidf_matrix(
            preprocessed_query, doc_type=doc_type)
    except:
        query_tfidf_matrix, doc_tfidf_matrix = store_doc_tfidf_matrix(
            preprocessed_query, preprocessed_docs, doc_type=doc_type)
    print("tfidf vector creation: starts")
    print("Similarity Score Calc: starts")
    similarity_scores = compute_cosine_similarity_score(
        query_tfidf_matrix, doc_tfidf_matrix)
    print("Similarity Score Calc: ends")

    # return top_docs
    if doc_type == "Case":
        top_docs_idx = load_top_case_docs(similarity_scores, preprocessed_docs)
        return top_docs_idx
    elif doc_type == "Statute":
        top_docs = load_top_documents(similarity_scores, documents)
        return top_docs


def rel_cases_search(query):
    top_docs_idx = rel_search(query, doc_type="Case")

    try:
        case_pdfs_df = pd.read_csv(os.path.join(data_dir_path, "case_pdfs.csv"))
        top_case_pdfs_df = case_pdfs_df.iloc[top_docs_idx]
        if not top_case_pdfs_df.empty:
            return top_case_pdfs_df.to_dict(orient='records')
    except:
        print("Error no relevant case found")

    # # Create a list of dictionaries to represent the top documents
    # top_documents = []
    # for i, document in enumerate(top_docs):
    #     try:
    #         doc = document.split("\n")
    #         content = {
    #             "court": doc[1],
    #             "title": doc[0],
    #             "case_num": doc[4],
    #             "judge_date": doc[3],
    #             "judge_by": doc[5].split(": ")[1],
    #             "pet_name": doc[0].split(" v ")[0],
    #             "resp_name": doc[0].split(" v ")[1],
    #             "details": document
    #         }
    #         # Create a dictionary for each document
    #         doc_dict = {"doc_id": i+1, "content": content}
    #         top_documents.append(doc_dict)  # Add the dictionary to the list
    #     except:
    #         continue

    # return top_documents


def rel_statutes_search(query):
    top_docs = rel_search(query, doc_type="Statute")

    # Create a list of dictionaries to represent the top documents
    top_documents = []
    for i, document in enumerate(top_docs):
        try:
            doc = document.split("\n")
            doc_new = "\n".join(doc[4:])
            chapter_num = doc[0].split(" ")[1]
            section_num = doc[3].split(". ")[0]
            order_num = section_order_dict[f"{section_num}"]

            section_url = f"https://www.indiacode.nic.in/show-data?actid=AC_CEN_45_76_00001_200021_1517807324077&sectionId={13009+order_num}&sectionno={section_num}&orderno={order_num}"
            pdf_url = f"data/statute_docs/IT_ACT_2000/C{chapter_num}_S{section_num}.txt"

            content = {
                "act": "Information Technology Act 2000",
                "chapter_num": chapter_num,
                "chapter_title": doc[1].title(),
                "section_num": section_num,
                "section_title": doc[3].split(". ")[1],
                "section_url": section_url,
                "pdf_url": pdf_url,
                "details": doc_new,
            }
            # Create a dictionary for each document
            doc_dict = {"doc_id": i+1, "content": content}
            top_documents.append(doc_dict)  # Add the dictionary to the list
        except:
            continue

    return top_documents
    # return rel_statutes_search(query)


def case_search():
    return judgement_urls


def statute_search(query):
    # Define the regex pattern to extract the section number

    section_nums = extract_sections(query)

    sections_details = {}
    for section_num in section_nums:
        sections_details[section_num] = get_section_details(section_num)

    # Create a list of dictionaries to represent the top documents
    top_documents = []
    for i, document in enumerate(list(sections_details.values())):
        try:
            doc = document.split("\n")
            doc_new = "\n".join(doc[4:])
            chapter_num = doc[0].split(" ")[1]
            section_num = doc[3].split(". ")[0]
            order_num = section_order_dict[f"{section_num}"]

            section_url = f"https://www.indiacode.nic.in/show-data?actid=AC_CEN_45_76_00001_200021_1517807324077&sectionId={13009+order_num}&sectionno={section_num}&orderno={order_num}"
            pdf_url = f"data/statute_docs/IT_ACT_2000/C{chapter_num}_S{section_num}.txt"

            content = {
                "act": "Information Technology Act 2000",
                "chapter_num": chapter_num,
                "chapter_title": doc[1].title(),
                "section_num": section_num,
                "section_title": doc[3].split(". ")[1],
                "section_url": section_url,
                "pdf_url": pdf_url,
                "details": doc_new,
            }
            # Create a dictionary for each document
            doc_dict = {"doc_id": i+1, "content": content}
            top_documents.append(doc_dict)  # Add the dictionary to the list
        except:
            continue

    return top_documents
    # return rel_statutes_search(query)



if __name__ == "__main__":
    pass
