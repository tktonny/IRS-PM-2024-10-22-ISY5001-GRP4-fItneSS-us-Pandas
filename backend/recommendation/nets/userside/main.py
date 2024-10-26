from adjacency_list_cora import generate_adjacency_list
from feature_extraction_cora import generate_features
from class_label_mapping import map_nodes_class_label
from fairwalk import generate_fairwalks
from randomwalk import generate_randomwalks
from generate_embeddings_node2vec import generate_embeddings_node2vec
from generate_embeddings_fasttext import generate_embeddings_fasttext
from visualize import visualize_embedding
from sub_nodes import sub_node
from sub_vec_plot import sub_vec_plot
from find_similar_non_friends import find_similar_non_friends
from map_similar_nodes import map_similar_nodes
from not_connected_samples import find_not_connected_samples
from safewalk import safewalk


if __name__ == '__main__':
    dataset_directory = "/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/"
    cites_files = generate_adjacency_list(dataset_directory)#split2/8=>edges adjacency_list(train edges)=>Adjacency_Lists directory

    features, class_label_featnum = generate_features(cites_files, dataset_directory)#0-1434

    map_nodes_class_label(cites_files, class_label_featnum, features, dataset_directory)#Class_Label_Adjacency_Lists

    num_walks = 20
    walk_len = 80
    generate_fairwalks(cites_files, num_walks, walk_len)
    generate_randomwalks(cites_files, num_walks, walk_len)

    ndims = 128
    window_size = 10
    divide = 3
    methods = ['fairwalks', 'randomwalks']
    generate_embeddings_fasttext(cites_files, methods[0], divide, ndims, window_size)
    generate_embeddings_fasttext(cites_files, methods[1], divide, ndims, window_size)
    generate_embeddings_node2vec(cites_files, methods[0], ndims, window_size)
    generate_embeddings_node2vec(cites_files, methods[1], ndims, window_size)

    visualize_embedding(cites_files, methods[0])
    visualize_embedding(cites_files, methods[1])
'''
    sub_node(cites_files, methods[0])
    sub_node(cites_files, methods[1])

    sub_vec_plot(cites_files, methods[0])
    sub_vec_plot(cites_files, methods[1])

    safewalk(cites_files, methods[0])
    safewalk(cites_files, methods[1])

    find_similar_non_friends(cites_files)

    map_similar_nodes(cites_files)

    find_not_connected_samples(cites_files)
'''