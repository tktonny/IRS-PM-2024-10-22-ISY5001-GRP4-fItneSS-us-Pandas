import math
import gensim
import pickle
import os
from gensim.models.fasttext import FastText


def sub_node(cites_files, method):
    """
    sub_node(cites_files, method) generates sub-node file for all the nodes in the network
    It saves sub-embeddings for all the nodes for each instance of all the ego networks in the directory
    ../Sub_Embeddings/
    It also saves the respective FastText models trained in the directory ../Sub_Embeddings/
    """

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings')
    except:
        pass

    for cites in cites_files:
        dataset_directory = '/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/'
        content = open(dataset_directory + str(cites) + '.content')
        private = {}
        for line in content:
            private[line.split()[0]] = line.split()[-1]
        with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/privateLable', 'wb') as f:
            pickle.dump(private, f)
        f.close()

        for i in range(5):
            model_fasttext = gensim.models.fasttext.FastTextKeyedVectors.load('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings_Model/embeddings_model_'
                                                                              'fasttext_{}_{}_{}.model'.format(method,
                                                                                                               cites, i))
            frontList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            divid = int(len(model_fasttext.index_to_key[0])/8)
            dividCount = 8 * divid - 7
            frontList = frontList[0:divid]
            divide_vec = {}
            divide_dist = {}
            aplha_vec = {}

            for aplha in frontList:
                aplha_vec[aplha] = model_fasttext[aplha*8]
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/aplha_vec_{}_{}_{}.list'.format(method, cites, i), 'wb') as f:
                pickle.dump(aplha_vec, f)
            f.close()

            for key in model_fasttext.index_to_key:
                node = "".join(list(filter(str.isdigit, key[0:8])))
                divide_vec[node] = []
                divide_dist[node] = []
                keyVec = model_fasttext[key]
                for k in range(dividCount):
                    iVec = model_fasttext[key[k:k+8]]
                    divide_vec[node].append(iVec)
                    divide_dist[node].append(eucliDist(iVec, keyVec))
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/divide_vec_{}_{}_{}.map'.format(method, cites, i), 'wb') as f:
                pickle.dump(divide_vec, f)
            f.close()
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/divide_dist_{}_{}_{}.map'.format(method, cites, i), 'wb') as f:
                pickle.dump(divide_dist, f)
            f.close()


def eucliDist(A,B):
    return math.sqrt(sum([(a - b)**2 for (a,b) in zip(A,B)]))


if __name__ == '__main__':
    cites_files = ['cora']
    method = 'fairwalks'
    sub_node(cites_files, method)
