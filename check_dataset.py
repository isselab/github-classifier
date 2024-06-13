import pandas as pd

old_data = '../old_dataset/random_sample_icse_CO.xls'
new_data = '../dataset_200_co.xlsx'

old = pd.read_excel(old_data)
new = pd.read_excel(new_data)
count = 0
for row in old.iterrows():
    object = row[1]
    url = object.get('html_url')
    for other_row in new.iterrows():
        object2 = other_row[1]
        url2 = object2.get('html_url')
        if url == url2:
            print(url)
        else:
            count += 1
print(f'not found: {count/len(old)}')