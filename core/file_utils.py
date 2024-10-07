import json
import pandas as pd
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Union, Callable, Any

from core.loggers import logger


class FileHandler:
    def __init__(self):
        self.loaders = {
            '.csv': pd.read_csv,
            '.xls': pd.read_excel,
            '.xlsx': pd.read_excel,
            '.json': pd.read_json
        }
        self.supported_extensions = tuple(self.loaders.keys())
        self.data = None

    def load_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load a file and return its contents as a list of dictionaries.

        :param file_path: Path to the file to be loaded.
        :return: List of dictionaries representing the file contents.
        :raises ValueError: If the file format is unsupported.
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        if extension in self.loaders:
            logger.info(f"Loading file: {file_path}")
            return self.loaders[extension](file_path).drop_duplicates().to_dict(orient='records')
        else:
            logger.error(f"Unsupported file format: {extension}")
            raise ValueError(f"Unsupported file format: {extension}")

    def load_data(self, path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load data from a file or a directory.

        :param path: Path to the file or directory.
        :return: List of dictionaries representing the data.
        :raises ValueError: If the path is invalid.
        """
        path = Path(path)

        if path.is_file():
            return self.load_file(path)
        elif path.is_dir():
            return self.load_directory(path)
        else:
            logger.error(f"Invalid path: {path}")
            raise ValueError(f"Invalid path: {path}")

    def load_directory(self, directory_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load data from all supported files in a directory.

        :param directory_path: Path to the directory.
        :return: List of dictionaries representing the data from all files.
        """
        directory = Path(directory_path)
        files = [f for f in directory.glob('*') if f.suffix.lower() in self.supported_extensions]
        
        all_data = []
        logger.info(f"Loading data from directory: {directory_path}")
        for file in files:
            try:
                all_data.extend(self.load_file(file))
            except ValueError as e:
                logger.warning(f"Could not load file {file}: {e}")

        return all_data
    
    def to_json(self, output_file: Union[str, Path]) -> None:
        """
        Save data to a JSON file.

        :param output_file: Path to the output JSON file.
        """
        output_file = Path(output_file)
        logger.info(f"Saving data to JSON file: {output_file}")
    
        # Replace NaN values with empty strings
        cleaned_data = [{k: ('' if pd.isna(v) else v) for k, v in item.items()} for item in self.data]
    
        with open(output_file, 'w') as f:
            json.dump(cleaned_data, f, indent=4)

    def to_csv(self, output_file: Union[str, Path]) -> None:
        """
        Save data to a CSV file.

        :param output_file: Path to the output CSV file.
        """
        output_file = Path(output_file)
        logger.info(f"Saving data to CSV file: {output_file}")
        df = pd.DataFrame(self.data)
        df.to_csv(output_file, index=False)

    def to_excel(self, output_file: Union[str, Path]) -> None:
        """
        Save data to an Excel file.

        :param output_file: Path to the output Excel file.
        """
        output_file = Path(output_file)
        logger.info(f"Saving data to Excel file: {output_file}")
        df = pd.DataFrame(self.data)
        df.to_excel(output_file, index=False)

    def load(
        self,
        input_path: Union[str, Path],
        modifiers: Union[None, Callable, List[Dict[str, Any]]] = None
    ) -> None:
        """
        Process data from input to output with optional modifier functions.

        :param input_path: Path to the input data file or directory.
        :param modifiers: Optional modifier function or list of dictionaries containing modifier functions and their arguments.
                          If a single function is provided, it will be applied directly.
                          If a list is provided, each dictionary should have the following structure:
                          {
                              'modifier': Callable,
                              'args': List[Any],
                              'kwargs': Dict[str, Any]
                          }
        """
        self.data = self.load_data(input_path)
        
        if modifiers:
            if callable(modifiers):
                logger.info(f"Applying modifier `{modifiers.__name__}` function to data")
                self.data = modifiers(self.data)
            elif isinstance(modifiers, list):
                for modifier_dict in modifiers:
                    modifier_func = modifier_dict['modifier']
                    modifier_args = modifier_dict.get('args', [])
                    modifier_kwargs = modifier_dict.get('kwargs', {})
                    
                    logger.info(f"Applying modifier `{modifier_func.__name__}` function to data")
                    self.data = modifier_func(self.data, *modifier_args, **modifier_kwargs)
            else:
                raise TypeError("modifiers must be a callable or a list of modifier dictionaries")
            
class Modifiers:
    @staticmethod
    def column_exists(data: List[Dict[str, Any]], column: str) -> List[Dict[str, Any]]:
        """
        Filter data to include only items that have the specified column.

        :param data: List of dictionaries to filter.
        :param column: Column to check for existence.
        :return: Filtered list of dictionaries.
        """
        return [item for item in data if column in item]

    @staticmethod
    def filter_items_by_column(data: List[Dict[str, Any]], column: str, value: str) -> List[Dict[str, Any]]:
        """
        Filter data based on a specific column and value.

        :param data: List of dictionaries to filter.
        :param column: Column to check.
        :param value: Value to filter by.
        :return: Filtered list of dictionaries.
        """
        return [item for item in data if item.get(column) == value]

    @staticmethod
    def add_id_column(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add a new column with unique IDs based on a specific column.
        :param data: List of dictionaries to modify.
        :return: Modified list of dictionaries.
        """
        for item in data:
            item['id'] = str(uuid4())
        return data
    
    @staticmethod
    def remove_columns(data: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
        """
        Remove specified columns from the data.
        :param data: List of dictionaries to modify.
        :param columns: List of column names to remove.
        :return: Modified list of dictionaries.
        """
        logger.warning(f"Removing columns: {columns}")
        for item in data:
            for column in columns:
                if column in item:
                    del item[column]
        return data


if __name__ == "__main__":
    # Example usage
    file_utils = FileHandler()
    file_utils.load(
        input_path="input_files/Jewelosco_30_09_2024.json",
        modifier_func=Modifiers.add_id_column
    )
    file_utils.to_json("output.json")
