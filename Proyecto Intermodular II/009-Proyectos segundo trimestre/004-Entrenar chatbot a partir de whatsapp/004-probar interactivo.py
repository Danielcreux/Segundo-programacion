#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
BASE_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_DIR       = "qwen25-05b-jvc"   # carpeta donde guardaste el modelo entrenado

MAX_NEW_TOKENS = 128
TEMPERATURE    = 0.7
TOP_P          = 0.9

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype  = torch.float16 if device == "cuda" else torch.float32

print("🔧 Loading tokenizer and model...")
print(f"Using device: {device}")

# -------------------------------------------------------------------
# TOKENIZER
# -------------------------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# -------------------------------------------------------------------
# MODEL LOADING (AUTO-DETECT PEFT vs FULL MODEL)
# -------------------------------------------------------------------
adapter_config_path = os.path.join(MODEL_DIR, "adapter_config.json")

if os.path.exists(adapter_config_path):
    # Caso: LoRA / PEFT
    print(f"Detected PEFT adapter at '{MODEL_DIR}'. Loading base model + adapter...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        dtype=dtype,
    )
    model = PeftModel.from_pretrained(base_model, MODEL_DIR)
else:
    # Caso: modelo completo ya fine-tuned en MODEL_DIR
    print(f"No adapter_config.json found in '{MODEL_DIR}'.")
    print("Assuming full fine-tuned model directory. Loading directly...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        dtype=dtype,
    )

model.to(device)
model.eval()
print("✅ Model loaded.")


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

    # Keep only newly generated tokens (ignore the prompt part)
    generated_ids = output_ids[0, input_ids.shape[-1]:]
    reply = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    return reply


# -------------------------------------------------------------------
# SIMPLE INTERACTIVE LOOP
# -------------------------------------------------------------------
def main():
    print("\nInteractive test with trained model.")
    print("Type your question and press Enter.")
    print("Type 'exit' or 'quit' to finish.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        reply = generate_reply(user_input)
        print(f"AI: {reply}\n")


if __name__ == "__main__":
    main()

