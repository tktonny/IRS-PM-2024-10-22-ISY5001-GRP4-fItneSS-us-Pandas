import math
import gensim
import pickle
import os
from gensim.models.fasttext import FastText


def safewalk(cites_files, method):
    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Safe_Embeddings')
    except:
        pass

    for cites in cites_files:
        safe_vec = {}
        for i in range(5):
            safe_vec[i] = []
            frontList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            divid = 3
            dividCount = 8 * divid - 7
            frontList = frontList[0:divid]
            divide_vec = {}
            vec = {}
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/divide_vec_{}_{}_{}.map'.format(method, cites, i), 'rb') as f:
                divide_vec = pickle.load(f)
            f.close()
            for node in divide_vec:
                vec[node] = [0 for x in range(128)]
                for j in range(dividCount):
                    if j != 0 and j != dividCount-1 and j != (dividCount+1)/2:
                        vec[node] = [x + dividCount*y/(dividCount-3) for x, y in zip(vec[node], divide_vec[node][j])]
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Safe_Embeddings/safe_vec_{}_{}_{}.map'.format(method, cites, i), 'wb') as f:
                pickle.dump(vec, f)
            f.close()
        print(cites)



if __name__ == '__main__':
    cites_files = ['cora']
    method = 'randomwalks'
    safewalk(cites_files, method)