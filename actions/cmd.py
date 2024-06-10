from .action import Action, Param
from subprocess import Popen, PIPE

# create specific functions for some common Command Prompt commands (on cmd)
# these functions will be used as tools for the chatbot
# the chatbot will execute these functions when the user asks for the command
# the user will get the output of the command as a response
# the user can then ask for another command

@Action.action("enter_command_prompt",
                "Enter the Command Prompt. From here, you can run windows commands in order to make directories, list files, or anything else that is possible via command prompt",
                [],
                requried_state="any", change_state="cmd")
def enter_command_prompt():
    return "You have entered the Command Prompt. You can now run Windows commands"

@Action.action("exit_command_prompt",
                "Exit the Command Prompt in order to run other commands.",
                [],
                requried_state="cmd", change_state="none")
def exit_command_prompt():
    return "You have exited the Command Prompt."

@Action.action("list_files",
                "List all the files and directories in the current directory.",
                [],
                requried_state="cmd", change_state="keep")
def list_files():
    return execute_command("dir")

@Action.action("change_directory",
                "Change the current directory to the given directory.  The username of the Windows machine is: '''manna'''" ,
                [Param("directory", "string", "Directory to change to")],
                requried_state="cmd", change_state="keep")
def change_directory(directory):
    return execute_command(f"cd {directory}")

@Action.action("make_directory",
                "Create a directory with the given name in the current directory. The username of the Windows machine is: '''manna'''",
                [Param("directory", "string", "Directory to create")],
                requried_state="cmd", change_state="keep")
def make_directory(directory):
    return execute_command(f"mkdir {directory}")

@Action.action("remove_directory",
                "Remove the directory with the given name in the current directory.",
                [Param("directory", "string", "Directory to remove")],
                requried_state="cmd", change_state="keep")
def remove_directory(directory):
    return execute_command(f"rmdir {directory}")

@Action.action("copy_file",
                "Copy the file with the given name to the given destination.",
                [Param("file", "string", "File to copy"),
                 Param("destination", "string", "Destination to copy the file to")],
                requried_state="cmd", change_state="keep")
def copy_file(file, destination):
    return execute_command(f"copy {file} {destination}")

@Action.action("move_file",
                "Move the file with the given name to the given destination.",
                [Param("file", "string", "File to move"),
                 Param("destination", "string", "Destination to move the file to")],
                requried_state="cmd", change_state="keep")
def move_file(file, destination):
    return execute_command(f"move {file} {destination}")

@Action.action("delete_file",
                "Delete the file with the given name.",
                [Param("file", "string", "File to delete")],
                requried_state="cmd", change_state="keep")
def delete_file(file):
    return execute_command(f"del {file}")

@Action.action("create_file",
                "Create a file with the given name in the current directory.",
                [Param("file", "string", "File to create")],
                requried_state="cmd", change_state="keep")
def create_file(file):
    return execute_command(f"echo. > {file}")

@Action.action("read_file",
                "Read the contents of the file with the given name.",
                [Param("file", "string", "File to read")],
                requried_state="cmd", change_state="keep")
def read_file(file):
    return execute_command(f"type {file}")

@Action.action("write_to_file",
                "Write the given text to the file with the given name.",
                [Param("file", "string", "File to write to"),
                 Param("text", "string", "Text to write to the file")],
                requried_state="cmd", change_state="keep")
def write_to_file(file, text):
    return execute_command(f"echo \"{text}\" > {file}")

@Action.action("find_file",
                "Find the file with the given name in the current directory.",
                [Param("file", "string", "File to find")],
                requried_state="cmd", change_state="keep")
def find_file(file):
    return execute_command(f"dir /s /b {file}")

@Action.action("execute_command", 
                "Execute the given command in the terminal. This is a windows command prompt command. The username of the Windows machine is: '''manna'''", 
                [Param("command", "string", "Command to execute")],
                requried_state="cmd", change_state="keep")
def execute_command(command):
    print("\nExecuting command:\n", command)
    
    stdout, stderr = Popen(command, shell=True, stdout=PIPE, stderr=PIPE).communicate()
    
    cmd_result = f"The result of running the command is:\nSTDOUT:'''{stdout.decode('utf-8')}'''\nSTDERR:'''{stderr.decode('utf-8')}'''"

    print(cmd_result)

    if stderr and not stdout:
        cmd_result+="\nYour command didn't work. Please execute_command a DIFFERENT command in order to try and get the result you want."

    print()
    return cmd_result
