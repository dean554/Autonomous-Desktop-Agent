from httpx import stream
from llama_cpp import Llama
# 1. Download the specific Q3_K_M GGUF model file if not already present

model_path = "coders/qwen2.5-coder-3b-instruct-q3_k_m.gguf"

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
            {"role": "system", "content": """You are an expert developer. Write clean, functional code to fulfill the user's request. 
            Provide ONLY the code. Do not include any conversational filler, greetings, or explanations before or after the code. 
            Once you have generated the complete code, you must append the exact string :-done-: on a new line at the very end of your response."""},
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

