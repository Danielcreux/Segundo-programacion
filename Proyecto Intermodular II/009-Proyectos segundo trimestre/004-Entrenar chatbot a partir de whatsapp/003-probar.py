#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

try:
    from peft import PeftModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False


# ==========================
# CONFIGURACIÓN
# ==========================
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"        # mismo modelo base que en entrenar.py
LORA_DIR   = "./qwen25-05b-jvc"             # carpeta donde entrenar.py guardó el LoRA o el modelo
MAX_NEW_TOKENS = 256
TEMPERATURE    = 0.7
TOP_P          = 0.9


def print_header():
    print("🚀 Test de modelo Qwen2.5 fine-tune (LoRA)")
    print(f"🧠 Modelo base: {MODEL_NAME}")
    print(f"📁 Carpeta LoRA / modelo: {LORA_DIR}")
    print("-" * 60)


def detect_device():
    if torch.cuda.is_available():
        device = "cuda"
        torch_dtype = torch.float16
        print("💻 GPU detectada (CUDA). Usando GPU con float16.")
    else:
        device = "cpu"
        torch_dtype = torch.float32
        print("💻 No se detecta GPU. Usando CPU con float32.")
    return device, torch_dtype


def load_tokenizer(model_name):
    print("✅ Cargando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # Por si el tokenizer no tiene pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_base_model(model_name, device, torch_dtype):
    print("✅ Cargando modelo base...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        device_map="auto" if device == "cuda" else None,
    )
    if device == "cpu":
        model.to(device)
    return model


def load_with_lora_if_possible(base_model, lora_dir, device):
    """
    Intenta cargar adaptador LoRA desde lora_dir.
    - Si hay adapter_config.json, se asume que es un LoRA PEFT.
    - Si no, se asume que lora_dir es un modelo HF completo (modelo fusionado).
    """
    if not os.path.isdir(lora_dir):
        print(f"❌ La carpeta '{lora_dir}' NO existe.")
        print("   Revisa en entrenar.py cuál fue el 'output_dir' / carpeta donde se guardó el LoRA o el modelo.")
        sys.exit(1)

    adapter_config_path = os.path.join(lora_dir, "adapter_config.json")

    # Caso 1: LoRA PEFT (adapter_config.json presente)
    if os.path.exists(adapter_config_path):
        if not PEFT_AVAILABLE:
            print("❌ Se ha encontrado un adaptador LoRA (adapter_config.json),")
            print("   pero el paquete 'peft' no está instalado.")
            print("   Instálalo con: pip install peft")
            sys.exit(1)

        print(f"✅ Encontrado adaptador LoRA en: {lora_dir}")
        from peft import PeftModel

        model = PeftModel.from_pretrained(
            base_model,
            lora_dir,
            device_map="auto" if device == "cuda" else None,
        )
        # Opcional: fusionar LoRA para inferencia
        try:
            model = model.merge_and_unload()
            print("✅ LoRA fusionado con el modelo base para inferencia.")
        except Exception:
            print("ℹ️ No se ha fusionado el LoRA (merge_and_unload falló o no está disponible).")
        return model

    # Caso 2: No hay adapter_config.json → intentar cargar lora_dir como modelo completo
    print("⚠️ No se encontró 'adapter_config.json' en la carpeta LoRA.")
    print("   Se intentará cargar la carpeta como un modelo completo (modelo ya fusionado).")
    print("   Si esto falla, revisa que entrenar.py esté llamando a model.save_pretrained(LORA_DIR).")

    try:
        model = AutoModelForCausalLM.from_pretrained(
            lora_dir,
            torch_dtype=base_model.dtype,
            device_map="auto" if device == "cuda" else None,
        )
        if device == "cpu":
            model.to(device)
        print("✅ Modelo cargado directamente desde la carpeta.")
        return model
    except Exception as e:
        print("❌ No se ha podido cargar la carpeta como modelo completo.")
        print(f"   Error: {e}")
        sys.exit(1)


def build_prompt(tokenizer, user_text: str) -> str:
    """
    Construye el texto de entrada siguiendo la plantilla de chat de Qwen, si existe.
    Si no, usa un formato sencillo tipo chat.
    """
    if hasattr(tokenizer, "apply_chat_template"):
        messages = [
            {"role": "system", "content": "Eres un profesor de programación llamado Jose Vicente. Explicas en español de forma clara y didáctica."},
            {"role": "user",   "content": user_text},
        ]
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    else:
        # fallback simple
        return f"Sistema: Eres un profesor de programación llamado Jose Vicente.\nUsuario: {user_text}\nAsistente:"


def generate_answer(tokenizer, model, device: str, prompt: str) -> str:
    model.eval()
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Nos quedamos solo con la parte generada (sin el prompt) para que sea más limpio
    generated_ids = output_ids[0][inputs["input_ids"].shape[-1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return text.strip()


def main():
    print_header()

    device, torch_dtype = detect_device()

    # 1. Tokenizer y modelo base
    tokenizer = load_tokenizer(MODEL_NAME)
    base_model = load_base_model(MODEL_NAME, device, torch_dtype)

    # 2. Cargar LoRA o modelo completo desde LORA_DIR
    model = load_with_lora_if_possible(base_model, LORA_DIR, device)

    # 3. Bucle de prueba interactivo
    print("\n✅ Modelo listo para probar.")
    print("Escribe una pregunta (en español). Ctrl+C o línea vacía para salir.\n")

    try:
        while True:
            user_text = input("💬 Tú: ").strip()
            if not user_text:
                print("👋 Saliendo.")
                break

            prompt = build_prompt(tokenizer, user_text)
            print("\n🤖 Modelo (pensando)...\n")
            answer = generate_answer(tokenizer, model, device, prompt)
            print("🤖 Respuesta:\n")
            print(answer)
            print("\n" + "-" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n👋 Saliendo por Ctrl+C.")


if __name__ == "__main__":
    main()

