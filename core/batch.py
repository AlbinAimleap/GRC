import time
from openai import OpenAI
from pathlib import Path
from typing import Any

from core.config import Config
from core.loggers import logger


class BatchProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def upload_batch_file(self, file_path: Path) -> Any:
        """Uploads a batch file to OpenAI and returns the file object."""
        with open(file_path, "rb") as f:
            return self.client.files.create(file=f, purpose="batch")

    def start_batch(self, batch_input_file: Any) -> Any:
        """Starts a batch process with the given input file."""
        return self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window=Config.COMPLETION_WINDOW,
            metadata=Config.BATCH_METADATA
        )

    def get_batch_status(self, batch_id: str) -> Any:
        """Retrieves the status of a batch using its ID."""
        return self.client.batches.retrieve(batch_id)

    def save_responses(self, file_id: str, filename: str) -> None:
        """Retrieves the responses from a file using its ID and saves to filename."""
        output_path = Config.OUTPUT_DIR / filename
        with open(output_path, "w") as f:
            data = self.client.files.content(file_id)
            for line in data.text:
                f.write(line)
    
    def process(self, batch_input_file: Any, batch_output_file) -> None:
        """Mocks the process method to simulate the batch processing."""
        batch_processor = BatchProcessor()
        file = batch_processor.upload_batch_file(batch_input_file)
        batch_request = batch_processor.start_batch(file)
        
        while batch_request.status != "completed":
            batch_request = batch_processor.get_batch_status(batch_request.id)
            if batch_request.status == "completed":
                logger.info(f"Batch status: {batch_request.status}")
                break
            
            logger.info(f"Batch status: {batch_request.status}")
            logger.status(f"Processed: {batch_request.request_counts.completed}/{batch_request.request_counts.total}")
            logger.info("Waiting for 30 seconds...")
            time.sleep(30)
        
        batch_processor.save_responses(batch_request.output_file_id, batch_output_file)
        logger.info(f"Batch processing completed. Data saved to {batch_output_file}")



if __name__ == "__main__":
    batch_processor = BatchProcessor()
    batch_processor.process()