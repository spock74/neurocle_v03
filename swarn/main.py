import os
from pydantic import BaseModel
from typing import Optional, Dict
from openai import OpenAI
import json
import inspect


_OPENAI_API_KEY_ = os.getenv("OPENAI_NEUROCURSO_API_KEY")
_OPENAI_ORG_ID_  = ""
_MODEL_ = "gpt-4o-mini"
client = OpenAI(api_key=_OPENAI_API_KEY_)


system_message = (
    "You are a customer support agent for ACME Inc.\n"
    "Always answer in a sentence or less.\n"
    "Follow the following routine with the user:\n"
    "1. First, ask probing questions and understand the user's problem deeper.\n"
    " - unless the user has already provided a reason.\n"
    "2. Propose a fix (make one up).\n"
    "3. ONLY if not satesfied, offer a refund.\n"
    "4. If accepted, search for the ID and then execute refund."
    ""
)


def look_up_item(search_query):
    """Use to find item ID.
    Search query can be a description or keywords."""

    return "item_132612938"


def execute_refund(item_id, reason="not provided"):
    print("summary:", idem_id, reason)
    return "success"


# To execute a routine, let's implement a simple loop that:
# 1. Gets user input.
# 2. Appends user message to messages.
# 3. Calls the model.
# 4. Appends model response to messages.

def run_full_turn(system_message, messages):
    response = client.chat.completions.create(
        model=_MODEL_,
        messages=[
            {"role":"system", "content": system_message}
        ] + messages,
    )
    message = response.choices[0].message
    messages.append(message)
    
    return message


messages = []
while True:
    user = input("User: ")
    messages.append({"role":"user", "content": message.content})
    
    run_full_turn(system_message=system_message, messages=messages)
    
# helper function that turns python functions into the corresponding function schema.
def function_to_schema(func) -> Dict:
    type_map = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",          
        "list": "array",
        "dict": "object",
        "type(None)": "null",
    }
    
    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed t oget signature for the function {func.__name__}: {str(e)}"
        )
    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, string)
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter param.name"
            )
        parameters[param.name] = {"type": param_type}
        
    required = [
        param.name 
        for param in signature.parameters.values()
        if param.default == inspect._empty   
    ]
    
    return {
        "type": "function",
        "function":{
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required
            }
        }
    }
    
# EXEMPLO
def sample_function(param_1,
                    param_2,
                    the_third_one: int, 
                    some_optiona="John Doe"):
    """
    Call this function when you want
    """
    print ("Hello, world!")
    

# Now, we can use this function to pass the tools to the model when we call it.

messages = []
tools = [execute_refund, look_up_item]
tool_schemas = [function_to_schema(tool) for tool in tools]

response = client.chat.completions.create(
    model=_MODEL_,
    messages=[{"role": "user", "content": "look up the black boot"}],
    tools=tool_schemas,
    )

message = response.choices[0].message

message.tool_calls[0].function


# Finally, when the model calls a tool we need to execute the corresponding function and provide the result back to the model.

# We can do this by mapping the name of the tool to the python function in a tool_map, then looking it up in execute_tool_call and calling it. Finally we add the result to the conversation.

tools_map = {tool.__name__: tool for tool in tools}


def execute_tool_call(tools_call, tools_map):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"Assistant": )



import os
from tonic_validate import ValidateMonitorer
monitorer = ValidateMonitorer(api_key=os.getenv("TONIC_VALIDATE_API_KEY"))
monitorer.log(
    project_id="f504f1e5-6d9b-405d-8167-b9f0dbca236d",
    question="What is the capital of France?",
    answer="Paris",
    context_list=["Paris is the capital of france"]
)