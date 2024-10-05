import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    INPUT_DIR = BASE_DIR / "input_files"
    OUTPUT_DIR = BASE_DIR / "output"
    PROMPTS_DIR = BASE_DIR / "prompts"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_ORG")
    OPENAI_MODEL = "gpt-3.5-turbo-0125"
    
    PROMPT_TEMPLATE_FILE = BASE_DIR / "prompt.txt"
    BATCH_INPUT_FILE = PROMPTS_DIR / "batch_inputs.jsonl"
    BATCH_OUTPUT_FILE = PROMPTS_DIR / "batch_output.jsonl"
    
    COMPLETION_WINDOW = "24h"
    BATCH_METADATA = {"description": "STS Get Promo Price"}
