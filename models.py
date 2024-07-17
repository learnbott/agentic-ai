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


class NameExtractor(dspy.Signature):
    """Extract the variable name from the question."""

    question = dspy.InputField(format=str)
    # question = dspy.InputField(format=lambda x: "\n---\n\n" + str(x) + "\n\n---\n")
    extracted_variable_name = dspy.OutputField(desc='Only return the variable name without any additional information.')

class NameExtractorQuestionRewriter(dspy.Signature):
    """The extracted variable name from the question is wrong. Rewrite the original question to focus on extracting the correct variable name."""

    question = dspy.InputField(format=str, desc='Original question.')
    extracted_variable_name = dspy.InputField(format=str, desc='Wrong variable name extracted from the original question.')
    rephrased_question = dspy.OutputField(format=str, desc='Improved version of the original question that focuses on extracting the correct variable name.')

class SpreadsheetValueExtractor(dspy.Signature):
    """Given the variable name, find and extract its corresponding value from the context."""

    variable_name = dspy.InputField(format=str)
    context = dspy.InputField(format=str, desc='Spreadsheet data.')
    extracted_value = dspy.OutputField(desc='Only return the extracted value.')

class FloatQuestionCorrector(dspy.Signature):
    """The original extracted value is not a float because the original question was not specific enough. 
    Rephrase the original question so that the new question focuses on a float value for the variable name given in the question."""

    question = dspy.InputField(format=str, desc='Original question.')
    # extracted_value = dspy.InputField(format=str, desc='Original extracted value from the original question for reference.')
    rephrased_float_question = dspy.OutputField(format=str, desc='Improved version of the original question that focuses on asking for a float value.')

class FormatCorrectQuestion(dspy.Signature):
    """The original extracted value is outside its designated format range because the original question was not specific enough. 
    Rephrase the original question so that the new question includes the format description."""

    question = dspy.InputField(format=str, desc='Original question.')
    # extracted_value = dspy.InputField(format=str, desc='Original extracted value from the original question for reference.')
    format_description = dspy.InputField(format=str, desc='Format description for the variable name in the question.')
    rephrased_format_question = dspy.OutputField(format=str, desc='Improved version of the original question asking for the value that fits the format description.')

class SpreadSheetAnalyzer(dspy.Module):
    def __init__(self, range_description_json, operators_dict, num_passages=3):
        super().__init__()
        self.range_description_json = range_description_json
        self.operators_dict = operators_dict
        self.retriever = dspy.Retrieve(num_passages)
        self.variable_name_question_rewriter = dspy.Predict(NameExtractorQuestionRewriter)
        # self.retriever_question_rewriter = dspy.Predict(RetrieverQuestionRewriter)
        self.variable_name_extractor = dspy.Predict(NameExtractor)
        self.extraction = dspy.Predict(SpreadsheetValueExtractor)
        self.question_rewriter = dspy.Predict(FormatCorrectQuestion)
        self.float_question_corrector = dspy.Predict(FloatQuestionCorrector)

    def correct_extracted_variable_name(self, question, extracted_variable_name, max_attempts=3, verbose=False):
        rewritten_var_question=question
        for _ in range(max_attempts):
            if verbose: print('   Extracted Variable Name Failed:   ', rewritten_var_question)
            rewritten_var_question_out = self.variable_name_question_rewriter(question=rewritten_var_question, extracted_variable_name=extracted_variable_name)
            rewritten_var_question = parse_output(rewritten_var_question_out.rephrased_question, 'Rephrased Question')
            extracted_variable_name = self.variable_name_extractor(question=rewritten_var_question)
            parsed_name = parse_output(extracted_variable_name.extracted_variable_name, 'Extracted Variable Name')
            if verbose: print('   Extracted Variable Name Corrected:', rewritten_var_question)
            if verbose: print('   Extracted Variable Name:', parsed_name)
            if is_in_dict(parsed_name, self.operators_dict):
                return parsed_name
        return parsed_name

    def correct_float_question(self, question, parsed_name, data=None, max_attempts=3, verbose=False):
        rewritten_question = question
        for _ in range(max_attempts):
            if verbose: print('   Float Question Failed:   ', rewritten_question)
            rewritten_out = self.float_question_corrector(question=rewritten_question)
            rewritten_question = parse_output(rewritten_out.rephrased_float_question, 'Rephrased Float Question')
            if verbose: print('   Float Question Corrected:', rewritten_question)
            if self.retriever is not None:
                data = self.retriever(query_or_queries=rewritten_question).passages
            extracted_out = self.extraction(variable_name=parsed_name, context=data)
            extracted_value = parse_output(extracted_out.extracted_value, 'Extracted Value')
            parsed_values = extracted_value.split(': ')[-1]
            parsed_values=string_delete(parsed_values, delete_chars=['$', ',', '%'])
            if verbose: print('   Float Parsed Values:', parsed_values)
            if is_float(parsed_values):
                return parsed_values
        return parsed_values

    def correct_format_question(self, question, parsed_name, data=None, max_attempts=3, verbose=False):
        rephrased_format_question = question
        for _ in range(max_attempts):
            if verbose: print('   Format Question Failed:   ', rephrased_format_question)
            rewritten_out = self.question_rewriter(question=rephrased_format_question, format_description=self.range_description_json[parsed_name])
            rephrased_format_question = parse_output(rewritten_out.rephrased_format_question, 'Rephrased Format Question')
            if verbose: print('   Format Question Corrected:', rephrased_format_question)
            if self.retriever is not None:
                data = self.retriever(query_or_queries=rephrased_format_question).passages
            extracted_out = self.extraction(variable_name=parsed_name, context=data)
            extracted_value = parse_output(extracted_out.extracted_value, 'Extracted Value')
            parsed_values = extracted_value.split(': ')[-1]
            parsed_values = string_delete(parsed_values, delete_chars=['$', ',', '%'])
            if verbose: print('   Format Parsed Values:', parsed_values)
            if is_float(parsed_values):
                parsed_values = float(parsed_values)
            else:
                continue
            if is_in_range(parsed_values, bounds=self.operators_dict[parsed_name]['bounds'], ops=self.operators_dict[parsed_name]['operators']):
                return parsed_values
        return parsed_values

    def forward(self, question, verbose=False):
        
        extracted_variable_name = self.variable_name_extractor(question=question)
        parsed_name = parse_output(extracted_variable_name.extracted_variable_name, 'Extracted Variable Name')
        valid_var_name_tf = is_in_dict(parsed_name, self.operators_dict)
        if not valid_var_name_tf:
            parsed_values = self.correct_extracted_variable_name(question, parsed_name, verbose=verbose)

        if self.retriever is not None:
            retriever_question = question
            data = self.retriever(query_or_queries=retriever_question).passages

        extracted_out = self.extraction(variable_name=parsed_name, context=data)
        parsed_values = parse_output(extracted_out.extracted_value, 'Extracted Value')
        # parsed_output = extracted_value.split(': ')
        # parsed_values, parsed_name = parsed_output[-1], parsed_output[0]
        # parsed_values = parsed_output[-1], parsed_output[0]
        # TODO: write helper agent that checks the parsed name against the self.operators_dict
        if parsed_name not in self.operators_dict:
            if verbose: print(f'   Parsed name: {parsed_name} not in operators_dict')
            return dspy.Prediction(answer=f"{parsed_name}: {parsed_values}")
        
        if verbose: print(f'   Parsed Name: {parsed_name}, Parsed Values: {parsed_values}')
        # Safeguard - check if the extracted value can be converted to a float
        valid_float_tf = is_float(parsed_values)
        if not valid_float_tf:
            parsed_values = self.correct_float_question(question,
                                                        verbose=verbose)
            
        # Safeguard - check if the extracted value falls within the expected range
        if parsed_values is not None:
            valid_format_tf = is_in_range(float(parsed_values), 
                                        bounds=self.operators_dict[parsed_name]['bounds'], 
                                        ops=self.operators_dict[parsed_name]['operators'])
            if not valid_format_tf:
                parsed_values = self.correct_format_question(question, 
                                                             parsed_name, 
                                                             verbose=verbose)

        return dspy.Prediction(answer=f"{parsed_name}: {parsed_values}")