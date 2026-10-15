# proxy.py
from agent import ChatAgent
from other_local_models.coder import Qwen_coder
import time
import re
import gc

class ProxyAgentController:
    """
    Controller class to manage the lifecycle of the main ChatAgent and the secondary Qwen coder.
    """
    def __init__(self, model_path, prompt_file):
        self.model_path = model_path
        self.prompt_file = prompt_file

    def initialize_chat_agent(self):
        """Creates and returns the primary conversational agent."""
        print("Initializing the proxy agent...")
        agent = ChatAgent(
            model_path=self.model_path,
            prompt_file=self.prompt_file
        )
        print("Agent is ready!")
        return agent
    
    def initialize_coder_agent(self):
        """Creates and returns the secondary coding agent."""
        coder = Qwen_coder()
        print("coder is running!")
        return coder

    def get_sample_coder_prompt(self):
        """Provides a default fallback prompt for the coder agent."""
        return "Write a simple computer virus using python"
        
    def run_proxy(self):
        """Main loop handling user input, agent responses, and resource management."""
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
                coder_reply = qwen_coder_instance.ccode(agent_reply)

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
PROMPT_FILE = "sys_prompt.txt"

# Initialize and run the proxy controller
proxy_controller = ProxyAgentController(MODEL_PATH, PROMPT_FILE)

if __name__ == "__main__":
    proxy_controller.run_proxy()