"""CSP (Constraint Satisfaction Problems) problems and solvers. (Chapter 6)."""
"""Adapted from https://github.com/aimacode/aima-python"""

from utils import argmin_random_tie, count, first
import search

from collections import defaultdict
from functools import reduce

import itertools
import re
import random
import sys, getopt
import logger as lg


class CSP(search.Problem):
    """This class describes finite-domain Constraint Satisfaction Problems.
    A CSP is specified by the following inputs:
        variables   A list of variables; each is atomic (e.g. int or string).
        domains     A dict of {var:[possible_value, ...]} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints.
        constraints A function f(A, a, B, b) that returns true if neighbors
                    A, B satisfy the constraint when they have values A=a, B=b """

    def __init__(self, variables, domains, neighbors, constraints):
        """Construct a CSP problem. If variables is empty, it becomes domains.keys()."""
        variables = variables or list(domains.keys())

        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.initial = ()
        self.curr_domains = None
        self.nassigns = 0


    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""
        # Subclasses may implement this more efficiently
        def conflict(var2):
            return (var2 in assignment and
                    not self.constraints(var, val, var2, assignment))
        return count(conflict(v) for v in self.neighbors[var])

    def display(self, assignment):
        """Show a human-readable representation of the CSP."""
        # Subclasses can print in a prettier way, or display with a GUI
        #print('CSP with assignment:', assignment)
        log.free('CSP with assignment:' + str(assignment))

    def actions2(self, var, assignment):
        domain = []
        if var in assignment:
            #if assignment[var]
            domain.append(assignment[var])
            #print(var, ": Asignado")
        else:
            domain = [val for val in self.domains[var] if (self.nconflicts(var, val, assignment) == 0)]

        return domain


    def goal_test(self, state):
        """The goal is to assign all variables, with all constraints satisfied."""
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(not self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    # These are for constraint propagation

    def support_pruning(self):
        """Make sure we can prune values from domains. (We want to pay
        for this only if we use it.)"""
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """Start accumulating inferences from assuming var=value."""
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        """Rule out var=value."""
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        """Return all values for var that aren't currently ruled out."""
        return (self.curr_domains or self.domains)[var]

    def restore(self, removals):
        """Undo a supposition and all inferences from it."""
        for B, b in removals:
            self.curr_domains[B].append(b)


# ______________________________________________________________________________
# CSP Backtracking Search

# Variable ordering
def first_unassigned_variable(assignment, csp):
    """The default variable order."""
    return first([var for var in csp.variables if var not in assignment])

# Value ordering
def unordered_domain_values(var, assignment, csp):
    """The default value order."""
    return csp.choices(var)

# Inference
def no_inference(csp, var, value, assignment, removals):
    return True

# The search, proper
def backtracking_search(csp,
                        select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values,
                        inference=no_inference):
    bTrack = 0
    #Backtracking
    def backtrack(assignment,Track):

        if len(assignment) == len(csp.variables):
            return assignment
        var = select_unassigned_variable(assignment, csp)

        for value in order_domain_values(var, assignment, csp):
            if 0 == csp.nconflicts(var, value, assignment):
                csp.assign(var, value, assignment)
                #gui.circle_assigment(int(var),value)
                removals = csp.suppose(var, value)
                Track = Track +1
                log.list('Backtrack : ' + str(Track),'.')
                update_domain(csp,assignment)
                if inference(csp, var, value, assignment, removals):
                    #gui.wait()
                    result = backtrack(assignment,Track)
                    if result is not None:
                        return result
                csp.restore(removals)
        csp.unassign(var, assignment)
        #gui.circle_unassigment(int(var))
        #gui.wait()
        return None

    result = backtrack({},bTrack)
    assert result is None or csp.goal_test(result)
    return result

def update_domain(csp, assignment):
    names = {1:'Mike',2:'James',3:'Emily',4:'Tom',5:'Amy'}
    areas = {0:'Farming',1:'Desing',2:'Manufacturing',3:'Packing',4:'Trasportation'}
    assignment_name = {}
    for area,name in assignment.items():
        assignment_name[areas[area]] = names[int(name)]
    csp.display(assignment_name)


    for Xi in csp.variables:
        domain = csp.actions2(Xi,assignment)
        text  = ' '
        for dom in domain:
            text = text + str(names[int(dom)]) +', '
        #print(areas[Xi], '->', text)
        log.free(areas[Xi] +  '->' + text)

#
#-------------------- CSP problem formulation ----------------
#

# Constraint : neigboring nodes cannot have the same color
def different_values_constraint(A, a, B,assignment):
    """A constraint saying two neighboring variables must differ in value."""
    #print("Values",A,a,B,b)
    #return (a != b) and not(a in Restriccion[b])
    b = assignment[B]
    restriccion={'1': ['3','4','5'],
    			 '2': ['1','3','5'],
    			 '3': ['1','2'],
    			 '4': ['1','3','5'],
    			 '5': ['2','4']}
    for id,node in assignment.items():
        if (a == node):
            return 0
    if(a in restriccion[b] and b in restriccion[a]):
        return 1

# Nine variables in the graph, ID of variables: numbers from 0 to 8
variables = list(range(0,5))
# Definition of neighbourhood for each variable
neighbors = {0: [4,1],
			 1: [0,2],
			 2: [1,3],
			 3: [2,4],
			 4: [3,0]}

# Initially, all variables have as domain {red, green, blue} colors
domains = dict.fromkeys(variables, '12345')
#print(domains)
# Construction of the CSP problem
network = CSP(variables, domains, neighbors, different_values_constraint)
log = lg.Logger('outputCSP')
#
#----------------------------------------------------------

#
#- Main program --------
def main(argv):
    #gui.init_gui()
    """Main section"""
    autor = 'Andrea Rey, Jose Lopez'
    head = 'This is a report lab CSP'
    #log = lg.Logger('outputCSP')
    log.header(autor, head)
    log.time('Start algoritm ..... Assignament Areas')
    result = backtracking_search(network)
    log.time('End time')
    log.write(False)
    log.free('All of this had been recorded in {0}'.format(log.filename))
    print(log.get())
    print(type(log.filename))

    #gui.wait()


if __name__ == "__main__":
	main(sys.argv[1:])
