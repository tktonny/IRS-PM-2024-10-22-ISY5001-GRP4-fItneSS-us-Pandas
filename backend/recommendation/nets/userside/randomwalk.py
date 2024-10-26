import copy
import random
import os

def generate_randomwalks(cites_files, num_walks = 20, walk_len = 80):
    """
    generate_randomwalks(cites_files) generates randomwalks for all the nodes in all of the ego-networks
    It takes list of cites_files, number of walks and length of each walk as its arguments.
    It saves the Randomwalk traces, which contain num_walks iterations of randomwalks for
    all the nodes of each instance of all the ego-networks, each of length walk_len
    The directory for the output Randomwalk traces is ../Randomwalks/
    """

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Walks/')
    except:
        pass

    label_choices = [0, 1, 2, 3, 4, 5, 6, 7]

    for cites in cites_files:
        for i in range(5):
            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Adjacency_Lists/adjacency_list_{}_{}.txt'.format(cites, i), 'r')
            adjacency_list = {}
            lines = file.readlines()
            j = 0
            nodes = []
            while j < len(lines) and len(lines[j].strip()) != 0:
                node = int(lines[j].strip().split()[0])
                nodes.append(node)
                adjacency_list[node] = []
                adjacency_list[node] = [int(n) for n in lines[j].strip().split()]
                j = j + 1
            file.close()

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Walks/randomwalks_{}_{}.txt'.format(cites, i), 'w')
            for walk in range(num_walks):
                for node in nodes:
                    prev_node = -1
                    trace = []
                    current_node = node
                    for covered_len in range(walk_len):
                        trace.append(current_node)
                        next_node = random.choice(adjacency_list[current_node])
                        prev_node = current_node
                        current_node = next_node
                    line = ''
                    for step in trace:
                        line = line + str(step) + ' '
                    file.write(line.strip() + '\n')
                    line = ''
                    for step in trace[::-1]:
                        line = line + str(step) + ' '
                    file.write(line.strip() + '\n')
            file.close()


if __name__ == '__main__':
    cites_files = ['cora']
    num_walks = 20
    walk_len = 80
    generate_randomwalks(cites_files, num_walks, walk_len)