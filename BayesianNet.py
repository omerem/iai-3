from _constants import ALL_TIMES, THERE_ARE_PEOPLE, VERTICES, EDGES, PATH, MOST_LIKELY_PATH
from _constants import VERTEX, EDGE, RESET_EVIDENCE, ADD_EVIDENCE, PROB_REASONING, QUIT
from _constants import VERTEX_1_PARENT, VERTEX_2_PARENT, TEMPORAL_PARENT
from _constants import PROB_GIVEN_1_VERTEX
from _constants import PROB_GIVEN_0_VERTICES
from _constants import PROB_GIVEN_PREV_TIME_IS_TRUE
from _constants import PROB_GIVEN_PREV_TIME_IS_FALSE
from _settings import debug_print
from _constants import ROUND
from BayesianNode import BayesianNode
from Graph import Graph


class BayesianNet:
    def __init__(self, graph, persistence):
        self.graph = graph
        self.persistence = persistence
        self.constructNet()

    def probReasoning(self, element_type, args=None, need_to_print=True):
        if element_type == VERTICES:
            vertices_bayes_nodes = (element for element in self.bayesian_nodes if element.type == VERTEX)
            for vertex_bayes_node in vertices_bayes_nodes:
                self.probReasoningVertex(vertex_bayes_node)
        elif element_type == EDGES:
            edges_bayes_nodes = [element for element in self.bayesian_nodes if element.type == EDGE]
            edges_bayes_nodes.sort(key=lambda node: [node.time, node.element.key])
            for edge_bayes_node in edges_bayes_nodes:
                self.probReasoningEdge(edge_bayes_node)
        elif element_type == PATH:
            return self.enumerationAskPath(args, need_to_print)
        else:
            raise Exception("Incompatible type.")

    def probReasoningVertex(self, vertex_bayes_node):
        if vertex_bayes_node.isEvidence():
            prob_for_true = int(vertex_bayes_node.observation)
        else:
            prob_for_true = self.enumerationAsk(vertex_bayes_node)
        vertex_bayes_node.print_vertex_probs(prob_for_true)


    @classmethod
    def enumerate_all(cls, prepared_b_net):
        if not prepared_b_net:
            return 1
        bayesian_node = prepared_b_net[0]
        if bayesian_node.isEvidence():
            rest = BayesianNet.enumerate_all(prepared_b_net[1:])
            prob = bayesian_node.getProbabilityOfEvidenceGivenParents(val=bayesian_node.observation)
            return prob * rest
        sum = 0
        prob_of_false_given_parents = bayesian_node.getProbabilityOfEvidenceGivenParents(False)
        bayesian_node.observation = False
        tmp = BayesianNet.enumerate_all(prepared_b_net[1:])
        tmp2 = round(prob_of_false_given_parents * tmp,ROUND)
        sum+=tmp2
        prob_of_true_given_parents = bayesian_node.getProbabilityOfEvidenceGivenParents(True)
        bayesian_node.observation = True
        tmp = BayesianNet.enumerate_all(prepared_b_net[1:])
        tmp4 = round(prob_of_true_given_parents * tmp, ROUND)
        sum+=tmp4
        bayesian_node.observation = None
        sum = round(sum, ROUND)
        return sum

    def constructNet(self):
        self.bayesian_nodes = []
        for vertex in self.graph.vertices:
            bayes_node = BayesianNode(vertex, time=ALL_TIMES)
            vertex.corresponding_bayesian_node = bayes_node
            self.bayesian_nodes.append(bayes_node)
        for edge in self.graph.edges:
            bayes_node_vertex_1 = edge.vertex1.corresponding_bayesian_node
            bayes_node_vertex_2 = edge.vertex2.corresponding_bayesian_node
            bayes_node_edge_time_0 = BayesianNode(edge, time=0,
                                                  parents={VERTEX_1_PARENT: bayes_node_vertex_1,
                                                           VERTEX_2_PARENT: bayes_node_vertex_2})
            bayes_node_edge_time_1 = BayesianNode(edge, time=1,
                                                  parents={TEMPORAL_PARENT: bayes_node_edge_time_0},
                                                  persistence=self.persistence)
            bayes_node_edge_time_0.children.extend([bayes_node_edge_time_1])
            bayes_node_vertex_1.children.extend([bayes_node_edge_time_0, bayes_node_edge_time_1])
            bayes_node_vertex_2.children.extend([bayes_node_edge_time_0, bayes_node_edge_time_1])
            self.bayesian_nodes.extend([bayes_node_edge_time_0, bayes_node_edge_time_1])
        self.reset_evidences()
        BayesianNet.sortNet(self.bayesian_nodes)

    def reset_evidences(self):
        for bayes_node in self.bayesian_nodes:
            bayes_node.reset_evidence()

    def addEvidence(self, element_type, element_key, observation, evidence_time):
        bayes_node = next(node for node in self.bayesian_nodes
                          if node.element.key == element_key
                          and node.type == element_type
                          and node.time == evidence_time)  # finds the right bayes_node
        bayes_node.commitEvidence(observation)

    def prepareBayesianNetwork(self, objective_nodes):
        prepared = self.bayesian_nodes.copy()
        for i in range(2):
            changed = True
            while changed:
                changed = False
                for bayesian_node in prepared:
                    tmp = bayesian_node in objective_nodes
                    if tmp == False:
                        if bayesian_node.isEvidence() and bayesian_node.isDiverging(prepared):
                            prepared.remove(bayesian_node)
                            changed = True
                            continue
                        if not bayesian_node.isEvidence() and bayesian_node.isConverging(prepared):
                            prepared.remove(bayesian_node)
                            changed = True
                            continue
            prepared.sort(key=lambda element: element.time)
        # prepared.sort(key=lambda element: 0 if element.type == VERTEX else 1)
        return prepared

    def prepareBayesianNetwork1(self, objective_nodes):
        prepared = []
        for bayesian_node in self.bayesian_nodes:
            if not bayesian_node in objective_nodes:
                # if a Bayesian node is not an evidence and it has no children we can delete it.
                if not bayesian_node.isEvidence() and not bayesian_node.children:
                    continue
                # Maybe need to delete the second condition.
                if bayesian_node.isEvidence() and not bayesian_node.parents:
                    continue
            prepared.append(bayesian_node)
        # make a topological order (parents before children)
        prepared.sort(key=lambda element: 0 if element.type == VERTEX else 1)
        return prepared

    def to_print(self):
        for node in self.bayesian_nodes:
            node.to_print()

    @classmethod
    def sortNet(cls, bayesian_nodes):
        # Recall that node.time = ALL_TIMES < 0
        bayesian_nodes.sort(key=lambda node: [node.time, node.element.key])

    def enumerationAskPath(self, args, need_to_print):
        path_keys = args['path_keys']
        time = int(args['time'])
        objective_nodes = self.getBayesianNodesFromEdgesKeys(path_keys, time)
        if not objective_nodes:
            print(BayesianNet.printPathProb(1.0))
            return 1.0
        if any(node.observation == True for node in objective_nodes):
            print(BayesianNet.printPathProb(0.0))
            return 0.0
        # keep only stochastic nodes
        objective_nodes = [b_node for b_node in objective_nodes if b_node.observation == None]
        prepared_b_net = self.prepareBayesianNetwork(objective_nodes)
        for node in objective_nodes:
            node.observation = False
        prob_for_false = self.enumerate_all(prepared_b_net)
        sum_of_probs = prob_for_false
        for bin in range(1, (2 ** len(objective_nodes))):
            BayesianNet.modifyEvidencesBinary(objective_nodes, bin)
            tmp = self.enumerate_all(prepared_b_net)
            sum_of_probs += tmp
        if need_to_print:
            print(BayesianNet.printPathProb(prob_for_false / sum_of_probs))
        for node in objective_nodes:
            node.observation = None
        return prob_for_false / sum_of_probs

    def enumerationAsk(self, bayes_node):
        if bayes_node.observation == True:
            probability_for_true = 1.0
        elif bayes_node.observation == False:
            probability_for_true = 0.0
        else:
            prepared_bayesian_network = self.prepareBayesianNetwork([bayes_node])
            bayes_node.observation = False
            unnormalized_probability_for_false = BayesianNet.enumerate_all(prepared_bayesian_network)
            bayes_node.observation = True
            unnormalized_probability_for_true = BayesianNet.enumerate_all(prepared_bayesian_network)
            bayes_node.observation = None
            probability_for_true = unnormalized_probability_for_true / (unnormalized_probability_for_true + unnormalized_probability_for_false)
        return probability_for_true


    def probReasoningEdge(self, edge_bayes_node):
        if edge_bayes_node.isEvidence():
            prob_for_true = int(edge_bayes_node.observation)
        else:
            prob_for_true = self.enumerationAsk(edge_bayes_node)
        edge_bayes_node.print_edge_probs(prob_for_true)

    @classmethod
    def modifyEvidencesBinary(cls, objective_nodes, bin):
        prev_bin = str("{0:b}".format(bin - 1))
        bin = str("{0:b}".format(bin))
        if len(bin) > len(prev_bin):
            prev_bin = "0" + prev_bin
        bin = bin[::-1]
        prev_bin = prev_bin[::-1]
        change_indices = [i for i in range(len(bin)) if bin[i] != prev_bin[i]]
        print("")
        for i in change_indices:
            objective_nodes[i].observation = not objective_nodes[i].observation

    def getBayesianNodesFromEdgesKeys(self, path_keys, time):
        if len(path_keys) <= 1:
            return []
        key1 = path_keys[0]
        key2 = path_keys[1]
        for node in self.bayesian_nodes:
            if not node.type == EDGE:
                continue
            if node.element.occurs_in_vertices_keys(key1, key2) and node.time == time:
                return [node] + self.getBayesianNodesFromEdgesKeys(path_keys[1:], time)
        raise Exception("There is no edge between {} and {}".format(key1, key2))

    @classmethod
    def printPathProb(cls, prob):
        pr = ""
        pr += "P(path is free) = {}\n".format(round(prob, ROUND))
        pr += "P(path is blocked) = {}".format(round(1 - prob, ROUND))
        return pr

    def getMostLikelyPath(self, vertex_key_1, vertex_key_2, time):
        real_paths = self.graph.getAllPaths(vertex_key_1, vertex_key_2, first_call=True)
        times = [0, 1] if time == ALL_TIMES else [time]
        cur_max = -float('inf')
        # cur_best_path = None
        for time in times:
            for real_path in real_paths:
                tmp = self.probReasoning(PATH, args={'path_keys': Graph.realPathToKeys(real_path), 'time':time} , need_to_print=False)
                if tmp > cur_max:
                    cur_max=tmp
                    cur_best_path = real_path
                    best_time = time
        return {'real_path':cur_best_path,'time':best_time}



        # return max([{'real_path': real_path, 'time': time} for real_path in real_paths for time in times],
        #            key=lambda pair:
        #            self.probReasoning(PATH, args={'path_keys': Graph.realPathToKeys(pair['real_path']),
        #                                           'time': pair['time']},
        #                               need_to_print=False))

    def print_evidences(self):
        evidences = [node for node in self.bayesian_nodes if not node.observation is None]
        if not evidences:
            pr = "There are no evidences,\n"
        else:
            pr = "Evidences are:\n"
            for node in evidences:
                pr+="\t"
                if node.observation == False:
                    pr+= "No "
                if node.type == VERTEX:
                    pr+= "evacuees at vertex {}\n".format(node.element.key)
                else:
                    pr += "evacuees at edge {} at time {}\n".format(node.element.key,node.time)
        print(pr)
