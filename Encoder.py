import pandas as pd
from sklearn.preprocessing import OneHotEncoder

'''one hot encoding for node features'''


def one_hot_encoding(labels, matrix):
    """
    Perform one-hot encoding on the given labels.

    Args:
        labels (array-like): The labels to be encoded, which will be transformed into a one-hot encoded format.
        matrix (array-like): The matrix containing the original data, which is not used in the encoding process but is required for function signature.

    Returns:
        np.ndarray: A one-hot encoded array representing the input labels.
    """
    one_hot_encoder = OneHotEncoder(
        handle_unknown='ignore', sparse_output=False)
    labels = pd.DataFrame(labels)
    one_hot_encoder.fit(labels)
    matrix = pd.DataFrame(matrix)
    enc = one_hot_encoder.transform(matrix)
    return enc


'''encodes the not mutually exclusive labels in the dataset,
   labels: ['Application', 'Framework', 'Library', 'Plugin']'''


def multi_hot_encoding(graph_classes, graph_list):
    """
    Perform multi-hot encoding for a list of graph classes.

    Args:
        graph_classes: A list of unique class labels that can be assigned to nodes in the graph.
        graph_list: A list of labels for each node, where each label can be a single class or a comma-separated string of multiple classes.

    Returns:
        list: A list of lists, where each inner list represents the multi-hot encoded vector for a corresponding label in `graph_list`.
    """
    num_classes = len(graph_classes)
    enc_labels = []
    for label in graph_list:
        enc = [0. for _ in range(0, num_classes)]
        if label == 'Application':
            enc[0] = 1.0
        if label == 'Framework':
            enc[1] = 1.0
        if label == 'Library':
            enc[2] = 1.0
        if label == 'Plugin':
            enc[3] = 1.0
        # if multiple labels are assigned to one repo
        if ',' in label:
            multiple_labels = label.split(',')
            for m_label in multiple_labels:
                if m_label == 'Application' or m_label == ' Application':
                    enc[0] = 1.0
                if m_label == 'Framework' or m_label == ' Framework':
                    enc[1] = 1.0
                if m_label == 'Library' or m_label == ' Library':
                    enc[2] = 1.0
                if m_label == 'Plugin' or m_label == ' Plugin':
                    enc[3] = 1.0
        enc_labels.append(enc)
    return enc_labels
