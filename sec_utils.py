import re


def get_tree_data(element, depth=0, list_depth=0, prev_depth=-1, lists=None, final_dict=None):
    if lists is None:
        lists = [[]]
    if final_dict is None:
        final_dict = {}

    if element.tag == "HEAD":

        if depth > list_depth:
            lists[-1].append(f"{element.text.strip()}")
        else:
            lists.append(lists[-1][:depth-2])
            lists[-1].append(f"{element.text.strip()}")
        
    elif element.tag == "P":
        # "P" indicates that there is text associated with the element
        # This only saves to the final_dict if the element has a child with tag "P"
        try:
            final_dict[str(lists[-1])] += ''.join(element.itertext())
        except:
            final_dict[str(lists[-1])] = ''.join(element.itertext())

    else:
        pass

    # Recursively call get_tree_data on each child, increasing the depth
    for child in element:
        get_tree_data(child, depth + 1, len(lists[-1])+1, depth, lists, final_dict)

    return final_dict


def get_metadata(s, text, metadata={"title":None, "chapter":None, "part":None, "subpart":None, "section":None, "description":None, "mentioned_sections":None}):
    s_split = s[2:-2].split("', '")
    key_lengths = {key: len(key) for key in metadata}
    for x in s_split:
        xsplit = x.lower().split("—")
        if len(xsplit) > 1:
            prefix = xsplit[0]
            for key, length in key_lengths.items():
                if prefix[:length] == key:
                    metadata[key] = x
                    break
    metadata["description"] = s_split[-1]
    metadata["section"] = s_split[-1].split("  ")[0]#.split(" ")[-1].strip()
    metadata["mentioned_sections"] = get_linked_sections(text)
    return metadata

def get_rule_and_description(document):
    first_split = document.metadata['description'].split("  ")
    rule = first_split[0].strip()#.split()[-1].strip()
    rule_description = first_split[-1].strip()
    return rule, rule_description

import re
def get_linked_sections(doc):
    cleaned_sections = []
    pattern = pattern = r'§§?\s\d{3}\.\d+(?:\s(?:and|through)\s\d{3}\.\d+)?'
    linked_sections = re.findall(pattern, doc)
    for section in linked_sections:
        # Check if the section contains 'and' or 'through'
        if 'and' in section or 'through' in section:
            # Remove the '§§' prefix if present
            section = section.replace('§§', '§')
            # Split the section into individual parts
            parts = re.split(r'\s(?:and|through)\s', section)
            # Add each part to the cleaned_sections list, ensuring each part has the '§' prefix
            for part in parts:
                if part[0] != '§':
                    cleaned_sections.append(part.strip())
                else:
                    cleaned_sections.append(part.strip())
        else:
            # If the section is already a single section, add it to the list
            cleaned_sections.append(section.strip())
    return list(set(cleaned_sections))