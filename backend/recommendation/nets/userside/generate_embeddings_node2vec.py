import os
from gensim.models import Word2Vec
import multiprocessing as mp
import random

def generate_embeddings_node2vec(cites_files, method, ndims = 128, window_size = 10):
    """
    generate_embeddings(cites_files, method, ndims, window_size, directory) generates vector embeddings for all the
    nodes in the network
    It uses a similar method as node2vec for generating embeddings from the fairwalk/randomwalk traces.
    It takes list of ego nodes as argument.
    Additionally, it takes the dimensions for embeddings and window size for the ngram model as arguments.
    It saves embeddings for all the nodes for each instance of all the ego networks in the directory ../Embeddings/
    It also saves the respective word2vec models trained in the directory ../Embeddings_Model/
    """

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings')
    except:
        pass

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings_Model/')
    except:
        pass

    for cites in cites_files:
        for i in range(5):
            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/walks/{}_{}_{}.txt'.format(method, cites, i), 'r')
            walks = []
            lines = file.readlines()
            for line in lines:
                if len(line) == 0:
                    continue
                walk = [element for element in line.strip().split()]
                walks.append(walk)
            random.shuffle(walks)
            model = Word2Vec(walks, vector_size = 128, window = 10, min_count = 10, sg = 1, workers = mp.cpu_count())
            model.wv.save_word2vec_format('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings/embeddings_node2vec_{}_{}_{}.emb'.format(method, cites, i))
            model.wv.save('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings_Model/embeddings_model_node2vec_{}_{}_{}.model'.format(method, cites, i))
            file.close()


if __name__ == '__main__':
    cites_files = ['cora']
    method = 'randomwalks'
    ndims = 128
    window_size = 10
    generate_embeddings_node2vec(cites_files, method, ndims, window_size)