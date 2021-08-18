from Graph import Graph
from Vertex import Vertex
from Edge import Edge
import _settings
#from Action import Action, TRAVERSE, TERMINATE, NO_OP, BLOCK
from BayesianNet import BayesianNet
#from GameTreeNode import STRATEGY_1, STRATEGY_2, STRATEGY_3
#from GameTree import GameTree
# from Agent import Agent
#from GameTreeNode import GameTreeNode
#from GameTree import GameTree
from _constants import COLOR
from _constants import THERE_ARE_PEOPLE, VERTICES, EDGES, PATH, MOST_LIKELY_PATH
from _constants import VERTEX, EDGE, RESET_EVIDENCE, ADD_EVIDENCE, PROB_REASONING
from _constants import QUIT, SHOW_GRAPH, SHOW_BAYES_NET, MENU
from _constants import ALL_TIMES, EVIDENCES
from _settings import debug_print


def _setInputFunction(func):
    global input
    input = func

class HurricaneEnv:
    def __init__(self, graph_input_file_name):
        self.number_of_vertices = None
        #self.evidences = {VERTICES: [], EDGES: []}
        self.read_graph_from_file(graph_input_file_name)

    def read_graph_from_file(self, file_name):
        file = open(file_name, "r")
        vertices = []
        edges = []
        for line in file:
            words = line.split()
            if not words:  # if the list is empty
                continue
            first_word = words[0]
            if first_word[0] == ';':
                continue
            if first_word[1] == 'N':
                self.number_of_vertices = int(words[1])
                continue
            if first_word[1] == 'D':
                self.deadline = float(words[1])
                continue
            if first_word[1] == 'V':
                key = int(first_word[2:])
                if len(words) <= 2:
                    evac_prob = 0.0
                else:
                    third_word = words[2]
                    evac_prob = float(third_word)
                vertex = Vertex(key, evac_prob)
                vertices.append(vertex)
                continue
            if first_word[1] == 'E':
                key = int(first_word[2:])
                second_word = words[1]
                third_word = words[2]
                fourth_word = words[3][1:]
                vertex1 = Vertex.get_vertex(vertices, int(second_word))
                vertex2 = Vertex.get_vertex(vertices, int(third_word))
                weight = int(fourth_word)
                edge = Edge(vertex1, vertex2, weight, key)
                edges.append(edge)
            if first_word[1] == 'P':
                second_word = words[1]
                persistence = float(second_word)
        self.graph = Graph(vertices, edges)
        self.bayes_net = BayesianNet(self.graph, persistence)

    def run_env(self):
        while True:
            user_action, args = self.getUserAction()
            if user_action == QUIT:
                return
            self.commitAction(user_action, args)

    def commitAction(self, user_action, args):
        if user_action == SHOW_GRAPH:
            print(self.to_print())
            return
        if user_action == SHOW_BAYES_NET:
            self.bayes_net.to_print()
            return
        if user_action == MENU:
            HurricaneEnv.print_types_of_probabilistic_reasonings()
            return
        if user_action == RESET_EVIDENCE:
            self.bayes_net.reset_evidences()
            return
        if user_action == ADD_EVIDENCE:
            element_type = args.get('element_type')
            element_key = args.get('element_key')
            observation = args.get('observation')
            self.bayes_net.addEvidence(element_type,
                                       element_key,
                                       observation,
                                       evidence_time=args.get('evidence_time') if element_type == EDGE else ALL_TIMES)
            return
        if user_action == PROB_REASONING:
            probabilistic_reasoning_type = args.get('probabilistic_reasoning_type')
            if probabilistic_reasoning_type == VERTICES:
                self.bayes_net.probReasoning(VERTICES)
            if probabilistic_reasoning_type == EDGES:
                self.bayes_net.probReasoning(EDGES)
            if probabilistic_reasoning_type == PATH:
                self.bayes_net.probReasoning(PATH, args)
            if probabilistic_reasoning_type == MOST_LIKELY_PATH:
                vertex_key_1 = args.get('vertex_key_1')
                vertex_key_2 = args.get('vertex_key_2')
                time = args.get('time')
                values = self.bayes_net.getMostLikelyPath(vertex_key_1, vertex_key_2, time)
                real_path = values['real_path']
                time = values['time']
                if not real_path:
                    print(COLOR['GREEN']+COLOR['BOLD']+"There isn't a valid path."+COLOR['END'])
                else:
                    print("The most likely path is:")
                    print('The time for the path is: '+COLOR['BOLD']+COLOR['BLUE']+str(time)+COLOR['END'])
                    self.graph.print_path(real_path, start_vertex_key = vertex_key_1)
            return
        raise Exception("Incorrect user_action.")

    @staticmethod
    def yesNoToBool(ch):
        if ch == 'Y' or ch == 'y':
            return True
        if ch == 'N' or ch == 'n':
            return False
        raise Exception("Input must be 'Y' or 'N'.")

    @staticmethod
    def print_types_of_probabilistic_reasonings():
        print("Options of the simulator:")
        print("1. Reset evidence list empty,\n"
              "2. Add an evidence,\n"
              "3. do a Probabilistic reasoning:\n"
              "\t3.1. What is the probability that each of the vertices contains evacuees?\n"
              "\t3.2. What is the probability that each of the edges is blocked?\n"
              "\t3.3. What is the probability that a certain path (set of edges) is free from"
              "blockages? (Note that the distributions of blockages in edges are NOT"
              "necessarily independent given the evidence.)\n"
              "\t3.4. What is the path between 2 given vertices that has the highest"
              "probability of being free from blockages at time t=1 given the evidence?\n"
              "4. Quit\n"
              "5. show Graph\n"
              "6. show CPT\n"
              "7. show Menu\n"
              )

    def getUserAction(self):
        bolding = COLOR['UNDERLINE']+COLOR['BOLD']
        print("What action to commit?\n"
              +bolding+"R"+COLOR['END']+"eset/"
              +bolding+"A"+COLOR['END']+"dd/"
              +bolding+"P"+COLOR['END']+"robabilistic/"
              +bolding+"Q"+COLOR['END']+"uit"
              +", "
              +bolding+"G"+COLOR['END']+"raph/"
              +"Bayesian-"+bolding+"N"+COLOR['END']+"etwork (CPT)/"
              +bolding+"M"+COLOR['END']+"enu"
              +"\t")

        choice = {
            '1' : RESET_EVIDENCE,
            'R' : RESET_EVIDENCE,
            'r' : RESET_EVIDENCE,
            '2': ADD_EVIDENCE,
            'A': ADD_EVIDENCE,
            'a': ADD_EVIDENCE,
            '3': PROB_REASONING,
            'P': PROB_REASONING,
            'p': PROB_REASONING,
            '4': QUIT,
            'Q': QUIT,
            'q': QUIT,
            '5': SHOW_GRAPH,
            'G': SHOW_GRAPH,
            'g': SHOW_GRAPH,
            '6': SHOW_BAYES_NET,
            'N': SHOW_BAYES_NET,
            'n': SHOW_BAYES_NET,
            '8': MENU,
            'M': MENU,
            'm': MENU,
        }.get(input())

        if (choice == RESET_EVIDENCE or choice == QUIT
                or choice == SHOW_GRAPH or choice == SHOW_BAYES_NET
                or choice == MENU or choice == EVIDENCES):
            return choice, None

        if choice == ADD_EVIDENCE:
            element_type = input("Is the evidence a Vertex or an Edge? ('V'/'E')\t")
            if element_type == 'V' or element_type == 'v':
                element_type = VERTEX
                element_key = int(input("What is the vertex's number?\t"))
                observation = self.yesNoToBool(input("Are there people there? (Y/N)\t"))
                return choice, {'element_type': element_type,
                                'element_key': element_key,
                                'observation': observation}
            if element_type == 'E' or element_type == 'e':
                element_type = EDGE
                element_key = int(input("What is the edge's number?\t"))
                evidence_time = int(input("What is the time of the observation? (0/1)\t"))
                observation = self.yesNoToBool(input("Is the edge blocked? (Y/N)\t"))
                return choice, {'element_type': element_type,
                                'element_key': element_key,
                                'evidence_time': evidence_time,
                                'observation': observation}
            raise Exception("Evidence must be 'V' or 'E'")

        if choice == PROB_REASONING:
            probabilistic_reasoning_type = {
                1: VERTICES,
                2: EDGES,
                3: PATH,
                4: MOST_LIKELY_PATH
            }.get(int(input("What type of probabilistic reasoning\n(1: vertices, 2: edges, 3: path, 4: most likely path)?\n")))

            if probabilistic_reasoning_type == VERTICES or probabilistic_reasoning_type == EDGES:
                return choice, {'probabilistic_reasoning_type':probabilistic_reasoning_type}
            if probabilistic_reasoning_type == PATH:
                path_keys = []
                print("Enter vertices numbers with new lines between keys. To end enter 'E' or 'e'\t")
                key_number = input()
                while key_number != 'E' and key_number != 'e':
                    key_number = int(key_number)
                    path_keys.append(key_number)
                    key_number = input()
                time = input("What time? (0/1)\t")
                return choice, {'probabilistic_reasoning_type':probabilistic_reasoning_type,
                                'path_keys':path_keys,
                                'time':time}
            if probabilistic_reasoning_type == MOST_LIKELY_PATH:
                vertex_key_1 = int(input("What's the key of the first vertex?\t"))
                vertex_key_2 = int(input("What's the key of the second vertex?\t"))
                time = int(input("What time to calculate the path? (0, 1, ALL_TIMES: -1)\t"))
                return choice, {'probabilistic_reasoning_type':probabilistic_reasoning_type,
                                'vertex_key_1':vertex_key_1,
                                'vertex_key_2':vertex_key_2,
                                'time': time}

        raise Exception("No such choice")


    def to_print(self, include_graph=True):
        color_name=['GREEN', 'YELLOW']
        turn_of_color = 'PURPLE'
        pr = ""
        # if self.epoch == 0:
        #     pr = "ENV STATE: EPOCH 0 (initial state)____________\n"
        # else:
        #     pr = "ENV STATE: EPOCH {} ___________________________\n".format(str(self.epoch))
        # pr += "\tdeadline:\t" + str(self.deadline) + "\n"
        if include_graph:
            pr += "\tgraph:\n"
            graph_str = self.graph.to_print()
            # if self.epoch == 0:
            #     graph_str = self.graph.to_print(with_unblocked_edges=True)
            # else:
            #     graph_str = self.graph.to_print(with_unblocked_edges=False)
            lines = graph_str.splitlines()
            for i, line in enumerate(lines):
                pr += "\t\t" + line + "\n"
        # pr += "\tTotal number people rescued: {}\n".format(self.total_rescued)
        # pr += "\tAgents:\n"
        # for i, agent in enumerate(self.agents):
        #     agent_str = agent.to_print(color_name[i])
        #     lines = agent_str.splitlines()
        #     if i==0:
        #         pr += COLOR[color_name[i]]+COLOR['BOLD']+"\t\t Agent A\n"+COLOR['END']
        #     if i==1:
        #         pr += COLOR[color_name[i]]+COLOR['BOLD']+"\t\t Agent B\n"+COLOR['END']
        #     for i, line in enumerate(lines):
        #         pr += "\t\t\t" + line + "\n"
        # pr += COLOR['BOLD']+"__________________________________________________"+COLOR['END']
        return pr













