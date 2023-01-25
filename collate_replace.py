import zipfile
import pandas as pd
import numpy as np
import re
from time import sleep as snooz
from tqdm import tqdm
from tempfile import mkdtemp
import shutil


def clean_taxon(name):
    return re.sub(r'[ ][^a-z]', '', name).replace(' ', '_').lower()


def unclean_name(name):
    return name.capitalize().replace('_', ' ')

# Read data from files
names = pd.read_excel('Species_and_subspecies.xlsx').to_numpy()[:,0].tolist()
updated_names = pd.read_excel('2014_to_2019_taxa_2023.xlsx')

# Sanitise updated names object
updated_names['Old'] = updated_names['Old'].apply(clean_taxon)
updated_names['New'] = updated_names['New'].apply(clean_taxon)

collated_data = []

for name in tqdm(names):
    name = clean_taxon(name) # Sanitise name
    updated_name = name # The default case - name doesn't need to be updated.

    q_name = updated_names['Old'].str.contains(name) # Check whether name needs to be updated
    if q_name.any():
        updated_name = unclean_name(updated_names.loc[q_name]['New'].item())
        
    try:
        filename = 'Species_and_subspecies/{}.zip'.format(name) # Set path to correct zip file
        dir = mkdtemp(dir='F:/') # Create temporary dir to extract zip file to

        # Extract zip file
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(dir)
        
        # Read data from zip file
        data = pd.read_csv('{}/data.csv'.format(dir), dtype=str)
        updated_name = unclean_name(updated_name)        
        data['scientificName_2019'] = updated_name # Add updated_name to new field for all entries 
        collated_data.append(data)
        shutil.rmtree(dir)
    except:
        print('error in {}'.format(name))
        continue

collated_data = pd.concat(collated_data)
collated_data.to_csv('collated_data_20230122.csv')

print(collated_data.head)

