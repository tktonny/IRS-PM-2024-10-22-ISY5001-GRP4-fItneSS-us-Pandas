import os
from gensim.models.fasttext import FastText
import multiprocessing as mp
import random
import copy

def generate_embeddings_fasttext(cites_files, method, divide = 3, ndims = 128, window_size = 10):
    """
    generate_embeddings_subnode(cites_files, method, divide <= 8, ndims, window_size, directory) generates vector embeddings for all the
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

    frontList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    
    for cites in cites_files:
        for i in range(5):
            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/walks/{}_{}_{}.txt'.format(method, cites, i), 'r')
            walks = []
            lines = file.readlines()
            for line in lines:
                walk = []
                if len(line) == 0:
                    continue
                for element in line.strip().split():
                    space = 8 - len(element)
                    node = ''
                    for count in range(divide):
                        elementwithfornt = copy.deepcopy(element)
                        for front in range(space):
                            elementwithfornt = frontList[count] + elementwithfornt
                        node = node + elementwithfornt
                    walk.append(node)
                walks.append(walk)
            random.shuffle(walks)
            model_divide = FastText(walks, vector_size = 128, window = 10, min_count = 10, sg = 1,
                                    workers = mp.cpu_count(), min_n=8, max_n=8) #node=》nodea—nodeb-nodec; max chars
            # of nodes is 7
            '''
            model_sub = FastText(walks, vector_size=128, window=10, min_count=10, sg=1,
                                    workers=mp.cpu_count(), min_n=1, max_n=7)  # 希望学习到abc
            '''
            model_divide.wv.save_word2vec_format('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings/embeddings_fasttext_{}_{}_{}.emb'.format(method, cites, i))
            model_divide.wv.save('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings_Model/embeddings_model_fasttext_{}_{}_{}.model'.format(method, cites, i))
            file.close()


if __name__ == '__main__':
    cites_files = ['cora']
    method = 'fairwalks'
    ndims = 128
    window_size = 10
    divide = 3
    generate_embeddings_fasttext(cites_files, method, divide, ndims, window_size)