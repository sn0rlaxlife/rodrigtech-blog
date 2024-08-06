import os
import requests
import json
from rich.console import Console
from groq import Groq
from dotenv import load_dotenv
from exa_py import Exa

# Initialize Rich
load_dotenv()


# Exa API
exa = Exa(api_key=os.environ.get("EXA_API_KEY"))

# Rich Initialize
console = Console()

# Define the search function
def search(query: str) -> list:
    """
    Perform a Exa SDK search against the given query

    @param query: Search query
    @return: List of search results

    """
    try:
        result = exa.search_and_contents(
            query=query,
            type="neural",
            include_domains=["arxiv.org", "https://scholar.google.com/"],
            start_published_date="2023-12-31",
            end_published_date="2024-8-05",
            use_autoprompt=True,
            num_results=5,
            text=True,
        )

        output = []

        # Assumes that SearchResponse object has a results attribute this is .results
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
        console.print(f"Error during search: {e}", style="bold red")
        return json.dumps({"error": str(e)})


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Query the user for a search query
query = input("Enter a desired query: ")

# Perform a search
def run_conversation(query):
    # Initial user message that is passed to the API
    messages = [{"role": "user", "content": query}]

    # Define the funciton for the model
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
    # First API call: Ask the model to use the function to search for the query
    chat_completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096,
    )
    
    # Process the model response
    response_message = chat_completion.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {
            "search": search,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions["search"]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                query=function_args.get("query")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        # Print the response
        console.print("Model's Response (LLM)", style="bold red")
        console.print(response_message, style="bold red")

        # Second API call: Pass the response to the model
        final_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            max_tokens=4096,
        )

         # Print the final response
        final = final_response.choices[0].message.content

         # Distinguish the print with a color to understand the function call
        console.print("Final Response:", final, style="bold blue")

        # Validate the function is called 
        console.print("Raw Final Response:", final_response, style="bold yellow")

        # Return the final response is needed otherwise you can comment this out
        # return final
print(run_conversation(query))
