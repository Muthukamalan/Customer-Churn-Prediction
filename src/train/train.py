import logging
import os

import hydra
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
import rootutils

from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
from omegaconf import DictConfig, OmegaConf
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, TargetEncoder


root = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=False)
load_dotenv()


# 1. Create a concrete structural intersection
class EstimatorClassifier(BaseEstimator, ClassifierMixin):
    pass


logger = logging.getLogger("SimpleLogger")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("train.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# -----------------------------------
# 1. MLflow Tracking Server
# # -----------------------------------
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

# -----------------------------------
# 2. Needed for MinIO Artifact Upload
# -----------------------------------
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
os.environ["AWS_SIGNATURE_VERSION"] = "s3v4"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL")
os.environ["MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING"] = "true"


artifact_destination = os.getenv("MLFLOW_ARTIFACTS_DESTINATION")



@hydra.main(config_path=os.path.join(root, "configs"), config_name="train", version_base=None)
def main(cfg: DictConfig):
    print("=" * 70)
    print("Configuration:")
    print(OmegaConf.to_yaml(cfg))
    print("=" * 70)

    model_name: str = str(cfg.model._target_).replace(".", "_")

    experiment = MlflowClient().get_experiment_by_name(cfg.mlflow.experiment_name)
    if experiment is None:
        logger.info(f"Experiment '{cfg.mlflow.experiment_name}' does not exist. Creating it.")
        mlflow.create_experiment(cfg.mlflow.experiment_name, artifact_location=artifact_destination)
        mlflow.set_experiment(cfg.mlflow.experiment_name)
    else:
        logger.info(f"Experiment '{cfg.mlflow.experiment_name}' already exists with ID: {experiment.experiment_id}")
        mlflow.set_experiment(cfg.mlflow.experiment_name)

    
    

    mlflow.sklearn.autolog(log_datasets=False,log_input_examples=False,extra_tags={"model": model_name},log_models=False,silent=True,serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE)

    data_path = os.path.join(root, cfg.data.path)
    logger.info(f"\nLoading data from: {data_path}")
    df: pd.DataFrame = pd.read_csv(data_path).drop(columns=cfg.data.get("drop_cols", []))

    model: EstimatorClassifier = hydra.utils.instantiate(cfg.model)
    logger.info(f"\nModel: {model.__class__.__name__}")

    ##  # PREPROCESSING
    # 1. Drop unnecessary columns
    # df.drop(columns=list(cfg.data.drop_cols),inplace=True)

    service_addons = [
        "online_security",
        "online_backup",
        "device_protection_plan",
        "premium_tech_support",
        "streaming_tv",
        "streaming_movies",
        "streaming_music",
    ]

    # 2. Create new features
    df["referral_engagement"] = df["referred_a_friend"].map({"No": 0, "Yes": 1}) * df["number_of_referrals"]
    df["service_addons"] = (df[service_addons].astype(str).apply(lambda x: x.str.lower()) == "yes").astype(int).sum(axis=1)

    df.drop(columns=["referred_a_friend", "number_of_referrals"], inplace=True)
    df.drop(columns=service_addons, inplace=True)

    # 3. Conversion of variables
    df[df.select_dtypes(include="object").columns.tolist()] = df[df.select_dtypes(include="object").columns.tolist()].astype("category")

    df[cfg.data.target_col] = df[cfg.data.target_col].map({"No": 0, "Yes": 1}).astype(int)

    # 4. Imputation
    df = df.assign(
        offer=df["offer"].cat.add_categories(new_categories="No Offer").fillna("No Offer", inplace=False),
        internet_type=df["internet_type"].cat.add_categories(new_categories="No").fillna("No", inplace=False),
    )

    ##  # SPLIT
    X = df.drop(columns=cfg.data.target_col)
    y = df[cfg.data.target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["category", "object"]).columns.tolist()

    # Transofrmation Pipeline
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # Categorical: impute missing → one-hot encode
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", TargetEncoder()),
        ]
    )

    ## # Combine both into a ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


    
    try:
        with mlflow.start_run(run_name=cfg.mlflow.run_name, log_system_metrics=True, nested=False):
            print(f"{mlflow.get_artifact_uri()=}")
            print(f"{mlflow.get_tracking_uri()=}")

            run = mlflow.active_run()
            print(f"run_id: {run.info.run_id}; status: {run.info.status}")
            pipe.fit(X_train, y_train)

            y_pred = pipe.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average="binary")
            rec = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="roc_auc")

            model_info = mlflow.sklearn.log_model(
                sk_model=pipe,
                name=model_name,
                tags={"model": cfg.model._target_, "run_name": cfg.mlflow.run_name},
            )
            logged_model = mlflow.get_logged_model(model_info.model_id)
            logger.info(f"Logged Model ID: {logged_model.model_id}")

            predictions = pipe.predict(X_train)
            mlflow.log_metrics(
                metrics={
                    "train_accuracy": accuracy_score(y_true=y_train, y_pred=predictions),
                    "train_precision": precision_score(y_true=y_train, y_pred=predictions),
                    "train_recall": recall_score(y_true=y_train, y_pred=predictions),
                    "train_f1_score": f1_score(y_true=y_train, y_pred=predictions),
                    "train_cv_mean_auc": np.mean(cv_scores),
                    "train_cv_std_auc": np.std(cv_scores),
                    "test_accuracy": acc,
                    "test_precision": prec,
                    "test_recall": rec,
                    "test_f1_score": f1,
                    "test_cv_mean_auc": np.mean(cv_scores),
                    "test_cv_std_auc": np.std(cv_scores),
                },
                model_id=logged_model.model_id,
            )

            # Log artifacts to MinIO
            logger.info("Logging artifacts to MinIO...")

            # Log confusion matrix as artifact

            fig, ax = plt.subplots()
            ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax)
            mlflow.log_figure(fig, "confusion_matrix.png")
            plt.close(fig=fig)

            # Log classification report as artifact
            report = classification_report(y_test, y_pred, output_dict=False)
            report_path = "classification_report.txt"
            with open(report_path, "w") as f:
                f.write(report)
            mlflow.log_artifact(report_path)
            logger.info(f"Logged classification report to S3: {report_path}")

            # Log training log
            # mlflow.log_artifact("train.log")
            logger.info("Logged training log to S3")

            # Clean up temporary artifact files
            if os.path.exists(report_path):
                os.remove(report_path)

    except Exception as e:
        logger.critical("Issue in the Train Flow:: " + str(e),exc_info=True)

    finally:
        mlflow.end_run()


if __name__ == "__main__":
    main()
