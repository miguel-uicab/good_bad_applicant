FROM python:3.8-slim-bullseye as build

WORKDIR /streamlit-app

COPY requirements.txt /streamlit-app/requirements.txt

RUN pip install -U pip && pip install -r /streamlit-app/requirements.txt 

COPY streamlit-app.py df_application_final_new.sav /streamlit-app/

EXPOSE 8501

CMD [ "streamlit", "run", "streamlit-app.py"]