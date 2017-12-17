from .data_processing import JSONFormatter
from .persistence import DataQuery
from .config_loader import BackendConfig
import json


class TwitterMonitor:
    """Serves query methods which are returning the data in the prepared JSON model to visualize in frontend including
    nodes and edges."""

    def __init__(self):
        self.config = BackendConfig()
        self.db_query = DataQuery(db_config=self.config.db_config)
        self.json_formatter = JSONFormatter()

    def get_tweet_count(self) -> int:
        """Total quanity of collected tweets so far."""
        return self.db_query.get_total_tweet_count()

    def get_top_hashtags(self, quantity: int) -> json:
        """Nodes for the top hashtags sorted in descending order by quantity"""
        if quantity > 50: quantity = 50  # limit quantity
        base_tree = self.db_query.get_top_hashtags(
            quantity + 1)  # add 1 beacause we want quantitiy of subnodes and root counts as well.
        return self.json_formatter.build_tree(base_tree)

    def expand_tree(self, quantity: int, hashtag: str) -> json:
        """adding leaves to a specific node on the existing tree. Sorted in descending order by quantity"""
        if quantity > 50: quantity = 50  # limit quantity
        tree_leaves = self.db_query.get_related_hashtags(hashtag, quantity)
        return self.json_formatter.handle_node_click(tree_leaves, hashtag)

    def hashtag_search(self, quantity: int, hashtag: str) -> json:
        """leaves for a specific node. Sorted in descending order by quantity"""
        if quantity > 50: quantity = 50  # limit quantity
        nodes = self.db_query.get_related_hashtags(hashtag, quantity)
        return self.json_formatter.build_tree_for_term(nodes, hashtag)

    def get_timeline(self, quantity: int) -> json:
        """Top hashtags with quantity per day to display in timeline. Sorted in descending order by quantity"""
        if quantity > 50: quantity = 50  # limit quantity
        data = self.db_query.get_top_hashtags(quantity + 1)  # add 1 beacause we want quantitiy of subterms.
        return self.json_formatter.build_timeline(data)

    def get_hashtag_list(self, quantity: int) -> json:
        """list of available hashtags"""
        if quantity > 5000: quantity = 5000  # limit quantity
        data = self.db_query.get_top_hashtags(quantity)
        return self.json_formatter.get_list_of_terms(data)
