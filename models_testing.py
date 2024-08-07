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

class OutputCleanup(dspy.Signature):
    """Clean up the output string by removing all unnecessary text."""
    
    agent_output = dspy.InputField(format=str)
    cleaned_output = dspy.OutputField(format=str)

class ExtractVariableName(dspy.Signature):
    """Extract the variable name from the question."""

    question = dspy.InputField(format=str)
    variable_name = dspy.OutputField(format=str, desc='Only return the variable name.')

class ExtractVariableValue(dspy.Signature):
    """Extract the value from the context."""

    variable_name = dspy.InputField(format=str, desc='Variable name to extract the value for.')
    context = dspy.InputField()
    variable_value = dspy.OutputField(format=str, desc='Only return the value of the variable.')

class FormatOutput(dspy.Signature):
    """Format the output string."""

    variable_name = dspy.InputField(format=str)
    variable_value = dspy.InputField(format=str)
    formatted_output = dspy.OutputField(format=str, desc="Return output in the format 'variable_name: variable_value'.")


class SpreadSheetAnalyzer(dspy.Module):
    def __init__(self, range_description_json, operators_dict,  num_passages=3):
        super().__init__()
        self.range_description_json = range_description_json
        self.operators_dict = operators_dict
        self.retriever = dspy.Retrieve(num_passages)

        self.name_extractor = dspy.Predict(ExtractVariableName)
        self.value_extractor = dspy.Predict(ExtractVariableValue)
        self.final_output = dspy.Predict(FormatOutput)
        # self.cleaner = dspy.Predict(OutputCleanup)

    def forward(self, question, verbose=False):
        context = self.retriever(query_or_queries=question).passages
        print(context)
        fasdfasdfasd

        variable_name_output = self.name_extractor(question=question)
        # variable_name = parse_output(variable_name_output.variable_name, "Variable Name")
        # variable_value_out = self.value_extractor(variable_name=variable_name_output.variable_name, context=context)
        variable_value_out = self.value_extractor(variable_name=variable_name_output.variable_name, context=context)
        # extracted_value_out = self.value_extractor(variable_name=variable_name, context=context)
        # variable_value = parse_output(variable_value_out.variable_value, "Variable Value")
        # parsed_output = name_and_value.split(': ')
        # parsed_values, parsed_name = parsed_output[-1].rstrip('.'), parsed_output[0]

        fin_out = self.final_output(variable_name=variable_name_output.variable_name, variable_value=variable_value_out.variable_value)
        return dspy.Prediction(answer=fin_out.formatted_output)
        # return dspy.Prediction(answer=f"{variable_name}: {variable_value}")