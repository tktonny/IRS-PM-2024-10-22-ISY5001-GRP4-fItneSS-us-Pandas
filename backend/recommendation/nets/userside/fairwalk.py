import copy
import random
import os

def generate_fairwalks(cites_files, num_walks = 20, walk_len = 80):
    """
    generate_fairwalks(cites_files) generates fairwalks for all the nodes in all of the ego-networks
    It takes list of cites_files, number of walks and length of each walk as its arguments.
    It saves the Fairwalk traces, which contain num_walks iterations of fairwalks for 
    all the nodes of each instance of all the ego-networks, each of length walk_len
    The directory for the output Fairwalk traces is ../Fairwalks/
    """

    try:
        os.mkdir('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Walks/')
    except:
        pass

    label_choices = [0, 1, 2, 3, 4, 5, 6, 7]

    for cites in cites_files:
        for i in range(5):
            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Class_Label_Adjacency_Lists/class_label_adjacency_list_{}_{}.txt'.format(cites, i), 'r')
            class_label_adjacency_list = {}
            lines = file.readlines()
            j = 0
            while j < len(lines) and len(lines[j].strip()) != 0:
                node = int(lines[j].strip())
                class_label_adjacency_list[node] = []
                for k in range(8):
                    j += 1
                    class_label_adjacency_list[node].append([int(n) for n in lines[j].strip().split()])
                j += 1
            nodes = [int(n.strip()) for n in lines[::9]]
            file.close()

            file = open('/Users/macbookair/Documents/Project/fItneSS_us/recommendation/datasets/cora/Walks/fairwalks_{}_{}.txt'.format(cites, i), 'w')
            for walk in range(num_walks):
                for node in nodes:
                    prev_node = -1
                    trace = []
                    current_node = node
                    for covered_len in range(walk_len):
                        trace.append(current_node)
                        choices = copy.deepcopy(label_choices)
                        for label in range(8):
                            if len(class_label_adjacency_list[current_node][label]) == 0:
                                choices.remove(label)
                        label_choice = random.choice(choices)
                        next_node = random.choice(class_label_adjacency_list[current_node][label_choice])
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
    generate_fairwalks(cites_files, num_walks, walk_len)