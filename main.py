import streamlit as st
import openai
import re
from streamlit.components.v1 import html
import PyPDF2
import subprocess
import textract
import spacy
from pyresparser import ResumeParser
import base64,random
from textblob import TextBlob
import pdfplumber
from spacy.matcher import Matcher
import docx2txt
from sklearn.feature_extraction.text import CountVectorizer
# Install required libraries
subprocess.check_call(["python", "-m", "pip", "install", "textblob"])


# Set up OpenAI API credentials
openai.api_key = "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"


# Set page title and favicon
#st.set_page_config(page_title="Project Description Generator", page_icon=":pencil2:")

# Define your CSS styles
css = """
    body {
        background-color: white !important;
    }
    h1 {
        color: white;
    }
    .description {
        font-size: 20px;
        color: white;
    }
    p{
        color: white;
    }
"""
# Render your CSS styles using st.markdown
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


nlp = spacy.load('en_core_web_sm')

def extract_keywords(text):
    response = openai.Completion.create(
        engine="davinci",  # select the GPT-3 engine
        prompt=f"Extract keywords from the following text:\n{text}",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    keywords = response.choices[0].text.strip().split("\n")
    return keywords


 
def analyze_resume(resume_file):
    pdf_reader = PyPDF2.PdfFileReader(resume_file)
    num_pages = pdf_reader.getNumPages()
    resume = ""
    for i in range(num_pages):
        page = pdf_reader.getPage(i)
        resume += page.extractText()
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Analyze the following resume:\n{resume}",
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()



def generate_project_description(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
    )
    # Extract the generated text from the response
    description = response.choices[0].text
    # Remove any unnecessary whitespace and formatting
    description = re.sub('\s+', ' ', description).strip()
    return description


# Define function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    text = ''
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        text += page.extractText()
    return text



# Define function to perform keyword matching
def perform_keyword_matching(job_posting_text, resume_text):
    # Define the list of keywords to match
    keywords = ['python', 'java', 'c++', 'javascript', 'html', 'css', 'git']
    
    # Preprocess the job posting and resume text
    job_posting_text = re.sub('[^A-Za-z0-9]+', ' ', job_posting_text.lower())
    resume_text = re.sub('[^A-Za-z0-9]+', ' ', resume_text.lower())
    
    # Count the number of keyword matches in the job posting and resume text
    job_posting_matches = sum(keyword in job_posting_text for keyword in keywords)
    resume_matches = sum(keyword in resume_text for keyword in keywords)
    
    # Calculate the similarity score as the ratio of keyword matches in the resume to the number of keywords
    similarity_score = resume_matches / len(keywords)
    
    # Return the similarity score
    return similarity_score


def preprocess(text):
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text)  # remove non-alphanumeric characters
    text = text.lower()  # convert text to lowercase
    return text


def extract_skills(resume):
    # Extract skills from resume using OpenAI's GPT-3 API
    prompt = "Extract skills from the following text: " + resume + "\n\nSkills:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100,
        n=1,
        stop=None,
        timeout=15,
    )
    skills = response.choices[0].text
    skills = re.sub("Skills: ", "", skills).split(", ")
    return skills



def compare_job_description_resume(job_description, resume):
    # Compare job description and resume using OpenAI's GPT-3 API
    prompt = "Compare the following job description: " + job_description + "\n\nWith the following resume: " + resume + "\n\nSuggestions:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100,
        n=1,
        stop=None,
        timeout=15,
    )
    suggestions = response.choices[0].text
    suggestions = re.sub("Suggestions: ", "", suggestions).split(", ")
    return suggestions


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def extract_text(file):
    file_type = file.name.split(".")[-1]
    if file_type == "pdf":
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    elif file_type == "docx":
        text = docx2txt.process(file)
        return text
    else:
        raise ValueError("Unsupported file type")
    
    


def NAME(resume_text):
    model_engine = "text-davinci-002"
    prompt = (f"Extract the name from the given resume:\n"
              f"{resume_text}\n"
              f"Name:")

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    name = response.choices[0].text.strip()
    return name


def extract_name(resume_text):
    # Use spaCy to extract named entities
    doc = nlp(resume_text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Use regex to extract email addresses and phone numbers
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'

    emails = re.findall(email_pattern, resume_text)
    phones = re.findall(phone_pattern, resume_text)

    # Find the most probable name based on heuristics
    name = None
    for ent in entities:
        if ent[1] == "PERSON":
            if name is None or len(ent[0]) > len(name):
                name = ent[0]

    return name, emails, phones


def suggest_template(resume_data):
    # Replace this with your actual algorithm for template suggestion
    return "Dear [Hiring Manager],\n\nI am excited to apply for the [Position] role at [Company]."

