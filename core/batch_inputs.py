import json
from uuid import uuid4
from typing import List, Dict, Any

from core.loggers import logger
from core.file_utils import FileHandler, Modifiers
from core.config import Config


class BatchInputProcessor:
    def __init__(self, input_filename: str, output_filename: str):
        self.file = FileHandler()
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.data: List[Dict[str, Any]] = []
        self.prompt_txt: str = ""
        self.prompts: List[Dict[str, Any]] = []

    def load_input_file(self, count) -> None:
        modifiers = [
            {
                "modifier": Modifiers.add_id_column,
                "args": [],
                "kwargs": {}
            },
            {
                "modifier": Modifiers.remove_columns,
                "args": [["coupon_short_description", "coupon_description"]],
                "kwargs": {}
            }
        ]
        self.file.load(self.input_filename, modifiers=modifiers)
        if count > 0:
            self.data = self.file.data[:count]
        else:
            self.data = self.file.data

    def load_prompt_template(self) -> None:
        with open(Config.PROMPT_TEMPLATE_FILE, "r") as f:
            self.prompt_txt = f.read()

    def generate_prompts(self) -> None:
        no_descriptions = []
        for item in self.data:
            if item["promo_description"] == "":
                logger.warning(f"No descriptions found for the following items: {item['id']}")
                no_descriptions.append(item)
                continue
            
            content = self.prompt_txt.replace("{INPUT}", str(item))

            prompt = {
                "custom_id": str(uuid4()),
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": Config.OPENAI_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert at calculating the price details of products. Your expertise in analyzing the promo description and calculation of the price is exceptional.",
                        },
                        {"role": "user", "content": content},
                    ],
                    "max_tokens": 1000,
                },
            }

            self.prompts.append(prompt)
        if no_descriptions:
            with open(Config.OUTPUT_DIR / "no_descriptions.json", "w") as f:
                json.dump(no_descriptions, f)

    def save_prompts(self) -> None:
        with open(Config.PROMPTS_DIR / self.output_filename, "w") as f:
            for prompt in self.prompts:
                f.write(json.dumps(prompt) + "\n")

    def process(self, count=0) -> None:
        self.load_input_file(count)
        self.load_prompt_template()
        self.generate_prompts()
        self.save_prompts()
        logger.info(f"Generated {len(self.prompts)} prompts.")

if __name__ == "__main__":
    processor = BatchInputProcessor("input_files/jewelesco_new.json", "marianos_batch_inputs_test.jsonl")
    processor.process()
