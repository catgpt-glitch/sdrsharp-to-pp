# sdrsharp-to-pp

# SDR# Frequencies.xml → SDR++ frequency_manager_config.json converter

A small Python tool to convert SDR# bookmark file (`Frequencies.xml`) into an SDR++ Frequency Manager config (`frequency_manager_config.json`).

## Requirements
- Python 3.9+ (works on Windows / Linux / macOS)

## Input / Output
- Input: `Frequencies.xml` (SDR#)
- Input: `frequency_manager_config.json` (SDR++ base file)
- Output: `frequency_manager_config.json.new`
- Mode mapping: NFM=0, WFM=1, AM=2, USB=4, LSB=5

## Usage (Windows)
1. Place the following files in the same directory:
   - `sdrsharp_to_sdrpp_bookmarks.py`
   - `Frequencies.xml`
   - `frequency_manager_config.json`
2. Open Command Prompt in that folder.
3. Run:
```bash
python sdrsharp_to_sdrpp_bookmarks.py
```
4. A new file will be generated:
   - `frequency_manager_config.json.new`
5. Replace your SDR++ config file with the new one (make a backup first).

## Notes / Limitations

- SDR++ may not display Japanese names properly (depends on the SDR++ build/UI).
    
- If a category name is missing or duplicated, the tool may use fallback names like:
    
    - `no category`, or `(1)`, `(2)` suffixes.
        
- Keep backups before overwriting any config file.

## Disclaimer
- This tool is not affiliated with SDR# or SDR++.
