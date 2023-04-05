import streamlit as st
import openai
import re
from streamlit.components.v1 import html
import PyPDF2
import subprocess
import textract
import spacy
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
# Install required libraries
subprocess.check_call(["python", "-m", "pip", "install", "textblob"])


# Set up OpenAI API credentials
openai.api_key = "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"


# Set page title and favicon
st.set_page_config(page_title="Project Description Generator", page_icon=":pencil2:")

# Define your CSS styles
css = """
    body {
        background-color: blue;
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





def app():
    
    st.title("Resume Suggestion App")

    job_posting_text = st.text_area("Enter the job description here:")
    resume_file = st.file_uploader("Upload a resume in PDF format")

    if st.button("Submit"):
        # Read the PDF file
        pdf_reader = PyPDF2.PdfFileReader(resume_file)
        resume_text = ""
        for page_num in range(pdf_reader.getNumPages()):
            resume_text += pdf_reader.getPage(page_num).extractText()
        resume_skills = extract_skills(resume_text)
        resume_suggestions = compare_job_description_resume(job_posting_text, resume_text)
        st.write("Resume Skills:", resume_skills)
        st.write("Resume Suggestions:", resume_suggestions)
        
        
        
        resume_text = extract_text_from_pdf(resume_file)
        
        # Perform keyword matching
        similarity_score = perform_keyword_matching(job_posting_text, resume_text)
        
        # Display the similarity score
        st.write(f'Resume similarity score: {similarity_score:.2f}')
        
        
        
        # Analyze the job posting using TextBlob
        job_posting_blob = TextBlob(job_posting_text)
        
        # Get the nouns and adjectives from the job posting
        job_posting_nouns = [word.lemmatize() for word, tag in job_posting_blob.tags if tag.startswith('NN')]
        job_posting_adjectives = [word.lemmatize() for word, tag in job_posting_blob.tags if tag.startswith('JJ')]
        
        # Analyze the resume using TextBlob
        resume_blob = TextBlob(resume_text)
        
        # Get the nouns and adjectives from the resume
        resume_nouns = [word.lemmatize() for word, tag in resume_blob.tags if tag.startswith('NN')]
        resume_adjectives = [word.lemmatize() for word, tag in resume_blob.tags if tag.startswith('JJ')]
        
        # Find the nouns and adjectives in the job posting that are not in the resume
        missing_nouns = set(job_posting_nouns) - set(resume_nouns)
        missing_adjectives = set(job_posting_adjectives) - set(resume_adjectives)
        
         # Display suggestions for improving the resume
        if len(missing_nouns) > 0 or len(missing_adjectives) > 0:
            st.write('Suggestions for improving your resume:')
            
            if len(missing_nouns) > 0:
                st.write('- Add more experience or skills related to these nouns:', ', '.join(missing_nouns))
                
            if len(missing_adjectives) > 0:
                st.write('- Use more of these adjectives to describe your experience or skills:', ', '.join(missing_adjectives))
        else:
            st.write('Your resume already appears to be a good match for this job posting!')
            
    
    
    
    st.title("Project Description Generator")
    
    prompt = st.text_area("Enter a prompt to generate a project description:")
    
    if st.button("Generate Description"):
        description = generate_project_description(prompt)
        st.markdown("## Project Description:")
        # Render your CSS styles using st.markdown
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

        html_string = """
            <p>{}</p>
        """.format(description)
        html(html_string)
        

    
            

            
            
  

            
              
            

if __name__ == '__main__':
    app()
