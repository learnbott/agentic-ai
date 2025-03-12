import re
import ast
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.colors import black

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


class PDF:
    def __init__(self, filename):
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Register fonts
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'DejaVuSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Italic', 'DejaVuSans-Oblique.ttf'))
        
        # Define styles
        self.styles = {
            'Title': ParagraphStyle(
                'Title',
                fontName='DejaVu-Bold',
                fontSize=14,
                spaceAfter=30,
                textColor=black,
            ),
            'Heading': ParagraphStyle(
                'Heading',
                fontName='DejaVu-Bold',
                fontSize=12,
                spaceAfter=16,
                spaceBefore=16,
                textColor=black,
            ),
            'Body': ParagraphStyle(
                'Body',
                fontName='DejaVu',
                fontSize=10,
                spaceAfter=12,
                textColor=black,
            ),
            'Analysis': ParagraphStyle(
                'Analysis',
                fontName='DejaVu-Italic',
                fontSize=10,
                spaceAfter=12,
                textColor=black,
            ),
            'BulletTitle': ParagraphStyle(
                'BulletTitle',
                fontName='DejaVu-Bold',
                fontSize=10,
                spaceAfter=6,
                spaceBefore=6,
                textColor=black,
            ),
            'BulletList': ParagraphStyle(
                'BulletList',
                fontName='DejaVu',
                fontSize=10,
                leftIndent=20,
                spaceBefore=3,
                spaceAfter=3,
                textColor=black,
            ),
            'Footer': ParagraphStyle(
                'Footer',
                fontName='DejaVu',
                fontSize=8,
                textColor=black,
                alignment=1,  # Center alignment
            )
        }
        
        self.story = []
    
    def header(self):
        self.story.append(Paragraph('Federal Regulation Summary', self.styles['Title']))
        
    def chapter_title(self, title):
        self.story.append(Paragraph(title, self.styles['Heading']))
    
    def chapter_body(self, body):
        body = body.replace('\n\n', '\n')
        # Split the text by newlines and filter out empty strings
        paragraphs = [p.strip() for p in body.split('\n') if p.strip()]
        
        # Add each paragraph with proper spacing
        for paragraph in paragraphs:
            self.story.append(Paragraph(paragraph, self.styles['Body']))
            self.story.append(Spacer(1, 2))

    def key_points_section(self, title, points):
        self.story.append(Paragraph(title, self.styles['BulletTitle']))
        for point in points:
            self.story.append(Paragraph(
                "• " + point,
                self.styles['BulletList']
            ))
        self.story.append(Spacer(1, 12))

    def guiding_principles_section(self, title, points):
        self.story.append(Paragraph(title, self.styles['BulletTitle']))
        for point in points:
            self.story.append(Paragraph(
                "• " + point,
                self.styles['BulletList']
            ))
        self.story.append(Spacer(1, 12))

    def analysis_section_title(self, title):
        self.story.append(Paragraph(title, self.styles['Heading']))
        
    def analysis_section_body(self, analysis):
        self.story.append(Paragraph(analysis, self.styles['Analysis']))
        self.story.append(Spacer(1, 12))
        
    def save(self):
        from reportlab.lib.units import inch
        from reportlab.platypus import Frame, PageTemplate
        
        def add_page_number(canvas, doc):
            page_num = canvas.getPageNumber()
            text = f"Page {page_num}"
            canvas.saveState()
            canvas.setFont('DejaVu', 8)
            canvas.drawCentredString(letter[0]/2, 0.5*inch, text)
            canvas.restoreState()
        
        # Create the page template with page numbering
        frame = Frame(
            self.doc.leftMargin, 
            self.doc.bottomMargin, 
            letter[0] - self.doc.leftMargin - self.doc.rightMargin, 
            letter[1] - self.doc.topMargin - self.doc.bottomMargin,
            id='normal'
        )
        
        # Replace the default template instead of adding a new one
        self.doc.addPageTemplates([
            PageTemplate(id='firstPage', frames=frame, onPage=add_page_number),
        ])
        
        # Make sure we use the custom template as the default
        self.doc.build(self.story, onFirstPage=add_page_number, onLaterPages=add_page_number)

def create_pdf(summaries, bullets_dict, output_filename, additional_analyses=None):
    '''Save the summaries to a PDF with proper text wrapping and page breaks.
    
    Args:
        summaries: Dictionary of section titles and their summaries
        output_filename: Path where to save the PDF file
        additional_analyses: Optional dict of analysis sections corresponding to each summary
    '''
    pdf = PDF(output_filename)
    
    # Add the header
    pdf.header()
    
    # Add each section
    for header, summary in summaries.items():
        # Clean up any special characters that might cause issues
        clean_header = header.replace("'", "'").replace('"', '"').replace('–', '-')
        clean_summary = summary.replace("'", "'").replace('"', '"').replace('–', '-')
        
        # Add the section title and body
        pdf.chapter_title(clean_header)
        pdf.key_points_section("Key Points", bullets_dict['bullet_points'][header])
        pdf.guiding_principles_section("Guiding Principles Key Points", bullets_dict['guiding_principles_bullet_points'][header])
        pdf.chapter_body(clean_summary)
        
        # Add additional analyses if provided
        if additional_analyses is not None and header in additional_analyses:
            analyses = additional_analyses[header]
            if isinstance(analyses, dict) and 'header' in analyses and 'text' in analyses:
                clean_header = analyses['header'].replace("'", "'").replace('"', '"').replace('–', '-')
                clean_text = analyses['text'].replace("'", "'").replace('"', '"').replace('–', '-')
                pdf.analysis_section_title(clean_header)
                pdf.analysis_section_body(clean_text)
    
    # Save the PDF
    pdf.save()
