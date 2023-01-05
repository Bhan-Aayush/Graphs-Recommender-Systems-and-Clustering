
from __future__ import annotations
import csv
from typing import Union

import a3_part2_recommendations


class ReviewScorePredictor:
    """A graph-based entity that predicts scores for book reviews.
    """
    graph: a3_part2_recommendations.WeightedGraph

    def __init__(self, graph: a3_part2_recommendations.WeightedGraph) -> None:
        """Initialize a new ReviewScorePredictor."""
        self.graph = graph

    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score (1-5) that the given user would give the given book.
        """
        raise NotImplementedError


class FiveStarPredictor(ReviewScorePredictor):
    """A book review predictor that always predicts a five-star review,
    ignoring the actual book and user.
    """
    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score that the given user would give the given book.
        """
        if self.graph.adjacent(user, book):
            return self.graph.get_weight(user, book)
        else:
            return 5


class BookAverageScorePredictor(ReviewScorePredictor):
    """A book review predictor that always predicts based on the book's average score,
    ignoring any user preferences.
    """
    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score that the given user would give the given book."""

        if self.graph.adjacent(user, book):
            return self.graph.get_weight(user, book)
        else:
            return round(self.graph.average_weight(book))


class SimilarUserPredictor(ReviewScorePredictor):
    """A book review predictor that makes a prediction based on how similar users rated the book.
    """
    # Private Instance Attributes:
    #   - _score_type: the type of similarity score to use when computing similarity score
    _score_type: str

    def __init__(self, graph: a3_part2_recommendations.WeightedGraph,
                 score_type: str = 'unweighted') -> None:
        """Initialize a new SimilarUserPredictor.
        """
        self._score_type = score_type
        ReviewScorePredictor.__init__(self, graph)

    def predict_review_score(self, user: str, book: str) -> int:
        """Predict the score that the given user would give the given book.
        """
        if self.graph.adjacent(user, book):
            return self.graph.get_weight(user, book)
        else:
            prev_revs = self.graph.get_neighbours(book)
            numerator = sum([self.graph.get_weight(x, book)
                            * self.graph.get_similarity_score(x, user, self._score_type)
                            for x in prev_revs])
            denominator = sum([self.graph.get_similarity_score(x, user, self._score_type)
                               for x in prev_revs])
            if denominator > 0:
                return_val = round(numerator / denominator)
            else:
                return_val = 0

            if return_val == 0:
                return round(self.graph.average_weight(book))
            else:
                return return_val


def evaluate_predictor(predictor: ReviewScorePredictor,
                       test_file: str, book_names_file: str) -> dict[str, Union[int, float]]:
    """Evaluate the given ReviewScorePredictor on the given test file.
    """
    num_reviews = 0
    num_correct = 0
    average_error = 0
    avg_error_list = []

    with open(test_file) as csv_file:
        reader = csv.reader(csv_file)

        for row in reader:
            with open(book_names_file) as csv_file2:
                book_reader = csv.reader(csv_file2)
                book_info = find_book(book_reader, row[1])

            num_reviews += 1
            predicted_score = predictor.predict_review_score(row[0], book_info[1])
            if predicted_score == int(row[2]):
                num_correct += 1
            avg_error_list.append(abs(predicted_score - int(row[2])))

        average_error += sum(avg_error_list) / len(avg_error_list)

    return {
        'num_reviews': num_reviews,
        'num_correct': num_correct,
        'average_error': average_error,
    }


def find_book(book_reader: csv.reader, book_id: str) -> list[str]:
    """Return the book given by the user's review"""

    for row in book_reader:
        if book_id in row:
            return row

    return []

