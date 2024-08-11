import json
import ast
import os
from groq import Groq, AsyncGroq
from dotenv import load_dotenv
from exa_py import Exa
import chainlit as cl


# Load environment variables
load_dotenv()

# Variables that are needed for Groq and Exa
api_key = os.environ.get("GROQ_API_KEY")


# Async call to Azure OpenAI
client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)
# Initialize Exa Client
exa = Exa(api_key=os.getenv("EXA_API_KEY"))



MAX_ITER = 5

cl.instrument_openai()


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
# Define the search function
def search(query: str) -> list:
    """
    Perform a search using Exa SDK

    @param query: Search query
    @return: List of search results

    """
    try:
        result = exa.search_and_contents(
            query=query,
            type="neural",
            use_autoprompt=True,
            num_results=10,
            text=True,
            include_domains=["arxiv.org", "bing.com"],
            start_published_date="2023-12-31",
            end_published_date="2024-08-11",
    )

        output = []

    # Assumes the searchresponse object has a results attribute
        for item in result.results:
            output.append({
                "title": item.title,
                "link": item.url,
                "snippet": item.text,
                "score": item.score,
                "publish": item.published_date,
            })

        return json.dumps(output)
    except Exception as e:
        print("failed to search for query: ", query)
        return json.dumps({"error": str(e)})        
tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search for any query that is not known or understood by the model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "LLM Security encompasses a variety of approaches that should be considered such as OWASP Top 10 LLMs.",
                        },
                    },
                    "required": ["query"],
                },
            }
        }
    ]


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.step(type="tool")
async def call_tool(tool_call, message_history):
    function_name = tool_call.function.name
    arguments = ast.literal_eval(tool_call.function.arguments)

    current_step = cl.context.current_step
    current_step.name = function_name

    current_step.input = arguments

    function_response = search(
        query=arguments.get("query"),
    )

    current_step.output = function_response
    current_step.language = "json"

    message_history.append(
        {
            "role": "function",
            "name": function_name,
            "content": function_response,
            "tool_call_id": tool_call.id,
        }
    )


async def call_groq(message_history):
    settings = {
        "model": "llama3-8b-8192",
        "messages": message_history,
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 4096,
    }

    response = await client.chat.completions.create(**settings)

    message_completions = response.choices[0].message

    for tool_call in message_completions.tool_calls or []:
        if tool_call.type == "function":
            await call_tool(tool_call, message_history)

    if message_completions.content:
        cl.context.current_step.output = message_completions.content

    elif message_completions.tool_calls:
        completion = message_completions.tool_calls[0].function

        cl.context.current_step.language = "json"
        cl.context.current_step.output = completion

    return message_completions


@cl.on_message
async def run_conversation(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"name": "user", "role": "user", "content": message.content})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        message = await call_groq(message_history)
        if not message.tool_calls:
            await cl.Message(content=message.content, author="Answer").send()
            break

        cur_iter += 1