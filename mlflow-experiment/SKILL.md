---
name: mlflow-experiment
description: MLflow patterns covering experiment tracking, model registry, artifact logging, hyperparameter tuning, model serving, and CI/CD integration for ML workflows.
---

# MLflow Experiment Tracking

This skill should be used when managing machine learning experiments with MLflow. It covers experiment tracking, model registry, artifacts, hyperparameter tuning, and serving.

## When to Use This Skill

Use this skill when you need to:

- Track ML experiments and parameters
- Log metrics, artifacts, and models
- Manage model versions with Model Registry
- Serve models for inference
- Integrate ML tracking into CI/CD

## Basic Experiment Tracking

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("text-classification")

with mlflow.start_run(run_name="distilbert-v1"):
    # Log parameters
    mlflow.log_params({
        "model_name": "distilbert-base-uncased",
        "learning_rate": 2e-5,
        "batch_size": 16,
        "epochs": 3,
        "max_length": 256,
    })

    # Train model
    model, metrics = train_model(config)

    # Log metrics
    mlflow.log_metrics({
        "accuracy": metrics["accuracy"],
        "f1_score": metrics["f1"],
        "loss": metrics["loss"],
    })

    # Log artifacts
    mlflow.log_artifact("config.yaml")
    mlflow.log_artifact("confusion_matrix.png")

    # Log model
    mlflow.pytorch.log_model(model, "model")
```

## Step-Based Metric Logging

```python
with mlflow.start_run():
    for epoch in range(num_epochs):
        train_loss = train_epoch(model, train_loader)
        val_loss, val_acc = evaluate(model, val_loader)

        mlflow.log_metrics({
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
        }, step=epoch)
```

## Autologging

```python
# Scikit-learn
mlflow.sklearn.autolog()
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)  # Automatically logged

# PyTorch Lightning
mlflow.pytorch.autolog()

# XGBoost
mlflow.xgboost.autolog()

# Transformers
mlflow.transformers.autolog()
```

## Hyperparameter Tuning

```python
import optuna

def objective(trial):
    params = {
        "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True),
        "batch_size": trial.suggest_categorical("batch_size", [8, 16, 32]),
        "dropout": trial.suggest_float("dropout", 0.1, 0.5),
        "hidden_size": trial.suggest_int("hidden_size", 64, 512),
    }

    with mlflow.start_run(nested=True):
        mlflow.log_params(params)
        metrics = train_and_evaluate(params)
        mlflow.log_metrics(metrics)
        return metrics["f1_score"]

with mlflow.start_run(run_name="hyperopt-sweep"):
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=50)

    mlflow.log_params(study.best_params)
    mlflow.log_metric("best_f1", study.best_value)
```

## Model Registry

```python
# Register model from a run
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri, "text-classifier")

# Transition model stage
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="text-classifier",
    version=1,
    stage="Production",
)

# Load production model
model = mlflow.pyfunc.load_model("models:/text-classifier/Production")
predictions = model.predict(data)
```

## Model Serving

```bash
# Serve model locally
mlflow models serve -m "models:/text-classifier/Production" -p 5001

# Build Docker image
mlflow models build-docker -m "models:/text-classifier/Production" -n "classifier"
docker run -p 5001:8080 classifier
```

```python
# Query served model
import requests

response = requests.post(
    "http://localhost:5001/invocations",
    json={"inputs": ["Great product!", "Terrible experience"]},
)
predictions = response.json()
```

## Custom Model Wrapper

```python
class TextClassifier(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        from transformers import pipeline
        self.pipe = pipeline("text-classification",
                            model=context.artifacts["model_path"])

    def predict(self, context, model_input):
        texts = model_input["text"].tolist()
        results = self.pipe(texts)
        return [r["label"] for r in results]

# Log custom model
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=TextClassifier(),
        artifacts={"model_path": "./trained_model"},
        pip_requirements=["transformers", "torch"],
    )
```

## Additional Resources

- MLflow: https://mlflow.org/docs/latest/
- Model Registry: https://mlflow.org/docs/latest/model-registry.html
- Tracking: https://mlflow.org/docs/latest/tracking.html
