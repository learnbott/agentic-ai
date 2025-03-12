from bs4 import BeautifulSoup
import re

def parse_and_clean_xml(response_content, first_section_title='Rule Introduction'):
    # Parse the XML string with BeautifulSoup
    soup = BeautifulSoup(response_content, 'xml')
    # Clean up and prettify the XML string
    cleaned_xml = soup.prettify()
    # Split XML into sections
    sections = cleaned_xml.split('<HD SOURCE="HD1">')
    # Get section titles
    titles = [section.split('</HD>')[0].replace('\n', ' ').strip() for section in sections]
    titles[0] = first_section_title
    return titles, sections

def clean_xml_text(xml_section, remove_footnotes=True, remove_page_references=True, remove_xml_tags=True, remove_extra_whitespace=True):
    cleaned_text = xml_section
    
    if remove_footnotes:
        cleaned_text = re.sub(r'<FTNT>.*?</FTNT>', '', cleaned_text, flags=re.DOTALL)
    
    if remove_page_references:
        cleaned_text = re.sub(r'<SU>.*?</SU>', '', cleaned_text, flags=re.DOTALL)
    
    if remove_xml_tags:
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
    
    if remove_extra_whitespace:
        cleaned_text = re.sub(r'\s*\n\s*\n\s*', ' ', cleaned_text)
    
    return cleaned_text.strip()

def get_page_numbers(section_content):
    pages = re.findall(r'<PRTPAGE\s+P="(\d+)"', section_content)
    # pages = re.findall(r'<SU>\s*(\d+)\s*</SU>', section_content)
    pages = [int(p) for p in pages]
    if pages:
        return min(pages)-1, max(pages)
    else:
        return None, None
    
def parse_xml_title(response_content) -> str:
    soup = BeautifulSoup(response_content, 'xml')
    # Clean up and prettify the XML string
    cleaned_xml = soup.prettify()
    # Split XML into sections
    match = re.search(r'<SUBJECT>(.*?)</SUBJECT>', cleaned_xml, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None