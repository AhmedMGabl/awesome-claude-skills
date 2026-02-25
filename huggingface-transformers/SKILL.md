---
name: huggingface-transformers
description: Hugging Face Transformers patterns covering pipeline API, model fine-tuning, tokenizers, dataset loading, training with Trainer, inference optimization, and model hub integration.
---

# Hugging Face Transformers

This skill should be used when working with NLP and ML models using Hugging Face Transformers. It covers pipelines, fine-tuning, tokenizers, datasets, training, and inference.

## When to Use This Skill

Use this skill when you need to:

- Use pre-trained models for NLP tasks
- Fine-tune models on custom datasets
- Optimize inference performance
- Load and process datasets
- Push models to Hugging Face Hub

## Pipeline API (Quick Start)

```python
from transformers import pipeline

# Text classification
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
result = classifier("This product is amazing!")
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Text generation
generator = pipeline("text-generation", model="meta-llama/Llama-3.1-8B-Instruct")
output = generator("Explain quantum computing in simple terms:", max_new_tokens=200)

# Embeddings
embedder = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2")
embeddings = embedder("Hello world")

# Zero-shot classification
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
result = classifier("I need to fix a bug in production", candidate_labels=["urgent", "feature", "documentation"])
```

## Model and Tokenizer Loading

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

# Tokenize
inputs = tokenizer("Hello world", return_tensors="pt", padding=True, truncation=True, max_length=512)
# {'input_ids': tensor([...]), 'attention_mask': tensor([...])}

# Inference
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.softmax(outputs.logits, dim=-1)
```

## Dataset Loading

```python
from datasets import load_dataset, Dataset

# From Hub
dataset = load_dataset("imdb")
train = dataset["train"]
test = dataset["test"]

# From CSV/JSON
dataset = load_dataset("csv", data_files={"train": "train.csv", "test": "test.csv"})

# From dict
dataset = Dataset.from_dict({
    "text": ["Great product", "Terrible service", "Average quality"],
    "label": [2, 0, 1],
})

# Preprocessing
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=256)

tokenized = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
```

## Fine-Tuning with Trainer

```python
from transformers import Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions, average="weighted"),
    }

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=False,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    compute_metrics=compute_metrics,
)

trainer.train()
trainer.evaluate()
```

## PEFT / LoRA Fine-Tuning

```python
from peft import LoraConfig, get_peft_model, TaskType

lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_lin", "v_lin"],
)

peft_model = get_peft_model(model, lora_config)
peft_model.print_trainable_parameters()
# trainable params: 300K || all params: 66M || trainable%: 0.45%
```

## Push to Hub

```python
model.push_to_hub("my-username/my-model")
tokenizer.push_to_hub("my-username/my-model")
```

## Inference Optimization

```python
# Quantization
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=quantization_config,
    device_map="auto",
)

# ONNX export for production
from optimum.onnxruntime import ORTModelForSequenceClassification

ort_model = ORTModelForSequenceClassification.from_pretrained(model_name, export=True)
ort_model.save_pretrained("./onnx_model")
```

## Additional Resources

- Transformers: https://huggingface.co/docs/transformers/
- Datasets: https://huggingface.co/docs/datasets/
- PEFT: https://huggingface.co/docs/peft/
