
class JSONFormatter:
    """Class to format the data, into right Structure for visualisation"""

    def __init__(self):
        self.frontend_data = dict()
        self.id_count = 1000
        self.expanded_nodes = list()

    def build_tree(self, nodes: list):
        """add edges based on the information in nodes. Format the structure to visualize it in frontend"""
        self.frontend_data['nodes'] = self.__format_leafes(nodes, nodes[0], expandable=True)
        self.frontend_data['edges'] = self.__format_edges(nodes, nodes[0])
        return self.frontend_data

    def build_tree_for_term(self, nodes: list, term: str):
        """add edges based on the information in nodes. Format the structure to visualize it in frontend"""

        root_node = dict()
        root_node['hashtag'] = term
        root_node['leaf'] = 'false'
        root_node['total_count'] = nodes[0]['total_count']
        root_node['id'] = self.__get_an_id()

        # delete the real root node
        del nodes[0]

        self.frontend_data['nodes'] = list()
        self.frontend_data['nodes'].append(root_node)
        self.frontend_data['nodes'] += self.__format_leafes(nodes, root_node, expandable=False)
        self.frontend_data['edges'] = self.__format_edges(nodes, root_node)
        return self.frontend_data

    def handle_node_click(self, leafes: list, clicked_node_name: str):
        """either expand subtree or implode if tree already expanded"""
        clicked_node = self.__get_node_by_name(clicked_node_name)

        # if the root node was clicked, return the existing model with no change.
        if (clicked_node == self.frontend_data['nodes'][0]):
            return self.frontend_data

        # remove the first leaf because its is the same as the root not and we don't want it again as leaf.
        del leafes[0]

        # only expand node if its not yet expanded. Otherwise remove leafes
        if (clicked_node not in self.expanded_nodes):

            # remember which nodes are expanded
            self.expanded_nodes.append(clicked_node)

            # Adding the nodes and edges to the frontend model
            self.frontend_data['nodes'] += self.__format_leafes(leafes, clicked_node, expandable=False)
            self.frontend_data['edges'] += self.__format_edges(leafes, clicked_node)
            return self.frontend_data

        else:
            # remove leafes and its edges
            self.frontend_data['nodes'] = [x for x in self.frontend_data['nodes'] if x['parent'] != clicked_node['id']]
            self.frontend_data['edges'] = [x for x in self.frontend_data['edges'] if
                                           x['source_id'] != clicked_node['id']]

            # cleanup existing edge indexing
            self.__cleanup_edge_indexes()
            # remove node from expanded list. So it can be expanded again later.
            self.expanded_nodes.remove(clicked_node)

            return self.frontend_data

    def build_timeline(self, data: list) -> list:
        """form json object for each datapoint"""
        timeline = list()

        for index, record in enumerate(data):
            if index > 0:  # ignore the search term itself
                for date, count in record['daily_count'].items():
                    timeline.append({"name": record['hashtag'], "date": date, 'daily_total_tweets': count})
        return timeline

    def get_list_of_terms(self, data: list):
        """extract the terms from data and return as list"""
        list_of_terms = list()

        for record in data:
            list_of_terms.append(record['hashtag'])
        return list_of_terms

    def __format_leafes(self, leafes, parent_node: dict, expandable=True):
        """remove unused db fields and add needed fields for building the graph in frontend"""

        for leaf in leafes:
            del leaf['daily_count']
            del leaf['_id']
            leaf['id'] = self.__get_an_id()
            leaf['parent'] = parent_node['id']
            leaf['leaf'] = 'false' if expandable else 'true'

            # evaluate the right description of the new node and add the attribute, if the data is
            # from relation collection

            if ('hashtag_A' in leaf):
                if (leaf["hashtag_A"] == parent_node['hashtag']):
                    leaf["hashtag"] = leaf["hashtag_B"]
                else:
                    leaf["hashtag"] = leaf["hashtag_A"]
                del leaf['hashtag_A']
                del leaf['hashtag_B']
        return leafes

    def __format_edges(self, leafes: list, source_node: dict) -> list:
        # build the edges for the given nodes
        edges = []
        for leaf in leafes:
            edge = dict()
            # set source / target id's based on node id's
            edge['source_id'] = source_node['id']
            edge['target_id'] = leaf['id']

            # set source / target list index references
            edge['source'] = next(
                index for (index, d) in enumerate(self.frontend_data['nodes']) if d['id'] == source_node['id'])
            edge['target'] = next(
                index for (index, d) in enumerate(self.frontend_data['nodes']) if d['id'] == leaf['id'])

            edge['occurance'] = 2
            edges.append(edge)
        return edges

    def __cleanup_edge_indexes(self):
        """Cleanup list index references"""
        for edge in self.frontend_data['edges']:
            edge['target'] = next(
                index for (index, d) in enumerate(self.frontend_data['nodes']) if d['id'] == edge['target_id'])
            edge['source'] = next(
                index for (index, d) in enumerate(self.frontend_data['nodes']) if d['id'] == edge['source_id'])

    def __get_an_id(self) -> int:
        """Get a unique id"""
        self.id_count += 1
        return self.id_count

    def __get_node_by_name(self, clicked_node: str) -> dict:
        """evaluate the node dict with a given nodename"""
        for node in self.frontend_data['nodes']:
            if node['hashtag'] == clicked_node:
                return node