from CustomDataset import RepositoryDataset

'''this file can be executed when it's moved to the folder containing the file CustomDataset.py'''

labels = '../random_sample_icse_CO.xls'
output_directory = 'D:/tool_output'

print('---convert dataset labels for training---')
try:
    #labeled repositories should have column headers 'html_url' and 'type', and no empty lines in the columns
    RepositoryDataset.convert_labeled_graphs(labels, f'{output_directory}/csv_files')
except Exception as e:
    print(e)
    print('There is a problem with the labeled dataset. Check format in excel file. Labeled repositories should have column headers html_url and type, and no empty lines in the columns!')
