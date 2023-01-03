import treeswift
import tempfile
from Bio import Phylo


def parseTree(tree_path):
    tree = treeswift.read_tree_nexus(tree_path, translate=True).get('TREE1')
    temp_file = tempfile.NamedTemporaryFile(mode="w+t")
    tree.write_tree_newick(temp_file.name, hide_rooted_prefix=False)
    parsed_tree = Phylo.read(temp_file, 'newick')
    temp_file.close()
    return parsed_tree
