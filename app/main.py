# !/usr/bin/env python
# coding: utf-8

import pickle
import pandas as pd
import numpy as np
import uvicorn
from fastapi import FastAPI
from prediction_functions import *


# Inicializar la estancia de la app ###########################################
app = FastAPI(title='Predecir si es un buen o mal aplicante a un crédito.',
              version='1.0',
              description='Random Forest es usado para predicción.')


# Bienvenida ##################################################################
@app.get('/')
def welcome():
    """
    Mensaje de Bienvenida.
    """
    Mensaje = 'Bienvenido a la API para medir el riesgo.'

    return Mensaje


# Función de predicción ######################################################
@app.post("/predict")
def predict(json_dict: Json_Dict,
            path='./'):
    """
    Toma como entrada una estructura json con la features
    necesarias para la predicción.
    Devuelve una diccionario con las siguientes llaves:
    1. probability: Probabilidad que el aplicante sea considerado como "malo".
    2. category: Categoría dependiente de la probabilidad.
                 Si la probabilidad es mayor a 0.5, la categoría será
                 'MALO', en caso contrario, será 'BUENO'.
    3. version: Versión del modelo.
    """

    config = get_config()
    features_names = config['features_names']
    float_names = config['float_names']
    variable_names = config['variable_names']
    categorical_names = config['categorical_names']

    row_data = [
                json_dict.FLAG_OWN_CAR,
                json_dict.FLAG_OWN_REALTY,
                json_dict.CNT_CHILDREN,
                json_dict.AMT_INCOME_TOTAL,
                json_dict.NAME_INCOME_TYPE,
                json_dict.NAME_EDUCATION_TYPE,
                json_dict.NAME_FAMILY_STATUS,
                json_dict.NAME_HOUSING_TYPE,
                json_dict.DAYS_BIRTH,
                json_dict.DAYS_EMPLOYED,
                json_dict.FLAG_WORK_PHONE,
                json_dict.FLAG_PHONE,
                json_dict.FLAG_EMAIL,
                json_dict.OCCUPATION_TYPE
                ]

    df = pd.DataFrame(columns=variable_names,
                      data=np.array(row_data).reshape(1, 14))

    # Se convierte a tipó numérico las variables correspondientes.
    df = transform_data_type_to_float(data=df,
                                      list_names=['DAYS_BIRTH',
                                                  'DAYS_EMPLOYED'])

    df["AGE"] = -df['DAYS_BIRTH'] / 365
    df["AGE"] = df["AGE"].astype(int)
    df['WORK_YEARS'] = -df['DAYS_EMPLOYED'] / 365
    df["WORK_YEARS"] = df["WORK_YEARS"].astype(int)

    # Se convierte a tipó numérico las variables correspondientes.
    df = transform_data_type_to_float(data=df,
                                      list_names=float_names)

    df_FILLNA_CATEGORIC = fillna_categoric_data(data=df,
                                                list_names=categorical_names)

    df_HOMO_CLASS = df_FILLNA_CATEGORIC.copy()

    df_HOMO_CLASS['NAME_EDUCATION_TYPE'] = list(map(NAME_EDUCATION_TYPE_class,
    df_HOMO_CLASS['NAME_EDUCATION_TYPE']))
    df_HOMO_CLASS['NAME_HOUSING_TYPE'] = list(map(NAME_HOUSING_TYPE_clas,
    df_HOMO_CLASS['NAME_HOUSING_TYPE']))
    df_HOMO_CLASS['OCCUPATION_TYPE'] = list(map(OCCUPATION_TYPE_class,
    df_HOMO_CLASS['OCCUPATION_TYPE']))

    # Se tiene la data con el orden correcto de las variables.
    feature_names_order = get_feature_names_order(float_names=float_names,
    categorical_names=categorical_names)
    data_order = df_HOMO_CLASS[feature_names_order]

    # Se carga modelo.
    clf = pickle.load(open(f'{path}risk_model.sav', 'rb'))

    # Cálculo de probabilidades.
    predict_array = clf.predict_proba(data_order)
    probability = round(predict_array[0][1], 2)

    # Categoría.
    if probability <= 0.5:
        category = 'BUENO'
    else:
        category = 'MALO'

    # Estructura json resultante.
    output = {'probability': probability,
              'category': category,
              'version': '1.0'}

    return output


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=8000,
                log_level="info",
                reload=True)
