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