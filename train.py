import matplotlib.pylab as plt
import mlflow
import numpy as np
import torch
import torch.nn.functional as nn
from sklearn.metrics import classification_report
from sklearn.model_selection import KFold
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader

from CustomDataset import RepositoryDataset
from GCN import GCN
from GraphClasses import defined_labels
from settings import CONFIG

'''please prepare the dataset you want to train the tool with by using prepareDataset.py,
this file is for training the tool'''

# Load settings from Config
output_directory = CONFIG['training']['output_directory']
labels = CONFIG['training']['labels_file']
n_epoch = CONFIG['training']['n_epoch']
k_folds = CONFIG['training']['k_folds']
learning_rate = CONFIG['training']['learning_rate']
figure_output = CONFIG['training']['figure_output']
threshold = CONFIG['training']['threshold']
save_classification_reports = CONFIG['training']['save_classification_reports']
experiment_name = CONFIG['training']['experiment_name']


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

        # prepare input
        size = int(len(graph.y) / num_classes)
        graph.x = nn.normalize(graph.x, p=0.5)
        graph.edge_attr = nn.normalize(graph.edge_attr, p=2.0)
        graph.y = torch.reshape(graph.y, (size, num_classes))

        output = model(graph.x, graph.edge_index, graph.edge_attr, graph.batch)
        loss_train = criterion(output, graph.y)  # graph.y is label

        # backpropagation
        optimizer.zero_grad()
        loss_train.backward()

        # update weights
        optimizer.step()


def test(loader):
    global class_report, report_dict
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

        # prepare input
        size = int(len(graph.y) / num_classes)
        graph.y = torch.reshape(graph.y, (size, num_classes))

        # evaluate model
        output = model(graph.x, graph.edge_index, graph.edge_attr, graph.batch)
        loss = criterion(output, graph.y)
        loss_test += loss.item()
        total += len(loader)

        output = output.cpu().detach().numpy()
        graph.y = graph.y.cpu().detach().numpy()

        # transform output, if value above threshold label is considered to be predicted
        output = np.array(output)
        # Transform output based on the threshold T -> 1 , F -> 0
        output_after_threshold = (output >= threshold).astype(float)
        # Reshape the output to the desired shape
        output_after_threshold = output_after_threshold.reshape((size, num_classes))

        # better evaluation metrics for multilabel: precision, recall, f1_score
        # report is string, dict to extract results
        report_dict = classification_report(graph.y, output_after_threshold, target_names=defined_labels,
                                            output_dict=True)
        class_report = classification_report(graph.y, output_after_threshold, target_names=defined_labels)

    return loss_test / total, class_report, report_dict


print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
    print(f'Dataset size: {dataset.__len__()}')
except Exception as e:
    print(e)
    exit('Dataset can not be loaded.')

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=32)

if device == 'cuda':
    model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), learning_rate)
criterion = torch.nn.MultiLabelSoftMarginLoss()

# create a new MLflow Experiment
mlflow.create_experiment(experiment_name)
mlflow.set_experiment(experiment_name)

# k-fold cross validation
kfold = KFold(n_splits=k_folds, shuffle=True)

# for classification reports
reports = {}

# initialize overall model performance with negative infinity
best_avg = - np.inf

# training loop
for f, fold in enumerate(kfold.split(dataset)):
    # split into train and testset
    trainset, testset = random_split(dataset, [0.9, 0.1])
    print(
        f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=32, shuffle=False)
    print(
        f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')

    # log model parameters
    params = {"lr": learning_rate}
    for name, param in model.named_parameters():
        if param.requires_grad:
            params[f"{name}"] = param.data

    with mlflow.start_run():
        plt_epoch = []
        plt_train_loss = []
        plt_app_train = []
        plt_frame_train = []
        plt_lib_train = []
        plt_plugin_train = []
        plt_test_loss = []
        plt_app_test = []
        plt_frame_test = []
        plt_lib_test = []
        plt_plugin_test = []
        mlflow.log_params(params)

        for epoch in range(n_epoch):
            print(
                f'Fold {f}, Epoch {epoch}')
            train()
            train_loss, train_report, train_rep_dict = test(trainloader)
            test_loss, test_report, test_rep_dict = test(testloader)

            # log loss
            metrics = {"training loss": train_loss, "test loss": test_loss}
            mlflow.log_metrics(metrics,
                               step=epoch)  # one folder per fold, because metrics needs to be key value pairs not dicts
            reports[f'Fold_{f}_Epoch_{epoch}_train'] = train_report
            reports[f'Fold_{f}_Epoch_{epoch}_test'] = test_report

            # for plotting train results
            plt_epoch.append(epoch)
            plt_train_loss.append(train_loss)
            app_train = train_rep_dict['Application']
            app_f1_train = app_train['f1-score']
            plt_app_train.append(app_f1_train)
            frame_train = train_rep_dict['Framework']
            frame_f1_train = frame_train['f1-score']
            plt_frame_train.append(frame_f1_train)
            lib_train = train_rep_dict['Library']
            lib_f1_train = lib_train['f1-score']
            plt_lib_train.append(lib_f1_train)
            plugin_train = train_rep_dict['Plugin']
            plugin_f1_train = plugin_train['f1-score']
            plt_plugin_train.append(plugin_f1_train)

            # for plotting test results
            plt_test_loss.append(test_loss)
            app_test = test_rep_dict['Application']
            app_f1_test = app_test['f1-score']
            plt_app_test.append(app_f1_test)
            frame_test = test_rep_dict['Framework']
            frame_f1_test = frame_test['f1-score']
            plt_frame_test.append(frame_f1_test)
            lib_test = test_rep_dict['Library']
            lib_f1_test = lib_test['f1-score']
            plt_lib_test.append(lib_f1_test)
            plugin_test = test_rep_dict['Plugin']
            plugin_f1_test = plugin_test['f1-score']
            plt_plugin_test.append(plugin_f1_test)

            # print results
            print(f'training loss: {train_loss}')
            print(f'testing loss: {test_loss}')
            print('==============================================')
            print(f'f1-score of application during testing: {app_f1_test}')
            print(f'f1-score of framework during testing: {frame_f1_test}')
            print(f'f1-score of library during testing: {lib_f1_test}')
            print(f'f1-score of plugin during testing: {plugin_f1_test}')
            av_test = test_rep_dict['weighted avg']
            f1_test = av_test['f1-score']
            print(f'weighted average of labels (f1-score) during testing: {f1_test}')
            print('==============================================')

            # save trained model with best performance
            if best_avg < f1_test:
                best_avg = f1_test
                torch.save(model, 'graph_classification_model.pt')

        # write classification reports in file
        report_file = open(save_classification_reports, 'a')
        for key, value in reports.items():
            report_file.write(f'{key}:')
            report_file.write('\n')
            report_file.write(f'{value}')
            report_file.write('\n')
        report_file.close()

        # plot visualization for training
        fig_n = f + k_folds + 1  # so figures are separate for training and testing
        fig = plt.figure(fig_n)
        _, (ax1, ax2) = plt.subplots(2)
        fig.suptitle(f'Fold {f}')
        ax1.plot(plt_epoch, plt_train_loss, 'k', label='test loss')
        ax1.set(ylabel='train loss')
        ax2.plot(plt_epoch, plt_app_train, 'r', label='Application')
        ax2.plot(plt_epoch, plt_frame_train, 'g', label='Framework')
        ax2.plot(plt_epoch, plt_lib_train, 'b', label='Library')
        ax2.plot(plt_epoch, plt_plugin_train, 'y', label='Plugin')
        ax2.set(xlabel='epoch', ylabel='f1 score')
        plt.legend()
        plt.savefig(f'{figure_output}/fig_{f}_train.pdf', bbox_inches='tight')

        # plot visualization for testing
        fig = plt.figure(f)
        _, (ax1, ax2) = plt.subplots(2)
        fig.suptitle(f'Fold {f}')
        ax1.plot(plt_epoch, plt_test_loss, 'k', label='test loss')
        ax1.set(ylabel='test loss')
        ax2.plot(plt_epoch, plt_app_test, 'r', label='Application')
        ax2.plot(plt_epoch, plt_frame_test, 'g', label='Framework')
        ax2.plot(plt_epoch, plt_lib_test, 'b', label='Library')
        ax2.plot(plt_epoch, plt_plugin_test, 'y', label='Plugin')
        ax2.set(xlabel='epoch', ylabel='f1 score')
        plt.legend()
        plt.savefig(f'{figure_output}/fig_{f}_test.pdf', bbox_inches='tight')

mlflow.end_run()
