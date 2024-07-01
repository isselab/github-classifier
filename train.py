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
from sklearn.metrics import accuracy_score, multilabel_confusion_matrix, classification_report

#repository_directory = 'D:/dataset_repos'  # github repositories
#output_directory = 'D:/testing'
#labels = 'D:/testing.xlsx'
output_directory = 'D:/labeled_repos_less_bias_library'
labels = '../labeled_repos_less_bias_library.xlsx'
n_epoch = 10
k_folds = 2 #has to be at least 2
learning_rate = 0.001
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'
threshold = 0.5 #value above which label is considered to be predicted by model
save_classification_reports = 'classification_reports/test_no_tutorial.txt'
experiment_name = 'test_no_tutorial'

def train():
        model.train()
        
        num_classes = int(len(defined_labels))

        for graph in trainloader: 

            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                #graph.edge_attr = graph.edge_attr.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            #prepare input
            size = int(len(graph.y)/num_classes)
            graph.x = nn.normalize(graph.x, p=0.5)
            #graph.edge_attr = nn.normalize(graph.edge_attr, p=2.0)
            graph.y = torch.reshape(graph.y, (size, num_classes))
            
            output = model(graph.x, graph.edge_index, graph.batch)
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
                #graph.edge_attr = graph.edge_attr.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            #prepare input
            size = int(len(graph.y)/num_classes)
            graph.y = torch.reshape(graph.y, (size, num_classes))

            #evaluate model
            output = model(graph.x, graph.edge_index, graph.batch)
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

            #for multilabel not good/reliable metric
            #either 1 (all labels correct) or 0 (at least 1 label not correct predicted)
            acc = accuracy_score(graph.y, trafo_output)

            #better metrics for multilabel: precision, recall, f1_score
            confusion_matrix = multilabel_confusion_matrix(graph.y, trafo_output)
            #report is string, could be changed to dict
            class_report = classification_report(graph.y, trafo_output, target_names=defined_labels)

        return acc, loss_test/total, confusion_matrix, class_report


# create the graph dataset of the repositories, already done
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

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=32) #in paper K=10

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

#fold results for n epochs
results = {}

#for classification reports
reports = {}

#initialize overall model performance with infinity
best_loss = np.inf

#training loop
for f, fold in enumerate(kfold.split(dataset)):
    # split into train and testset, this is only for training the tool
    trainset, testset = random_split(dataset, [0.9, 0.1]) #more training data
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
        plt_test_acc = []
        plt_test_loss = []
        mlflow.log_params(params)

        for epoch in range(n_epoch):
            print(f'Fold {f}, Epoch {epoch}')
            train()
            train_acc, train_loss, train_conf, train_report = test(trainloader)
            test_acc, test_loss, test_conf, test_report = test(testloader)
            #currently not using confusion matrix
            metrics = {"training accuracy":train_acc, "training loss":train_loss, "test accuracy":test_acc, "test loss":test_loss}
            results[f'{f}_epoch_{epoch}'] = metrics
            mlflow.log_metrics(metrics, step=epoch) #one folder per fold, because metrics needs to be key value pairs not dicts
            reports[f'Fold_{f}_Epoch_{epoch}_train'] = train_report
            reports[f'Fold_{f}_Epoch_{epoch}_test'] = test_report

            plt_epoch.append(epoch)
            plt_test_acc.append(test_acc)
            plt_test_loss.append(test_loss)

            print(f'training acc: {train_acc}, training loss: {train_loss}')
            print(f'testing acc: {test_acc}, testing loss: {test_loss}')
            print('==============================================')
            print('training report:')
            print(train_report)
            print('testing report:')
            print(test_report)
            print('==============================================')
            
            #save trained model with best performance
            if test_loss < best_loss:
                best_loss = test_loss
                torch.save(model, 'graph_classification_model.pt')

        #write classification reports in file
        report_file = open(save_classification_reports, 'a')
        for key, value in reports.items():
            report_file.write(f'{key}:')
            report_file.write('\n')
            report_file.write(f'{value}')
            report_file.write('\n')
        report_file.close()

        #visualization of accuracy and loss from testing
        fig = plt.figure(f)
        plt.title(f"Fold {f}")
        p1 = plt.subplot(2, 1, 1)
        plt.plot(plt_epoch, plt_test_acc, 'b')
        plt.setp(p1.get_xticklabels(), visible=False)
        plt.ylabel('test accuracy')

        p2 = plt.subplot(2, 1, 2, sharex=p1)
        plt.plot(plt_epoch, plt_test_loss, 'r')
        plt.setp(p2.get_xticklabels())
        plt.xlabel('epoch')
        plt.ylabel('test loss')

        plt.savefig(f'{figure_output}/fig_{f}.pdf', bbox_inches='tight')

mlflow.end_run()

#print fold results, does not make sense without usable accuracy
#print(f'K-FOLD CROSS VALIDATION RESULTS FOR {k_folds} FOLDS')
#print('--------------------------------')
#sum = 0.0
#for key, value in results.items():
    #print(f'Fold {key}: {value} %')
    #sum += value
#print(f'Average: {sum/len(results.items())} %')