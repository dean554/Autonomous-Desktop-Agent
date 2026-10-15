# proxy.py
from agent import ChatAgent
from other_local_models.coder import Qwen_coder
import time
import re
import gc
import json

class ProxyAgentController:
    #Controller class to manage the lifecycle of the main ChatAgent and the secondary Qwen coder.
    
    def __init__(self, model_path, prompt_file):
        self.model_path = model_path
        self.prompt_file = prompt_file

    def initialize_chat_agent(self):
        #Creates and returns the primary conversational agent.
        print("Initializing the proxy agent...")
        agent = ChatAgent(
            model_path=self.model_path,
            prompt_file=self.prompt_file
        )
        print("Agent is ready!")
        return agent
    
    def initialize_coder_agent(self):
        #Creates and returns the secondary coding agent.
        coder = Qwen_coder()
        print("coder is running!")
        return coder
        
    def run_proxy(self):
        #Main loop handling user input, agent responses, and resource management.
        # Start the primary conversational agent
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
            coder_start_match = re.search(r":-start-:", agent_reply)

            # Handle the SLEEP command
            if sleep_match:
                sleep_duration = int(sleep_match.group(1))
                print(f"\n>>> Model requested sleep for {sleep_duration} seconds. Releasing model...")

                # Free up system memory (RAM/CPU) by completely destroying the agent
                del active_agent
                gc.collect()  # Force garbage collection to reclaim memory immediately
                active_agent = None

                print(f">>> Sleeping for {sleep_duration} seconds...")
                time.sleep(sleep_duration)

                # Reinitialize a fresh agent after the sleep period completes
                active_agent = self.initialize_chat_agent()
                print(">>> Model is back online.\n")

            # Handle the CODER command
            elif coder_start_match:
                print(">>> Model requested to run the Qwen_coder. Releasing model...")
                
                # Free up resources before loading the heavy coder model into memory
                del active_agent
                gc.collect() 
                active_agent = None

                print(">>> Running Qwen_coder...")
                qwen_coder_instance = self.initialize_coder_agent()

                # 1. Extract the JSON between the markers
                start_marker = ":-start-:"
                start = agent_reply.index(start_marker) + len(start_marker)
                end = agent_reply.index(start_marker, start)
                json_string = agent_reply[start:end].strip()

                # 2. Convert JSON string into a Python dictionary
                stages = json.loads(json_string)

                # Keep track of code written in previous stages so the coder can integrate it
                accumulated_code = ""

                for stage_name, stage_data in stages.items():
                    # Print stage details BEFORE generating the response
                    print("\n" + "-" * 50)
                    print(f"Executing: {stage_name}")
                    print("-" * 50)
                    print(stage_data)
                    print("-" * 50)

                    # Send clean instructions without markdown headers that trigger repetition
                    if stage_data.get("dependencies"):
                        stage_prompt = (
                            f"Now execute {stage_name}: {stage_data['plan']}\n"
                            f"Instructions: {stage_data['prompt']}\n\n"
                            f"CRITICAL RULES:\n"
                            f"1. Keep ALL imports, helper methods, and validation checks you wrote in the previous stage. Do NOT delete or omit any existing methods.\n"
                            f"2. Integrate the new methods and logic into the existing class/script and output the complete, unified Python code inside a single ```python code block."
                        )
                    else:
                        stage_prompt = (
                            f"Execute {stage_name}: {stage_data['plan']}\n"
                            f"Instructions: {stage_data['prompt']}\n"
                            f"Write ONLY the Python code required for this stage inside a single ```python code block."
                        )

                    coder_reply = qwen_coder_instance.ccode(stage_prompt)
                
                # Clean up coder model before restoring primary model
                print("\n>>> Qwen_coder has finished execution.")
                del qwen_coder_instance
                gc.collect()

                print(">>> Restoring primary model...\n")
                active_agent = self.initialize_chat_agent()
                print(">>> Model is back online.\n")

                # Check if the coder output contains the completion marker
                coder_done_match = re.search(r":-done-:", coder_reply)

                if coder_done_match:
                    print(">>> Qwen_coder has finished execution.")
                    print(">>> Restoring primary model...\n")
                    
                    # Reinitialize the main chat agent once coding is complete
                    active_agent = self.initialize_chat_agent()
                    print(">>> Model is back online.\n")

# Configuration variables defined at the module level
MODEL_PATH = "Qwen3-4B-Q4_K_M.gguf"
PROMPT_FILE = "ruby_system_prompt.txt"

# Initialize and run the proxy controller
proxy_controller = ProxyAgentController(MODEL_PATH, PROMPT_FILE)

if __name__ == "__main__":
    proxy_controller.run_proxy()