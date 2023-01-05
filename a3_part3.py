
import random

from a3_part2_recommendations import WeightedGraph



def create_book_graph(review_graph: WeightedGraph,
                      threshold: float = 0.05,
                      score_type: str = 'unweighted') -> WeightedGraph:
    """Return a book graph based on the given review_graph.
    """
    new_wg = WeightedGraph()
    for x in review_graph.get_all_vertices('book'):
        new_wg.add_vertex(x, 'book')

    for x in new_wg.get_all_vertices():
        for y in new_wg.get_all_vertices():
            if x != y and review_graph.get_similarity_score(x, y, score_type) > threshold:
                new_wg.add_edge(x, y, review_graph.get_similarity_score(x, y, score_type))

    return new_wg


def cross_cluster_weight(book_graph: WeightedGraph, cluster1: set, cluster2: set) -> float:
    """Return the cross-cluster weight between cluster1 and cluster2.
    """
    cluster_sum_list = [book_graph.get_weight(x, y) for x in cluster1 for y in cluster2]
    return sum(cluster_sum_list) / (len(cluster1) * len(cluster2))


def find_clusters_random(graph: WeightedGraph, num_clusters: int) -> list[set]:
    """Return a list of <num_clusters> vertex clusters for the given graph.
    """

    # Each book starts in its own cluster
    clusters = [{book} for book in graph.get_all_vertices()]

    for _ in range(0, len(clusters) - num_clusters):
        print(f'{len(clusters)} clusters')

        c1 = random.choice(clusters)
        # Pick the best cluster to merge c1 into.
        best = -1
        best_c2 = None

        for c2 in clusters:
            if c1 is not c2:
                score = cross_cluster_weight(graph, c1, c2)
                if score > best:
                    best = score
                    best_c2 = c2

        best_c2.update(c1)
        clusters.remove(c1)

    return clusters


def find_clusters_greedy(graph: WeightedGraph, num_clusters: int) -> list[set]:
    """Return a list of <num_clusters> vertex clusters for the given graph.
    """

    # Each book starts in its own cluster
    clusters = [{book} for book in graph.get_all_vertices()]

    for _ in range(0, len(clusters) - num_clusters):
        print(f'{len(clusters)} clusters')

        # Merge the two communities with the most links
        best = -1
        best_c1, best_c2 = None, None

        for i1 in range(0, len(clusters)):
            for i2 in range(i1 + 1, len(clusters)):
                c1, c2 = clusters[i1], clusters[i2]
                score = cross_cluster_weight(graph, c1, c2)
                if score > best:
                    best, best_c1, best_c2 = score, c1, c2

        best_c2.update(best_c1)
        clusters.remove(best_c1)

    return clusters


