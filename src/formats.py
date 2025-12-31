import re

# Functions to format files to be batched through pipeline.
# Use temp file to avoid overwriting original file.

def is_noise(line: str) -> bool:
    noise_patterns = [
        r'^\s*$',
        r'^\d+$',
        r'^\d{1,2}:\d{2}(:\d{2})?',
        r'^\[.*?\]$',
        r'^\(.*?\)$',
    ]

    return any(re.match(pattern, line) for pattern in noise_patterns)

# TODO allow use of temporary files instead of holding sentences in memory
def format_file (input_path:str, output_path:str) -> None:
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            stripped_line = line.strip()
            if not is_noise(stripped_line):
                outfile.write(stripped_line + '\n')

def format_text (input_text:list[str]) -> list[str]:
    formatted_lines = []
    for line in input_text:
        stripped_line = line.strip()
        if not is_noise(stripped_line):
            formatted_lines.append(stripped_line)
    return formatted_lines

    