
"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from logic import * 

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def miniWumpusSearch(problem): 
    """
    A sample pass through the miniWumpus layout. Your solution will not contain 
    just three steps! Optimality is not the concern here.
    """
    from game import Directions
    e = Directions.EAST 
    n = Directions.NORTH
    return  [e, n, n]

def logicBasedSearch(problem):
    """

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())

    print "Does the Wumpus's stench reach my spot?", 
               \ problem.isWumpusClose(problem.getStartState())

    print "Can I sense the chemicals from the pills?", 
               \ problem.isPoisonCapsuleClose(problem.getStartState())

    print "Can I see the glow from the teleporter?", 
               \ problem.isTeleporterClose(problem.getStartState())
    
    (the slash '\\' is used to combine commands spanning through multiple lines - 
    you should remove it if you convert the commands to a single line)
    
    Feel free to create and use as many helper functions as you want.

    A couple of hints: 
        * Use the getSuccessors method, not only when you are looking for states 
        you can transition into. In case you want to resolve if a poisoned pill is 
        at a certain state, it might be easy to check if you can sense the chemicals 
        on all cells surrounding the state. 
        * Memorize information, often and thoroughly. Dictionaries are your friends and 
        states (tuples) can be used as keys.
        * Keep track of the states you visit in order. You do NOT need to remember the
        tranisitions - simply pass the visited states to the 'reconstructPath' method 
        in the search problem. Check logicAgents.py and search.py for implementation.
    """
    # array in order to keep the ordering
    visitedStates = []
    startState = problem.getStartState()
    visitedStates.append(startState)

    """
    ####################################
    ###                              ###
    ###        YOUR CODE HERE        ###
    ###                              ###
    ####################################
    """
    knowledgeBase = dict()
    safeStatesContainer = set()
    safeStates = set()
    notSafeStates = set()
    unsureStates = set()
    currentState = startState
    wumpusLocation = None

    while True:
        print "Visiting", currentState

        if problem.isGoalState(currentState):
            print "Yes, a teleporter!"
            return problem.reconstructPath(visitedStates)
        elif problem.isWumpus(currentState) or problem.isPoisonCapsule(currentState):
            print "Oh no, I'm dead."
            return problem.reconstructPath(visitedStates)

        S = problem.isWumpusClose(currentState)
        C = problem.isPoisonCapsuleClose(currentState)
        G = problem.isTeleporterClose(currentState)
        knowledgeBase.setdefault(currentState, {}).update({'S': S, 'C': C, 'G': G, 'O': True})

        nextStates = [position(state) for state in problem.getSuccessors(currentState)]
        for state in nextStates:
            if (state not in visitedStates) and (state not in notSafeStates):
                knowledgeForState = knowledgeBase.setdefault(state, {})

                print "\n\tState:", state
                clauses = getClauses(nextStates, currentState, knowledgeBase, wumpusLocation)

                W = checkConclusion(knowledgeForState, clauses, state, 'W')
                P = checkConclusion(knowledgeForState, clauses, state, 'P')
                T = checkConclusion(knowledgeForState, clauses, state, 'T')
                O = checkConclusion(knowledgeForState, clauses, state, 'O')

                knowledgeForState.update({'W': W, 'P': P, 'T': T, 'O': O})
                print "\t\tW: ", W, ", P: ", P, ", T: ", T, ", O: ", O

                if T:
                    currentState = state
                    visitedStates.append(currentState)
                    return problem.reconstructPath(visitedStates)
                elif O:
                    if state not in safeStatesContainer:
                        if state in unsureStates:
                            unsureStates.remove(state)
                        safeStatesContainer.add(state)
                        safeStates.add(state)
                elif W:
                    if state in unsureStates:
                        unsureStates.remove(state)
                    notSafeStates.add(state)
                    wumpusLocation = state
                elif P:
                    if state in unsureStates:
                        unsureStates.remove(state)
                    notSafeStates.add(state)
                else:
                    unsureStates.add(state)

        if safeStatesContainer:
            currentState = minStateWeight(list(safeStatesContainer))
            safeStatesContainer.remove(currentState)
        elif unsureStates:
            currentState = minStateWeight(list(unsureStates))
            unsureStates.remove(currentState)
        else:
            print "No place to go!"
            return problem.reconstructPath(visitedStates)

        visitedStates.append(currentState)

def checkConclusion(knowledgeForState, clauses, state, label):
    conclusion = knowledgeForState.get(label, None)

    if conclusion is not None:
        return conclusion
    else:
        conclusion = resolution(clauses, Clause(Literal(label, state, False)))
        if conclusion:
            return conclusion
        # check if it's false or not sure
        elif conclusion != resolution(clauses, Clause(Literal(label, state, True))):
            return conclusion
        else:
            return None


def position(state):
    return state[0]

def direction(state):
    return state[1]

def minStateWeight(states):
    minState = states[0]
    min = stateWeight(states[0])
    for state in states[1:]:
        if stateWeight(state) < min:
            min = stateWeight(state)
            minState = state

    return minState

def getClauses(nextStates, currentState, knowledgeBase, wumpusLocation):
    S = knowledgeBase.setdefault(currentState, {}).get('S', None)
    C = knowledgeBase.setdefault(currentState, {}).get('C', None)
    G = knowledgeBase.setdefault(currentState, {}).get('G', None)

    print "\t\tSensed S: ", S
    print "\t\tSensed C: ", C
    print "\t\tSensed G: ", G

    WClauses = set()
    if S:
        literals = set()
        for state in nextStates:
            W = knowledgeBase.setdefault(state, {}).get('W', None)
            if W is not None:
                WClauses.add(Clause({Literal('W', state, not W)}))
            else:
                if wumpusLocation is not None:
                    WClauses.add(Clause({Literal('W', state, not (state == wumpusLocation))}))
                else:
                    literals.add(Literal('W', state, False))

        WClauses.add(Clause(literals))
    else:
        for state in nextStates:
            WClauses.add(Clause({Literal('W', state, True)}))
            knowledgeBase.setdefault(state, {}).update({'W': False})

    PClauses = set()
    if C:
        literals = set()
        for state in nextStates:
            P = knowledgeBase.setdefault(state, {}).get('P', None)
            if P is not None:
                PClauses.add(Clause({Literal('P', state, not P)}))
            else:
                literals.add(Literal('P', state, False))
        PClauses.add(Clause(literals))
    else:
        for state in nextStates:
            PClauses.add(Clause({Literal('P', state, True)}))
            knowledgeBase.setdefault(state, {}).update({'P': False})

    TClauses = set()
    if G:
        literals = set()
        for state in nextStates:
            literals.add(Literal('T', state, False))
        TClauses.add(Clause(literals))
    else:
        for state in nextStates:
            TClauses.add(Clause({Literal('T', state, True)}))
            knowledgeBase.setdefault(state, {}).update({'T': False})

    OClauses = set()
    if not C and not S:
        for state in nextStates:
            OClauses.add(Clause({Literal('O', state, False)}))
            knowledgeBase.setdefault(state, {}).update({'O': True})

    for state in nextStates:
        W = knowledgeBase.setdefault(state, {}).get('W', None)
        P = knowledgeBase.setdefault(state, {}).get('P', None)

        if W or P:
            OClauses.add(Clause({Literal('O', state, True)}))
            knowledgeBase.setdefault(state, {}).update({'O': False})

        elif (W is not None) and (P is not None) and (not W) and (not P):
            OClauses.add(Clause({Literal('O', state, False)}))
            knowledgeBase.setdefault(state, {}).update({'O': True})

    clauses = WClauses | PClauses | TClauses | OClauses
    print '\t\t', clauses
    return clauses

####################################
###                              ###
###        YOUR CODE THERE       ###
###                              ###
####################################

"""
        ####################################
        ###                              ###
        ###      YOUR CODE EVERYWHERE    ###
        ###                              ###
        ####################################
"""

# Abbreviations
lbs = logicBasedSearch
