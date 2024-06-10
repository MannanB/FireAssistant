from .action import Action, Param

@Action.action( "stop_function_calling", 
                "Stop calling any function. Call this tool once you have completed the task assigned to you or if there is no task to be done. If there IS a task then call make_plan. If there ISNT a task, then call this", 
                params = [],
                requried_state="any", change_state="none", return_type=None )
def stop_function_calling():
    """
    Stop calling any function. Call this tool once you have completed the task assigned to you.
    :required_state: any
    :change_state: none
    :return: None
    """
    pass
    
