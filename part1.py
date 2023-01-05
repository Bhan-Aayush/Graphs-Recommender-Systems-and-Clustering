from __future__ import annotations
import csv
from typing import Any


import networkx as nx


class _Vertex:
    """A vertex in a book review graph, used to represent a user or a book."""

    item: Any
    kind: str
    neighbours: set[_Vertex]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'user', 'book'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


    def similarity_score(self, other: _Vertex) -> float:
        """Return the similarity score between this vertex and other.
        """

        if self.degree() == 0 or other.degree() == 0:
            return 0.0
        else:
            return len(self.neighbours & other.neighbours) / len(
                self.neighbours | other.neighbours)


class Graph:
    """A graph used to represent a book review network.
    """

    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph."""

        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph."""

        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.item, kind=v.kind)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.item, kind=u.kind)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx


    def get_similarity_score(self, item1: Any, item2: Any) -> float:
        """Return the similarity score between the two given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 not in self.get_all_vertices() or item2 not in self.get_all_vertices():
            raise ValueError('item1 and/or item2 does not appear as a vertex in the graph.')

        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.similarity_score(v2)



    def recommend_books(self, book: str, limit: int) -> list[str]:
        """Return a list of up to <limit> recommended books based on similarity to the given book. """

        # 1. Generate a list of all the possible books (exclude users & the given book)
        pos_books = [self._vertices[x] for x in self._vertices if self._vertices[x].kind == 'book']
        # 2. Loop to sort books based on sim. score
        for i in range(0, len(pos_books)):
            for j in range(0, len(pos_books)):
                if i > j and pos_books[i].similarity_score(self._vertices[book]) > \
                        pos_books[j].similarity_score(self._vertices[book]):
                    pos_books[i], pos_books[j] = pos_books[j], pos_books[i]
                elif i > j and pos_books[i].similarity_score(self._vertices[book]) == \
                        pos_books[j].similarity_score(self._vertices[book]) and pos_books[i].item \
                        > pos_books[j].item:
                    pos_books[i], pos_books[j] = pos_books[j], pos_books[i]
        # 3. Get rid of any sim. scores that are 0, duplicates (turn into set, and back into list)
        pos_books = [x for x in pos_books if x.similarity_score(self._vertices[book]) != 0]
        # 4. Use lst[:b] to get a list either upto limit OR highest # lower than limit
        if len(pos_books) >= limit:
            pos_books = pos_books[:(limit + 1)]
            # 5. Finally, return list of TITLES of books
            pos_books = [x.item for x in pos_books]

        return pos_books


def load_review_graph(reviews_file: str, book_names_file: str) -> Graph:
    """Return a book review graph corresponding to the given datasets."""

    final_graph = Graph()
    book_id = []
    user_name = []

    with open(reviews_file) as csv_file:
        rev_reader = csv.reader(csv_file)

        for row in rev_reader:
            final_graph.add_vertex(row[0], 'user')
            book_id.append(row[1])
            user_name.append(row[0])

    with open(book_names_file) as csv_file2:
        book_reader = csv.reader(csv_file2)

        for row in book_reader:
            if row[0] in book_id:
                final_graph.add_vertex(row[1], 'book')

                user = user_name[book_id.index(row[0])]
                final_graph.add_edge(user, row[1])

    return final_graph
