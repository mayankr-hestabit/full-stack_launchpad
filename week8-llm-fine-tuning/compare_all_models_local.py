import gc
import os
import re
import subprocess
import time
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

PROJECT_ROOT = Path(__file__).resolve().parent
ADAPTER_PATH = PROJECT_ROOT / "adapters"
INT8_PATH = PROJECT_ROOT / "quantized" / "model-int8"
INT4_PATH = PROJECT_ROOT / "quantized" / "model-int4"
GGUF_PATH = PROJECT_ROOT / "quantized" / "model.gguf"

PROMPT = "Explain Docker containers in simple terms."
MAX_NEW_TOKENS = 64


def folder_size_gb(path: Path) -> float:
    total = 0
    for root, _, files in os.walk(path):
        for filename in files:
            file_path = Path(root) / filename
            if file_path.is_file():
                total += file_path.stat().st_size
    return total / (1024 ** 3)


def model_weight_size_gb(model) -> float:
    total_bytes = 0
    for parameter in model.parameters():
        total_bytes += parameter.numel() * parameter.element_size()
    return total_bytes / (1024 ** 3)


def quality_check(response: str) -> str:
    text = response.lower()
    if "docker" in text and "container" in text and len(response.strip()) >= 40:
        return "Pass"
    return "Review"


def clear_gpu():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def format_prompt(tokenizer):
    messages = [{"role": "user", "content": PROMPT}]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )


def generate_transformers(model, tokenizer):
    formatted_prompt = format_prompt(tokenizer)
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        _ = model.generate(
            **inputs,
            max_new_tokens=4,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    torch.cuda.synchronize()
    start = time.perf_counter()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    token_count = len(generated_tokens)
    tps = token_count / elapsed if elapsed > 0 else 0.0

    return response, elapsed, tps


def find_llama_cli():
    candidates = [
        PROJECT_ROOT / "llama.cpp" / "build" / "bin" / "llama-cli",
        PROJECT_ROOT.parent / "llama.cpp" / "build" / "bin" / "llama-cli",
        Path.home() / "llama.cpp" / "build" / "bin" / "llama-cli",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    result = subprocess.run(["which", "llama-cli"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())

    return None


def test_fp16(results, responses):
    print("\n" + "=" * 75)
    print("TESTING FP16 FINE-TUNED MODEL")
    print("=" * 75)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=torch.float16,
        device_map="auto"
    )

    model = PeftModel.from_pretrained(base_model, str(ADAPTER_PATH))
    model.eval()

    size_gb = model_weight_size_gb(model)
    response, latency, tps = generate_transformers(model, tokenizer)
    quality = quality_check(response)

    results.append({
        "Format": "FP16",
        "Size_GB": size_gb,
        "Tokens_per_sec": tps,
        "Latency_sec": latency,
        "Quality": quality
    })
    responses["FP16"] = response

    print(f"Approx. weight size : {size_gb:.3f} GB")
    print(f"Speed               : {tps:.3f} tokens/sec")
    print(f"Latency             : {latency:.3f} sec")
    print(f"Quality             : {quality}")
    print("\nResponse:")
    print(response)

    del model, base_model, tokenizer
    clear_gpu()


def test_saved_quantized_model(model_path, name, results, responses):
    print("\n" + "=" * 75)
    print(f"TESTING {name}")
    print("=" * 75)

    if not model_path.exists():
        raise FileNotFoundError(f"{name} folder not found: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(
        str(model_path),
        local_files_only=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        device_map="auto",
        low_cpu_mem_usage=True,
        local_files_only=True
    )

    model.eval()

    size_gb = folder_size_gb(model_path)
    response, latency, tps = generate_transformers(model, tokenizer)
    quality = quality_check(response)

    results.append({
        "Format": name,
        "Size_GB": size_gb,
        "Tokens_per_sec": tps,
        "Latency_sec": latency,
        "Quality": quality
    })
    responses[name] = response

    print(f"Folder size : {size_gb:.3f} GB")
    print(f"Speed       : {tps:.3f} tokens/sec")
    print(f"Latency     : {latency:.3f} sec")
    print(f"Quality     : {quality}")
    print("\nResponse:")
    print(response)

    del model, tokenizer
    clear_gpu()


def test_gguf(results, responses):
    print("\n" + "=" * 75)
    print("TESTING GGUF Q4_0")
    print("=" * 75)

    if not GGUF_PATH.exists():
        raise FileNotFoundError(f"GGUF model not found: {GGUF_PATH}")

    llama_cli = find_llama_cli()
    if llama_cli is None:
        raise FileNotFoundError(
            "llama-cli was not found. Build llama.cpp first and make sure "
            "llama-cli exists at ./llama.cpp/build/bin/llama-cli, "
            "~/llama.cpp/build/bin/llama-cli, or is available in PATH."
        )

    size_gb = GGUF_PATH.stat().st_size / (1024 ** 3)

    command = [
        str(llama_cli),
        "-m", str(GGUF_PATH),
        "-p", PROMPT,
        "-n", str(MAX_NEW_TOKENS),
        "--temp", "0",
        "--ctx-size", "512",
        "-ngl", "0"
    ]

    start = time.perf_counter()
    run = subprocess.run(command, capture_output=True, text=True)
    latency = time.perf_counter() - start

    if run.returncode != 0:
        raise RuntimeError("llama.cpp failed:\n\n" + run.stderr)

    response = run.stdout.strip()
    performance_log = run.stderr

    matches = re.findall(
        r"([0-9]+(?:\.[0-9]+)?)\s+tokens per second",
        performance_log
    )

    if matches:
        tps = float(matches[-1])
    else:
        tps = MAX_NEW_TOKENS / latency if latency > 0 else 0.0

    quality = quality_check(response)

    results.append({
        "Format": "GGUF Q4_0",
        "Size_GB": size_gb,
        "Tokens_per_sec": tps,
        "Latency_sec": latency,
        "Quality": quality
    })
    responses["GGUF Q4_0"] = response

    print(f"File size : {size_gb:.3f} GB")
    print(f"Speed     : {tps:.3f} tokens/sec")
    print(f"Latency   : {latency:.3f} sec")
    print(f"Quality   : {quality}")
    print("\nResponse:")
    print(response)


def main():
    print("=" * 75)
    print("WEEK 8 - DAY 3: FP16 vs INT8 vs INT4 vs GGUF")
    print("=" * 75)

    print("\nCUDA available:", torch.cuda.is_available())

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is not available. PyTorch must be able to access the NVIDIA GPU."
        )

    print("GPU:", torch.cuda.get_device_name(0))
    print("Prompt:", PROMPT)

    required_paths = [
        ADAPTER_PATH / "adapter_model.safetensors",
        ADAPTER_PATH / "adapter_config.json",
        INT8_PATH,
        INT4_PATH,
        GGUF_PATH
    ]

    for p in required_paths:
        if not p.exists():
            raise FileNotFoundError(f"Required file/folder missing: {p}")

    results = []
    responses = {}

    test_fp16(results, responses)
    test_saved_quantized_model(INT8_PATH, "INT8", results, responses)
    test_saved_quantized_model(INT4_PATH, "INT4", results, responses)
    test_gguf(results, responses)

    comparison = pd.DataFrame(results)
    comparison["Size_GB"] = comparison["Size_GB"].round(3)
    comparison["Tokens_per_sec"] = comparison["Tokens_per_sec"].round(3)
    comparison["Latency_sec"] = comparison["Latency_sec"].round(3)

    print("\n\n" + "=" * 75)
    print("FINAL QUANTISATION COMPARISON")
    print("=" * 75)
    print(comparison.to_string(index=False))

    print("\n" + "=" * 75)
    print("RESPONSES USED FOR QUALITY COMPARISON")
    print("=" * 75)

    for model_name, response in responses.items():
        print("\n" + "-" * 75)
        print(model_name)
        print("-" * 75)
        print(response)

    print(
        "\nNOTE: 'Pass' is only a basic sanity check. "
        "Use the displayed responses for the final qualitative judgement "
        "in QUANTISATION-REPORT.md."
    )


if __name__ == "__main__":
    main()
