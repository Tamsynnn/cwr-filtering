import pandas as pd
from tools import clean_taxon

filename = r'output/filter_output_2023-02-06_2056.csv'
df = pd.read_csv(filename)
map = pd.read_excel(r'data/taxa_concat.xlsx')


df['scientificName_2019'] = df['scientificName_2019'].apply(clean_taxon)
map['Full'] = map['Full'].apply(clean_taxon)
map['Concat'] = map['Concat'].apply(clean_taxon)

df['shortenedTaxa'] = df['scientificName_2019'].replace(map['Full'].to_list(), map['Concat'].to_list())

df.to_csv(filename.replace('filter', 'concat'))
