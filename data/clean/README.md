# Hydrovoltaic dataset provenance

The canonical model-ready dataset is
`data/processed/hydrovoltaic_dataset_phase2_input_utf8.csv` (159 records,
52 columns). The source curation workbook is `data/raw/hydrovoltaic_data.xlsx`;
it also contains the controlled vocabulary, data dictionary, and excluded-record
sheet.

Notebooks `01_data_cleaning.ipynb` through
`03_modeling_v7_validation.ipynb` document the main processing sequence. Key
steps include scope screening, exclusion of galvanic and non-comparable systems,
unit and label standardization, and construction of
`log_estimated_power_density`.

The dataset is heterogeneous and cross-literature. Missing values remain for
incompletely reported descriptors such as internal resistance. The older CSVs
stored in `notebooks/` are intermediate or compatibility copies; use the file in
`data/processed/` for final analyses.
