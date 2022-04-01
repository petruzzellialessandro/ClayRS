import abc
from typing import Dict, List, Set

from orange_cb_recsys.content_analyzer.ratings_manager.ratings import Interaction
from orange_cb_recsys.recsys.algorithm import Algorithm

from orange_cb_recsys.recsys.graphs.graph import UserNode, Node, Graph, ItemNode, \
    BipartiteDiGraph

import pandas as pd


class GraphBasedAlgorithm(Algorithm):
    """
    Abstract class for the graph-based algorithms

    Args:
    feature_selection (FeatureSelectionAlgorithm): a FeatureSelectionAlgorithm algorithm if the graph needs to be
        reduced
    """

    def __init__(self):
        # this can be expanded in making the page rank keeping also PropertyNodes, etc.
        self._nodes_to_keep = {ItemNode}

    def filter_result(self, graph: BipartiteDiGraph, result: Dict, filter_list: List[Node],
                      user_node: UserNode) -> Dict:
        """
        Method which filters the result dict returning only items that are also in the filter_list

        Args:
            result (dict): dictionary representing the result (keys are nodes and values are their score prediction)
            filter_list (list): list of the items to predict, if None all unrated items will be predicted
        """

        def must_keep(node: object, user_profile):
            must_be_kept = True
            if node in user_profile or type(node) not in self._nodes_to_keep:
                must_be_kept = False

            return must_be_kept

        if filter_list is not None:
            filtered_keys = result.keys() & set(filter_list)
            filtered_result = {k: result[k] for k in filtered_keys}
        else:
            extracted_profile = set(graph.get_successors(user_node))
            filtered_result = {k: result[k] for k in result.keys() if must_keep(k, extracted_profile)}

        return filtered_result

    @staticmethod
    def extract_profile(graph: BipartiteDiGraph, user_id: str) -> Dict:
        """
        Extracts the user profile (the items that the user rated, or in general the nodes with a link to the user).

        Returns a dictionary containing the successor nodes as keys and the weights in the graph for the edges between
        the user node and his successors as values

        EXAMPLE::
             graph: i1 <---0.2--- u1 ---0.4---> i2

            > print(extract_profile('u1'))
            > {'i1': 0.2, 'i2': 0.4}

        Args:
            graph (FullGraph): graph from which the profile of the user will be extracted
            user_id (str): id for the user for which the profile will be extracted
        Returns:
            profile (dict): dictionary with item successor nodes to the user as keys and weights of the edge
                connecting them in the graph as values
        """
        succ = graph.get_successors(UserNode(user_id))
        profile = {a: graph.get_link_data(UserNode(user_id), a).get('weight') for a in succ}

        return profile  # {t: w for (f, t, w) in adj}

    @abc.abstractmethod
    def predict(self, all_users: Set[str], graph: Graph, filter_dict: Dict[str, Set] = None) -> List[Interaction]:
        """
        |  Abstract method that predicts the rating which a user would give to items
        |  If the algorithm is not a PredictionScore Algorithm, implement this method like this:

        def predict():
            raise NotPredictionAlg

        One can specify which items must be predicted with the filter_list parameter,
        in this case ONLY items in the filter_list will be predicted.
        One can also pass items already seen by the user with the filter_list parameter.
        Otherwise, ALL unrated items will be predicted.

        Args:
            user_id (str): id of the user of which predictions will be calculated
            graph (FullGraph): graph containing interactions between users and items (and optionally other types of
                nodes)
            filter_list (list): list of the items to predict, if None all unrated items will be score predicted
        Returns:
            pd.DataFrame: DataFrame containing one column with the items name,
                one column with the score predicted
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rank(self, all_users: Set[str], graph: Graph, recs_number: int = None,
             filter_dict: Dict[str, Set] = None) -> List[Interaction]:
        """
        |  Rank the top-n recommended items for the user. If the recs_number parameter isn't specified,
        |  all items will be ranked.
        |  If the algorithm is not a Ranking Algorithm, implement this method like this:

        def rank():
            raise NotRankingAlg

        One can specify which items must be ranked with the filter_list parameter,
        in this case ONLY items in the filter_list will be ranked.
        One can also pass items already seen by the user with the filter_list parameter.
        Otherwise, ALL unrated items will be ranked.

        Args:
            user_id (str): id of the user of which predictions will be calculated
            graph (FullGraph): graph containing interactions between users and items (and optionally other types of
                nodes)
            filter_list (list): list of the items to predict, if None all unrated items will be score predicted
        Returns:
            pd.DataFrame: DataFrame containing one column with the items name,
                one column with the rating predicted, sorted in descending order by the 'rating' column
        """
        raise NotImplementedError
