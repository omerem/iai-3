from _constants import PROB_OF_VERTEX

class Vertex:
    def __init__(self, key, probability, corresponding_bayesian_node=None):
        self.key = key
        self.probability = probability
        self.corresponding_bayesian_node = corresponding_bayesian_node

    def get_key(self):
        return self.key

    def minimum(vertex1, vertex2):
        if vertex1.key <= vertex2.key:
            return vertex1
        return vertex2

    def maximum (vertex1, vertex2):
        if vertex1.key >= vertex2.key:
            return vertex1
        return vertex2

    @staticmethod
    def get_vertex(vertices, key):
        for vertex in vertices:
            if vertex.key == key:
                return vertex
        print("No vertex found")
        return None

    def is_same_vertex(self, vertex2):
        if self == vertex2: return True
        if self == None and vertex2 != None: return False
        if self != None and vertex2 == None: return False
        if self.key != vertex2.key or self.probability != vertex2.probability:
            return False
        return True

    def to_print(self):
        return "{0}, evac. prob.: {1}".format(self.key, self.corresponding_bayesian_node.probability)
