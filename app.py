import streamlit as st
import openai
import re
from streamlit.components.v1 import html
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
        color: red;
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


def app():
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
