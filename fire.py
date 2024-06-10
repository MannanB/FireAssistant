from actions import action, default, web
import os
import shutil

from llm import LLM, FIREWORKSCLIENT, OPENAICLIENT

from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, OpenAIEngine

with open("./planner.txt", "r") as f:
    PLANNER_PROMPT = f.read()


@action.Action.action("make_plan",
                    "Use this to create an amazing plan to complete the task. It is highly recommended to use this first.",
                    [action.Param("task", "string", required=True)],
                    requried_state="plan", change_state="none")
def make_plan(task):
    plannerLLM = LLM(model="accounts/fireworks/models/llama-v3-70b-instruct",
                          system_prompt="Write an amazing plan to complete the task.",
                          client=FIREWORKSCLIENT,
                          save_history_fp= None)
    return plannerLLM.ask(PLANNER_PROMPT, task=task)
    

class FireAgent:
    def __init__(self, verbose=False):
        self.actions = action.Actions(verbose=verbose)

        self.taskLLM = LLM(model="accounts/fireworks/models/firefunction-v1", 
                       system_prompt="You are a helpful assistant with access to functions. Use them if required.",
                       actions=self.actions, 
                       client=FIREWORKSCLIENT,
                       save_history_fp="./task.json" if verbose else None)
        
        
        self.verbose = verbose

        reset_action_space()

    def execute_task(self, task):
        # self.taskLLM.reset()
        self.actions.state = "plan"

        self.taskLLM.append_history("user", task)

        while 1:
            response, tool_call = self.taskLLM.chat(require_tooling=True)

            assert tool_call, "No tool calls returned"# even though require_tooling is True."

            if tool_call.name == "stop_function_calling":
                if self.verbose:
                    print("Function calling stopped.")
                break

            self.taskLLM.call_action(tool_call)

        response, tool_call = self.taskLLM.chat(require_tooling=False)

        return response
    
def reset_action_space():
    
    if os.path.exists("./agent_action_space"):
        shutil.rmtree("./agent_action_space")
    os.makedirs("./agent_action_space")
    os.chdir("./agent_action_space")

def run_voice():
    agent = FireAgent(verbose=True)

    recorder = AudioToTextRecorder(wake_words="jarvis,computer")

    speaker = TextToAudioStream(OpenAIEngine(voice="fable"))

    print("Waiting on user input...")
    while 1:
        user_input = recorder.text()
        print("User: " + user_input)
        speaker.stop()
        print()
        response = agent.execute_task(user_input)
        print()
        print("Assistant:", response)
        speaker.feed(response)
        speaker.play_async()
        print()

def run_text():
    reset_action_space()
    agent = FireAgent(verbose=True)

    while 1:
        user_input = input("User: ")
        print()
        response = agent.execute_task(user_input)
        print()
        print("Assistant:", response)
        print()

import argparse
if __name__ == "__main__":

    # cmd argument for using text or voice

    parser = argparse.ArgumentParser(description='Fire Agent')
    # add boolean argumetn for voice or not
    parser.add_argument('--voice', action='store_true', help='Use voice input/output')
    args = parser.parse_args() 

    print(f"voice: {args.voice}, cwd: {os.getcwd()}")

    if not args.voice:
        run_text()
    else:
        run_voice()

