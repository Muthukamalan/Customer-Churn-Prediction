
import hydra
import mlflow
import pandas as pd
from omegaconf import DictConfig, OmegaConf
import os
from dataclasses import dataclass
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import numpy as np


from hydra.utils import instantiate
import rootutils
root = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=False)



# MLflow Setup
# # mlflow.set_tracking_uri("http://localhost:5000")

# os.environ["AWS_ACCESS_KEY_ID"] = "minio"
# os.environ["AWS_SECRET_ACCESS_KEY"] = "minio"
# os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"

@hydra.main(config_path=os.path.join(root, 'configs'), config_name="hparams", version_base=None)
def main(cfg: DictConfig):
    """
    Fine-tune model using Hydra Optuna Sweeper.
    Each trial trains a model with different hyperparameters.
    """
    
    print("=" * 80)
    print(f"Training with config: {cfg.get('model', {}).get('_target_', 'unknown')}")
    print("=" * 80)
    print()
    print("Configuration:")
    print(OmegaConf.to_yaml(cfg))
    print("=" * 80)
    print()

    model = instantiate(cfg.model)
    print(f"Instantiated model: {model.__class__.__name__}")
    
    import random
    score = random.random()
    return score


     
    
if __name__ == "__main__":
    main()