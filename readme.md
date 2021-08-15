# Rappi Pay Fraudster Detection

## Repository Structure
This repository has the next structure:
- data: Directory where the raw and processed data sets are.
- notebooks:
    - 00-dbc-data-exploration.ipynb: In this notebook we explore the raw data and define the categorization of customers.
    - 01-dbc-fraudsters-model.ipynb: This notebook describes the development of the fraudsters detection model and test its accuracy.
- model: Directory with all the required resources to deploy the model as a lambda AWS function.
    - logit.py: File with the lambda function.
    - logistic.pkl: Model trained in notebooks/01-dbc-fraudsters-model.ipynb.
    - Required libraries.
- readme.md
- requirements.txt: Text file with all the required libraries and their specific versions. It could be used with pip to install them all.

## Key Findings
These are the relevant relationships we found in the data:
- There is a dependency between the place of transactions and the number of transactions. 
- Customers that usually make physical transacitions make more transactions.
- There is a positive linear relationship between the amount, cashback and discount of transactions.
- Customers who usually get accepted transactions, make more transactions.
- Customers that have commited fraud make more transactions.
- Customers that usually make physical transactions get less cashback.
- The more discount, the more cashback.

From our findings we propose the next hypothesis: Customers with higher number of transactions that usually buy in physical places are more likely to commit fraud.
In order to test this hypothesis we categorized customers as follows:
- Very High Potential Fraudster: Usually makes physical transactions and belong to the highest quartile of number of transactions.
- High Potential Fraudster: Usually makes physical transactions and belong to the second or third quartile of number of transactions.
- Low potential Fraudster: Otherwise.

After test the hypothesis by plotting the frequency of fraudster per cluster, we concluded that this categorization measures the likelihood of fraudsters rightly. We got the next likelihood per cluster:
- Very High Potential Fraudster: ~52% 
- High Potential Fraudster: ~36%
- Low potential Fraudster: ~12%

## Model Performance
The chosen model to detect a fraudster was a logistic regression. We trained the regression with all the variables of the customers table as the exogenous variables, except for *ID_USER* and *fraude*. The non numeric variables were transformed to binary variables.
After observed the ROC curve of true postive and false positives rates, we decided to fix the threshold to detect a fraudster in 20% of propability. After this threshold the rate of false positives keeps near 15% and the true postive rate is above 50%. Our model achives the following metrics:
- Accuracy rate: ~80%, probability of identify rightly a customer between fraudster and no fraudster.
- True positives rate: ~54%, probability of identify a fraudster given the customer actually is a fraudster.
- False postivies rate: ~15%, probability of identify a customer as fraudster and be mistaken.

For this model and given a significance level of 10%, the only significant variables are *monto*, *numero_tc* and *dcto*. So we can infer that knowing the frequency of transactions of a customer, its amounts and descounts we could detect if he or she is a fraudster. On the other hand, by comparing the absolute value of the coefficients of the binary variables, the most relevant non numeric variables are:
1. Most common type of transaction between "Física" and "Virtual".
2. Most frequent type of place where the customer makes his/her transactions.
3. Most common status of transactions.

In conclusion, having the data about the transactions of a customer we should be able of detecting if he or she is a potential fraudster regardless of personal features. This conclusion is coherent with our categorization of customers. We were able to cluster the customers by likelihood of fraudster only with their number of transactions and the type of transactions their usually does, physical or virtual.

## Model's Trade-Off
Our model assumes there is available data of previous transactions for the customer we want to assess. So it could be use to asses users of Rappi in order to detect their risk of become fraudster before offer them to became Rappi Pay cutomers, however this model couldn't be used to asses potential customers without records of previous transactions.

One possible improvement for this model is to train a logistic regression per cluster of customers as we ctaegorized them (Low, High and Very High potential fraudsters). This could improve precision due to we already demonstrate that the 3 defined segments have different distribution of people who have commited at least one fraud.

## Model Deployment

Finally, to deploy the model we used AWS lambda functions. The next steps were followed to deployment:
1. Develop a lambda function in a .py file and save it in a directory (model) with all the required resources to run it.
2. Upload the directory to S3 Amazon Service.
3. Create a lambda function in AWS that reads its code from the directory saved in S3.
4. Create a Trigger as an API Gateway with REST protocol.

In order to use the API make a POST request to the next URL: https://us34m7wtk8.execute-api.us-west-1.amazonaws.com/default/rappi-fraudsters-detection . The body of the request must be a JSON with the next variables and values:
- genero: gender (M, F or --).
- monto: average amount that the customer usually makes in each transaction.
- numero_tc: number of transactions that the customer makes per month.
- hora: Median hour of transactions.
- establecimiento: Most frequent type of place where the customer makes his/her transactions (Super, MPago, Abarrotes, Farmacia, Restaurante, Otro).
- ciudad: Most common city where the customer makes his/her transactions (Merida, Guadalajara, Toluca, Monterrey, Otro).
- tipo_tc: Most common type of transaction between "Física" and "Virtual".
- linea_tc: Maximum credit line of the customer.
- interes_tc: Maximum credit rate of the customer.
- status_txn:  Most common status of transactions (Aceptada, Rechazada, En Proceso).
- is_prime: If the customer is has a prime membership (Boolean).
- dcto: Average descount.
- cashback: Average cashback.
- model: Most common device model from where the customer perform his/her transactions (year).
- device_score:  Most common device score from where the customer perform his/her transactions (1 to 5). 
- os: Most common operating system from where the customer perform his/her transactions (ANDROID, ., WEB, %%).

An example of the body for the request would be:
{
    "genero": "M",
    "monto": 318.5659316422405,
    "numero_tc": 3,
    "hora": 11,
    "establecimiento": "Farmacia",
    "ciudad": "Monterrey",
    "tipo_tc": "Física",
    "linea_tc": 33000,
    "interes_tc": 54,
    "status_txn": "Aceptada",
    "is_prime": false,
    "dcto": 45.39313788479337,
    "cashback": 2.731727937574471,
    "model": 2020,
    "device_score": 2,
    "os": "WEB"
  }
  
The model returns the probability of being a fraudster and if we consider him/her a fraudster (probability > 20%). The response body of the example request is:

{
    "risk": 0.16823082037079862,
    "fraudster": "False"
}

To test the API you could use the next web site, make a POST request with a similar body to the listening URL.
- Web Stie: https://reqbin.com/
- Listening URL: https://us34m7wtk8.execute-api.us-west-1.amazonaws.com/default/rappi-fraudsters-detection 