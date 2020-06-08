import subprocess
import weather_get

class FSM:
    """Finite State Machine.
    First, give states using setState(),
    then, give input data using setState()"""
    def __init__ (self):
        self.states = []
        self.currentState = None

    def setState(self, state, isInit = False):
        """setState(state, isInit = False)
        state : object of the class State
        isInit: True if the state is the initial state."""
        if isInit or self.currentState == None:
            self.currentState = state
        self.states.append(state)
        
    def feed(self, input):
        """feed(input)
        give input"""
        self.currentState = self.currentState.feed(input)
                        
class State:
    """ State class for FSM.
    setTransition: a transition consists of thre params,
        inputs   : If the input is a member of the list, invoke this rule.
        nextState: Next state of this transition rule.
        action   : Do something
    feed: give input"""

    def __init__(self):
        self.rules = []

    def setTransition(self, getfunc, inputs, nextState, action):
        """setTransition(getfunc, inputs, nextState, action)
        getfunc (function): converte function from input to "inputs"
        inputs (list):  a set of conditions to invoke this rule.
        nextState (int): next state.
        action (string/function): execute when this rule is invoked.
            string: call shell
            function: call the function"""
        if not(type(inputs) == type([])):
            raise TypeError("inputs must be list, but:" \
                                        + str(type(inputs)))
        self.rules.append({"input": inputs,
                            "next": nextState,
                            "action": action,
                            "getfunc": getfunc})
    def feed(self, inp):
        for rule in self.rules:
            if rule["getfunc"](inp) in rule["input"]:
                if type(rule["action"]) == type(""):
                    subprocess.call(rule["action"].split())
                elif type(rule["action"] )== type(lambda x:x):
                    rule["action"](inp)
                else:
                    print(type(rule["action"]))
                return rule["next"]
        else:
            weather_get.output("申し訳ありません。もう一度仰ってもらってもいいですか？")
            #raise exceptions.ValueError("No transition rule registered")
            return self

if __name__ == "__main__":
    fsm = FSM()

    st0 = State()
    st1 = State()
    fsm.setState(st0)
    fsm.setState(st1)
    
    st0.setTransition(lambda x:x, ["st1",], st1, "echo goto st1".split())
    st1.setTransition(lambda x:x, ["st0",], st0, "echo goto st0".split())

    
    while 1:
        line = input()
        print("input: ", line)
        fsm.feed(line)
                
