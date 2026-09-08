import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from peft import PeftModel


BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER_PATH = "adapters"


# -----------------------------------------
# 1. LOAD TOKENIZER
# -----------------------------------------

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# -----------------------------------------
# 2. LOAD BASE MODEL IN 4-BIT
# -----------------------------------------

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
)


# -----------------------------------------
# 3. ATTACH YOUR TRAINED LORA ADAPTER
# -----------------------------------------

model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH
)

model.eval()

print("Fine-tuned model loaded successfully.")


# -----------------------------------------
# 4. CREATE TEST PROMPT
# -----------------------------------------

prompt = "Explain Docker containers in simple terms."

messages = [
    {
        "role": "user",
        "content": prompt
    }
]


# -----------------------------------------
# 5. CONVERT PROMPT TO QWEN CHAT FORMAT
# -----------------------------------------

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)


# -----------------------------------------
# 6. TOKENIZE PROMPT
# -----------------------------------------

inputs = tokenizer(
    text,
    return_tensors="pt"
).to(model.device)


# -----------------------------------------
# 7. GENERATE RESPONSE
# -----------------------------------------

with torch.no_grad():

    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        do_sample=False
    )


# -----------------------------------------
# 8. DECODE ONLY GENERATED TOKENS
# -----------------------------------------

generated_tokens = outputs[0][
    inputs["input_ids"].shape[1]:
]

response = tokenizer.decode(
    generated_tokens,
    skip_special_tokens=True
)


# -----------------------------------------
# 9. PRINT RESULT
# -----------------------------------------

print("\nPrompt:")
print(prompt)

print("\nFine-tuned model response:")
print(response)