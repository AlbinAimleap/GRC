import json
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.loggers import logger
from core.config import Config


class BatchOutputProcessor:
    def __init__(self, input_filename: str, output_filename: str, format: str = "json"):
        self.input_filename = input_filename
        self.output_filename = Path(output_filename).with_suffix('')
        self.format =  Path(output_filename).suffix or f".{format.lower()}"

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
    def clean_url(url: str) -> str:
        return url.replace("\/", "/")

    @staticmethod
    def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def merge_data(temp_data: List[Dict[str, Any]], filtered_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_out = []
        for t_item in temp_data:
            updated = False
            for f_item in filtered_data:
                if t_item["id"] == f_item["id"]:
                    new_out.append({**t_item, **f_item})
                    updated = True
                    break
            if not updated:
                new_out.append(t_item)
        return new_out

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        for column in ['store_logo', 'url', 'image_url']:
            if column in df.columns:
                df[column] = df[column].apply(lambda x: BatchOutputProcessor.clean_url(x) if isinstance(x, str) else x)
        
        for column in ["regular_price", "sale_price", "promo_price", "unit_price"]:
            if column in df.columns:
                df[column] = df[column].apply(lambda x: float(x) if x and isinstance(x, str) else x)
                
        return df.drop_duplicates()

    @staticmethod
    def save_data(output_file: Path, data: List[Dict[str, Any]], format: str) -> None:
        """Saves the processed data to a file in the specified format."""
        filtered_data = [item for item in data if item is not None]
        temp_data = BatchOutputProcessor.load_json_file(Path("output/temp_data.json"))
        
        merged_data = BatchOutputProcessor.merge_data(temp_data, filtered_data)
        
        df = BatchOutputProcessor.clean_dataframe(pd.DataFrame(merged_data))

        format_handlers = {
            '.json': lambda: df.to_json(f"{output_file}.json", orient='records', indent=4),
            '.csv': lambda: df.to_csv(f"{output_file}.csv", index=False),
            '.tsv': lambda: df.to_csv(f"{output_file}.tsv", sep='\t', index=False),
            '.excel': lambda: df.to_excel(f"{output_file}.xlsx", index=False, engine='openpyxl')
        }

        format_lower = format.lower()
        if format_lower in format_handlers:
            format_handlers[format_lower]()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
    def process(self) -> str:
        input_file = Config.OUTPUT_DIR / self.input_filename
        output_file = Config.OUTPUT_DIR / self.output_filename
        data = self.load_data(input_file)
        processed_items = [self.process_item(item) for item in data if self.process_item(item) is not None]
        
        self.save_data(output_file, processed_items, self.format)
        
        logger.info(f"Processed {len(processed_items)} items.")
        return self.format

if __name__ == "__main__":
    processor = BatchOutputProcessor("prompts/batch_output.jsonl", "test.json")
    processor.process()
