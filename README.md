# URJA-TEZHACK2026-ML08

## Reference

## About the dataset
A high-resolution three-year dataset supporting rooftop photovoltaics (PV) generation analytics

article link
https://www.nature.com/articles/s41597-025-04397-y#Sec8

database link
https://datadryad.org/dataset/doi:10.5061/dryad.m37pvmd99 

### Objective
To forecast solar power generation with respect to weather parameters.

### Data Preprocessing

#### Stage-1
unzip the Dataset
and paste the 'Dataset; folder under '/data'

1. Fix typo in metadata
at file 'PV generation system metadata.ttl'
fix `brick:value 68.62 ] .` to `brick:value 68.62 ] ;` at line number 876

2. merge meterological data
run `merge-meteorological-data.ipynb`

3. merge pv generation data
run `merge-pv-data.ipynb`

#### Stage-2
run `normolize-generation.ipynb`

1. Create site_id_ttl to filename mapping
2. add column 'ratedPowerKW' to pv-generation data

#### Stage-3
run `pretrain_preprocessing.ipynb`
1. fixed length output size
2. Split training and testing data
training < 2023
testing > 2022

### Expected Output
