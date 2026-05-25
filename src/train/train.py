
import hydra
import mlflow
import pandas as pd
from omegaconf import DictConfig, OmegaConf
import os
from pathlib import Path

from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report,mean_squared_error, mean_absolute_error, r2_score
import numpy as np

import rootutils
root = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=False)

from sklearn.preprocessing import LabelEncoder,TargetEncoder,OneHotEncoder,OrdinalEncoder,StandardScaler
from sklearn.impute import SimpleImputer,KNNImputer,MissingIndicator
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import ClassifierMixin,BaseEstimator
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
# from sklearn.neighbors import KNeighborsClassifier



# 1. Create a concrete structural intersection 
class EstimatorClassifier(BaseEstimator, ClassifierMixin):
    pass

import logging
logger = logging.getLogger("SimpleLogger")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("train.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# -----------------------------------
# 1. MLflow Tracking Server
# # -----------------------------------
mlflow.set_tracking_uri("http://localhost:5000")

# -----------------------------------
# 2. Needed for MinIO Artifact Upload
# -----------------------------------
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minio"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"


@hydra.main(config_path=os.path.join(root, 'configs'), config_name="train", version_base=None)
def main(cfg: DictConfig):
    print("=" * 70)
    print("Configuration:")
    print(OmegaConf.to_yaml(cfg))
    print("=" * 70)

    mlflow.set_experiment(cfg.mlflow.experiment_name)
    mlflow.sklearn.autolog(
        log_datasets=False,
        log_input_examples=False,
        extra_tags={"model": cfg.model.__class__.__name__},
        log_models=True,
        silent=True,
        serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE
    )

    data_path = os.path.join(root, cfg.data.path)
    logger.info(f"\nLoading data from: {data_path}")
    df:pd.DataFrame = pd.read_csv(data_path).drop(columns=cfg.data.get("drop_cols", []))


    model:EstimatorClassifier = hydra.utils.instantiate(cfg.model)
    logger.info(f"\nModel: {model.__class__.__name__}")





    ##  # PREPROCESSING
    # 1. Drop unnecessary columns
    # df.drop(columns=list(cfg.data.drop_cols),inplace=True)

    service_addons= ['online_security', 'online_backup', 'device_protection_plan', 'premium_tech_support', 'streaming_tv', 'streaming_movies', 'streaming_music']
    
    # 2. Create new features
    df['referral_engagement'] = (df['referred_a_friend'].map({'No':0,'Yes':1}) * df['number_of_referrals'])
    df['service_addons'] = (df[service_addons].astype(str).apply(lambda x: x.str.lower()) == 'yes').astype(int).sum(axis=1)

    df.drop(columns=['referred_a_friend','number_of_referrals'],inplace=True) 
    df.drop(columns=service_addons,inplace=True)

    # 3. Conversion of variables
    df[df.select_dtypes(include='object').columns.tolist()]  = df[df.select_dtypes(include='object').columns.tolist()].astype('category')
    
    df[cfg.data.target_col] = df[cfg.data.target_col].map({'No':0,'Yes':1}).astype(int)

    # 4. Imputation 
    df = df.assign(
        offer = df['offer'].cat.add_categories(new_categories='No Offer').fillna('No Offer', inplace=False),
        internet_type = df['internet_type'].cat.add_categories(new_categories="No").fillna("No",inplace=False)
    )



    ##  # SPLIT
    
    X = df.drop(columns=cfg.data.target_col)
    y = df[cfg.data.target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y       
    )

    numerical_cols = X.select_dtypes(include=['int64','float64']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['category']).columns.tolist()


    # Transofrmation Pipeline
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])
    
    # Categorical: impute missing → one-hot encode
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot",  TargetEncoder()),
    ])


    ## # Combine both into a ColumnTransformer
    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer,   numerical_cols),
        ("cat", categorical_transformer, categorical_cols),
    ])

    pipe = Pipeline(steps=[("preprocessor", preprocessor),("model", model)])

    
    with mlflow.start_run(run_name=cfg.mlflow.run_name):
        pipe.fit(X_train, y_train)

        y_pred = pipe.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="roc_auc")
        rmse = mean_squared_error(y_test, y_pred) 
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        model_info = mlflow.sklearn.log_model(sk_model=pipe,tags={"model": cfg.model.__class__.__name__})
        logged_model = mlflow.get_logged_model(model_info.model_id)
        logger.info(f"Logged Model ID: {logged_model.model_id}")
        logger.info(f"Logged Model Params: {logged_model.params}")


        predictions = pipe.predict(X_train)
        mlflow.log_metrics(
            metrics={
                "rmse": rmse,
                "r2": r2,
                "mae": mae,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "cv_mean_auc": np.mean(cv_scores),
                "cv_std_auc": np.std(cv_scores)
            },
            model_id=logged_model.model_id,
            
        )
    


if __name__ == "__main__":
    main()