FROM python:3.9.0
EXPOSE 8501
cmd mkdir -p /app
WORKDIR /app
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt && \
    python -m spacy download en_core_web_sm
RUN pip install textblob nltk
RUN python -m textblob.download_corpora
RUN python -m nltk.downloader stopwords
COPY . .
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]