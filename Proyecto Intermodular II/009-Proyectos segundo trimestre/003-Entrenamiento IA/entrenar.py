#!/usr/bin/env python3
import os
import json
from dataclasses import dataclass

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
)

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)

# -------------------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -------------------------------------------------------------------

DATA_PATH = "training_data.jsonl"
# Modelo pequeño y abierto de Qwen2.5 (ajústalo si quieres otro)
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
OUTPUT_DIR = "./qwen25-05b-jvc"

MAX_LENGTH = 512        # suficiente para ejemplos cortos
NUM_EPOCHS = 3
LR = 2e-4
BATCH_SIZE = 1
GRAD_ACCUM = 4          # batch efectivo = 4


def main():
    print("🚀 Inicio de entrenamiento Qwen2.5 (Python puro)")
    print(f"📁 Usando dataset: {DATA_PATH}")
    print(f"🧠 Modelo base: {MODEL_NAME}")
    print("-" * 60)

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"No se encontró el dataset en {DATA_PATH}")

    # -------------------------------------------------------------------
    # DETECTAR DISPOSITIVO
    # -------------------------------------------------------------------
    if torch.cuda.is_available():
        device = "cuda"
        use_4bit = True
        print("💻 GPU detectada (CUDA). Entrenando con QLoRA 4-bit.")
    else:
        device = "cpu"
        use_4bit = False
        print("💻 No hay GPU CUDA. Entrenando en CPU en float32 (esto será más lento).")

    # -------------------------------------------------------------------
    # CARGAR DATASET
    # -------------------------------------------------------------------
    print("📥 Cargando dataset con datasets.load_dataset(...)")
    raw_dataset = load_dataset(
        "json",
        data_files=DATA_PATH,
        split="train"
    )
    print(f"✅ Dataset cargado con {len(raw_dataset)} ejemplos.")

    # -------------------------------------------------------------------
    # CARGAR TOKENIZER Y MODELO
    # -------------------------------------------------------------------
    print("✅ Cargando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast=True
    )

    # Asegurar que tenemos pad_token definido
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("✅ Cargando modelo base...")
    if use_4bit:
        # QLoRA 4-bit en GPU
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        model = prepare_model_for_kbit_training(model)

        # Configuración LoRA
        lora_config = LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
    else:
        # Entrenamiento clásico en CPU
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        model.to(device)

    # -------------------------------------------------------------------
    # CONVERTIR messages → texto usando plantilla de chat
    # -------------------------------------------------------------------
    print("🧱 Transformando mensajes (user/assistant) en texto plano con plantilla de chat...")

    def messages_to_text(example):
        """
        Convierte el campo 'messages' del JSONL en un único texto
        usando la plantilla de chat del tokenizer.
        """
        conv = []
        for m in example["messages"]:
            role = m.get("role", "user")
            if role not in ("user", "assistant", "system"):
                role = "user"
            conv.append({"role": role, "content": m["content"]})

        try:
            text = tokenizer.apply_chat_template(
                conv,
                tokenize=False,
                add_generation_prompt=False,
            )
        except Exception:
            # Fallback sencillo si falla apply_chat_template
            partes = []
            for m in conv:
                if m["role"] == "user":
                    prefix = "Usuario"
                elif m["role"] == "assistant":
                    prefix = "Asistente"
                else:
                    prefix = m["role"]
                partes.append(f"{prefix}: {m['content']}")
            text = "\n".join(partes)
        return {"text": text}

    text_dataset = raw_dataset.map(
        messages_to_text,
        remove_columns=raw_dataset.column_names
    )

    # -------------------------------------------------------------------
    # TOKENIZACIÓN
    # -------------------------------------------------------------------
    print("✅ Tokenizando dataset...")

    def tokenize_fn(batch):
        out = tokenizer(
            batch["text"],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
        )
        out["labels"] = out["input_ids"].copy()
        return out

    tokenized_dataset = text_dataset.map(
        tokenize_fn,
        batched=True,
        remove_columns=["text"]
    )

    # -------------------------------------------------------------------
    # TRAINING ARGUMENTS (SIN evaluation_strategy NI HISTORIAS RARAS)
    # -------------------------------------------------------------------
    print("✅ Configurando argumentos de entrenamiento...")

    # Solo uno de fp16 / bf16 puede ser True. Usamos fp16 en GPU, nada en CPU.
    use_fp16 = (device == "cuda")
    use_bf16 = False

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        overwrite_output_dir=True,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        weight_decay=0.01,
        warmup_ratio=0.03,
        logging_steps=1,
        save_steps=20,
        save_total_limit=1,
        fp16=use_fp16,
        bf16=use_bf16,
        dataloader_pin_memory=False,
        report_to="none",  # sin wandb ni nada
    )

    # -------------------------------------------------------------------
    # TRAINER
    # -------------------------------------------------------------------
    print("✅ Creando Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # -------------------------------------------------------------------
    # ENTRENAR
    # -------------------------------------------------------------------
    print("🚂 Comenzando entrenamiento...")
    trainer.train()
    print("🏁 Entrenamiento terminado.")

    # -------------------------------------------------------------------
    # GUARDAR MODELO Y TOKENIZER
    # -------------------------------------------------------------------
    print("💾 Guardando modelo y tokenizer en", OUTPUT_DIR)
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("✅ Todo listo.")


if __name__ == "__main__":
    main()

