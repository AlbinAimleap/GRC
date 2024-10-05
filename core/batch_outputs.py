import json
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.loggers import logger
from core.config import Config


class BatchOutputProcessor:
    def __init__(self, input_filename: str, output_filename: str, format: str = "json"):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.format = format

    @staticmethod
    def load_data(file_path: Path) -> List[Dict[str, Any]]:
        """Loads JSON lines from the file and returns as a list of dictionaries."""
        with open(file_path, "r") as f:
            return [json.loads(line) for line in f]

    @staticmethod
    def process_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes an item and returns the 'content' if no error, otherwise None."""
        if item.get("error"):
            print(item["error"])
            return None
        content: str = item["response"]["body"]["choices"][0]["message"]["content"]
        content = content.replace("", "") \
                    .replace("", "") \
                    .replace('"', '"') \
                    .replace("...", ",") \
                    .replace("```json", "") \
                    .replace("```", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {content} \n error: {str(e)}")
            return None

    @staticmethod
    def save_data(output_file: Path, data: List[Dict[str, Any]], format: str) -> None:
        """Saves the processed data to a file in the specified format."""
        try:
            with open(Config.OUTPUT_DIR / "no_descriptions.json", "r") as f:
                no_description_data = json.load(f)
        except FileNotFoundError:
            no_description_data = []
        
        data.extend(no_description_data)
        filtered_data = [item for item in data if item is not None]
        df = pd.DataFrame(filtered_data)

        if format.lower() == 'json':
            output_file = f"{output_file}.json"
            df.to_json(output_file, orient='records', indent=4)
        elif format.lower() == 'csv':
            output_file = f"{output_file}.csv"
            df.to_csv(output_file, index=False)
        elif format.lower() == 'tsv':
            output_file = f"{output_file}.tsv"
            df.to_csv(output_file, sep='\t', index=False)
        elif format.lower() == 'excel':
            output_file = f"{output_file}.xlsx"
            df.to_excel(output_file, index=False, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported format: {format}")

    def process(self) -> None:
        input_file = Config.OUTPUT_DIR / self.input_filename
        output_file = Config.OUTPUT_DIR / self.output_filename
        data = self.load_data(input_file)
        processed_items = [self.process_item(item) for item in data if self.process_item(item) is not None]
        
        self.save_data(output_file, processed_items, self.format)
        
        logger.info(f"Processed {len(processed_items)} items.")

if __name__ == "__main__":
    processor = BatchOutputProcessor("marianos_output.jsonl", "marianos_sample_30_09_2024.json", "json")
    processor.process()
