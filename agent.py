from llama_cpp import Llama #type: ignore

# Initialize the model
llm = Llama(
    model_path="Qwen3-4B-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=4
)

# Define your system instructions and user prompt
system_prompt = "You are a helpful assistant that speaks like a 1920s pirate."

while True:
    user_prompt = input("User: ")
    if user_prompt.lower() in ["exit", "quit"]:
        print("Exiting the chat. Farewell, matey!")
        break

    # Format the input using Qwen's chat template
    full_prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
        f"<think>\n\n</think>\n\n"
    )

    # Generate response
    output = llm(
        full_prompt, 
        max_tokens=150,
        stop=["<|im_end|>", "<|im_start|>"], # Prevent the model from hallucinating a response to itself
        temperature=0.7
    )

    # Print the model's text response
    print(output["choices"][0]["text"])
