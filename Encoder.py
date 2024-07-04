from sklearn.preprocessing import OneHotEncoder
import pandas as pd

'''one hot encoding for node features'''
def one_hot_encoding(labels, matrix):
    one_hot_encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    labels = pd.DataFrame(labels)
    one_hot_encoder.fit(labels)
    matrix = pd.DataFrame(matrix)
    enc = one_hot_encoder.transform(matrix)
    return enc

'''encodes the not mutually exclusive classes of graphs in the dataset,
   labels ['Application', 'Framework', 'Library']'''
def multi_hot_encoding(graph_classes, graph_list):
    num_classes = len(graph_classes)
    enc_labels = []
    for label in graph_list:
        enc = [0. for i in range(0, num_classes)]
        if label == 'Application':
            enc[0] = 1.0
        if label == 'Framework':
            enc[1] = 1.0
        if label == 'Library':
            enc[2] = 1.0
        if ',' in label:
            multiple_labels = label.split(',')
            for m_label in multiple_labels:
                if m_label == 'Application' or m_label == ' Application':
                    enc[0] = 1.0
                if m_label == 'Framework' or m_label == ' Framework':
                    enc[1] = 1.0
                if m_label == 'Library' or m_label == ' Library':
                    enc[2] = 1.0
        enc_labels.append(enc)
    return enc_labels
