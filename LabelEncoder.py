from sklearn.preprocessing import LabelEncoder

def convert_labels(labels, matrix):
    label_encoder = LabelEncoder()
    label_encoder.fit(labels)
    encoded_nodes = label_encoder.transform(matrix)
    return encoded_nodes
