from Vertex import Vertex
from Edge import Edge
from copy import deepcopy
from _constants import COLOR
from bisect import insort

class Graph:
    def __init__(self, vertices=[], edges=[], to_copy=False, old_graph=None):
        if not to_copy:
            self.vertices = vertices
            self.vertices.sort(key=Vertex.get_key)
            self.edges = edges
            #self.blocked_edges = []
            self.edges.sort(key=Vertex.get_key)
        else:
            self.vertices = deepcopy(old_graph.vertices)
            self.edges = Edge.copyEdges(self.vertices, old_graph.edges)

    def is_same_graph(self, graph2):
        vertices2 = graph2.vertices
        edges2 = graph2.edges
        if len(self.vertices) != len(vertices2): return False
        if len(self.edges) != len(edges2): return False
        for i in range(len(self.vertices)):
            if not Vertex.is_same_vertex(self.vertices[i], vertices2[i]): return False
        for i in range(len(self.edges)):
            if not Edge.is_same_edge(self.edges[i], edges2[i]): return False
        return True

    def has_vertex(self, vertex):
        return vertex in self.vertices

    def are_connected(self, v1, v2):
        for edge in self.edges:
            if edge.occurs_in_vertices_keys(v1, v2):
                return True
            return False

    def to_print(self):
        pr = "Vertices:\n"
        for vertex in self.vertices:
            pr += "\t" + vertex.to_print() + "\n"
        pr += "Edges:\n"
        for edge in self.edges:
            pr += "\t" + edge.to_print() + "\n"
        return pr

    def get_vertex(self, vertex_number):
        for vertex in self.vertices:
            if vertex.key == vertex_number:
                return vertex
        print("No vertex found.")
        return None

    def get_edge(self, edge_number):
        for edge in self.edges:
            if edge.key == edge_number:
                return edge
        raise Exception("No edge found.")

    def find_distance(self, vertex1, vertex2):
        for edge in self.edges:
            if edge.occurs_in_vertices_elements(vertex1, vertex2):
                return edge.weight

    def neighbours_of(self, vertex):
        neighbours = []
        for edge in self.edges:
            if edge.occurs_in_vertex_element(vertex):
                neighbours.append(edge.get_other_end(vertex))
        return neighbours

    def Dijkstra(self, start, end):
        length = len(self.vertices)
        visited = [False] * length
        dist = [float("inf")] * length
        prev = [None] * length
        dist[self.vertices.index(start)] = 0
        while not all(visited):
            v_idx = min([i for i, x in enumerate(visited) if not x], key=dist.__getitem__)

            v = self.vertices[v_idx]
            if v == end:
                break
            if dist[v_idx] == float("inf"):  # there is no path from start to end
                return None
            visited[v_idx] = True
            neighbours = self.neighbours_of(v)
            for neighbour in neighbours:
                neig_idx = self.vertices.index(neighbour)
                if visited[neig_idx]:
                    continue
                alt = dist[v_idx] + self.find_distance(v, neighbour)
                if alt < dist[neig_idx]:
                    dist[neig_idx] = alt
                    prev[neig_idx] = v
        path = [end]
        vertex = end
        while vertex != start:
            ancestor = prev[self.vertices.index(vertex)]
            path = [ancestor] + path
            vertex = ancestor
        return path

    def get_adjacent_edges(self, vertex, blocked_also):
        adjacent_edges = []
        for edge in self.edges:
            if edge.occurs_in_vertex_element(vertex):
                adjacent_edges.append(edge)
        return adjacent_edges

    def getAllPaths(self, vertex1, vertex2, first_call=True):
        if vertex1.__class__ == int:
            vertex1 = self.get_vertex(vertex1)
            vertex2 = self.get_vertex(vertex2)
        if vertex1 == vertex2:
            return [[]]
        paths = []
        adjacent_edges = self.get_adjacent_edges(vertex1, blocked_also = False)
        for edge in adjacent_edges:
            self.edges.remove(edge)
            tmp_paths = self.getAllPaths(edge.get_other_end(vertex1),vertex2, first_call = False)
            self.edges.append(edge)
            if tmp_paths != None:
                for tmp_path in tmp_paths:
                    tmp_path.insert(0, edge)
                paths = paths + tmp_paths

        if first_call:
            self.edges.sort(key=Vertex.get_key)
        return paths

    def print_path(self, path, start_vertex_key):
        prev_vertex = self.get_vertex(start_vertex_key)
        if path[0].get_other_end(prev_vertex) == None:
            path.reverse()
        pr = str(start_vertex_key)
        for edge in path:
            pr += " --> "
            prev_vertex = edge.get_other_end(prev_vertex)
            pr+=str(prev_vertex.key)
        print(COLOR['YELLOW'] +COLOR['BOLD']+pr+COLOR['END'])
        pass

    @classmethod
    def realPathToKeys(cls, real_path):
        if len(real_path) == 1:
            return [real_path[0].vertex1.key, real_path[0].vertex2.key]
        keys_path = [real_path[0].vertex1.key] if real_path[1].occurs_in_vertex_key(real_path[0].vertex2.key) else [real_path[0].vertex2.key]
        for i, edge in enumerate(real_path):
            keys_path.append(edge.get_other_key(keys_path[i]))
        return keys_path

