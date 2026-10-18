# proxy.py
from agent import ChatAgent
from other_local_models.coder import Qwen_coder
from code_builder import StagedCodeBuilder
import time
import re
import gc
from pathlib import Path

MEMORY = Path("memory.txt")

class ProxyAgentController:
    # Controller class to manage the lifecycle of the main ChatAgent and the secondary Qwen coder.

    def __init__(self, model_path, prompt_file):
        self.model_path = model_path
        self.prompt_file = prompt_file
        self.code_builder = StagedCodeBuilder()

    def initialize_chat_agent(self):
        # Creates and returns the primary conversational agent.
        print("Initializing the proxy agent...")
        agent = ChatAgent(
            model_path=self.model_path,
            prompt_file=self.prompt_file
        )
        print("Agent is ready!")
        return agent

    def initialize_coder_agent(self):
        # Creates and returns the secondary coding agent.
        coder = Qwen_coder()
        print("coder is running!")
        return coder

    def write_memory(self, memory_path, string):
        if memory_path.is_file():
            with open(memory_path, 'a')as f:
                f.write(string)
        else:
            with open(memory_path, 'w')as f:
                f.write(f"{string}\n")

    def run_proxy(self):
        # Main loop handling user input, agent responses, and resource management.
        active_agent = self.initialize_chat_agent()

        while True:
            user_prompt = input("User: ").strip()

            if user_prompt.lower() in ["exit", "quit"]:
                print("Exiting the chat.")
                break

            # Retrieve the response from the active agent
            agent_reply = active_agent.chat(user_prompt)

            # Search the reply for special command markers
            sleep_match = re.search(r"\[SLEEP:(\d+)\]", agent_reply)
            coder_planning_match = re.search(r":-planning-:", agent_reply)
            Memory_match = re.search(r":-PermMemory-:", agent_reply)

            # Handle the SLEEP command
            if sleep_match:
                sleep_duration = int(sleep_match.group(1))
                print(f"\n>>> Model requested sleep for {sleep_duration} seconds. Releasing model...")

                del active_agent
                gc.collect()
                active_agent = None

                print(f">>> Sleeping for {sleep_duration} seconds...")
                time.sleep(sleep_duration)

                active_agent = self.initialize_chat_agent()
                print(">>> Model is back online.\n")

            elif Memory_match:
                clean_reply = agent_reply.replace(":-PermMemory-:", "")
                parts = clean_reply.split("--")
                if len(parts) >= 2:
                    result = parts[1].strip()
                    self.write_memory(MEMORY, result)

            # Handle the CODER command
            elif coder_planning_match:
                # Release the current model
                del active_agent
                gc.collect()
                active_agent = None
                self.prompt_file = CODE_PLANNER_FILE

                active_agent = self.initialize_chat_agent()

                print("system prompt switch to code plan.")
                agent_reply = active_agent.chat(user_prompt)

                agent_reply = ":-start-:" + agent_reply + ":-start-:"

                print("-/"*20)
                print(agent_reply)

                coder_start_match = re.search(r":-start-:", agent_reply)

                if coder_start_match:
                    print(">>> Model requested to run the Qwen_coder. Releasing model...")
                
                    # Free up resources before loading the coder model into memory
                    del active_agent
                    gc.collect()
                    active_agent = None
                
                    print(">>> Running Qwen_coder...")
                    qwen_coder_instance = self.initialize_coder_agent()

                    # Delegate file creation, stage execution, and code appending to StagedCodeBuilder
                    coder_reply, file_path = self.code_builder.execute_stages(agent_reply, qwen_coder_instance)

                    # Clean up coder model before restoring primary model
                    print(">>> Qwen_coder has finished execution.")
                    del qwen_coder_instance
                    gc.collect()
                
                    print(">>> Restoring primary model...\n")
                    active_agent = self.initialize_chat_agent()
                
                    print(">>> Model is back online.\n")
                


# Configuration variables defined at the module level
MODEL_PATH = "models/main/Qwen3-4B-Q4_K_M.gguf"
PROMPT_FILE = "system_prompts/ruby_system_prompt.txt"
CODE_PLANNER_FILE = "system_prompts/ruby_system_prompt_code.txt"

# Initialize and run the proxy controller
proxy_controller = ProxyAgentController(MODEL_PATH, PROMPT_FILE)

if __name__ == "__main__":
    proxy_controller.run_proxy()