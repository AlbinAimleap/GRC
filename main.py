import argparse
from typing import Optional

from core.loggers import logger
from core.batch_inputs import BatchInputProcessor
from core.batch_outputs import BatchOutputProcessor
from core.batch import BatchProcessor
from core.config import Config
from pathlib import Path


class BatchProcessingManager:
    def __init__(self, input_file: str, output_file: str, prompt_file: Optional[str] = None, format: Optional[str] = "json", count: int = 0):
        self.input_file = input_file
        self.output_file = output_file
        self.format = format
        self.count = int(count)
        self.prompt_file = prompt_file or Config.PROMPT_TEMPLATE_FILE
        self.input_processor: Optional[BatchInputProcessor] = None
        self.processor: Optional[BatchProcessor] = None 
        self.output_processor: Optional[BatchOutputProcessor] = None

    def initialize_input_processor(self) -> None:
        self.input_processor = BatchInputProcessor(self.input_file, Config.BATCH_INPUT_FILE)
        self.input_processor.process(self.count)

    def process_batch(self) -> None:
        self.processor = BatchProcessor()
        self.processor.process(Config.BATCH_INPUT_FILE, Config.BATCH_OUTPUT_FILE)

    def process_output(self) -> None:
        self.output_processor = BatchOutputProcessor(Config.BATCH_OUTPUT_FILE, self.output_file, self.format)
        return self.output_processor.process()

    def run(self) -> None:
        logger.info("Starting batch processing and output processing...")
        self.initialize_input_processor()
        logger.info("Batch input processing completed.")
        logger.info("Starting batch processing...")
        self.process_batch()
        logger.info("Batch processing completed.")
        logger.info("Starting output processing...")
        self.process_output()        
        logger.info("Output processing completed.")


def main():
    parser = argparse.ArgumentParser(description="Batch Processing CLI")
    parser.add_argument("-I", "--input_file", required=True, help="Path to the input file")
    parser.add_argument("-O", "--output_filename", required=True, help="Output file name (without extension)")
    parser.add_argument("-f", "--format", choices=["json", "csv", "tsv", "excel"], default="json", help="Output file format (default: json)")
    parser.add_argument("-p", "--prompt_file", help="Path to the prompt file (optional)")
    parser.add_argument("-c", "--count", help="Path to the prompt file (optional)", default=0)
    
    args = parser.parse_args()
    supported_file_formats = ["csv", "json", "tsv", "xlsx"]
    manager = BatchProcessingManager(args.input_file, args.output_filename, args.prompt_file, args.format, args.count)
    manager.run()

if __name__ == "__main__":
    main()
