from _constants import VERTEX, EDGE, ALL_TIMES
from _constants import PROB_OF_VERTEX
from _constants import PROB_GIVEN_0_VERTICES
from _constants import PROB_GIVEN_1_VERTEX
from _constants import PROB_GIVEN_2_VERTICES
from _constants import PROB_GIVEN_PREV_TIME_IS_TRUE
from _constants import PROB_GIVEN_PREV_TIME_IS_FALSE
from _constants import TEMPORAL_PARENT, VERTEX_1_PARENT, VERTEX_2_PARENT
from _constants import ROUND
from Vertex import Vertex
from Edge import Edge



class BayesianNode:
    def __init__(self, element, time, persistence=None, parents=False, children=False):
        if not parents:
            self.parents = {}
        else:
            self.parents = parents
        if not children:
            self.children = []
        else:
            self.children = children
        self.element = element
        self.time = time
        if self.element.__class__ == Vertex:
            self.type = VERTEX
        else:
            if self.element.__class__ == Edge:
                self.type = EDGE
            else:
                raise Exception("Incompatible element.")
        self.persistence = persistence
        self.set_probability()
        self.reset_evidence()

    def isEvidence(self):
        return self.observation==True or self.observation==False

    def hasEvacuees(self):
        return self.type == VERTEX and self.probability==1

    def reset_evidence(self):
        if self.probability == 0.0:
            self.observation = False
        elif self.probability == 1.0:
            self.observation = True
        else:
            self.observation = None

    def set_probability(self):
        if self.type == VERTEX:
            self.probability = self.element.probability
            return
        if self.type == EDGE:
            if self.time == 0:
                self.probability = {
                    PROB_GIVEN_0_VERTICES : 0.001,
                    PROB_GIVEN_1_VERTEX : 0.6 / self.element.weight,
                    PROB_GIVEN_2_VERTICES : 1- ((1- (0.6 / self.element.weight))**2)
                }
            else:
                self.probability = {
                    PROB_GIVEN_PREV_TIME_IS_TRUE : self.persistence,
                    PROB_GIVEN_PREV_TIME_IS_FALSE : 0.001
                }
            return
        raise Exception()

    def commitEvidence(self, observation):
        self.observation = observation

    def print_vertex_probs(self, prob):
        key = self.element.key
        print("Vertex {}:".format(key))
        print("\tP(Evacuees {}) = {}".format(key, round(prob, ROUND)))
        print("\tP(not Evacuees {}) = {}\n".format(key, round(1-prob, ROUND)))
        return

    def print_edge_probs(self, prob):
        key = self.element.key
        time = self.time
        print ("Edge {}, time {}:".format(key, time))
        print("\tP(Blockage {}) = {}".format(key, round(prob, ROUND)))
        print("\tP(not Blockage {}) = {}".format(key, round(1-prob, ROUND)))


    def getProbabilityOfEvidenceGivenParents(self, val):
        if self.type == VERTEX:
            prob = self.probability
        else: #self.type == EDGE
            if self.time == 0:
                number_of_activated_vertices = self.numberOfAvtivatedVertices()
                prob = (self.probability[PROB_GIVEN_0_VERTICES] if number_of_activated_vertices==0
                        else self.probability[PROB_GIVEN_1_VERTEX] if number_of_activated_vertices==1
                        else self.probability[PROB_GIVEN_2_VERTICES])
            else: # time>0
                prob = (self.probability[PROB_GIVEN_PREV_TIME_IS_TRUE] if self.edgeBlockPrevTime()
                        else self.probability[PROB_GIVEN_PREV_TIME_IS_FALSE])
        return prob if val else 1-prob

    def numberOfAvtivatedVertices(self):
        return (int(self.parents[VERTEX_1_PARENT].observation)
                + int(self.parents[VERTEX_2_PARENT].observation))

    def edgeBlockPrevTime(self):
        return self.parents[TEMPORAL_PARENT].observation

    def to_print(self):
        if self.type == VERTEX:
            self.print_vertex_probs(self.probability if self.observation is None else int(self.observation))
            return
        else:
            self.printEdgeConditionalProbs()

    def printEdgeConditionalProbs(self):
        time = self.time
        edge_key = self.element.key
        print("Edge {}, time {}".format(edge_key, time))
        if time == 0:
            vertex_1_key = self.element.vertex1.key
            vertex_2_key = self.element.vertex2.key
            print("\tP(Blockage {} | not Evaxuees {}, not Evacuees {}) = {}"
                  .format(edge_key, vertex_1_key, vertex_2_key,
                          round(self.probability[PROB_GIVEN_0_VERTICES], ROUND)))
            print("\tP(Blockage {} | Evaxuees {}, not Evacuees {}) = {}"
                  .format(edge_key, vertex_1_key, vertex_2_key,
                          round(self.probability[PROB_GIVEN_1_VERTEX], ROUND)))
            print("\tP(Blockage {} | not Evaxuees {}, Evacuees {}) = {}"
                  .format(edge_key, vertex_1_key, vertex_2_key,
                          round(self.probability[PROB_GIVEN_1_VERTEX],ROUND)))
            print("\tP(Blockage {} | Evaxuees {}, Evacuees {}) = {}"
                  .format(edge_key, vertex_1_key, vertex_2_key,
                          round(self.probability[PROB_GIVEN_2_VERTICES], ROUND)))
        else:
            print("\tP(Blockage {} | Edge {} is not blocked at time {}) = {}"
                  .format(edge_key, edge_key, time-1,
                          round(self.probability[PROB_GIVEN_PREV_TIME_IS_FALSE], ROUND)))
            print("\tP(Blockage {} | Edge {} is blocked at time {}) = {}"
                  .format(edge_key, edge_key, time-1,
                          round(self.probability[PROB_GIVEN_PREV_TIME_IS_TRUE], ROUND)))

    def isDiverging(self, prepared):
        for parent in list(self.parents.values()):
            if parent in prepared:
                return False
        return True
        # return not set(self.parents).intersection(prepared)

    def isConverging(self, prepared):
        return not set(self.children).intersection(prepared)
    #    return not set(self.children).intersection(prepared)


