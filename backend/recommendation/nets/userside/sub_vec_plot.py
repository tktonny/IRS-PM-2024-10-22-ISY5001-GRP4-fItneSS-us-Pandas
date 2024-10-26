import math
import gensim
import pickle
import os
import matplotlib.pyplot as plt
import random


def sub_vec_plot(cites_files, method):
    """
    sub_vec_plot(cites_files, method) generates visualizations.
    It saves sub-embeddings' distance for all the nodes for each instance of all the ego networks in the directory
    ../Plot/
    """

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Plot')
    except:
        pass

    for cites in cites_files:
        private = []
        with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/privateLable', 'rb') as f:
            private = pickle.load(f)
        f.close()

        for i in range(5):
            frontList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            divid = 3
            dividCount = 8 * divid - 7
            frontList = frontList[0:divid]
            divide_vec = {}
            divide_dist = {}
            aplha_vec = {}

            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/aplha_vec_{}_{}_{}.list'.format(method, cites, i), 'rb') as f:
                aplha_vec = pickle.load(f)
            f.close()
            '''
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/divide_vec_{}_{}_{}.map'.format(method, cites, i), 'rb') as f:
                divide_vec = pickle.load(f)
            f.close()
            '''
            with open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Sub_Embeddings/divide_dist_{}_{}_{}.map'.format(method, cites, i), 'rb') as f:
                divide_dist = pickle.load(f)
            f.close()

            plot_with_matplotlib(divide_dist,method, cites, i)

        print(cites)


def plot_with_matplotlib(dist, method, cites, i):
    a = list(dist.keys())
    dist_average = dist[a[0]]
    plt.figure(figsize=(12, 12))
    for k in dist:
        if k != a:
            dist_average = [x + y for x, y in zip(dist_average, dist[k])]
        plt.plot(dist[k], '.')
    dist_average = [k/len(dist) for k in dist_average]
    plt.plot(dist_average, '-', label='average distance')
    plt.xlabel('sub-vector')
    plt.ylabel('distance')
    plt.legend(loc='lower center')
    plt.title('divide_dist_{}_{}_{}'.format(method, cites, i))

    plt.savefig('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Plot/divide_dist_{}_{}_{}.png'.format(method, cites, i))


if __name__ == '__main__':
    cites_files = ['cora']
    method = 'randomwalks'
    sub_vec_plot(cites_files, method)
