import os

def create_output_folders(directory):
    if not os.path.exists(directory): 
        os.makedirs(directory)
    #create sub folders for converter output and dataset
    if not os.path.exists(f'{directory}/xmi_files'):
        os.makedirs(f'{directory}/xmi_files')
    if not os.path.exists(f'{directory}/csv_files'):
        os.makedirs(f'{directory}/csv_files')   
    if not os.path.exists(f'{directory}/labeled_repositories'):
        os.makedirs(f'{directory}/labeled_repositories') 