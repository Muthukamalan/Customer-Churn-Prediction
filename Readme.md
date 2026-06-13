# Telecommunication Churn Prediction


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
[![Makefile](https://img.shields.io/badge/Makefile-6D00CC?logo=gnu&logoColor=white)](https://www.gnu.org/software/make/)
[![DVC](https://img.shields.io/badge/DVC-945DD6?logo=dvc&logoColor=white)](https://dvc.org/)
[![Postgresql](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![S3](https://img.shields.io/badge/Amazon_S3-569A31?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
[![prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)



tags: #MachineLearning #Classification #Supervised #MLOps
tech: #python #numpy #pandas #scikit-learn #matplotlib #hydra #mlflow #postgresql #grafana #prometheus #Makefile #Linux #Docker #Docker-Compose #ruff #mypy #onnx #minio #s3 #pre-commit #fastapi

![Churn Prediction](./assets/CustomerChurn.png)


## DATA
[Telecommunication](https://accelerator.ca.analytics.ibm.com/bi/?perspective=authoring&pathRef=.public_folders%2FIBM%2BAccelerator%2BCatalog%2FContent%2FDAT00148&id=i9710CF25EF75468D95FFFC7D57D45204&objRef=i9710CF25EF75468D95FFFC7D57D45204&action=run&format=HTML&cmPropStr=%7B%22id%22%3A%22i9710CF25EF75468D95FFFC7D57D45204%22%2C%22type%22%3A%22reportView%22%2C%22defaultName%22%3A%22DAT00148%22%2C%22permissions%22%3A%5B%22execute%22%2C%22read%22%2C%22traverse%22%5D%7D) taken as part of this exercise

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

## Sample Script
### Debug
```sh
HYDRA_FULL_ERROR=1 python src/train/train.py mlflow.run_name=logistic_best_hparams
```

### Hyperparameter Search
```sh
HYDRA_FULL_ERROR=1 python src/hparams/hparams.py  -m hparams=random_forest_hparam
```