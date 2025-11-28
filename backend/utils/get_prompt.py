from langchain_core.prompts import ChatPromptTemplate

from utils.parsers import welcome_parser, history_response_parser, \
    procedure_parser, guardrail_parser, aggregate_response_parser, \
    analysis_parser
from utils.prompts import welcome_prompt, history_prompt, \
    procedure_selector_prompt, guardrail_prompt, aggregate_prompt, \
    analysis_prompt

def get_prompt_by_task(task: str):
    if task == "guardrail":
        parser = guardrail_parser
        prompt_template = guardrail_prompt

    elif task == "analysis":
        parser = analysis_parser
        prompt_template = analysis_prompt

    elif task == "welcome":
        parser = welcome_parser
        prompt_template = welcome_prompt

    elif task == "procedure_select":
        parser = procedure_parser
        prompt_template = procedure_selector_prompt

    elif task == "chat_history":
        parser = history_response_parser
        prompt_template = history_prompt
    
    
    elif task == "aggregate":
        parser = aggregate_response_parser
        prompt_template = aggregate_prompt
    
    else:
        raise ValueError(f"Unknown task: {task}")
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template + """{format_instructions}"""),
            ("human", "{question}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    return prompt_template, parser
