from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import json
from torch.utils.data import Dataset, DataLoader
from transformers import Trainer, TrainingArguments

# Load IndicBERT model and tokenizer (once)
MODEL_NAME = "ai4bharat/indic-bert-classification"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Map model outputs to domain intents
INTENT_LABELS = [
    "crop_advisory",
    "market_info",
    "weather_update",
    "pest_alert",
    "scheme_info",
    "faq"
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TRAIN_FILE = os.path.join(DATA_DIR, "train.jsonl")

class IntentDataset(Dataset):
    def __init__(self, data, tokenizer, label_map):
        self.data = data
        self.tokenizer = tokenizer
        self.label_map = label_map

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer(
            item["query"],
            truncation=True,
            padding="max_length",
            max_length=64,
            return_tensors="pt"
        )
        encoding = {k: v.squeeze(0) for k, v in encoding.items()}
        encoding["labels"] = torch.tensor(self.label_map[item["intent"]])
        return encoding

def load_training_data(train_file):
    with open(train_file, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return data

def train_model():
    label_map = {label: i for i, label in enumerate(INTENT_LABELS)}
    train_data = load_training_data(TRAIN_FILE)
    dataset = IntentDataset(train_data, tokenizer, label_map)
    training_args = TrainingArguments(
        output_dir=os.path.join(DATA_DIR, "output"),
        num_train_epochs=2,
        per_device_train_batch_size=8,
        logging_steps=10,
        save_steps=20,
        save_total_limit=2,
        remove_unused_columns=False,
        report_to=[]
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )
    trainer.train()
    trainer.save_model(os.path.join(DATA_DIR, "output"))

def classify_intent(query):
    inputs = tokenizer(query, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
    intent = INTENT_LABELS[predicted_class]
    return intent