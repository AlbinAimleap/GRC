# GRC Batch Processing CLI Tool

This command-line interface (CLI) tool is designed for batch processing of input data using a specified prompt and generating output in various formats.

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AlbinAimleap/GRC
   cd GRC
   ```

2. **Install Required Dependencies:**
    Create a virtual environment and install the required dependencies:
    Linux/macOS:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    Windows:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
    Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
Create a .env file in the root directory of your project and add the following environment variables:
```bash
OPENAI_API_KEY_ORG=OPENAI_API_KEY
```
To run the batch processing tool, use the following command:

```bash
python main.py -I <input_file> -O <output_filename> [-f <format>] [-p <prompt_file>]
```

### Arguments:

- `-I, --input_file`: **Path to the input file** (required)
- `-O, --output_filename`: **Output file name** (required)
- `-f, --format`: **Output file format** (optional, default: json)
  - **Choices:** json, csv, tsv, excel
- `-p, --prompt_file`: **Path to the prompt file** (optional)

### Example:
```bash
python main.py -I input_data.json -O processed_output.csv
```
This command processes the input from `input_data.json`, utilizes the prompt from `custom_prompt.txt`, and generates the output in CSV format as `processed_output.csv`.

## Output

The tool generates an output file in the specified format (json, csv, tsv, or excel) with the provided filename in the output directory.

## Notes

- If no prompt file is specified, the tool defaults to using a predefined prompt template from the configuration.
- Ensure you have the necessary permissions to read from the input file and write to the output file location.

