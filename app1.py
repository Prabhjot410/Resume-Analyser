import streamlit as st
from textblob import TextBlob
import PyPDF2
import time
from pyresparser import ResumeParser
import os
from app import generate_project_description, extract_text_from_pdf, perform_keyword_matching,extract_skills, compare_job_description_resume,extract_name,show_pdf,extract_text,NAME


def main():
    #st.set_page_config(page_title="Resume Suggestion App", page_icon=":pencil2:")

    st.title("Resume Suggestion App")

    st.sidebar.title("Select an option")

    option = st.sidebar.selectbox("", ["User information","Project Description Generator", "Resume Analysis","Resume Score"])

    if option == "Project Description Generator":
        st.header("Generate Project Descriptions")
        prompt = st.text_input("Enter a prompt to generate a project description:")
        if st.button("Generate"):
            description = generate_project_description(prompt)
            st.write(description)

    elif option == "Resume Analysis":
        st.header("Analyze Resumes")
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
    
    
    
    elif option == "Resume Score":
        st.header("Resume Sections")     

        resume_file = st.file_uploader("Upload a resume in PDF format")

        if resume_file is not None:
            resume_text = extract_text_from_pdf(resume_file)

            resume_score = 0
            if 'Experience' or 'INTERNSHIP' in resume_text:
                resume_score = resume_score+20
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your Experience, It also indicates that you possess the skills and experience necessary to succeed in the role you are applying for.</h4>''',unsafe_allow_html=True)

            if 'Education' or 'EDUCATION'  in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education✍/h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Education✍. it helps potential employers build a picture of your qualifications for the job</h4>''',unsafe_allow_html=True)

            if 'SKILLS'in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Skills⚽</h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Skilss⚽. It will shows employers you have the abilities required to succeed in the role..</h4>''',unsafe_allow_html=True)

            if 'Achievements' or 'Accomplishments' or 'CERTIFICATIONS' in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certification🏅 </h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add certification🏅. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

            if 'Projects' or 'PERSONAL PROJECTS' in resume_text:
                resume_score = resume_score + 20
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',unsafe_allow_html=True)
            else:
                st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects🏅. It will show that you are experiences with real world problems.</h4>''',unsafe_allow_html=True)
            
            st.subheader("**Resume Score📝**")
            st.markdown(
                """
                <style>
                    .stProgress > div > div > div > div {
                        background-color: #d73b5c;
                    }
                </style>""",
                unsafe_allow_html=True,
            )
            my_bar = st.progress(0)
            score = 0
            for percent_complete in range(resume_score):
                score +=1
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1)
            st.success('** Your Resume Writing Score: ' + str(score)+'**')
            st.warning("** Note: This score is calculated based on the content that you have added in your Resume. **")
            st.balloons()
            
            
    elif option == "User information":
        
        st.header("Resume Info Extraction")
        # Resume analysis code
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            save_image_path = './Uploaded_Resumes/'+uploaded_file.name
            with open(save_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            show_pdf(save_image_path)
            resume_text = extract_text(uploaded_file)
            name,emails, phones = extract_name(resume_text)

            name = NAME(resume_text)

            st.write("Name:", name)
            st.write("Emails:", emails)
            st.write("Phones:", phones)
    

        
        

        

        

if __name__ == "__main__":
    main()
