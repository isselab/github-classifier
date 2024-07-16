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

repository_directory = 'D:/classifyhub_dataset_repos'  #downloaded github repositories
output_directory = 'D:/classifyhub_converted_output'
labels = 'data/classifyhub-dataset.xlsx'
n_epoch = 100
k_folds = 3 #has to be at least 2
learning_rate = 0.001
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot_alt_data'
threshold = 0.5 #value above which label is considered to be predicted by model
save_classification_reports = 'classification_reports/train_with_classifyhub_100epochs1.txt'
experiment_name = 'train_with_classifyhub_100epochs1'

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

#create a new MLflow Experiment
mlflow.create_experiment(experiment_name)
mlflow.set_experiment(experiment_name)

#k-fold cross validation
kfold = KFold(n_splits=k_folds, shuffle=True)

#for classification reports
reports = {}

#initialize overall model performance with negative infinity
best_avg = - np.inf

#training loop
for f, fold in enumerate(kfold.split(dataset)):
    #split into train and testset
    trainset, testset = random_split(dataset, [0.8, 0.2])
    print(f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=32, shuffle=False)
    print(f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')

    #log model parameters
    params = {"lr": learning_rate}
    for name, param in model.named_parameters():
        if param.requires_grad:
            params[f"{name}"] = param.data

    latex_table_train = open(f'latex_results_train_{f}.txt', 'a')
    latex_table_test = open(f'latex_results_test_{f}.txt', 'a')

    with mlflow.start_run():
        plt_epoch = []
        plt_train_loss = []
        plt_dev_train = []
        plt_edu_train  = []
        plt_hw_train  = []
        plt_other_train = []
        plt_test_loss = []
        plt_dev_test = []
        plt_edu_test  = []
        plt_hw_test  = []
        plt_other_test = []
        mlflow.log_params(params)

        for epoch in range(n_epoch):
            print(f'Fold {f}, Epoch {epoch}')
            train()
            train_loss, train_report, train_rep_dict = test(trainloader)
            test_loss, test_report, test_rep_dict = test(testloader)

            #log loss
            metrics = {"training loss":train_loss, "test loss":test_loss}
            mlflow.log_metrics(metrics, step=epoch) #one folder per fold, because metrics needs to be key value pairs not dicts
            reports[f'Fold_{f}_Epoch_{epoch}_train'] = train_report
            reports[f'Fold_{f}_Epoch_{epoch}_test'] = test_report
            
            #for plotting train results
            plt_epoch.append(epoch)
            plt_train_loss.append(train_loss)
            dev_train = train_rep_dict['Dev']
            dev_f1_train = dev_train['f1-score']
            plt_dev_train.append(dev_f1_train)
            edu_train = train_rep_dict['Edu']
            edu_f1_train = edu_train['f1-score']
            plt_edu_train.append(edu_f1_train)
            hw_train = train_rep_dict['Hw']
            hw_f1_train = hw_train['f1-score']
            plt_hw_train.append(hw_f1_train)
            other_train = train_rep_dict['Other']
            other_f1_train = other_train['f1-score']
            plt_other_train.append(other_f1_train)

            #for writing training results in a latex table
            latex_table_train.write('\hline')
            latex_table_train.write('\n')
            dev_prec_train = dev_train['precision']
            dev_recall_train = dev_train['recall']
            edu_prec_train = edu_train['precision']
            edu_recall_train = edu_train['recall']
            hw_prec_train = hw_train['precision']
            hw_recall_train = hw_train['recall']
            other_prec_train = other_train['precision']
            other_recall_train = other_train['recall']
            latex_table_train.write(f'  {epoch} & ')
            latex_table_train.write('%4.3f %4.3f %4.3f & %4.3f %4.3f %4.3f & %4.3f %4.3f %4.3f & %4.3f %4.3f %4.3f \\' % (dev_prec_train, dev_recall_train, dev_f1_train, edu_prec_train, edu_recall_train, edu_f1_train, hw_prec_train, hw_recall_train, hw_f1_train, other_prec_train, other_recall_train, other_f1_train))
            latex_table_train.write('\n')

            #for plotting test results
            plt_test_loss.append(test_loss)
            dev_test = test_rep_dict['Dev']
            dev_f1_test = dev_test['f1-score']
            plt_dev_test.append(dev_f1_test)
            edu_test = test_rep_dict['Edu']
            edu_f1_test = edu_test['f1-score']
            plt_edu_test.append(edu_f1_test)
            hw_test = test_rep_dict['Hw']
            hw_f1_test = hw_test['f1-score']
            plt_hw_test.append(hw_f1_test)
            other_test = test_rep_dict['Other']
            other_f1_test = other_test['f1-score']
            plt_other_test.append(other_f1_test)

            #for writing test results in a latex table
            latex_table_test.write('\hline')
            latex_table_test.write('\n')
            dev_prec_test = dev_test['precision']
            dev_recall_test = dev_test['recall']
            edu_prec_test = edu_test['precision']
            edu_recall_test = edu_test['recall']
            hw_prec_test = hw_test['precision']
            hw_recall_test = hw_test['recall']
            other_prec_test = other_test['precision']
            other_recall_test = other_test['recall']
            latex_table_test.write(f'  {epoch} & ')
            latex_table_test.write('%4.3f %4.3f %4.3f & %4.3f %4.3f %4.3f & %4.3f %4.3f %4.3f & %4.3f %4.3f %4.3f \\' % (dev_prec_test, dev_recall_test, dev_f1_test, edu_prec_test, edu_recall_test, edu_f1_test, hw_prec_test, hw_recall_test, hw_f1_test, other_prec_test, other_recall_test, other_f1_test))
            latex_table_test.write('\n')
            
            #print results
            print(f'training loss: {train_loss}')
            print(f'testing loss: {test_loss}')
            print('==============================================')
            print(f'f1-score of Dev during testing: {dev_f1_test}')
            print(f'f1-score of Edu during testing: {edu_f1_test}')
            print(f'f1-score of Hw during testing: {hw_f1_test}')
            print(f'f1-score of Other during testing: {other_f1_test}')
            av_test = test_rep_dict['weighted avg']
            f1_test = av_test['f1-score']
            print(f'weighted average of labels (f1-score) during testing: {f1_test}')
            print('==============================================')
            
            #save trained model with best performance
            if best_avg < f1_test:
                best_avg = f1_test
                torch.save(model, 'graph_classification_model.pt')

        #write classification reports in file
        report_file = open(save_classification_reports, 'a')
        for key, value in reports.items():
            report_file.write(f'{key}:')
            report_file.write('\n')
            report_file.write(f'{value}')
            report_file.write('\n')
        report_file.close()
        
        #plot visualization for training
        fig_n = f + k_folds + 1 #so figures are separate for training and testing
        fig = plt.figure(fig_n)
        fig, (ax1,ax2) = plt.subplots(2)
        fig.suptitle(f'Fold {f}')
        ax1.plot(plt_epoch, plt_train_loss, 'k', label='test loss')
        ax1.set(ylabel='train loss')
        ax2.plot(plt_epoch, plt_dev_train, 'r', label='Dev')
        ax2.plot(plt_epoch, plt_edu_train, 'g', label='Edu')
        ax2.plot(plt_epoch, plt_hw_train, 'b', label='Hw')
        ax2.plot(plt_epoch, plt_other_train, 'y', label='Other')
        ax2.set(xlabel='epoch', ylabel='f1 score')
        plt.legend()
        plt.savefig(f'{figure_output}/fig_{f}_train.pdf', bbox_inches='tight')

        #plot visualization for testing
        fig = plt.figure(f)
        fig, (ax1,ax2) = plt.subplots(2)
        fig.suptitle(f'Fold {f}')
        ax1.plot(plt_epoch, plt_test_loss, 'k', label='test loss')
        ax1.set(ylabel='test loss')
        ax2.plot(plt_epoch, plt_dev_test, 'r', label='Dev')
        ax2.plot(plt_epoch, plt_edu_test, 'g', label='Edu')
        ax2.plot(plt_epoch, plt_hw_test, 'b', label='Hw')
        ax2.plot(plt_epoch, plt_other_test, 'y', label='Other')
        ax2.set(xlabel='epoch', ylabel='f1 score')
        plt.legend()
        plt.savefig(f'{figure_output}/fig_{f}_test.pdf', bbox_inches='tight')

mlflow.end_run()
