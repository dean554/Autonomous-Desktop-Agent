import os
from dotenv import load_dotenv
from groq import Groq

# Load the API key from the .env file into the environment
load_dotenv()

# Initialize the client
client = Groq()

# 1. Initialize Memory and Cache
# 3 conversations = 3 user messages + 3 assistant messages = 6 total items
MAX_HISTORY = 6 
conversation_history = []
prompt_cache = {}

system_prompt = {"role": "system", "content": "You are a sarcastic robot. Keep your answers under 20 words."}

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting...")
        break
    
    current_user_message = {"role": "user", "content": user_input}
    
    # Construct the full context: System + History + Current User Input
    messages = [system_prompt] + conversation_history + [current_user_message]
    
    # 2. Create a unique cache key based on the exact conversation context
    # Converting the messages list to a string creates a unique identifier for this exact state
    cache_key = str(messages)
    
    # 3. Check Cache
    if cache_key in prompt_cache:
        ai_response = prompt_cache[cache_key]
        print(f"AI (Cached): {ai_response}")
    else:
        # 4. Call the API if not in cache
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages
        )
        ai_response = response.choices[0].message.content
        print(f"AI: {ai_response}")
        
        # Store the new API response in the cache
        prompt_cache[cache_key] = ai_response

    # 5. Update Memory
    # Append both the user's input and the AI's response to the history
    conversation_history.append(current_user_message)
    conversation_history.append({"role": "assistant", "content": ai_response})
    
    # Trim the history to ensure it only keeps the last 3 conversations (6 messages)
    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]