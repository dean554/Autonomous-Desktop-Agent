# Autonomous-Desktop-Agent

A lightweight, fully local AI assistant designed to run on low-end PCs. It uses small quantized models through [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python), loads only **one model at a time**, and frees it from memory whenever another model is needed. No GPU, no cloud, no API keys.

The main assistant, **Ruby**, chats with you, keeps a small permanent memory, and can hand coding work off to a second, code-focused model.

## Features

- **Runs locally on modest hardware**: 4-bit / 3-bit GGUF models, memory-mapped weights (`use_mmap`), no RAM pinning (`use_mlock=False`), and a 4096-token context window.
- **One model in RAM at a time**: the controller unloads the active model before loading the next one (chat -> planner -> coder -> checker -> chat).
- **Permanent memory**: facts Ruby saves are written to `memory/memory.txt` and injected into the system prompt the next time a model is loaded.
- **Rolling conversation history**: only the last 3 turns are kept in the prompt to save context.
- **Streaming responses with interrupt**: output streams token by token and can be stopped by the user.
- **Automatic code pipeline**: Ruby plans the code, a dedicated coder model writes it, the file is saved to a sandbox folder, and Ruby reviews it.
- **Self-managed sleep**: the model can ask to be unloaded for a number of seconds and then be reloaded.

## Models

| Role | Model | Quantization |
|------|-------|--------------|
| Chat / planning / code check ("Ruby") | Qwen3-4B | Q4_K_M |
| Code generation | Qwen2.5-Coder-3B-Instruct | Q3_K_M |

Model files are not included in the repository. Download the GGUF files and place them at:

```
models/main/Qwen3-4B-Q4_K_M.gguf
models/coders/qwen2.5-coder-3b-instruct-q3_k_m.gguf
```

## Repository Structure

```
Autonomous-Desktop-Agent/
├── proxy.py                 # Main entry point: controller, command handling, model lifecycle
├── agent.py                 # ChatAgent: loads the LLM, builds prompts, streams replies
├── code_builder.py          # StagedCodeBuilder: writes generated code into sandbox/
├── other_local_models/
│   └── coder.py             # Qwen_coder: the code-generation model
├── system_prompts/          # Prompts for chat, code planning, coding and code checking
├── memory/
│   └── memory.txt           # Permanent memory (created automatically)
├── sandbox/                 # Generated code files (created automatically)
└── README.md
```

## Installation

```bash
git clone https://github.com/dean554/Autonomous-Desktop-Agent.git
cd Autonomous-Desktop-Agent
pip install llama-cpp-python
```

Then add the model files as described above. The `system_prompts/` folder must contain the prompt files used by the code:

- `ruby_system_prompt.txt`: Ruby's main persona and command rules
- `ruby_system_prompt_code.txt`: the code-planning prompt
- `coder_system_prompt.txt`: the coder model's system prompt
- `code_check.txt`: the code-review prompt

## Usage

```bash
python proxy.py
```

Type messages at the `User:` prompt.

| Input | Effect |
|-------|--------|
| `exit` / `quit` | Close the program |
| `free` / `im off` | Free mode: the model runs on its own prompt; press **Enter** to interrupt it |

## How It Works

`proxy.py` runs a loop that sends your message to the active agent and then scans Ruby's reply for special command markers:

| Marker in reply | Action |
|-----------------|--------|
| `[SLEEP:<seconds>]` | Unloads the model, waits for the given time, then reloads it |
| `:-PermMemory-:` | Extracts the text after `--` and appends it to `memory/memory.txt` |
| `:-planning-:` | Starts the code pipeline (below) |

### Code pipeline

1. The chat model is unloaded and reloaded with the **code-planning prompt**, which produces a plan.
2. The planner model is unloaded and the **Qwen2.5-Coder** model is loaded to write the code.
3. The file name is read from the first `[...]` in the plan, and `StagedCodeBuilder` saves the code to `sandbox/<file name>`.
4. The coder is unloaded and the chat model is loaded with the **code-check prompt** to review the file.
5. The model is unloaded again and Ruby is restored.

Because each stage frees the previous model first, peak memory use stays close to the size of a single model.

## Configuration

Settings you may want to tune for your machine:

- `n_ctx`, `n_threads`, `n_threads_batch` in `agent.py` and `other_local_models/coder.py`
- `max_history` in `ChatAgent` (default `3` turns)
- `max_tokens` (default `1024`) and `temperature` (`0.7` for chat, `0.1` for coding)
- `MODEL_PATH` and `PROMPT_FILE` at the bottom of `proxy.py`

## Notes

- Code is written to `sandbox/` and is **not executed** automatically.
- Memory is read when a model is loaded, so newly saved facts appear after the next model reload.