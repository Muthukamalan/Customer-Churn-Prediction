#!/bin/bash
set -e


# mlflow_db Table already create  
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE mlchurn;
EOSQL


psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "mlchurn" <<-EOSQL

DROP TABLE IF EXISTS customer_churn;
CREATE TABLE customer_churn (
    customer_id                        TEXT,
    city                               TEXT,
    zip_code                           TEXT,
    partner                            TEXT,
    senior_citizen                     TEXT,
    under_30                           TEXT,
    total_charges                      TEXT,
    total_long_distance_charges        TEXT,
    tech_support                       TEXT,
    device_protection                  TEXT,
    population                         TEXT,
    monthly_charges                    TEXT,
    total_revenue                      TEXT,
    cltv                               TEXT,
    total_refunds                      TEXT,
    total_extra_data_charges           TEXT,
    age                                TEXT,
    gender                             TEXT,
    married                            TEXT,
    number_of_dependents               TEXT,
    contract                           TEXT,
    tenure_months                      TEXT,
    phone_service                      TEXT,
    multiple_lines                     TEXT,
    internet_service                   TEXT,
    internet_type                      TEXT,
    unlimited_data                     TEXT,
    avg_monthly_long_distance_charges  TEXT,
    avg_monthly_gb_download            TEXT,
    paperless_billing                  TEXT,
    payment_method                     TEXT,
    online_security                    TEXT,
    online_backup                      TEXT,
    device_protection_plan             TEXT,
    premium_tech_support               TEXT,
    streaming_tv                       TEXT,
    streaming_movies                   TEXT,
    streaming_music                    TEXT,
    referred_a_friend                  TEXT,
    number_of_referrals                TEXT,
    offer                              TEXT,
    satisfaction_score                 TEXT,
    churn_category                     TEXT,
    churn_label                        TEXT,
    customer_status                    TEXT,
    churn_score                        TEXT,
    churn_reason                       TEXT,
    churn_value                        TEXT
);

\COPY customer_churn FROM '/docker-entrypoint-initdb.d/customer_churn.csv'  DELIMITER ','  CSV HEADER;

EOSQL