import torch
import numpy as np
import pymysql
from adjacency_list_cora import generate_adjacency_list
from feature_extraction_cora import generate_features
from class_label_mapping import map_nodes_class_label
from fairwalk import generate_fairwalks
from randomwalk import generate_randomwalks
from generate_embeddings_node2vec import generate_embeddings_node2vec
from generate_embeddings_fasttext import generate_embeddings_fasttext
from visualize import visualize_embedding

def user_embeddings(dataset_directory,num_walks = 20, walk_len = 80, ndims = 128, window_size = 10, divide = 3):
    cites_files = generate_adjacency_list(dataset_directory)#split2/8=>edges adjacency_list(train edges)=>Adjacency_Lists directory

    features, class_label_featnum = generate_features(cites_files, dataset_directory)#0-1434

    map_nodes_class_label(cites_files, class_label_featnum, features, dataset_directory)#Class_Label_Adjacency_Lists

    
    generate_fairwalks(cites_files, num_walks, walk_len)
    generate_randomwalks(cites_files, num_walks, walk_len)


    methods = ['fairwalks', 'randomwalks']
    generate_embeddings_fasttext(cites_files, methods[0], divide, ndims, window_size)
    generate_embeddings_fasttext(cites_files, methods[1], divide, ndims, window_size)
    generate_embeddings_node2vec(cites_files, methods[0], ndims, window_size)
    generate_embeddings_node2vec(cites_files, methods[1], ndims, window_size)


def main():
    num_walks = 20
    walk_len = 80
    ndims = 128
    window_size = 10
    divide = 3
    methods = ['fairwalks', 'randomwalks']
    dataset_directory = "/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/"
    graph_embeddings = user_embeddings(dataset_directory,num_walks, walk_len, ndims, window_size, divide)
    print(graph_embeddings.shape)

if __name__ == "__main__":
    main()
