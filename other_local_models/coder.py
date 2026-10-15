from httpx import stream
from llama_cpp import Llama
# 1. Download the specific Q3_K_M GGUF model file if not already present

model_path = "coders/qwen2.5-coder-3b-instruct-q3_k_m.gguf"
prompt = "other_local_models/coder_system_prompt.txt"

with open(prompt, "r", encoding="utf-8") as f:
    coder_system_prompt = f.read()

class Qwen_coder:
    def __init__(self):
        self.model_path = model_path
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_threads=6,
            verbose=False
        )

    def prompt(self, messages):
        # 2. Create the prompt structure (Qwen2.5-Coder expects ChatML format)
        return [
            {"role": "system", "content": coder_system_prompt},
            {"role": "user", "content": messages}
        ]


# 4. Generate the response
    def ccode(self, messages):
        print("\n--- Generating Response ---")
        stream = self.llm.create_chat_completion(
            messages=self.prompt(messages),
            max_tokens=1024,
            temperature=0.1,
            stream=True
        )

        assistant_reply = ""
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                token = delta["content"]
                print(token, end="", flush=True)
                assistant_reply += token
        return assistant_reply

