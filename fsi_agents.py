from utils import parse_list_from_output_string
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

class RegulationsExtractionAgent(Event):
    result: str

class FormatCorrectionAgent(Event):
    regs: list
    result: str

class SummarizationAgent(Event):
    summary: str

class SummarizationValidation(Event):
    pass


class SummarizationFlow(Workflow):

    @step.


for i,sec in enumerate(sections):

    rule_prompt = f"""
    Extract all mentions of any regulatory sections, rules, and acts in the following text.
    Compile all extracted items into a single Python List of Strings object.
    For example, ["Item 1", "Item 2", "Item 3"].

    Here is the text:
    {sec}
    """
    response = llm.complete(rule_prompt)

    # List checker
    rewrite_counter=0
    while True:
        try: 
            extracted_reg = parse_list_from_output_string(response.text)
            break
        except:
            print("Correcting list format...")
            response = llm.complete(f"""The following text does not contain a valid Python List of Strings? 
                                        Rewrite the text so that the List is in a valid Python format.
                                        For example, ["Item 1", "Item 2", "Item 3"].\n\n{response.text}
                                    """)
            rewrite_counter+=1
            print(f"   Rewrote list {rewrite_counter} times.")
            if rewrite_counter>5:
                raise ValueError("Could not correct list format.")

    extracted_regs.append(extracted_reg)
    prompt_summary = f"""
    Summarize the content of the following section from a new SEC rule proposal or amendment. Ensure that the summary:

    1. Includes every reference to any specific regulatory section, rule, or act mentioned in the text (e.g., 12 U.S.C. 1843(k)(4)(C), 240.13a-15, Unfunded Mandates Reform Act (section 202(a)), Investment Company Act of 1940).
    2. Stays strictly within the information presented in the text, without incorporating any outside or prior knowledge.
    3. Is detailed, thorough, and specific in its coverage of all key points.
    4. Avoids adding any introductory or concluding remarks outside the scope of the summary itself.

    Here are some of the regulatory sections, rules, and acts:
    {extracted_reg} 
    """
    print(f"Summarizing section {i+1}/{len(sections)}...")
    parser = SentenceSplitter(chunk_size=500, chunk_overlap=20)
    nodes = parser.get_nodes_from_documents([documents_proposal[i]], show_progress=True)
    response = await summarizer.aget_response(prompt_summary, [doc.text for doc in nodes])




class JokeFlow(Workflow):
    llm = OpenAI()

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        return StopEvent(result=str(response))


w = JokeFlow(timeout=60, verbose=False)
result = await w.run(topic="pirates")
print(str(result))


    