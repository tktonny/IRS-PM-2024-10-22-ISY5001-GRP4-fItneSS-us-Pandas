def generate_features(cites_files, dataset_directory = '/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/'):
    """
    generate_features(ego_nodes, dataset_directory) generates a list of word_attributes(feature numbers) for all the ego
    nodes in the network
    It also finds the feature number for the sensitive attribute - class_label
    It takes list of ego nodes and dataset directory as arguments
    It returns a dictionary features and a list class_label_featnum, which tell list of feature numbers for ego nodes and
    feature numbers for class_label respectively
    It scrapes .content files for all the ego nodes for this purpose
    """

    if dataset_directory[-1] != '/':
        dataset_directory = dataset_directory + '/'

    features = {}
    class_label_featnum = []
    for cites in cites_files:
        content = open(dataset_directory + str(cites) + '.content')
        features_node = []
        for line in content:
            count = len(line.split('\t'))
            for i in range(count):
                features_node.append(i)
            class_label_featnum.append(count)
            features[cites] = features_node
            content.close()
            break
    class_label_featnum.sort()

    print(features, class_label_featnum)
    return features, class_label_featnum


if __name__ == '__main__':
    cites_files = ['cora']
    dataset_directory = "/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/"
    features, class_label_featnum = generate_features(cites_files, dataset_directory)