import pandas as pd
import numpy as np
from statsmodels.discrete.discrete_model import Logit
import statsmodels.api as sm
import json

model_fit = sm.load('logistic.pkl')

def f_tranform_customer_features(customer):
    columns = ['monto', 'numero_tc', 'hora', 'linea_tc', 'interes_tc', 'is_prime',
       'dcto', 'cashback', 'device_score', 'ciudad_Guadalajara',
       'ciudad_Merida', 'ciudad_Monterrey', 'ciudad_Otro', 'ciudad_Toluca',
       'genero_--', 'genero_F', 'genero_M', 'model_2020', 'tipo_tc_Física',
       'tipo_tc_Virtual', 'status_txn_Aceptada', 'status_txn_En proceso',
       'status_txn_Rechazada', 'establecimiento_Abarrotes',
       'establecimiento_Farmacia', 'establecimiento_MPago',
       'establecimiento_Otro', 'establecimiento_Restaurante',
       'establecimiento_Super', 'os_%%', 'os_.', 'os_ANDROID', 'os_WEB']
    
    df_customer = pd.DataFrame.from_dict(customer, orient='index').transpose()
    df_customer = pd.get_dummies(data=df_customer,
                                 columns=['genero','establecimiento','ciudad','tipo_tc','status_txn','os']
                                )
    df_customer['is_prime'] = df_customer['is_prime']*1 
    for col in columns:
        try:
            df_customer[col] = df_customer[col]
        except:
            df_customer[col] = 0
    return df_customer[columns]

def f_detect_fraudster(customer):
    customer_mod = f_tranform_customer_features(customer)
    fraudster_risk = model_fit.predict(customer_mod.astype(float))[0]
    return {'risk':fraudster_risk,'fraudster':str(fraudster_risk>0.2)}

def lambda_handler(event, context):  
    customer = json.loads(event['body'])
    print("Customer params: " + str(customer))
    
    return {  "body": json.dumps(f_detect_fraudster(customer)) }