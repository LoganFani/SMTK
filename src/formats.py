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

def join_sentences(input_text: list[str]) -> list[str]:
    """
    Takes a list of transcript lines and merges fragments into complete sentences.
    Handles English/Spanish abbreviations and inverted punctuation marks.
    """
    if not input_text:
        return []

    # Common abbreviations that shouldn't trigger a sentence break
    abbreviations = r'(?:[Aa]pprox|[Aa]ppt|[Dd]r|[Ee]sq|[Ff]ig|[Gg]en|[Mm]r|[Mm]rs|[Mm]s|[Pp]rof|[Ss]r|[Ss]ra|[Vv]iz)\.'
    # Terminal punctuation: . ! ? or " or » (Spanish/French quotation)
    terminal_punc = r'[.!?\"»]\s*$'
    
    joined_lines = []
    buffer = ""

    for line in input_text:
        clean_line = line.strip()
        if not clean_line: 
            continue
            
        # Sanity Check: If the buffer has content but the NEW line starts with ¿ or ¡,
        # the previous buffer was almost certainly its own complete sentence.
        if buffer and re.match(r'^[¿¡]', clean_line):
            joined_lines.append(buffer)
            buffer = clean_line
            continue

        # Add current line to buffer
        if buffer:
            buffer = f"{buffer} {clean_line}"
        else:
            buffer = clean_line

        # Check if the current buffer ends with terminal punctuation
        is_terminal = re.search(terminal_punc, buffer)
        # Ensure the terminal punctuation isn't just an abbreviation (e.g., "Mr.")
        is_abbrev = re.search(f'{abbreviations}$', buffer)

        if is_terminal and not is_abbrev:
            joined_lines.append(buffer)
            buffer = ""

    # Flush any remaining text in the buffer
    if buffer:
        joined_lines.append(buffer)

    return joined_lines