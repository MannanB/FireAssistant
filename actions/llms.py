from .action import Action, Param
import openai
from subprocess import Popen, PIPE

client = openai.Client()

def ask_gpt(sys_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

@Action.action("task_failed_helper",
                "If you are struggling to complete a task, or the functions/tools you are calling are giving errors or not working as expected, call this tool to get help.",
                [Param("what_task_failed", "string", "What task failed?"),
                 Param("why_did_task_fail", "string", "Why did the task fail / What happened when the task failed?"),
                 Param("what_have_you_tried", "string", "What have you tried so far to fix the issue?")],
                requried_state="any", change_state="keep", return_type=None)
def task_failed_helper(what_task_failed, why_did_task_fail, what_have_you_tried):
    sys_prompt = "Use the provided information to give a detailed explanation of how to solve the issue that is being faced. This is all the info you have. Do not ask for more information."
    user_prompt = f"What task failed? {what_task_failed}\nWhy did the task fail / What happened when the task failed? {why_did_task_fail}\nWhat have you tried so far to fix the issue? {what_have_you_tried}"
    return ask_gpt(sys_prompt, user_prompt)

@Action.action("python_code_writer",
                "Use this to write a python script give the description of what you want the script to do. The python file will be saved in the current directory, and you can run it with the python_code_runner tool.",
                [Param("name", "string", "Name of the python file you want to create"),
                 Param("description", "string", "Description of what you want the script to do")],
                requried_state="none", change_state="keep", return_type=None)
def python_code_writer(name, description):
    sys_prompt = "Use the following information to write a python script. This is all the info you have. Do not ask for more information. Make sure to write the python code well."
    user_prompt = f"Name of the python file you want to create: {name}\nDescription of what you want the script to do: {description}"
    py_code = ask_gpt(sys_prompt, user_prompt)

    if "```" in py_code:
        py_code = py_code.split('```')[1].strip().strip("python")

    if not name.endswith(".py"):
        name += ".py"

    with open(name, "w") as f:
        f.write(py_code)

    return py_code + f"\n\nPython script {name} created successfully. You can now run it with the python_code_runner tool."

@Action.action("python_code_runner",
                "Use this to run a python script. The python script should be in the current directory. STDOUT and STDERR will be returned as the response.",
                [Param("name", "string", "Name of the python file you want to run")],
                requried_state="none", change_state="keep", return_type=None)
def python_code_runner(name):
    if not name.endswith(".py"):
        name += ".py"

    print()
    print(f"Running the python program {name}...")
    stdout, stderr = Popen(f"python {name}", shell=True, stdout=PIPE, stderr=PIPE).communicate()
    
    cmd_result = f"The result of running the python program {name} is:\nSTDOUT:'''{stdout.decode('utf-8')}'''\nSTDERR:'''{stderr.decode('utf-8')}'''"

    print(cmd_result)

    if stderr and not stdout:
        cmd_result+="\nYour python program didn't work. Use python_code_debugger tool to debug it."

    print()
    return cmd_result
               
@Action.action("python_code_debugger",
                "Use this to debug a non-working python script. Ensure that you provide the error message you got when running the python script. The fixed python file will be saved in the current directory, and you can run it with the python_code_runner tool.",
                [Param("name", "string", "Name of the python file you want to debug"),
                 Param("error", "string", "Error message you got when running the python script")],
                requried_state="none", change_state="keep", return_type=None)
def python_code_debugger(name, error):
    if not name.endswith(".py"):
        name += ".py"

    with open(name, "r") as f:
        py_code = f.read()

    sys_prompt = "You want to debug a python script. Please use the following information to do so."
    user_prompt = f"python script: \n'''{py_code}'''\n\nerror msg: '''{error}'''\n Edit the python script to fix the error."

    py_code = ask_gpt(sys_prompt, user_prompt)
    
    if "```" in py_code:
        py_code = py_code.split('```')[1].strip().strip("python")

    with open(name, "w") as f:
        f.write(py_code)

    return py_code + f"\n\nPython script {name} debugged successfully. You can now run it with the python_code_runner tool."
