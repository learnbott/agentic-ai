import operator
import dspy


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

def parse_output(output: str, field: str) -> str:
    field = field+': '
    parsed_out = output.split(field)[-1]
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
    """Extract the values for variable names contained in the context."""

    question = dspy.InputField(format=str)
    context = dspy.InputField(format=str, desc="json string representation of a spreadsheet.")
    answer = dspy.OutputField(desc='{variable name}: {extracted value}.')

class FloatQuestionCorrector(dspy.Signature):
    """The extracted value for the given variable name cannot be converted to a float. 
    Rephrase the question to focus on extracting a float value for the variable name 
    given in the question."""

    question = dspy.InputField(format=str, desc="The original question.")
    extracted_value = dspy.InputField(format=str)
    corrected_float_question = dspy.OutputField(format=str)

class FormatCorrectQuestion(dspy.Signature):
    """The extracted value for the given variable name is in the wrong format range.
    Rephrase the question and include the format description."""

    question = dspy.InputField(format=str, desc="The original question.")
    extracted_value = dspy.InputField(format=str)
    format_description = dspy.InputField(format=str)
    corrected_question = dspy.OutputField(format=str)

class SpreadSheetAnalyzer(dspy.Module):
    def __init__(self, range_description_json, operators_dict):
        super().__init__()
        self.range_description_json = range_description_json
        self.operators_dict = operators_dict
        self.extraction = dspy.Predict(SpreadsheetValueExtractor)
        self.question_rewriter = dspy.Predict(FormatCorrectQuestion)
        self.float_question_corrector = dspy.Predict(FloatQuestionCorrector)

    def correct_float_question(self, question, extracted_value, data, max_attempts=3, verbose=False):
        for _ in range(max_attempts):
            if verbose: print('   Float Question Failed:', question)
            rewritten_out = self.float_question_corrector(question=question, extracted_value=extracted_value)
            question = parse_output(rewritten_out.corrected_float_question, 'Corrected Float Question')
            if verbose: print('   Float Question Corrected:', question)
            extracted_out = self.extraction(question=question, context=data)
            extracted_value = parse_output(extracted_out.answer, 'Answer')
            parsed_values = extracted_value.split(': ')[-1]
            parsed_values=string_delete(parsed_values, delete_chars=['$', ',', '%'])
            if verbose: print('   Float Parsed Values:', parsed_values)
            if is_float(parsed_values):
                return parsed_values, question
        return None, question

    def correct_format_question(self, question, data, parsed_name, extracted_value, max_attempts=3, verbose=False):
        for _ in range(max_attempts):
            if verbose: print('   Format Question Failed:', question)
            rewritten_out = self.question_rewriter(question=question, extracted_value=extracted_value, format_description=self.range_description_json[parsed_name])
            question = parse_output(rewritten_out.corrected_question, 'Corrected Question')
            if verbose: print('   Format Question Corrected:', question)
            extracted_out = self.extraction(question=question, context=data)
            extracted_value = parse_output(extracted_out.answer, 'Answer')
            parsed_values = extracted_value.split(': ')[-1]
            parsed_values = string_delete(parsed_values, delete_chars=['$', ',', '%'])
            if verbose: print('   Format Parsed Values:', parsed_values)
            if is_float(parsed_values):
                parsed_values = float(parsed_values)
            else:
                continue
            if is_in_range(parsed_values, bounds=self.operators_dict[parsed_name]['bounds'], ops=self.operators_dict[parsed_name]['operators']):
                return parsed_values, question
        return parsed_values, question

    def forward(self, data, question, verbose=False):
        extracted_out = self.extraction(question=question, context=data)
        extracted_value = parse_output(extracted_out.answer, 'Answer')
        parsed_output = extracted_value.split(': ')
        parsed_values, parsed_name = parsed_output[-1], parsed_output[0]
        # TODO: write helper agent that checks the parsed name against the self.operators_dict
        if parsed_name not in self.operators_dict:
            return None, None
        
        if verbose: print(f'   BEGINNING Parsed Name: {parsed_name}, Parsed Values: {parsed_values}')
        # Safeguard - check if the extracted value can be converted to a float
        valid_float_tf = is_float(parsed_values)
        if not valid_float_tf:
            parsed_values, question = self.correct_float_question(question,
                                                                  extracted_value, 
                                                                  data,
                                                                  verbose=verbose)
            
        if parsed_values is not None:
            # Safeguard - check if the extracted value falls within the expected range
            valid_format_tf = is_in_range(float(parsed_values), 
                                        bounds=self.operators_dict[parsed_name]['bounds'], 
                                        ops=self.operators_dict[parsed_name]['operators'])
            if not valid_format_tf:
                parsed_values, question = self.correct_format_question(question, 
                                                                    data, 
                                                                    parsed_name, 
                                                                    extracted_value,
                                                                    verbose=verbose)

        # return str(parsed_name), str(parsed_values)
        return dspy.Prediction(answer=f"{parsed_name}: {parsed_values}")