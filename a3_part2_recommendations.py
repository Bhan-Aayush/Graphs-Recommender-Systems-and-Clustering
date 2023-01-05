
from __future__ import annotations
import csv
from typing import Any, Union

from a3_part1 import Graph


class _WeightedVertex:
    """A vertex in a weighted book review graph, used to represent a user or a book.
    """
    item: Any
    kind: str
    neighbours: dict[_WeightedVertex, Union[int, float]]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.
        """
        self.item = item
        self.kind = kind
        self.neighbours = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


    def similarity_score_unweighted(self, other: _WeightedVertex) -> float:
        """Return the unweighted similarity score between this vertex and other.
        """
        if self.degree() == 0 or other.degree() == 0:
            return 0.0
        else:
            n = set(self.neighbours)
            o = set(other.neighbours)
            return len(n & o) / len(n | o)

    def similarity_score_strict(self, other: _WeightedVertex) -> float:
        """Return the strict weighted similarity score between this vertex and other.

        """
        if self.degree() == 0 or other.degree() == 0:
            return 0.0
        else:
            n = set(self.neighbours)
            o = set(other.neighbours)
            no = n & o
            return len({z for z in no if z.neighbours[self] == z.neighbours[other]}) / len(n | o)


class WeightedGraph(Graph):
    """A weighted graph used to represent a book review network that keeps track of review scores.

    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _WeightedVertex object.
    _vertices: dict[Any, _WeightedVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

        # This call isn't necessary, except to satisfy PythonTA.
        Graph.__init__(self)

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, kind)

    def add_edge(self, item1: Any, item2: Any, weight: Union[int, float] = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_weight(self, item1: Any, item2: Any) -> Union[int, float]:
        """Return the weight of the edge between the given items.

        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def average_weight(self, item: Any) -> float:
        """Return the average weight of the edges adjacent to the vertex corresponding to item.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return sum(v.neighbours.values()) / len(v.neighbours)
        else:
            raise ValueError


    def get_similarity_score(self, item1: Any, item2: Any,
                             score_type: str = 'unweighted') -> float:
        """Return the similarity score between the two given items in this graph.
        """
        if item1 not in self.get_all_vertices() or item2 not in self.get_all_vertices():
            raise ValueError('item1 and/or item2 does not appear as a vertex in the graph.')

        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        if score_type == 'unweighted':
            return v1.similarity_score_unweighted(v2)
        else:
            return v1.similarity_score_strict(v2)

    def recommend_books(self, book: str, limit: int,
                        score_type: str = 'unweighted') -> list[str]:
        """Return a list of up to <limit> recommended books based on similarity to the given book.
        """

        # 1. Generate a list of all the possible books (exclude users & the given book)
        pos_books = [self._vertices[x] for x in self._vertices if self._vertices[x].kind == 'book']

        if score_type == 'unweighted':
            # 2. Loop to sort books based on sim. score
            for i in range(0, len(pos_books)):
                for j in range(0, len(pos_books)):
                    if i > j and pos_books[i].similarity_score_unweighted(self._vertices[book]) > \
                            pos_books[j].similarity_score_unweighted(self._vertices[book]):
                        pos_books[i], pos_books[j] = pos_books[j], pos_books[i]
                    elif i > j and pos_books[i].similarity_score_unweighted(self._vertices[book]) \
                            == pos_books[j].similarity_score_unweighted(self._vertices[book]) \
                            and pos_books[
                        i].item \
                            > pos_books[j].item:
                        pos_books[i], pos_books[j] = pos_books[j], pos_books[i]
            # 3. Get rid of sim. scores that are 0, duplicates (turn into set, and back into list)
            pos_books = [x for x in pos_books
                         if x.similarity_score_unweighted(self._vertices[book]) != 0]
        else:
            # 2. Loop to sort books based on sim. score
            for i in range(0, len(pos_books)):
                for j in range(0, len(pos_books)):
                    if i > j and pos_books[i].similarity_score_strict(self._vertices[book]) > \
                            pos_books[j].similarity_score_strict(self._vertices[book]):
                        pos_books[i], pos_books[j] = pos_books[j], pos_books[i]
                    elif i > j and pos_books[i].similarity_score_strict(self._vertices[book]) == \
                            pos_books[j].similarity_score_strict(self._vertices[book]) \
                            and pos_books[i].item > pos_books[j].item:
                        pos_books[i], pos_books[j] = pos_books[j], pos_books[i]
            # 3. Get rid of sim. scores that are 0, duplicates (turn into set, and back into list)
            pos_books = [x for x in pos_books
                         if x.similarity_score_strict(self._vertices[book]) != 0]

        # 4. Use lst[:b] to get a list either upto limit OR highest # lower than limit
        if len(pos_books) >= limit:
            pos_books = pos_books[:(limit + 1)]
            # 5. Finally, return list of TITLES of books
            pos_books = [x.item for x in pos_books]

        return pos_books


def load_weighted_review_graph(reviews_file: str, book_names_file: str) -> WeightedGraph:
    """Return a book review WEIGHTED graph corresponding to the given datasets."""

    final_graph = WeightedGraph()
    book_id = []
    user_name = []
    review = []
    book_user_dict = {}

    with open(reviews_file) as csv_file:
        rev_reader = csv.reader(csv_file)

        for row in rev_reader:
            final_graph.add_vertex(row[0], 'user')
            book_id.append(row[1])
            user_name.append(row[0])
            review.append(row[2])

    with open(book_names_file) as csv_file2:
        book_reader = csv.reader(csv_file2)

        for row in book_reader:
            if row[0] in book_id:
                final_graph.add_vertex(row[1], 'book')
                book_user_dict[row[0]] = row[1]

    for i in range(0, len(book_id)):
        user = user_name[i]
        book_name = book_user_dict[book_id[i]]
        rev = review[i]
        final_graph.add_edge(user, book_name, int(rev))

    return final_graph

