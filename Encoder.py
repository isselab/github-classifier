from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import pandas as pd

def label_encoding(labels, matrix):
    label_encoder = LabelEncoder()
    label_encoder.fit(labels)
    enc = label_encoder.transform(matrix)
    return enc

def one_hot_encoding(labels, matrix):
    df = pd.DataFrame(matrix)
    categorical_columns = df.select_dtypes(include=['object']).columns.to_list()
    one_hot_encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    enc = one_hot_encoder.fit_transform(df[categorical_columns]) #now makes extra column for two labels
    #labels = pd.DataFrame(labels)
    #one_hot_encoder.fit(labels)
    #matrix = pd.DataFrame(matrix)
    #enc = one_hot_encoder.transform(matrix)
    return enc
