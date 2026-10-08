from llama_cpp import Llama  # type: ignore

# Initialize the model
llm = Llama(
    model_path="Qwen3-4B-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=6,
    n_threads_batch=8,
)

system_prompt = "You are a helpful and friendly assistant named 'Ruby'."

# Rolling memory: list of (user, assistant) pairs – keep only the last 3
history = []          # max length 3
MAX_HISTORY = 3

while True:
    user_prompt = input("User: ")
    if user_prompt.lower() in ["exit", "quit"]:
        print("Exiting the chat. Farewell, matey!")
        break

    # Build the full prompt
    full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"

    # Add the last ≤3 conversation turns
    for past_user, past_assistant in history:
        full_prompt += (
            f"<|im_start|>user\n{past_user}<|im_end|>\n"
            f"<|im_start|>assistant\n{past_assistant}<|im_end|>\n"
        )

    # Add the current user message
    full_prompt += (
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
        f"<think>\n\n</think>\n\n"
    )

    # Generate response
    output = llm(
        full_prompt,
        max_tokens=150,
        stop=["<|im_end|>", "<|im_start|>"],
        temperature=0.7,
    )

    assistant_reply = output["choices"][0]["text"].strip()
    print(assistant_reply)

    # Update memory (keep only the latest 3 turns)
    history.append((user_prompt, assistant_reply))
    if len(history) > MAX_HISTORY:
        history.pop(0)   # drop the oldest turn