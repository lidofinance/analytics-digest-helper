from langchain.chat_models import ChatOpenAI
from langchain.schema import (AIMessage, HumanMessage, SystemMessage)
from .prompts import DIGEST_SYSTEM_PROMPT

def write_thread(formatted_dune_info: dict[str, str]) -> str:
    chat = ChatOpenAI(temperature=0, model="gpt-4") # type: ignore
    dune_info = ""
    for k, v in formatted_dune_info.items():
        dune_info += f"{k}: {v}\n"

    dune_info += "\n\nWrite a thread with the above information. The current date is July 12th. This digest contains information for the week of July 3rd to July 10th."

    digest_user_prompt = HumanMessage(content=dune_info)
    thread = chat.predict_messages([SystemMessage(content=DIGEST_SYSTEM_PROMPT.format(DATE="July 12th 2023")), digest_user_prompt])

    return thread.content
