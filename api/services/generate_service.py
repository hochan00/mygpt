import torch

from api.core.llm import tokenizer, polyglot_model


async def generate_text(prompt: str, max_length: int = 128, temperature: float = 0.8, top_k: int = 50) -> str:
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    with torch.no_grad():
        output_ids = polyglot_model.generate(
            input_ids,
            max_length=input_ids.shape[1] + max_length,
            temperature=temperature,
            top_k=top_k,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    return tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
