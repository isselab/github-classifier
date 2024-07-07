from CustomDataset import RepositoryDataset
from Pipeline import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from GCN import GCN
import torch
import mlflow
import matplotlib.pylab as plt
from sklearn.model_selection import KFold
import torch.nn.functional as nn
import numpy as np
from GraphClasses import defined_labels
from sklearn.metrics import classification_report

#repository_directory = 'D:/labeled_dataset_repos'  #downloaded github repositories
output_directory = 'D:/labeled_repos_output'
labels = 'data/labeled_dataset_repos.xlsx'
n_epoch = 100
k_folds = 4 #has to be at least 2
learning_rate = 0.001
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'
threshold = 0.5 #value above which label is considered to be predicted by model
save_classification_reports = 'classification_reports/train_with_115.txt'
experiment_name = 'train_with_115'

def train():
        model.train()
        
        num_classes = int(len(defined_labels))

        for graph in trainloader: 

            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                graph.edge_attr = graph.edge_attr.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            #prepare input
            size = int(len(graph.y)/num_classes)
            graph.x = nn.normalize(graph.x, p=0.5)
            graph.edge_attr = nn.normalize(graph.edge_attr, p=2.0)
            graph.y = torch.reshape(graph.y, (size, num_classes))
            
            output = model(graph.x, graph.edge_index, graph.edge_attr, graph.batch)
            loss_train = criterion(output, graph.y) #graph.y is label

            #backpropagation
            optimizer.zero_grad()
            loss_train.backward()

            #update weights
            optimizer.step()

def test(loader):
        model.eval()
        loss_test = 0
        total = 0
        num_classes = int(len(defined_labels))

        for graph in loader:

            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                graph.edge_attr = graph.edge_attr.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            #prepare input
            size = int(len(graph.y)/num_classes)
            graph.y = torch.reshape(graph.y, (size, num_classes))

            #evaluate model
            output = model(graph.x, graph.edge_index, graph.edge_attr, graph.batch)
            loss = criterion(output, graph.y)
            loss_test += loss.item()
            total += len(loader)

            output = output.cpu().detach().numpy()
            graph.y = graph.y.cpu().detach().numpy()
            
            #transform output, if value above threshold label is considered to be predicted
            trafo_output = []
            for slice in output:
                new_item = []
                for item in slice:
                    if item>=threshold:
                        new_item.append(1.0)
                    else:
                        new_item.append(0.0)
                trafo_output.append(new_item)
            trafo_output = np.reshape(trafo_output, (size, num_classes))

            #better evaluation metrics for multilabel: precision, recall, f1_score
            #report is string, dict to extract results 
            report_dict = classification_report(graph.y, trafo_output, target_names=defined_labels, output_dict=True)
            class_report = classification_report(graph.y, trafo_output, target_names=defined_labels)

        return loss_test/total, class_report, report_dict

#create the graph dataset of the repositories, already done
#try:
   # prepare_dataset(repository_directory, output_directory)
#except Exception as e:
   # print(e)

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
    print(f'Dataset size: {dataset.__len__()}')
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=32)

if device == 'cuda':
    model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), learning_rate)
criterion = torch.nn.MultiLabelSoftMarginLoss()

#set our tracking server uri for logging
#mlflow.set_tracking_uri(uri="https://community.cloud.databricks.com/ml/experiments?o=286453794264191")

#create a new MLflow Experiment
mlflow.create_experiment(experiment_name)
mlflow.set_experiment(experiment_name)

#k fold cross validation
kfold = KFold(n_splits=k_folds, shuffle=True)

#for classification reports
reports = {}

#initialize overall model performance with negative infinity
best_avg = - np.inf

#training loop
for f, fold in enumerate(kfold.split(dataset)):
    # split into train and testset, this is only for training the tool
    trainset, testset = random_split(dataset, [0.9, 0.1])
    print(f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=32, shuffle=False)
    print(f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')

    #log model parameters
    params = {"lr": learning_rate}
    for name, param in model.named_parameters():
        if param.requires_grad:
            params[f"{name}"] = param.data

    with mlflow.start_run():
        plt_epoch = []
        plt_test_loss = []
        plt_app = []
        plt_frame = []
        plt_lib = []
        mlflow.log_params(params)

        for epoch in range(n_epoch):
            print(f'Fold {f}, Epoch {epoch}')
            train()
            train_loss, train_report, train_rep_dict = test(trainloader)
            test_loss, test_report, test_rep_dict = test(testloader)

            #log loss
            metrics = {"training loss":train_loss, "test loss":test_loss}
            #alternatively extract params from dicts and log those/write in csv
            mlflow.log_metrics(metrics, step=epoch) #one folder per fold, because metrics needs to be key value pairs not dicts
            reports[f'Fold_{f}_Epoch_{epoch}_train'] = train_report
            reports[f'Fold_{f}_Epoch_{epoch}_test'] = test_report
            #log report strings with ml flow? no have to be type float64
            
            #for plotting
            plt_epoch.append(epoch)
            plt_test_loss.append(test_loss)
            app = test_rep_dict['Application']
            app_f1 = app['f1-score']
            plt_app.append(app_f1)
            frame = test_rep_dict['Framework']
            frame_f1 = frame['f1-score']
            plt_frame.append(frame_f1)
            lib = test_rep_dict['Library']
            lib_f1 = lib['f1-score']
            plt_lib.append(lib_f1)
            
            #print results
            print(f'training loss: {train_loss}')
            print(f'testing loss: {test_loss}')
            print('==============================================')
            av = test_rep_dict['weighted avg']
            f1 = av['f1-score']
            print(f'weighted average of labels (f1-score): {f1}')
            print('==============================================')
            
            #save trained model with best performance
            if best_avg < f1:
                best_avg = f1
                torch.save(model, 'graph_classification_model.pt')

        #write classification reports in file
        report_file = open(save_classification_reports, 'a')
        for key, value in reports.items():
            report_file.write(f'{key}:')
            report_file.write('\n')
            report_file.write(f'{value}')
            report_file.write('\n')
        report_file.close()
        
        #plot visualization
        fig = plt.figure(f)
        fig, (ax1,ax2) = plt.subplots(2)
        fig.suptitle(f'Fold {f}')
        ax1.plot(plt_epoch, plt_test_loss, 'k', label='test loss')
        ax1.set(ylabel='test loss')
        ax2.plot(plt_epoch, plt_app, 'r', label='Application')
        ax2.plot(plt_epoch, plt_frame, 'g', label='Framework')
        ax2.plot(plt_epoch, plt_lib, 'b', label='Library')
        ax2.set(xlabel='epoch', ylabel='f1 score')
        plt.legend()
        plt.savefig(f'{figure_output}/fig_{f}.pdf', bbox_inches='tight')

mlflow.end_run()
