import os
import pandas as pd

BASE_DIR = os.path.dirname(os.getcwd())

telco_customer_churn = pd.read_excel(os.path.join(BASE_DIR,'data','raw','Telco_customer_churn.xlsx')).drop(columns=['Count','Country','State','Latitude','Longitude','Lat Long','Dependents'])
telco_customer_demographics = pd.read_excel(os.path.join(BASE_DIR,"data","raw","Telco_customer_churn_demographics.xlsx")).drop(columns=['Gender', 'Count', 'Senior Citizen', 'Dependents'])
telco_customer_location = pd.read_excel(os.path.join(BASE_DIR,"data","raw","Telco_customer_churn_location.xlsx")).drop(columns=['City', 'Zip Code','Count','Country','State','Lat Long','Latitude','Longitude'])
telco_customer_population = pd.read_excel(os.path.join(BASE_DIR,"data","raw","Telco_customer_churn_population.xlsx"))
telco_customer_services= pd.read_excel(os.path.join(BASE_DIR,"data","raw","Telco_customer_churn_services.xlsx")).drop(columns=['Online Backup','Monthly Charge','Tenure in Months','Streaming Movies','Streaming TV','Payment Method','Paperless Billing','Contract','Online Security','Phone Service','Total Charges','Multiple Lines','Internet Service'])
telco_customer_churn_status = pd.read_excel(os.path.join(BASE_DIR,"data","raw","Telco_customer_churn_status.xlsx")).drop(columns=['Churn Label', 'Churn Reason', 'Churn Value', 'Churn Score', 'CLTV'])


df = (
pd.merge(left=telco_customer_churn,right=telco_customer_demographics,left_on='CustomerID',right_on='Customer ID')
    .drop(columns=['Customer ID'])
    .merge(right=telco_customer_location,left_on='CustomerID',right_on='Customer ID')
    .drop(columns=['Customer ID'])
    .merge(right=telco_customer_population,on='Zip Code')
    .drop(columns=['ID'])
    .merge(right=telco_customer_services,left_on='CustomerID',right_on='Customer ID')
    .drop(columns=['Quarter','Count','Service ID','Customer ID'])
    .merge(right=telco_customer_churn_status,left_on='CustomerID',right_on='Customer ID')
    .drop(columns=['Count','Quarter','Status ID','Customer ID'])
).drop(columns=['Location ID','CustomerID'])


# df = df.assign(
#     phone_service = df['phone_service'].astype('category'),
#     multiple_lines = df['multiple_lines'].astype('category'),
#     partner = df['partner'].astype('category'),
#     senior_citizen = df['senior_citizen'].astype('category'),
#     gender = df['gender'].astype('category'),
#     internet_service = df['internet_service'].astype('category'),
#     online_security = df['online_security'].astype('category'),
#     online_backup= df['online_backup'].astype('category'),
#     device_protection= df['device_protection'].astype('category'),
#     tech_support= df['tech_support'].astype('category'),
#     streaming_tv= df['streaming_tv'].astype('category'),
#     streaming_movies= df['streaming_movies'].astype('category'),
#     contract= df['contract'].astype('category'),
#     paperless_billing= df['paperless_billing'].astype('category'),
#     payment_method= df['payment_method'].astype('category'),
#     total_charges = df['total_charges'].replace(r'^\s*$', '0', regex=True).astype(float),
#     churn_label = df['churn_label'].astype('category'),
#     churn_reason = df['churn_reason'].astype('category'),
#     under_30 = df['under_30'].astype('category'),
#     married = df['married'].astype('category'),
#     offer = df['offer'].astype('category'),
#     internet_type = df['internet_type'].astype('category'),
#     device_protection_plan = df['device_protection_plan'].astype('category'),
#     premium_tech_support = df['premium_tech_support'].astype('category'),
#     streaming_music = df['streaming_music'].astype('category'),
#     unlimited_data = df['unlimited_data'].astype('category'),
#     customer_status = df['customer_status'].astype('category'),
#     churn_category = df['churn_category'].astype('category'),
# )


demographics = ['Age','Gender','Married','Number of Dependents']
tenture_contract = ['Contract','Tenure Months']
services = ['Phone Service','Multiple Lines','Internet Service','Internet Type','Unlimited Data','Avg Monthly Long Distance Charges','Avg Monthly GB Download']
billing = ['Paperless Billing','Payment Method']
service_addons = ['Online Security', 'Online Backup', 'Device Protection Plan','Premium Tech Support','Streaming TV', 'Streaming Movies', 'Streaming Music']
engagement= ['Referred a Friend','Number of Referrals','Offer','Satisfaction Score']

###### Target 
target_labels = ['Churn Category', 'Churn Label', 'Customer Status', 'Churn Score', 'Churn Reason', 'Churn Value']

###### Drop
redundant = ['City','Zip Code','Partner','Senior Citizen','Under 30','Total Charges','Total Long Distance Charges','Tech Support','Device Protection','Population','Monthly Charges']
leakage_drops = ['Total Revenue', 'CLTV', 'Total Refunds', 'Total Extra Data Charges']


df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
process_cols =[ i.lower().replace(" ", "_") for i in (redundant + leakage_drops + demographics + tenture_contract + services + billing + service_addons + engagement + target_labels)]

df[process_cols].reset_index().rename(columns={'index':'customer_id'}).to_csv(path_or_buf=os.path.join(BASE_DIR,'postgres','customer_churn.csv'),doublequote=True,index=False)

