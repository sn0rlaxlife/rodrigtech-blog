import os
from openai import AzureOpenAI
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

endpoint = os.environ.get('AZURE_ENDPOINT')
api_key = os.environ.get('AZURE_OPENAI_API_KEY')
deployment_name = os.environ.get('DEPLOYMENT_NAME')
api_version = os.environ.get('API_VERSION')

# Define a class for the Azure OpenAI client
class ModelRouterAgent:
    def __init__(self, system_prompt):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )
        self.system_prompt = system_prompt
    # Define a method to send a message to the model
    def run(self, user_prompt):
        response = self.client.chat.completions.create(
            #stream=True, # Enable streaming responses this won't allow model router to display the model
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8192,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=self.deployment_name,
        )
        output = response.choices[0].message.content
       # output = ""
       # for update in response: # Streaming response
       #     if update.choices:
       #         output += update.choices[0].delta.content or ""
        # Print or return the model used
        print("Model chosen by the router:", response.model)
        return output, response.model
# Initialize the ModelRouterAgent with the system message
    def close(self):
        self.client.close()

if __name__ == "__main__":
    agent1 = ModelRouterAgent("You are a senior engineer focused on cloud security posture management (CSPM). You've received a response from a Kubernetes cluster that the privileges of a ServiceAccount is permissive with automountServiceAccountToken active on a production pod application. Please summarize the main security risks in this CSPM report.")
    agent2 = ModelRouterAgent("You are a security analyst focused on compliance and risk mitigation. Understanding the context of blast radius of this finding propose a solution to find this in code")

    prompt = "Summarize the main security risks in this CSPM report."

    print("Agent 1 response:")
    agent1_response,agent1_model = agent1.run(prompt)
    print(agent1_response)
    print("Model chosen by the router:", agent1_model)

    print("\nAgent 2 response: (using Agent 1's output):")
    agent2_response, agent2_model = agent2.run(agent1_response)
    print(agent2_response)
    print("Model chosen by the router:", agent2_model)

    agent1.close()
    agent2.close()
