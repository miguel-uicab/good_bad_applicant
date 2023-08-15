import streamlit
import requests
import pandas as pd
import pickle

df = pickle.load(open('df_application_final_new.sav',
                      'rb'))


def run():
    """
    Desarrollo de un prototipo de aplicación web que despliega un modelo de
    predicción de morosos.
    """

    streamlit.title("Predicción de Perfil de Riesgo.")
    FLAG_OWN_CAR = streamlit.selectbox("¿TIENE CARRO PROPIO?",
                                       df.FLAG_OWN_CAR.unique())
    FLAG_OWN_REALTY = streamlit.selectbox("¿TIENE ALGUNA PROPIEDAD?",
                                          df.FLAG_OWN_REALTY.unique())
    NAME_INCOME_TYPE = streamlit.selectbox("TIPO DE INGRESO",
                                           df.NAME_INCOME_TYPE.unique())
    NAME_EDUCATION_TYPE = streamlit.selectbox("GRADO EDUCATIVO",
                                              df.NAME_EDUCATION_TYPE.unique())
    NAME_FAMILY_STATUS = streamlit.selectbox("ESTADO CIVIL",
                                             df.NAME_FAMILY_STATUS.unique())
    NAME_HOUSING_TYPE = streamlit.selectbox("TIPO DE VIVIENDA",
                                            df.NAME_HOUSING_TYPE.unique())
    OCCUPATION_TYPE = streamlit.selectbox("TIPO DE OCUPACIÓN",
                                          df.OCCUPATION_TYPE.unique())
    CNT_CHILDREN = streamlit.number_input("NÚMERO DE HIJOS")
    AMT_INCOME_TOTAL = streamlit.number_input("INGRESO TOTAL ANUAL")
    AGE = streamlit.number_input("EDAD")                             # 50
    WORK_YEARS = streamlit.number_input("AÑOS TRABAJANDO")           # 4
    DAYS_BIRTH = round(-365 * AGE, 2)
    DAYS_EMPLOYED = round(-365 * WORK_YEARS, 2)

    data = {
            "FLAG_OWN_CAR": FLAG_OWN_CAR,
            "FLAG_OWN_REALTY": FLAG_OWN_REALTY,
            "CNT_CHILDREN": CNT_CHILDREN,
            "AMT_INCOME_TOTAL": AMT_INCOME_TOTAL,
            "NAME_INCOME_TYPE": NAME_INCOME_TYPE,
            "NAME_EDUCATION_TYPE": NAME_EDUCATION_TYPE,
            "NAME_FAMILY_STATUS": NAME_FAMILY_STATUS,
            "NAME_HOUSING_TYPE": NAME_HOUSING_TYPE,
            "DAYS_BIRTH": DAYS_BIRTH,
            "DAYS_EMPLOYED": DAYS_EMPLOYED,
            "FLAG_WORK_PHONE": 0,
            "FLAG_PHONE": 0,
            "FLAG_EMAIL": 0,
            "OCCUPATION_TYPE": OCCUPATION_TYPE
           }

    if streamlit.button("Predict"):
        response = requests.post("http://0.0.0.0:8000/predict", json=data)
        prediction = response.text
        streamlit.success(f"RESULTADO: {prediction}")


if __name__ == '__main__':
    # by default it will run at 8501 port
    run()
