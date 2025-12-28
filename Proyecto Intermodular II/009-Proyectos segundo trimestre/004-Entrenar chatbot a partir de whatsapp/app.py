#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import torch
from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
BASE_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_DIR       = "qwen25-05b-jvc"   # carpeta del modelo entrenado

MAX_NEW_TOKENS = 128
TEMPERATURE    = 0.7
TOP_P          = 0.9

# -------------------------------------------------------------------
# LOAD TOKENIZER + MODEL ONCE
# -------------------------------------------------------------------
print("🔧 Loading tokenizer and model for Flask app...")

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype  = torch.float16 if device == "cuda" else torch.float32

print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

adapter_config_path = os.path.join(MODEL_DIR, "adapter_config.json")

if os.path.exists(adapter_config_path):
    # LoRA / PEFT case
    print(f"Detected PEFT adapter at '{MODEL_DIR}'. Loading base model + adapter...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        dtype=dtype,
    )
    model = PeftModel.from_pretrained(base_model, MODEL_DIR)
else:
    # Full fine-tuned model case
    print(f"No adapter_config.json found in '{MODEL_DIR}'.")
    print("Assuming full fine-tuned model directory. Loading directly...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        dtype=dtype,
    )

model.to(device)
model.eval()
print("✅ Model loaded for Flask app.")


def generate_reply(user_message: str) -> str:
    """
    Given a user message, build a chat-style conversation and
    generate the assistant reply using Qwen's chat template.
    """
    messages = [
        {"role": "user", "content": user_message}
    ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_ids = output_ids[0, input_ids.shape[-1]:]
    reply = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    return reply


# -------------------------------------------------------------------
# FLASK APP
# -------------------------------------------------------------------
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": ""})

    print(f"User: {user_message}")
    reply = generate_reply(user_message)
    print(f"AI:   {reply}")

    return jsonify({"reply": reply})


if __name__ == "__main__":
    # Development server
    app.run(host="0.0.0.0", port=5000, debug=True)

