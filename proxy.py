# proxy.py
from agent import ChatAgent

def run_proxy():
    print("Initializing the proxy agent...")
    
    # Create an instance of the agent
    # You can pass different model paths or prompts here if needed
    proxy_agent = ChatAgent(
        model_path="Qwen3-4B-Q4_K_M.gguf", 
        prompt_file="sys_prompt.txt"
    )
    
    print("Agent is ready!")
    
    # Start the interactive console loop
    proxy_agent.start_console()

if __name__ == "__main__":
    run_proxy()