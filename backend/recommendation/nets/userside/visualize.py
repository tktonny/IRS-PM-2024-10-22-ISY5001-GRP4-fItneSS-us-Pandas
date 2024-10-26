import gensim
from sklearn.decomposition import IncrementalPCA    # inital reduction
from sklearn.manifold import TSNE                   # final reduction
import numpy as np                                  # array handling
import os
from gensim.models.fasttext import FastText
from gensim.models import Word2Vec
import matplotlib.pyplot as plt
import random


def visualize_embedding(cites_files, method):
    """
    visualize(cites_files, method, ndims, window_size, directory) generates visualizations for all the
    nodes in the network
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
        dataset_directory = '/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/'
        content = open(dataset_directory + str(cites) + '.content')
        private = {}
        for line in content:
            private[line.split()[0]] = line.split()[-1]
        i = 0
        model_word2vec = gensim.models.KeyedVectors.load_word2vec_format(
            '/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings/embeddings_node2vec_{}_{}_{}.emb'.format(method, cites, i), binary=False)
        model_fasttext = gensim.models.KeyedVectors.load_word2vec_format(
            '/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Embeddings/embeddings_fasttext_{}_{}_{}.emb'.format(method, cites, i), binary=False)

        x_vals, y_vals, labels = reduce_dimensions(model_word2vec, private)
        plot_function = plot_with_matplotlib
        plot_function(x_vals, y_vals, labels)

        x_vals, y_vals, labels = reduce_dimensions(model_fasttext, private)
        plot_function = plot_with_matplotlib
        plot_function(x_vals, y_vals, labels)


def reduce_dimensions(model, private):
    num_dimensions = 2  # final num dimensions (2D, 3D, etc)

    # extract the words & their vectors, as numpy arrays
    vectors = np.asarray(model.vectors)
    plist = []
    for a in model.index_to_key:
        if len(a) == 24:
            a = "".join(list(filter(str.isdigit, a[0:8])))
        plist.append(private[a])
    labels = np.asarray(plist)  # fixed-width numpy strings

    # reduce using t-SNE
    tsne = TSNE(n_components=num_dimensions, random_state=0)
    vectors = tsne.fit_transform(vectors)

    x_vals = [v[0] for v in vectors]
    y_vals = [v[1] for v in vectors]
    return x_vals, y_vals, labels


def plot_with_matplotlib(x_vals, y_vals, labels):
    random.seed(0)
    cla = ['Case_Based', 'Genetic_Algorithms', 'Neural_Networks', 'Probabilistic_Methods', 'Reinforcement_Learning', \
    'Rule_Learning', 'Theory', 'Other']
    colors = ['mediumblue', 'green', 'red', 'yellow', 'cyan', 'mediumvioletred', 'mediumspringgreen', 'black']
    color = []
    for l in labels:
        index = cla.index(l)
        color.append(colors[index])

    plt.figure(figsize=(12, 12))
    plt.scatter(x_vals, y_vals, c=color)
    #
    # Label randomly subsampled 25 data points
    #
    indices = list(range(len(labels)))
    selected_indices = random.sample(indices, 25)
    for i in selected_indices:
        plt.annotate(labels[i], (x_vals[i], y_vals[i]))
    plt.show()


if __name__ == '__main__':
    cites_files = ['cora']
    method = 'randomwalks'
    visualize_embedding(cites_files, method)