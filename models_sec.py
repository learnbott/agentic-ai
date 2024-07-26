import dspy


class GenerateAnswer(dspy.Signature):
    """Answer questions with a summary of them most relevant facts in the context."""

    context = dspy.InputField(desc="contains rules and regulations that can be considered facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="cite any rule or regulation codes (e.g. § 230.503, Rule 501(a)) from context that support the answer")
    # answer = dspy.OutputField()

class SECQnA(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        # self.generate_answer = dspy.ReAct(GenerateAnswer, num_results=num_passages)
    
    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)

class ReActGenerateAnswer(dspy.Signature):
    """Answer questions with a summary of them most relevant facts."""

    question = dspy.InputField()
    answer = dspy.OutputField()

class SECQnAReAct(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.generate_answer = dspy.ReAct(ReActGenerateAnswer, num_results=num_passages)
    
    def forward(self, question):
        prediction = self.generate_answer(question=question)
        return dspy.Prediction(answer=prediction.answer)