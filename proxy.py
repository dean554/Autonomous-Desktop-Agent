# proxy.py
from agent import ChatAgent
from other_local_models.coder import Qwen_coder
import time
import re
import gc

class handle_Ruby:
    def __init__(self, model_path, prompt_file):
        self.model_path = model_path
        self.prompt_file = prompt_file

    def create_agent(self):
        print("Initializing the proxy agent...")
        agent = ChatAgent(
            #model_path="Qwen3-4B-Q4_K_M.gguf",
            #prompt_file="sys_prompt.txt"
            model_path=self.model_path,
            prompt_file=self.prompt_file
        )
        print("Agent is ready!")
        return agent
    
    def coder_agent(self):
        coder = Qwen_coder()

        print("coder is running!")
        return coder
        
    def run_proxy(self):
        agent = self.create_agent()

        while True:
            user_prompt = input("User: ").strip()

            if user_prompt.lower() in ["exit", "quit"]:
                print("Exiting the chat.")
                break

            # Let the model reply
            reply = agent.chat(user_prompt)

            # Check if the model asked to sleep
            sleep_match = re.search(r"\[SLEEP:(\d+)\]", reply)

            command = re.search(r":-start-:", reply)

            if sleep_match:
                seconds = int(sleep_match.group(1))
                print(f"\n>>> Model requested sleep for {seconds} seconds. Releasing model...")

                # Completely destroy the agent (releases the LLM from RAM/CPU)
                del agent
                gc.collect()# force garbage collection
                agent = None

                print(f">>> Sleeping for {seconds} seconds...")
                time.sleep(seconds)

                # Restart a brand-new agent
                agent = self.create_agent()
                print(">>> Model is back online.\n")

            elif command:
                print(">>> Model requested to run the Qwen_coder. Releasing model...")
                del agent
                gc.collect()# force garbage collection
                agent = None

                print(">>> Running Qwen_coder...")
                coder_agent = self.coder_agent()
                coder_agent.prompt("make a simple calculator in python")

                coder_reply = coder_agent.ccode()
                c = re.search(r":-done-:", coder_reply)

                if c:
                    print(">>> Qwen_coder has finished execution.")
                    print(">>> Model is back online.\n")
                    agent = self.create_agent()
                    print(">>> Model is back online.\n")



model_path="Qwen3-4B-Q4_K_M.gguf"
prompt_file="sys_prompt.txt"

C_Ruby = handle_Ruby(model_path, prompt_file)

if __name__ == "__main__":
    C_Ruby.run_proxy()