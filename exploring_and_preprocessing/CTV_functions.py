# !/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import plotly.express as px


def threshold_str(due_list):
    """
    String necesario para el titulo de la gráfica.
    """
    if ('1' in due_list) and (len(due_list) == 5):
        string = '30'
    elif ('2' in due_list) and (len(due_list) == 4):
        string = '60'
    elif ('3' in due_list) and (len(due_list) == 3):
        string = '90'
    elif ('4' in due_list) and (len(due_list) == 2):
        string = '120'
    elif ('5' in due_list) and (len(due_list) == 1):
        string = '150'

    return string


def filter_integers(interval, lst):
    """
    XD
    """
    sorted_lst = sorted(lst, reverse=True)
    if interval == "bimonthly":
        return sorted_lst[::2]
    elif interval == "quarterly":
        return sorted_lst[::3]
    elif interval == "four-month period":
        return sorted_lst[::4]
    elif interval == "semester":
        return sorted_lst[::6]
    elif interval == "yearly":
        return sorted_lst[::12]
    else:
        raise ValueError("Interval not recognized")


def get_cohort_graph(df_vintage, chosen_bucket):
    """
    XD
    """
    threshold_value = threshold_str(chosen_bucket)
    fig = px.line(df_vintage,
                  x='month_on_book',
                  y='due_rate',
                  color='opening_month',
                  markers=True)
    fig.update_traces(marker=dict(size=5))
    title_str = f"Porcentaje acumulado de clientes morosos (> {threshold_value} días de atraso)"
    fig.update_layout(title=title_str)
    fig.show()


def get_vintage_analysis(n=None,
                         df_credit_extend=None,
                         chosen_bucket=None):  # , time_interval=None, with_graph=True):
    """
    XD
    """

    df_credit_extend_trunc = df_credit_extend[df_credit_extend['window'] >= n]

    df_credit_extend_trunc['STATUS_0_1'] = 0
    bad_aplicants_index_list =(df_credit_extend_trunc['STATUS'].isin(chosen_bucket))
    df_credit_extend_trunc.loc[bad_aplicants_index_list, 'STATUS_0_1'] = 1

    ##### denominator
    df_count_by_cohort = (df_credit_extend_trunc.groupby(['opening_month'])['ID']
                                                .nunique()
                                                .to_frame())
    df_count_by_cohort.reset_index(inplace=True)
    df_count_by_cohort.columns = ['opening_month', 'cohort_count']

    new_columns = ['opening_month', 'month_on_book']
    df_raw_vintage = (df_credit_extend_trunc[new_columns].drop_duplicates()
                                                         .sort_values(new_columns)
                                                         .reset_index(drop=True))
    df_raw_vintage['due_count'] = np.nan

    df_vintage = pd.merge(df_raw_vintage,
                          df_count_by_cohort,
                          on=['opening_month'],
                          how='left')

    for i in range(-60, 1):  # mes en el que se abrió la cuenta
        due_ids_lst = []
        for j in range(0, 61):  # mes después de que se abrió la cuenta
            df_1 = df_credit_extend_trunc[(df_credit_extend_trunc['STATUS_0_1']==1)  # localización de los clientes morosos
                                          & (df_credit_extend_trunc['month_on_book'] == j)
                                          & (df_credit_extend_trunc['opening_month'] == i)]
            due_ids = list(df_1['ID'])  # obtener el ID que cumple con la condición
            due_ids_lst.extend(due_ids)  # A medida que pasa el tiempo, añadir clientes morosos
            df_vintage.loc[(df_vintage['month_on_book'] == j)
                            & (df_vintage['opening_month'] == i), 'due_count'] = len(set(due_ids_lst))  # calcular números de ID no duplicados usando set()

    df_vintage['due_rate'] = df_vintage['due_count'] / df_vintage['cohort_count']  # calcular el % acumulado de clientes morosos"

    return df_vintage


def get_vintage_analysis_by_interval(df_vintage, time_interval):
    """
    Hace un filtrado del análisis completo de cohorts, obtenido de la
    función get_vintage_analysis. Las opciones son:
    1. "bimonthly": por bimestre.
    2. "quarterly": por trimestre.
    3. "four-month period": por cuatrimestre.
    4. "semester": por semestre.
    5. "yearly": anual.
    """
    lst_opening_month = df_vintage['opening_month'].unique().tolist()
    list_period = filter_integers(time_interval, lst_opening_month)
    df_final = df_vintage[df_vintage['opening_month'].isin(list_period)]

    return df_final


def get_mean_cohort(df_vintage=None,
                    chosen_bucket=None,
                    with_graph=True):
    """
    XD
    """
    threshold_value = threshold_str(chosen_bucket)
    df_vintage_pivot = df_vintage.pivot(index='opening_month',
                                        columns='month_on_book',
                                        values='due_rate')

    d_mean = df_vintage_pivot.reset_index(drop=True).mean().to_frame()
    d_mean.reset_index(drop=False, inplace=True)
    d_mean.columns = ['month_on_book', 'mean_porcentajes']

    if with_graph:
        fig = px.scatter(d_mean,
                         x='month_on_book',
                         y='mean_porcentajes',
                         title=f'Cohort promedio (> {threshold_value} días de atraso)')
        line_fig = px.line(d_mean,
                           x='month_on_book',
                           y='mean_porcentajes',
                           line_shape='linear')

        fig.add_traces(line_fig.data)  # Agregar las líneas al gráfico de dispersión

        fig.show()

    return d_mean


def inner_join(df1, df2):
    """
    df
    """
    df = pd.merge(df1,
                  df2,
                  on='month_on_book',
                  how='inner')

    return df
