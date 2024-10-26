import os
import random


def generate_adjacency_list(dataset_directory="/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/"):
    """
    generate_adjacency_list(dataset_directory) generates adjacency list for all the nodes in all the ego networks.
    It takes path to dataset as the argument.
    The edges are extracted and split into 80% and 20%, five times for each ego-network, and saved in ../Edges
    directory.
    The training edges (80%) are then used to form adjacency lists for all the nodes in the training edges file.
    These adjacency lists are saved in ../Adjacency_Lists directory.
    It returns the list of ego nodes.
    It scrapes .circles and .edges files for all the ego nodes for this purpose
    """

    all_files = os.listdir(dataset_directory)

    cites_files = [file for file in all_files if (file.split('.')[-1] == 'cites')]
    cites_files = [file.split('.')[0] for file in cites_files]

    nodes = {}
    for cites in cites_files:
        edges_list = open(dataset_directory + str(cites) + '.cites', 'r')
        for pairs in edges_list:
            pairs = pairs.split()
            cited_node, citing_node = int(pairs[0]), int(pairs[1])
            if cited_node not in nodes.keys():
                nodes[cited_node] = set()
            nodes[cited_node].add(citing_node)
        edges_list.close()

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Edges/')
    except:
        pass

    for cites in cites_files:
        edges_list = open(dataset_directory + str(cites) + '.cites', 'r')
        edges = []
        for pairs in edges_list:
            pairs = pairs.split()
            edges.append(pairs)
        random.shuffle(edges)
        size = len(edges)
        for i in range(5):
            edges_20 = edges[i * (size // 5):(i + 1) * (size // 5)]  # 20%
            edges_80 = edges[:i * (size // 5)] + edges[(i + 1) * (size // 5):]  # 80%

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Edges/edges_20_{}_{}.txt'.format(cites, i), 'w')
            for edge in edges_20:
                file.write('{} {}\n'.format(edge[0], edge[1]))
            file.close()

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Edges/edges_80_{}_{}.txt'.format(cites, i), 'w')
            for edge in edges_80:
                file.write('{} {}\n'.format(edge[0], edge[1]))
            file.close()
        edges_list.close()

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Adjacency_Lists/')
    except:
        pass

    for cites in cites_files:
        for i in range(5):
            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Edges/edges_80_{}_{}.txt'.format(cites, i), 'r')
            adjacency_list = {}
            for line in file:
                if len(line) == 0:
                    continue
                line = line.split()
                node1, node2 = int(line[0]), int(line[1])
                if node1 not in adjacency_list.keys():
                    adjacency_list[node1] = set()
                if node2 not in adjacency_list.keys():
                    adjacency_list[node2] = set()
                adjacency_list[node1].add(node2)
                adjacency_list[node2].add(node1)
            file.close()
            keys = list(adjacency_list.keys())
            keys.sort()

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Adjacency_Lists/adjacency_list_{}_{}.txt'.format(cites, i), 'w')
            for key in keys:
                file.write('{}'.format(key))
                for node in adjacency_list[key]:
                    file.write(' {}'.format(node))
                file.write('\n')
            file.close()
    print(cites_files)
    return cites_files


if __name__ == '__main__':
    dataset_directory = "/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/"
    cites_files = generate_adjacency_list(dataset_directory)
