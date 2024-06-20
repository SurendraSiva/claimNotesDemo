from django.shortcuts import render
from .forms import DocumentForm,PromptForm
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
import os
import pandas as pd
from langchain_community.llms import Ollama
from Claim.models import Prompts
from django.http import JsonResponse
import json
question=[]
def save_table_data(request):
    global question
    question=[]
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table_data = data.get("data", [])
            for i in table_data:
                question.append(' '.join([i[1],i[2],'in the provided',i[3],', you are expected to output a',i[0],'in the',i[4],'format',i[5]]))
            print(question)
            print('\n')
            request.session['question'] = question
            return JsonResponse({"success": True})
        except Exception as e:
            print(e)
            return JsonResponse({"success": False})
    else:
        return JsonResponse({"success": False})


def extract_text(file_path):
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        text = f"Error extracting text from PDF: {e}"
    return text

def tokenize(text):
    chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=500)
    t_chunks = splitter.split_text(text)
    for i in t_chunks:
        chunks.append(re.sub(r'[\s\n\uf0b7]{2,}', ' ', i))
    return chunks

def Vectorize(chunks):
    embeddings = OllamaEmbeddings(model='nomic-embed-text')
    vector_store = Chroma.from_texts(embedding=embeddings, texts=chunks)
    return vector_store

def similarity_search(vector_store, question):
    relevant_docs = []
    for i in question:
        relevant_docs.append(vector_store.as_retriever().invoke(i))
    return relevant_docs

def Query_manipulation(retrieved_docs, question):
    updated_queries = []
    for i in range(len(question)):
        doc_content = '\n\n'.join(doc.page_content for doc in retrieved_docs[i])
        updated_queries.append(f"Question: {question[i]}\n\nContext: {doc_content}")
    return updated_queries

def model_form_upload(request):
    response = []
    entry_list = []
    request.session['entry_list'] = entry_list
    global question
    s = Prompts.objects.all()
    s.delete()

    if request.method == 'POST' and 'upload' in request.POST:
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc_instance = form.save()
            file_path = doc_instance.document.path
            text = extract_text(file_path)
            request.session['text'] = text
            file_path2 = doc_instance.question.path
            excel = pd.read_excel(file_path2, sheet_name='Django_sheet')
            l = excel.values.tolist()
            entry_list = []
            for i in l:
                entry_list.append(i)
            for i in entry_list:
                question.append(i[8])
            request.session['question'] = question
            print(question)
            request.session['entry_list'] = entry_list
            for i in entry_list:
                Prompts.objects.create(Variable=i[0], Question_head=i[1], Entity_context=i[2], Document_type=i[3], Output_format=i[4], Gpt_instruction=i[5], Final_prompt=i[8])
            request.session['model'] = request.POST.get('model', 'llama3:latest')
            model_name = request.POST.get('model', 'llama3:latest')
            os.remove(file_path)
            os.remove(file_path2)
            text_chunks = tokenize(text)
            vector_store = Vectorize(text_chunks)
            relevant_docs = similarity_search(vector_store, question)
            updated_queries = Query_manipulation(relevant_docs, question)
            request.session['updated_queries'] = updated_queries

    if request.method == 'POST' and 'get_answers' in request.POST:
        question = request.session.get('question', [])
        print(question)
        print('\n')
        updated_queries = request.session['updated_queries']
        model_name = request.session['model']
       
        response = return_result(updated_queries, model_name, question)
    return render(request, 'model_form_upload.html', {'form': DocumentForm(), 'response': response, 'entry_list': entry_list, 'question': question})

def return_result(updated_questions, model_name, question):
    model = Ollama(model=model_name)
    resp = []
    for i in range(len(updated_questions)):
        response = model.invoke(updated_questions[i])
        resp.append({'question': question[i], 'answer': response})
    return resp
