import scipy
import scipy.spatial
import numpy as np
import os


def find_similar_non_friends(cites_files):
    """
    find_similar_non_friends(ego_nodes) finds up to most similar nodes which are not connected as per the training (80%)
    data.
    It takes the list of ego nodes as its argument.
    It does so for all the nodes in all the instances of all the ego-networks.
    It uses cosine similarity between the vector embeddings of the nodes and then selects the most similar nodes, up to
    100 in number for each node.
    It saves the similar nodes found in the directory ../Similar_Nodes/
    """

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Similar_Nodes/')
    except:
        pass

    for cites in cites_files:
        for i in range(5):
            adjacency_list = {}
            nodes = set()

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Adjacency_Lists/adjacency_list_{}_{}.txt'.format(cites, i), 'r')
            lines = file.readlines()
            file.close()

            for line in lines:
                if len(line) == 0:
                    continue
                line = line.strip().split()
                nodes.add(int(line[0]))
                adjacency_list[int(line[0])] = [int(element) for element in line[1:]]

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings/embeddings_{}_{}_{}.emb'.format('fairwalks', cites, i))
            lines = file.readlines()
            file.close()

            embeddings = {}
            for line in lines[1:]:
                if len(line) == 0:
                    continue
                line = line.strip().split()
                embeddings[int(line[0])] = np.asarray([float(element) for element in line[1:]], dtype = np.float32)

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Similar_Nodes/similar_nodes_{}_{}.txt'.format(cites, i), 'w')
            for node in nodes:
                embedding_node = embeddings[node]
                not_in = [element for element in nodes if element not in adjacency_list[node]]
                cosines = {}

                for nin in not_in:
                    cosines[scipy.spatial.distance.cosine(embedding_node, embeddings[nin])] = nin

                values = list(cosines.keys())
                values.sort(reverse = True)
                similar = []

                for j in range(min(100, len(values))):
                    similar.append(cosines[values[j]])

                file.write(str(node))
                for same in similar:
                    file.write(' {}'.format(same))
                file.write('\n')
            file.close()


if __name__ == '__main__':
    cites_files = ['cora']
    find_similar_non_friends(cites_files)