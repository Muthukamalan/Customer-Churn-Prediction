# Telecommunication Churn Prediction

Blog Post: [churn-pred](https://muthukamalan.github.io/projects/mlops-churn-prediction/)

[![python](https://img.shields.io/badge/-Python_3.11_%7C_3.12_%7C_3.13-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![conda](https://img.shields.io/badge/Conda-44A833?logo=anaconda&logoColor=white)](https://docs.conda.io/)<br>

[![black](https://img.shields.io/badge/Code%20Style-Black-black.svg?labelColor=gray)](https://black.readthedocs.io/en/stable/)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) 
[![ruff](https://img.shields.io/badge/Ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![Precommit](https://img.shields.io/badge/pre--commit-FAB040?logo=precommit&logoColor=black)](https://pre-commit.com/)<br>

[![numpy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![sklearn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![hydra](https://img.shields.io/badge/Config-Hydra_1.3-89b8cd)](https://hydra.cc/)
[![Optuna](https://img.shields.io/badge/Optuna-6863FF?logo=optuna&logoColor=white)](https://optuna.org/)
[![Mlflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org/)<br>

[![DevContainer](https://img.shields.io/badge/Dev_Container-2496ED?logo=docker&logoColor=white)](https://containers.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

[![DVC](https://img.shields.io/badge/DVC-945DD6?logo=dvc&logoColor=white)](https://dvc.org/)
[![Postgresql](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![S3](https://img.shields.io/badge/Amazon_S3-569A31?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)

[![prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/)

[![Makefile](https://img.shields.io/badge/Makefile-6D00CC?logo=gnu&logoColor=white)](https://www.gnu.org/software/make/)


![Churn Prediction](./assets/CustomerChurn.png)


## DATA
[Telecommunication](https://accelerator.ca.analytics.ibm.com/bi/?perspective=authoring&pathRef=.public_folders%2FIBM%2BAccelerator%2BCatalog%2FContent%2FDAT00148&id=i9710CF25EF75468D95FFFC7D57D45204&objRef=i9710CF25EF75468D95FFFC7D57D45204&action=run&format=HTML&cmPropStr=%7B%22id%22%3A%22i9710CF25EF75468D95FFFC7D57D45204%22%2C%22type%22%3A%22reportView%22%2C%22defaultName%22%3A%22DAT00148%22%2C%22permissions%22%3A%5B%22execute%22%2C%22read%22%2C%22traverse%22%5D%7D) taken as part of this exercise


The primary objective is to show how modern MLOps tools work together to create a reproducible, scalable, and maintainable machine learning pipeline using all local setup.

1. Extract the zip and place it under mlchurn/data/raw/...
```sh
.
├── processed/
└── raw/
    ├── CustomerChurn.xlsx
    ├── Telco_customer_churn_demographics.xlsx
    ├── Telco_customer_churn_location.xlsx
    ├── Telco_customer_churn_population.xlsx
    ├── Telco_customer_churn_services.xlsx
    ├── Telco_customer_churn_status.xlsx
    └── Telco_customer_churn.xlsx
```
2. run `scripts/prep_db_ingestion.py` file. it'll prepares data and keeps is it in `mlchurn/data/processed/...` folder. postgresql pick this file and uploads into the "**mlchurn**" database and "**customer_churn**" table 


## Data Setup 
This project has designed to run everything on Docker.  But the requirement you need to install so, given from your input.
```sh
dvc init
dvc config core.autostage true
dvc config core.analytics false

# [dvc-doc](https://doc.dvc.org/command-reference/import-db#database-connections)
# dvc config db.pgsql.url postgresql://user@hostname:port/database
# dvc config --local db.pgsql.password password

dvc config db.pgsql.url "postgresql://mlflow_db:mlflow_db@localhost:5432/mlchurn"
dvc config --local db.pgsql.password mlflow_db

# [dvc-doc](https://doc.dvc.org/command-reference/import-db#installing-database-drivers)
# dvc import-db --table customers_table --conn pgsql

dvc import-db --table "customer_churn" --conn pgsql # import from table to CSV (local) md5 hash
```

## Components Setup
```sh
docker compose -f compose.local.yaml up -d # To setup all the container 
```
<div style="background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 12px 16px; margin: 16px 0; border-radius: 4px; font-family: sans-serif; color: #166534;">
<strong>💡 Tip:</strong> Service Discovery are all in build in the docker compose
</div>

  

![componets](/assets/containers_list.png)

### Hyersearch the Model  (Example: Decision Tree)
1. Decide which search space under `configs/hparams/decision_tree_hparam.yaml`
```yaml
params:
    model.max_depth: range(2, 20,5)
    model.min_samples_split: range(0,20,1)
    model.min_samples_leaf: choice(1, 2, 4)
```

2. Pass into the Shell 
```sh
HYDRA_FULL_ERROR=1 python src/hparams/hparams.py  -m hparams=decision_tree_hparam
# HYDRA_FULL_ERROR=1  to show full error the stdout
# -m indicate the --MULTIRUN
```

3. Optuna Under the hood.
```md
change no. of trails `n_trials: 20`
drection `direction: maxmize`
no of concurrent jobs `n_jobs: 1`
```

<!-- IMPORTANT CALLOUT (Purple) -->
<div style="background-color: #faf5ff; border-left: 5px solid #9333ea; padding: 12px 16px; margin: 16px 0; border-radius: 4px; font-family: sans-serif; color: #6b21a8;">
    <strong>✨ Important:</strong> Issues while facing multirun <br>
    - matplotlib.use("Agg")  # Forces a headless, thread-safe backend <br>
    - optimizing for <b>F1 Score</b>
</div>


![Hparam Search](./assets/hparams_search.png)

> [!IMPORTANT] Currently Supported Models
> 1. Logistic Regression
> 2. Decision Tree
> 3. Gradient Boosting Algorithms
> 4. Kneighbors 
> 5. Random Forest



### Run Model
```sh
HYDRA_FULL_ERROR=1 python src/train/train.py mlflow.run_name=rf_best_model model=random_forest
```

![Model Path](./assets/run_model.png)


**Each Model will be stored in the Minio Container**
![Artifact Path](./assets/minio_artifact_path.png)


### Inference
```sh
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000 AWS_ACCESS_KEY_ID=minio AWS_SECRET_ACCESS_KEY=minio123 mlflow models serve -m s3://BUCKET-NAME/models/MODELID/artifacts --env-manager local -p 
open http://localhost:5001/docs
```

```sh
curl -v http://localhost:5001/health
* Host localhost:5001 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:5001...
* connect to ::1 port 5001 from ::1 port 48692 failed: Connection refused
*   Trying 127.0.0.1:5001...
* Connected to localhost (127.0.0.1) port 5001
> GET /health HTTP/1.1
> Host: localhost:5001
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< date: Tue, 11 Aug 2026 19:27:10 GMT
< server: uvicorn
< content-length: 1
< content-type: application/json

###
$ curl -i http://localhost:5001/ping
HTTP/1.1 200 OK
date: Tue, 11 Aug 2026 19:29:42 GMT
server: uvicorn
content-length: 1
content-type: application/json
```

```
data = {
    "dataframe_split": {
        "columns": [ "day_number", "calories", "carbohydrates","protein", "fat", "sugar", "fiber", "sodium"],
        "data": [  [1, 2500, 300, 150, 80, 50, 25, 2000] ]
    }
}
```

```sh
ss -tupln | grep 5001
```

### Todo 
- [ ] Support All the Scikit Learn Model on the Classification Task
- [ ] Inference
- [ ] Add prometheus and Grafana Charts