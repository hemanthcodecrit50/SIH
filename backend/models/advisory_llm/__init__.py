from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import torch
import os
import json
from torch.utils.data import Dataset

MODEL_NAME = "ai4bharat/indic-gpt"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KCC_TRAIN_FILE = os.path.join(DATA_DIR, "kcc_train.jsonl")

class KCCDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        prompt = f"Question: {item['question']}\nAnswer:"
        target = item['answer']
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_tensors="pt"
        )
        labels = self.tokenizer(
            target,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_tensors="pt"
        )["input_ids"].squeeze(0)
        encoding = {k: v.squeeze(0) for k, v in encoding.items()}
        encoding["labels"] = labels
        return encoding

def load_kcc_training_data(train_file):
    with open(train_file, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return data

def train_indicgpt():
    train_data = load_kcc_training_data(KCC_TRAIN_FILE)
    dataset = KCCDataset(train_data, tokenizer)
    training_args = TrainingArguments(
        output_dir=os.path.join(DATA_DIR, "output"),
        num_train_epochs=2,
        per_device_train_batch_size=4,
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

def generate_advisory(static_info, api_info, personalized):
    # Compose prompt with all context sources
    prompt = (
        f"Static Knowledge:\n{static_info}\n\n"
        f"External Data:\n{json.dumps(api_info, ensure_ascii=False, indent=2)}\n\n"
        f"Personalization:\n{personalized}\n\n"
        "Generate a clear, actionable advisory for the farmer based on the above information."
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=256, do_sample=True, top_p=0.95)
        advisory = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return advisory