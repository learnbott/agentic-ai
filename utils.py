import re
import ast

def parse_list_from_output_string(output_string):
    """
    Parses and extracts a Python list from the given output string.

    Args:
    output_string (str): The output string containing the list representation.

    Returns:
    list: The extracted Python list.
    """
    try:
        # Use regex to find the list portion within the string
        list_match = re.search(r'(\[[^\]]*\])', output_string, re.DOTALL)
        if list_match:
            list_str = list_match.group(1)
            # Safely evaluate the list string
            data = ast.literal_eval(list_str)
            if isinstance(data, list):
                return data
            else:
                raise ValueError("The extracted portion is not a list.")
        else:
            raise ValueError("No list found in the output string.")
    except (ValueError, SyntaxError):
        raise ValueError("The output string is not a valid list representation.")


def extract_list_from_string(text):
    """
    Extracts a Python list from a given string containing the list.
    
    Parameters:
    text (str): The input string containing the list.
    
    Returns:
    list: The extracted list.
    """
    text = f""""{text}"""
    list_start_index = text.find('[')
    list_end_index = text.find(']') + 1
    if list_start_index == -1 or list_end_index == -1:
        raise ValueError("No list found in the provided text.")
    extracted_list = ast.literal_eval(text[list_start_index:list_end_index])
    return extracted_list

def fix_hyphenated_words(text):
    """
    Fix formatting issues for hyphenated words with spaces before or after the hyphen.
    Only make it one word if there is only one space before or after the hyphen.
    If there is a space before and after the hyphen, leave it alone.
    
    Args:
    text (str): The input text containing hyphenated words.
    
    Returns:
    str: The corrected text with proper hyphenation.
    """
    # Regular expression to match hyphenated words with a single space before or after the hyphen
    pattern = r'\b(\w+)\s*-\s*(\w+)\b'

    # Function to replace the matched patterns with the corrected format
    def replace_hyphen(match):
        word1, word2 = match.groups()
        if (match.group(0).count(' ') == 1):
            return f"{word1}-{word2}"
        return match.group(0)

    # Replace the matched patterns with the corrected format
    corrected_text = re.sub(pattern, replace_hyphen, text)
    
    return corrected_text

def extract_tuples_from_string(s):
    # Regular expression to match tuples
    tuple_pattern = r'\(\s*".+?"\s*,\s*".+?"\s*\)'
    
    # Find all matches in the string
    matches = re.findall(tuple_pattern, s)
    
    # Convert matched strings to actual tuples
    extracted_tuples = [ast.literal_eval(match) for match in matches]
    
    return extracted_tuples