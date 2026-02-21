# sdrsharp-to-pp

# SDR# Frequencies.xml → SDR++ frequency_manager_config.json converter

A small Python tool to convert SDR# bookmark file (`Frequencies.xml`) into an SDR++ Frequency Manager config (`frequency_manager_config.json`).

## Requirements
- Python 3.9+ (works on Windows / Linux / macOS)

## Input / Output
- Input: `Frequencies.xml` (SDR#)
- Input: `frequency_manager_config.json` (SDR++ base file)
- Output: `frequency_manager_config.json.new`

## Usage (Windows)
1. Put these files in the same folder:
   - `sdrsharp_to_sdrpp_bookmarks.py`
   - `Frequencies.xml`
   - `frequency_manager_config.json`
2. Open Command Prompt in that folder.
3. Run:
4. A new file will be generated:
   - `frequency_manager_config.json.new`
5. Replace your SDR++ config file with the new one (make a backup first).

```bash
python sdrsharp_to_sdrpp_bookmarks.py
