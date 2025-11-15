from langchain_core.prompts import ChatPromptTemplate

from utils.parsers import agent_selector_parser, welcome_parser, history_response_parser, procedure_parser 
from utils.prompts import agent_selector_prompt, welcome_prompt, history_prompt, procedure_selector_prompt

def get_prompt_by_task(task: str):
    if task == "agent_selector":
        parser = agent_selector_parser
        prompt_template = agent_selector_prompt

    elif task == "welcome":
        parser = welcome_parser
        prompt_template = welcome_prompt

    elif task == "procedure":
        parser = procedure_parser
        prompt_template = procedure_selector_prompt

    elif task == "chat_history":
        parser = history_response_parser
        prompt_template = history_prompt

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template + """{format_instructions}"""),
            ("human", "{question}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    return prompt_template, parser
