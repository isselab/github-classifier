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

'''encodes the not mutually exclusive labels in the classifyhub dataset,
   labels: ['Dev', 'Edu', 'Hw', 'Other']'''
def multi_hot_encoding(graph_classes, graph_list):
    num_classes = len(graph_classes)
    enc_labels = []
    for label in graph_list:
        enc = [0. for i in range(0, num_classes)]
        if label == 'Dev':
            enc[0] = 1.0
        if label == 'Edu':
            enc[1] = 1.0
        if label == 'Hw':
            enc[2] = 1.0
        if label == 'Other':
            enc[3] = 1.0
        #if multiple labels are assigned to one repo
        if ',' in label:
            multiple_labels = label.split(',')
            for m_label in multiple_labels:
                if m_label == 'Dev' or m_label == ' Dev':
                    enc[0] = 1.0
                if m_label == 'Edu' or m_label == ' Edu':
                    enc[1] = 1.0
                if m_label == 'Hw' or m_label == ' Hw':
                    enc[2] = 1.0
                if m_label == 'Other' or m_label == ' Other':
                    enc[3] = 1.0
        enc_labels.append(enc)
    return enc_labels
