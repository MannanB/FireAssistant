
# required_state: "any" acts as anything
# change_state: "none" acts as nothing, "keep" keeps the state the same

class Param:
    def __init__(self, name, dtype, description=None, enum=None, enum_supplier=None, required=True):
        self.name = name
        self.dtype = dtype
        self.description = description
        self.required = required

        self.enum = enum
        self.enum_supplier = enum_supplier # for reactive enums

    def to_dict(self):
        param_dict = {}

        param_dict.update({"type": self.dtype})
        
        if self.description:
            param_dict.update({"description": self.description})

        if self.enum:
            param_dict.update({"enum": self.enum})
        elif self.enum_supplier:
            param_dict.update({"enum": self.enum_supplier()})

        return {self.name: param_dict}


class Action:
    actions = []

    def __init__(self, func, name, description, params, requried_state="any", change_state="keep", return_type=None):
        self.func = func
        self.name = name
        self.description = description
        self.params = params
        self.requried_states = requried_state.split()
        self.change_state = change_state
        self.return_type = return_type

    def to_dict(self):
        props = {}
        required = []

        for param in self.params:
            props.update(param.to_dict())
            if param.required:
                required.append(param.name)

        return {"type": "function",
                "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required
                }
            }
        }
    
    def can_execute(self, state):
        return state in self.requried_states or "any" in self.requried_states

    def __call__(self, **kwargs):
        return self.func(**kwargs)
    
    @classmethod
    def action(cls, name, description, params, requried_state="any", change_state="keep", return_type=None):
        def decorator(func):
            cls.actions.append(Action(func, name, description, params, requried_state, change_state, return_type))
            return func
        return decorator

class Actions:
    def __init__(self, verbose=False):
        self.state = "none"
        self.verbose = verbose
        self.tools = []

    def load_actions(self):
        self.tools = []
        for action in Action.actions:
            if action.can_execute(self.state):
                self.tools.append(action.to_dict())

    def get_tools(self):
        self.load_actions()
        return self.tools
    
    def execute_action(self, action_name, **kwargs):
        for action in Action.actions:
            if action.name == action_name:
                if self.verbose:
                    print(f"Executing function: {action_name} with parameters: {kwargs}")
                    print(f"Current state changed from {self.state} to {action.change_state}.")

                if action.change_state != "keep":
                    self.state = action.change_state

                return action(**kwargs)

    