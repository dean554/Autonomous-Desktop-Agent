from httpx import stream
from llama_cpp import Llama
# 1. Download the specific Q3_K_M GGUF model file if not already present

model_path = "models/coders/qwen2.5-coder-3b-instruct-q3_k_m.gguf"
prompt = "system_prompts/coder_system_prompt.txt"

with open(prompt, "r", encoding="utf-8") as f:
    coder_system_prompt = f.read()

class Qwen_coder:
    def __init__(self):
        self.model_path = model_path
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_threads=6,
            n_threads_batch=8,
            use_mmap=True,
            use_mlock=False,
            verbose=False
        )

        # Keep multi-turn conversation history across stages
        self.messages = [
            {"role": "system", "content": coder_system_prompt}
        ]


# 4. Generate the response
    def ccode(self, messages):
        print("\n--- Generating Response ---")

        # 1. Add the current stage instructions to the conversation history
        self.messages.append({"role": "user", "content": messages})

        stream = self.llm.create_chat_completion(
            messages=self.messages,
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
        print()

        # Save the model's code in history so the next stage can build on it
        self.messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply

