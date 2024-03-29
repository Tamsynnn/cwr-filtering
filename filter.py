import pandas as pd
import numpy as np
import re
from datetime import date, datetime


#Data sources:
#    taxa_data (species, scarcity, lifeform)
#    population data = /Q_analysis/cliiped_v6.dbf
#    source datasets to remove = Filtering/Source_datasets


pop_data = pd.read_csv('data/collated_data_20230122.csv', dtype=str)
taxa_data = pd.read_excel('data/taxa_data_2019_2023.xlsx')
# source_datasets = pd.read_excel('data_resource_names.xlsx')

# Identify datasets which are to be kept
# desired_datasets = source_datasets[source_datasets['Kept'] == 'Y']

def clean_taxon(name):
    try:
        return re.sub(r'[ ][^a-z]', '', name)
    except TypeError:
        print(f'TypeError with name {name}')
        return ''
    
def count_entries(row, source, dest):
    row[dest] = int(np.sum(source['scientificName_2019'] == row['Taxon']))
    return row


# Remove unverified records from pop_data, or records without institution code
q_verified = pop_data['identificationVerificationStatus'].str.contains('Accepted')
q_institution = pop_data['institutionCode'].str.match(r"[A-Za-z]+")
# q_datasets = pop_data['data_resource'].isin(desired_datasets['Data_resource'])
pop_data_verified = pop_data[q_verified & q_institution]
# pop_data_verified = pop_data[q_verified & q_institution & q_datasets]

print('Verified:', len(pop_data_verified.index))

# Clean taxon names
taxa_data['Taxon'] = taxa_data['Taxon'].apply(clean_taxon)
print('Taxa data cleaned')
pop_data['scientificName_2019'] = pop_data['scientificName_2019'].apply(clean_taxon)
print('Pop data cleaned')

# Count no of occurences of each taxon in pop_data_verified
taxa_data['Count'] = pd.Series(dtype='int32')
taxa_data['Count_prefilter'] = pd.Series(dtype='int32')
taxa_data = taxa_data.apply(count_entries, axis=1, args=(pop_data, 'Count_prefilter'))
del pop_data

# Filter based on whether no. records more or less than 100
count_under_100 = taxa_data['Count_prefilter'] < 100
under_100 = taxa_data[count_under_100]
under_100_pop = pop_data_verified[pop_data_verified['scientificName_2019'].isin(under_100['Taxon'])]
over_100  = taxa_data[~count_under_100]
over_100_pop = pop_data_verified[pop_data_verified['scientificName_2019'].isin(over_100['Taxon'])]
del pop_data_verified

print('Under 100:', len(under_100.index), len(under_100_pop.index))

# Filter based on precision
q_is_precise = over_100_pop['coordinateUncertaintyInMeters'].astype('float') <= 2000
is_precise_pop = over_100_pop[q_is_precise]
not_precise_pop = over_100_pop[~q_is_precise]

print(f'Not precise: {len(not_precise_pop)}')

# Filter based on scarcity
q_is_scarce = (over_100['Scarce'] == 'Scarce') | (over_100['Scarce'] == 'Rare')
not_scarce = over_100[~q_is_scarce]
is_scarce = over_100[q_is_scarce]
is_scarce_pop = is_precise_pop[is_precise_pop['scientificName_2019'].isin(is_scarce['Taxon'])]
not_scarce_pop = is_precise_pop[~is_precise_pop['scientificName_2019'].isin(is_scarce['Taxon'])]
del is_precise_pop, over_100, over_100_pop

print('Scarce or rare:', len(is_scarce_pop.index))
print('Not scarce or rare:', len(not_scarce_pop.index))


# Split into herbaceous and woody life form
q_herbaceous = not_scarce['Life_form'].str.contains('Herbaceous')
print(f'Herbaceous taxa: {np.sum(q_herbaceous)}')
herbaceous_pop = not_scarce_pop[not_scarce_pop['scientificName_2019'].isin(not_scarce[q_herbaceous]['Taxon'])].fillna(0)

q_woody = not_scarce['Life_form'].str.contains('Woody')
print(f'Woody taxa: {np.sum(q_woody)}')
woody_pop = not_scarce_pop[not_scarce_pop['scientificName_2019'].isin(not_scarce[q_woody]['Taxon'])].fillna(0)

print('Herbaceous records:', len(herbaceous_pop.index))
print('Woody records:', len(woody_pop.index))

# Remove records older than 5 and 15 years from herbaceous and woody respectively
current_year = int(date.today().year)
age_limits = {
    'herbaceous': 5,
    'woody': 15,
}


q_blank_year_herbaceous = herbaceous_pop['year'] == ''
q_herbaceous_recent = herbaceous_pop[~q_blank_year_herbaceous]['year'].astype('int32') + age_limits['herbaceous'] >= current_year
herbaceous_recent_pop = herbaceous_pop[q_herbaceous_recent]

q_blank_year_woody = woody_pop['year'] == ''
q_woody_recent = woody_pop[~q_blank_year_woody]['year'].astype('int32') + age_limits['woody'] >= current_year
woody_recent_pop = woody_pop[q_woody_recent]

print('Herbaceous recent taxa:', len(herbaceous_recent_pop.index))
print('Woody recent taxa:', len(woody_recent_pop.index))

print('Herbaceous recent pop:', len(herbaceous_recent_pop.index))
print('Woody recent pop:', len(woody_recent_pop.index))

# Output datasets
output = [
    under_100_pop,
    is_scarce_pop,
    herbaceous_recent_pop,
    woody_recent_pop
    ]

# Write output to CSV
formatted_datetime = datetime.now().strftime('%Y-%m-%d_%H%M')
filtered_data = pd.concat(output)
filtered_data.to_csv(f'output/filter_output_{formatted_datetime}.csv')

# Write taxa data with before and after counts to csv
# taxa_data = taxa_data.apply(count_entries, axis=1, args=(filtered_data, 'Count'))
# taxa_data.to_excel('taxa_data_2019_with_counts.xlsx')
