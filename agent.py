from llama_cpp import Llama  # type: ignore

# Initialize the model
llm = Llama(
    model_path="Qwen3-4B-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=6,
    n_threads_batch=8,
    use_mmap=True,  # weights are paged in from disk; OS can drop them under pressure
    use_mlock=False, # do NOT pin into RAM on an 8 GB machine
    verbose=False,
)

with open('sys_prompt.txt', 'r')as f:
    system_prompt = f.read()

# Rolling memory: list of (user, assistant) pairs – keep only the last 3
history = []   # max length 3
MAX_HISTORY = 3

while True:
    user_prompt = input("User: ")
    if user_prompt.lower() in ["exit", "quit"]:
        print("Exiting the chat.")
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
    stream = llm(
        full_prompt,
        max_tokens=200,
        stop=["<|im_end|>", "<|im_start|>"],
        temperature=0.7,
        stream=True,
    )

    assistant_reply = ""

    for chunk in stream:
        token = chunk["choices"][0]["text"]
        print(token, end="", flush=True)
        assistant_reply += token
    print()  # for newline after the assistant's reply

    # Update memory (keep only the latest 3 turns)
    history.append((user_prompt, assistant_reply))
    if len(history) > MAX_HISTORY:
        history.pop(0)   # drop the oldest turn