import openai, json

FIREWORKS_API_KEY = "AAMvd8qyhKGAC3Z0nytjyGVzIQAE72m1n4AaFGWESA4PyjNJ"

fireworksClient = openai.OpenAI(
    base_url = "https://api.fireworks.ai/inference/v1",
    api_key = "AAMvd8qyhKGAC3Z0nytjyGVzIQAE72m1n4AaFGWESA4PyjNJ"
)
openAIClient = openai.Client()

FIREWORKSCLIENT = "fireworks"
OPENAICLIENT = "openai"

class LLM:
    def __init__(self, model, system_prompt=None, actions=None, client=FIREWORKSCLIENT, save_history_fp=None):
        if client == FIREWORKSCLIENT:
            self.client = fireworksClient
        else:
            self.client = openAIClient

        self.model = model
        self.actions = actions

        self.history = []
        self.save_history_fp = save_history_fp

        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = "You are a helpful assistant. Answer questions concisely and follow directions exactly."

        self.history.append({"role": "system", "content": self.system_prompt})

    def save_history(self): 
        if self.save_history_fp:
            with open(self.save_history_fp, "w") as f:
                json.dump(self.history, f, indent=4)
                
    def reset(self):
        self.history = []
        self.history.append({"role": "system", "content": self.system_prompt})

    def append_history(self, role, content):
        self.history.append({"role": role, "content": content})
        self.save_history()

    def call_api(self, messages, require_tooling=False, stream=False):
        if require_tooling:
            response = self.client.chat.completions.create(
                model=self.model,
                tools=self.actions.get_tools(),
                tool_choice={"type": "function"},
                messages=messages,
                stream=stream
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream
            )
        return response

    def ask(self, prompt, require_tooling=False, **kwargs):
        for key, value in kwargs.items():
            print(f"replacing {{{key}}} with {value} in prompt.")
            prompt = prompt.replace(f"{{{key}}}", value)    
        return self.call_api([{"role": "system", "content": self.system_prompt}, {"role": "user", "content": prompt}], require_tooling).choices[0].message.content

    def chat(self, prompt=None, require_tooling=False):
        if prompt: # if you want to re-call after a tool call
            self.history.append({"role": "user", "content": prompt})
        response = self.call_api(self.history, require_tooling)
        if response.choices[0].message.tool_calls:
            self.history.append({"role": "assistant", "content": "", "tool_calls": [tool_call.model_dump() for tool_call in response.choices[0].message.tool_calls]})
            self.save_history()
            return None, response.choices[0].message.tool_calls[0].function
        else:
            self.history.append({"role": "assistant", "content": response.choices[0].message.content})
            self.save_history()
            return response.choices[0].message.content, None
        
    def call_action(self, tool_call):
        tool_response = self.actions.execute_action(tool_call.name, **json.loads(tool_call.arguments))

        if not tool_response:
            tool_response = "Function executed successfully."

        self.history.append({"role": "tool", "content": tool_response})
        self.save_history()