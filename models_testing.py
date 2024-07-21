import operator
import dspy

def is_in_dict(key, dictionary):
    return key in dictionary

def string_delete(s, delete_chars=[',', '$', '%']):
    for char in delete_chars:
        s = s.replace(char, '')
    return s

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# def parse_output(output: str, field: str) -> str:
#     field = field+': '
#     parsed_out = output.split(field)[-1]
#     if '---' in parsed_out:
#         return parsed_out.split('---')[0].strip()
#     else:
#         return parsed_out.split('\n')[0].strip()
    
def parse_output(output: str, field: str) -> str:
    field = field+': '
    parsed_out = output.split(field)[2].split('\n')[0]
    if '---' in parsed_out:
        return parsed_out.split('---')[0].strip()
    else:
        return parsed_out.split('\n')[0].strip()
    
def is_in_range(value, bounds, ops=(operator.ge, operator.le)):
    """
    Check if a value falls within a range based on the provided operators.
    
    Parameters:
    - value: The float value to check.
    - lower: The lower and upper bounds limit of the range.
    - ops: A tuple of two functions from the operator module, where
           ops[0] is used for comparing the value with the lower limit,
           and ops[1], if upper is not None, for comparing the value with the upper limit.
           Defaults to greater than or equal to for lower and less than or equal to for upper.
           
    Returns:
    - True if the value is within the range based on the operators; False otherwise.
    """
    if len(bounds)==2: lower, upper = bounds
    else: lower, upper = bounds[0], None
    if upper is None:
        return ops[0](value, lower)
    else:
        return ops[0](value, lower) and ops[1](value, upper)


class SpreadsheetValueExtractor(dspy.Signature):
    """Extract the variable name from the question and its value from the context."""

    question = dspy.InputField(format=str)
    context = dspy.InputField()
    extracted_name_and_value = dspy.OutputField(format=str, desc='Output in this format "variable name: extracted value."')

class OutputCleanup(dspy.Signature):
    """Clean up the output string by removing all unnecessary text."""
    
    agent_output = dspy.InputField(format=str)
    cleaned_output = dspy.OutputField(format=str)


class SpreadSheetAnalyzer(dspy.Module):
    def __init__(self, range_description_json, operators_dict, query_engine=None, num_passages=3):
        super().__init__()
        self.range_description_json = range_description_json
        self.operators_dict = operators_dict
        if query_engine is None: self.retriever = dspy.Retrieve(num_passages)
        else: self.retriever = None
        self.query_engine = query_engine
        # self.extraction = dspy.Predict(SpreadsheetValueExtractor)
        # self.cleaner = dspy.Predict(OutputCleanup)

    def forward(self, question, verbose=False):
        if self.retriever is not None:
            retriever_question = question
            context = self.retriever(query_or_queries=retriever_question).passages

        elif self.query_engine is not None:
            response = self.query_engine.query(question)
            context = response.response
            # retrieved_data = self.query_engine.retrieve(question)
            # data = [x.get_content() for x in retrieved_data]

        else:
            context=[]

        extracted_out = self.extraction(question=question, context=context)
        name_and_value = parse_output(extracted_out.extracted_name_and_value, 'Extracted Name And Value')
        parsed_output = name_and_value.split(': ')
        parsed_values, parsed_name = parsed_output[-1].rstrip('.'), parsed_output[0]

        return dspy.Prediction(answer=f"{parsed_name}: {parsed_values}")