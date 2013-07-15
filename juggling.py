import operator

class Circuit:
    def __init__(self, name, events):
        self.name = name
        self.e_levels = self.handle_e_input(events)
        self.chosen_jugglers = []
    
    def handle_e_input(self, info):
        return {event:int(attract_level) for event, attract_level in [s.split(":") for s in info]}

class Juggler:
    def __init__(self, name, abilities, prefs):
        self.name = name
        self.a_levels = [(ability, int(level)) for ability, level in [s.split(":") for s in abilities]]
        self.prefs = prefs.split(",")[::-1] #reversed for pop() use
        self.circuit = None
        self.performance = None

def dot_prod(juggler, circuit): 
    return sum([level*circuit.e_levels[act] for (act,level) in juggler.a_levels])

def process_input(filename):
    '''cuts up the input file into structured data for the objects and returns two lists:
                    one of juggler objects, one of circuit objects'''

    js, cs = [], []
    input_file = open(filename, "r")
    for line in input_file:
        line = line.rstrip()
        if len(line) is 0:
            continue
        line = line.split()
        if line[0] is "C":
            cs.append(Circuit(line[1], line[2:]))
        elif line[0] is "J":
            js.append(Juggler(line[1], line[2:-1], line[-1]))
    input_file.close()
    return js, cs

def assign_by_prefs(js, cs):
    free_jugglers = [j for j in js]
    max_js_per_circuit = len(jugglers) / len(circuits)
    while len(free_jugglers) > 0:
        #add them by first, second... preference
        while len(free_jugglers) > 0:
            juggler = free_jugglers.pop()
            if len(juggler.prefs) > 0:
                top_avail_choice = int(juggler.prefs.pop()[1:])
            else: #brute force those who don't get matched to a preference
                top_avail_choice = 0
                for i in xrange(1, len(cs)):
                    if(len(cs[i].chosen_jugglers) < len(cs[top_avail_choice].chosen_jugglers)):
                        top_avail_choice = i
            
            juggler.performance = dot_prod(juggler, cs[top_avail_choice])
            cs[top_avail_choice].chosen_jugglers.append(juggler)
        #prune the circuits for low performers
        for circuit in cs:
            circuit.chosen_jugglers.sort(key=operator.attrgetter("performance"), reverse=True)
            if len(circuit.chosen_jugglers) > max_js_per_circuit:
                fitted, bad = circuit.chosen_jugglers[0:6], circuit.chosen_jugglers [6:]
                circuit.chosen_jugglers = fitted
                for j in bad:
                    j.assigned_circuit = None
                    free_jugglers.append(j)

def pick_circuit(circuits, choice):
    circuit_of_interest = circuits[choice]
    return sum([int(j.name.strip("J")) for j in circuit_of_interest.chosen_jugglers])

def pretty_write(js, cs):
    output = open("output.txt", 'w')
    for c in cs:
        js = ["%s %s:%i %s:%i %s:%i %s:%i %s:%i %s:%i %s:%i %s:%i %s:%i %s:%i" % (j.name, jugglers[int(j.name.strip("J"))].prefs[0], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[1], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[2], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[3], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[4], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[5], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[6], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[7], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[8], dot_prod(j, c), 
                                                                                        jugglers[int(j.name.strip("J"))].prefs[9], dot_prod(j, c)) for j in c.chosen_jugglers]
        output.write(''.join("%s %s %s %s %s %s %s\n" % (c.name, js[0], js[1], js[2], js[3], js[4], js[5])))
    output.close()

jugglers, circuits = process_input("jugglefest.txt")
assign_by_prefs(jugglers, circuits)
print pick_circuit(circuits, 1970)
jugglers, _ = process_input("jugglefest.txt")
pretty_write(jugglers, circuits)        