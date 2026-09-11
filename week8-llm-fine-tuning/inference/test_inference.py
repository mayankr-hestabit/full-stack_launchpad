import gc
import os
import re
import subprocess
import threading
import time
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = PROJECT_ROOT / "adapters"
GGUF_PATH = PROJECT_ROOT / "quantized" / "model.gguf"
RESULTS_PATH = PROJECT_ROOT / "benchmarks" / "results.csv"
MAX_NEW_TOKENS = 80

TEST_CASES = [
    {"prompt": "Explain Docker containers in simple terms.", "required_groups": [["docker"], ["container"], ["image"]]},
    {"prompt": "What is GitHub?", "required_groups": [["git", "code"], ["platform", "service", "website"]]},
    {"prompt": "What is an API?", "required_groups": [["application", "api"], ["interface"], ["communicate", "interaction", "interact"]]},
    {"prompt": "What does HTTP stand for?", "required_groups": [["hypertext"], ["transfer"], ["protocol"]]},
    {"prompt": "What is a Python list?", "required_groups": [["python"], ["list", "collection"], ["ordered", "sequence", "items"]]},
]

def clear_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

def reset_peak_vram():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

def peak_vram_gb():
    return torch.cuda.max_memory_allocated() / (1024 ** 3) if torch.cuda.is_available() else 0.0

def format_prompt(tokenizer, prompt):
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
    )

def accuracy_check(response, groups):
    text = response.lower()
    return int(all(any(term.lower() in text for term in group) for group in groups))

def find_llama_cli():
    for candidate in [
        Path.home() / "llama.cpp" / "build" / "bin" / "llama-cli",
        PROJECT_ROOT / "llama.cpp" / "build" / "bin" / "llama-cli",
    ]:
        if candidate.exists():
            return candidate
    result = subprocess.run(["which", "llama-cli"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())
    raise FileNotFoundError("llama-cli not found.")

def generate_transformers(model, tokenizer, prompt):
    formatted = format_prompt(tokenizer, prompt)
    inputs = tokenizer(formatted, return_tensors="pt").to("cuda")
    reset_peak_vram()
    start = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    torch.cuda.synchronize()
    latency = time.perf_counter() - start
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated, skip_special_tokens=True)
    tps = len(generated) / latency if latency > 0 else 0.0
    vram = peak_vram_gb()
    del inputs, outputs, generated
    return response, latency, tps, vram

def benchmark_transformers(model, tokenizer, name):
    print("\n" + "=" * 75)
    print(f"BENCHMARKING {name}")
    print("=" * 75)
    rows = []
    for i, case in enumerate(TEST_CASES, 1):
        response, latency, tps, vram = generate_transformers(model, tokenizer, case["prompt"])
        correct = accuracy_check(response, case["required_groups"])
        rows.append({
            "model": name,
            "prompt_id": i,
            "latency_sec": latency,
            "tokens_per_sec": tps,
            "vram_gb": vram,
            "correct": correct,
            "response": response,
        })
        print(f"\nPrompt {i}: {case['prompt']}")
        print("Response:", response)
        print(f"Latency: {latency:.3f} sec")
        print(f"Speed: {tps:.3f} tokens/sec")
        print(f"Peak VRAM: {vram:.3f} GB")
        print("Correct:", "Yes" if correct else "No")
    return rows

def streaming_demo(model, tokenizer, name):
    print("\n" + "=" * 75)
    print(f"STREAMING DEMO - {name}")
    print("=" * 75)
    formatted = format_prompt(tokenizer, TEST_CASES[0]["prompt"])
    inputs = tokenizer(formatted, return_tensors="pt").to("cuda")
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    kwargs = dict(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
        streamer=streamer,
        use_cache=True,
    )
    thread = threading.Thread(target=model.generate, kwargs=kwargs)
    print("\nStreaming response:\n")
    thread.start()
    for piece in streamer:
        print(piece, end="", flush=True)
    thread.join()
    print("\n")
    del inputs
    clear_memory()

def batch_demo(model, tokenizer, name):
    print("\n" + "=" * 75)
    print(f"BATCH INFERENCE - {name}")
    print("=" * 75)
    prompts = [case["prompt"] for case in TEST_CASES[:3]]
    formatted = [format_prompt(tokenizer, p) for p in prompts]
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    batch = tokenizer(formatted, padding=True, return_tensors="pt").to("cuda")
    reset_peak_vram()
    start = time.perf_counter()
    with torch.no_grad():
        outputs = model.generate(
            **batch,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    print(f"Batch size: {len(prompts)}")
    print(f"Batch latency: {elapsed:.3f} sec")
    print(f"Peak VRAM: {peak_vram_gb():.3f} GB")
    input_length = batch["input_ids"].shape[1]
    for i, output in enumerate(outputs):
        response = tokenizer.decode(output[input_length:], skip_special_tokens=True)
        print(f"\nPrompt {i + 1}: {prompts[i]}")
        print("Response:", response)
    del batch, outputs
    clear_memory()

def load_base_model_gpu():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=torch.float16,
        low_cpu_mem_usage=True,
    ).to("cuda")
    model.eval()
    return model, tokenizer

def load_fine_tuned_model_gpu():
    print("\nLoading base model on CPU for LoRA merge...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=torch.float16,
        device_map={"": "cpu"},
        low_cpu_mem_usage=True,
    )
    print("Attaching LoRA adapter...")
    peft_model = PeftModel.from_pretrained(base_model, str(ADAPTER_PATH))
    print("Merging LoRA adapter into base weights...")
    model = peft_model.merge_and_unload()
    del peft_model, base_model
    gc.collect()
    print("Moving merged fine-tuned FP16 model to GPU...")
    model = model.to("cuda")
    model.eval()
    return model, tokenizer

def run_gguf_prompt(llama_cli, prompt):
    command = [
        str(llama_cli), "-m", str(GGUF_PATH), "-p", prompt,
        "-n", str(MAX_NEW_TOKENS), "--temp", "0",
        "--ctx-size", "512", "-ngl", "0", "--no-display-prompt",
    ]
    start = time.perf_counter()
    run = subprocess.run(command, capture_output=True, text=True)
    latency = time.perf_counter() - start
    if run.returncode != 0:
        raise RuntimeError(run.stderr)
    matches = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s+tokens per second", run.stderr)
    return run.stdout.strip(), latency, float(matches[-1]) if matches else 0.0

def benchmark_gguf():
    print("\n" + "=" * 75)
    print("BENCHMARKING GGUF Q4_0")
    print("=" * 75)
    llama_cli = find_llama_cli()
    rows = []
    for i, case in enumerate(TEST_CASES, 1):
        response, latency, tps = run_gguf_prompt(llama_cli, case["prompt"])
        correct = accuracy_check(response, case["required_groups"])
        rows.append({
            "model": "GGUF Q4_0",
            "prompt_id": i,
            "latency_sec": latency,
            "tokens_per_sec": tps,
            "vram_gb": 0.0,
            "correct": correct,
            "response": response,
        })
        print(f"\nPrompt {i}: {case['prompt']}")
        print("Response:", response)
        print(f"Latency: {latency:.3f} sec")
        print(f"Speed: {tps:.3f} tokens/sec")
        print("VRAM: 0.000 GB (CPU llama.cpp)")
        print("Correct:", "Yes" if correct else "No")
    return rows

def main():
    print("=" * 75)
    print("WEEK 8 - DAY 4 INFERENCE BENCHMARK")
    print("=" * 75)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available.")
    print("GPU:", torch.cuda.get_device_name(0))
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []

    print("\nLoading base Qwen FP16...")
    base_model, tokenizer = load_base_model_gpu()
    all_rows.extend(benchmark_transformers(base_model, tokenizer, "Base Qwen FP16"))
    streaming_demo(base_model, tokenizer, "Base Qwen FP16")
    batch_demo(base_model, tokenizer, "Base Qwen FP16")
    del base_model, tokenizer
    clear_memory()
    print(f"\nGPU memory after clearing base model: {torch.cuda.memory_allocated() / (1024 ** 3):.3f} GB")

    fine_tuned_model, tokenizer = load_fine_tuned_model_gpu()
    all_rows.extend(benchmark_transformers(fine_tuned_model, tokenizer, "Fine-tuned Qwen FP16"))
    streaming_demo(fine_tuned_model, tokenizer, "Fine-tuned Qwen FP16")
    batch_demo(fine_tuned_model, tokenizer, "Fine-tuned Qwen FP16")
    del fine_tuned_model, tokenizer
    clear_memory()

    all_rows.extend(benchmark_gguf())

    df = pd.DataFrame(all_rows)
    df.to_csv(RESULTS_PATH, index=False)

    summary = (
        df.groupby("model")
        .agg(
            avg_latency_sec=("latency_sec", "mean"),
            avg_tokens_per_sec=("tokens_per_sec", "mean"),
            peak_vram_gb=("vram_gb", "max"),
            accuracy=("correct", "mean"),
        )
        .reset_index()
    )
    summary["accuracy"] *= 100

    print("\n" + "=" * 75)
    print("FINAL BENCHMARK SUMMARY")
    print("=" * 75)
    print(summary.to_string(index=False))
    print(f"\nSaved results to: {RESULTS_PATH}")

if __name__ == "__main__":
    main()
