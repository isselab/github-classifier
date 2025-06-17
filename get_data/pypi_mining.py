import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

def get_project_list():
    response=requests.get("https://pypi.org/simple/")
    soup = BeautifulSoup(response.text, "html.parser")
    packages = [a.text for a in soup.find_all("a")]
    print(len(packages))

    with open('get_data/projects.json',mode='w') as f:
        json.dump(packages,f,indent=4)    

def get_repo(package):
    urls=package['info']['project_urls']
    if not urls==None:
        for key in ['Source','source', 'Repository','Homepage','Home']:
            if key in urls.keys() and 'github' in urls[key]:
                return urls[key]
    return None


def main():
    with open('get_data/projects.json')as f:
        project_list=json.load(f)

    #Filter out applications and libraries
    applications=[]
    libraries=[]
    excluded=0
    not_found=0
    for p in project_list[:1000]:
        r=requests.get(f'https://pypi.org/pypi/{p}/json').json()

        #Apply filtering criteria
        try:
            #Common criteria: Language = Python
            if any(s.startswith('Programming Language :: Python :: 3') for s in r['info']['classifiers']):
                #Filter for libraries
                if any(s.startswith('Topic :: Software Development :: Libraries') for s in r['info']['classifiers']):
                    libraries.append(get_repo(r))
                #Filter for applications
                elif any(s.startswith('Intended Audience :: End Users/Desktop') for s in r['info']['classifiers']):
                    applications.append(get_repo(r))
                else:
                    excluded+=1
        except KeyError:
            #Disregard those not found
            not_found+=1

    print('Applications: ',len(applications))
    print('Libraries: ',len(libraries))
    print("Excluded: ",excluded)
    print("Not found: ",not_found)
    print("Applications without repository:",sum(x is None for x in applications))
    print("Libraries without repository:",sum(x is None for x in libraries))

    #Store results
    with open('get_data/applications.json','w') as f:
        json.dump(list(filter(None,applications)),f,indent=4)
    with open('get_data/libraries.json','w') as f:
        json.dump(list(filter(None,libraries)),f,indent=4)


if __name__=="__main__":
    # get_project_list()
    main()