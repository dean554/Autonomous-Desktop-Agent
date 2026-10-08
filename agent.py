from llama_cpp import Llama  # type: ignore

class ChatAgent:
    def __init__(self, model_path="Qwen3-4B-Q4_K_M.gguf", prompt_file='sys_prompt.txt', max_history=3):
        """Initializes the LLM, loads the system prompt, and sets up memory."""
        self.max_history = max_history
        self.history = []
        
        # Initialize the model
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=6,
            n_threads_batch=8,
            use_mmap=True,   # weights are paged in from disk
            use_mlock=False, # do NOT pin into RAM on an 8 GB machine
            verbose=False,
        )
        
        # Load the system prompt
        with open(prompt_file, 'r') as f:
            self.system_prompt = f.read()

    def _build_prompt(self, user_prompt):
        """Constructs the full prompt using the system prompt, history, and current input."""
        full_prompt = f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
        
        # Add the last ≤3 conversation turns
        for past_user, past_assistant in self.history:
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
        
        return full_prompt

    def _update_history(self, user_prompt, assistant_reply):
        """Updates rolling memory, keeping only the latest turns."""
        self.history.append((user_prompt, assistant_reply))
        if len(self.history) > self.max_history:
            self.history.pop(0) # drop the oldest turn

    def chat(self, user_prompt):
        """Generates and streams the response for a given prompt."""
        full_prompt = self._build_prompt(user_prompt)
        
        # Generate response
        stream = self.llm(
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
        
        self._update_history(user_prompt, assistant_reply)
        return assistant_reply

    def start_console(self):
        """Runs the interactive terminal chat loop."""
        while True:
            user_prompt = input("User: ")
            if user_prompt.lower() in ["exit", "quit"]:
                print("Exiting the chat.")
                break
            
            self.chat(user_prompt)

