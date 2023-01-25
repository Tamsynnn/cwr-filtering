import requests as rq
import pandas as pd
from re import sub
from time import sleep
from tqdm import tqdm


# Define a function to remove trailing whitespace from taxa
def clean_taxon(taxon):
    return sub(r'[ ][^a-z]', '', taxon)


# Specify API endpoint for retrieving data
endpoint = 'https://records-ws.nbnatlas.org/occurrences/index/download'

# Read taxa from file
taxa = pd.read_excel('Species_and_subspecies.xlsx')['Taxon']

# Iterate over each taxon
for taxon in tqdm(taxa):

    # Create HTTP GET request to retrieve taxon data
    request = rq.get(endpoint, params={'q': taxon, 'reasonTypeId': 4, 'dwcHeaders': True})

    # Specify output .zip file location
    filename = '../nbn_api/Species_and_subspecies/{}.zip'.format(taxon.replace(' ', '_').lower())

    # Write request binary content to file
    with open(filename, 'wb') as f:
        f.write(request.content)
    
    # Sleep for 1 second to reduce request frequency
    sleep(1)
 