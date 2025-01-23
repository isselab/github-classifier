import pandas as pd
import graphviz

def read_node_features(file_path):
    """Read node features from CSV file."""
    return pd.read_csv(file_path)

def read_adjacency_list(file_path):
    """Read adjacency list from CSV file."""
    return pd.read_csv(file_path, header=None, names=['source', 'target'])

def read_edge_attributes(file_path):
    """Read edge attributes from CSV file."""
    return pd.read_csv(file_path)

def create_graph(node_features, adjacency_list, edge_attributes):
    """Create a graph using Graphviz."""
    dot = graphviz.Digraph(comment='Graph Visualization')

    # Add nodes with features
    for index, row in node_features.iterrows():
        node_id = row['hashed_node_name']  # Assuming this is the column name for hashed node names
        node_type = row['node_type']  # Assuming this is the column name for node types
        library_flag = row['library_flag']  # Assuming this is the column name for library flags
        dot.node(node_id, f'{node_id}\nType: {node_type}\nLibrary: {library_flag}')

    # Add edges with attributes
    for index, row in adjacency_list.iterrows():
        source = row['source']
        target = row['target']
        edge_attr = edge_attributes.iloc[index]  # Assuming the order matches
        edge_type = edge_attr['edge_type']  # Assuming this is the column name for edge types
        dot.edge(source, target, label=edge_type)

    # Render the graph to a file and display it
    dot.render('graph_visualization', format='png', cleanup=True)
    dot.view()

def main(output_name):
    """Main function to read files and create graph."""
    node_features_file = f"{output_name}_nodefeatures.csv"
    adjacency_list_file = f"{output_name}_A.csv"
    edge_attributes_file = f"{output_name}_edge_attributes.csv"

    node_features = read_node_features(node_features_file)
    adjacency_list = read_adjacency_list(adjacency_list_file)
    edge_attributes = read_edge_attributes(edge_attributes_file)

    create_graph(node_features, adjacency_list, edge_attributes)

if __name__ == "__main__":
    output_name = "testing/csv_files/test_child_class"  # Replace with your actual output name
    main(output_name)