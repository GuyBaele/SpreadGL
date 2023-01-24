import re
import treeswift
import tempfile
from Bio import Phylo


def parse_tree(tree_path):
    tree_name = get_tree_name(tree_path)
    tree = treeswift.read_tree_nexus(tree_path, translate=True).get(tree_name)
    nodes = tree.traverse_postorder(leaves=True, internal=True)
    labels = []
    edges = []
    for node in nodes:
        end_name = 'None' if node.get_label() is None else node.get_label()
        labels.append(end_name)
        duration = 0.0 if node.get_edge_length() is None else node.get_edge_length()
        edges.append(duration)
    temp_file = tempfile.NamedTemporaryFile(mode="w+t")
    tree.write_tree_newick(temp_file.name, hide_rooted_prefix=False)
    parsed_tree = Phylo.read(temp_file, 'newick')
    temp_file.close()
    return parsed_tree, labels, edges


def get_tree_name(tree_path):
    tree_text = open(tree_path, "r").read()
    tree_info = re.compile(r'(?<=tree )(.*)(?<= \=)').findall(tree_text)[0][:-2]
    tree_identifier = tree_info.split(' ')[0]
    return tree_identifier
