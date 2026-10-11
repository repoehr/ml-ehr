# Using the ML–EHR notebooks with synthetic data

This tutorial shows how to use the repository’s feature-construction and Random
Forest training/evaluation code with synthetic EHR data. The dataset contains
120 simulated subjects (40 cases and 80 controls). Diagnosis, medication and
laboratory features use real Phecode, RxNorm and LOINC terminology; patient
records, values and labels are synthetic.

## Set up the conda environment

Run from the repository root. The versions match the manuscript’s Code
Availability statement: Python 3.10, scikit-learn 1.5.2, scipy 1.13.1,
joblib 1.4.2, numpy 1.26.4, pandas 2.2.2 and xgboost 2.1.2.

```bash
conda create -n ml-ehr-toy python=3.10 -y
conda activate ml-ehr-toy
python -m pip install -r toy_example/requirements.txt
python -m pip install jupyterlab
python -m jupyterlab toy_example/toy_example.ipynb
```

Select the Python kernel from `ml-ehr-toy`, then run the tutorial cells from top
to bottom. An executed [HTML preview](toy_example.html) is also included.

## Follow the tutorial

The original analysis notebooks cover data preprocessing, cohort preprocessing,
feature preprocessing, feature construction for different prediction windows,
and model evaluation. This toy example provides synthetic input tables and a
step-by-step tutorial to help readers run the feature-construction and Random
Forest training and evaluation code from those notebooks, inspect intermediate
feature matrices, and understand the expected inputs and outputs.

[toy_example.ipynb](toy_example.ipynb) uses the supplied input tables to walk
through the feature-construction and RF training/evaluation steps:

1. **Inspect the input tables.** Load the cohort, demographics, diagnosis,
   medication, laboratory and vital-sign tables.
2. **Use the original analysis notebooks.** Load the relevant functions from
   `feature_construction_for_prediction_window.ipynb` and
   `evaluation_retrain_parad.ipynb` for use in the following cells.
3. **Load the split.** Read the cohort’s `split` column: 84 training and 36
   hold-out testing subjects. The same assignments apply across prediction windows.
4. **Select the prediction window and construct the feature matrix.** Set
   `prediction_window` to 0 (1 day), 1, 2, 5 or 10 (years), then call
   `process_features` and inspect the resulting matrix.
5. **Prepare the model inputs.** Call `preprocess` to fit the age scaler on
   training subjects and transform the hold-out inputs.
6. **Model training and evaluation using Random Forest.** Use `build_RF_model`
   and `evaluate_params`, select parameters, fit the RF, and call
   `evaluate_ensemble_model` on hold-out testing.

For a quick run, the tutorial uses two RF settings and three inner folds.
To change the prediction window, rerun from step 4 onward.

## Input tables

The cohort supplies subject IDs, index dates and simulated labels. Diagnosis,
medication, laboratory and vital-sign CSVs have the columns expected by the
original `process_features` function. Demographics include age at index, sex,
race and ethnicity; birth dates allow conversion to age at the prediction window cutoff.

| File in `data/` | Main fields |
| --- | --- |
| cohort.csv | patid, INDEX_DATE, label, split |
| demographics.csv | patid, birth_date, age, sex, race, ethnicity |
| diagnosis.csv | patid, dx_date_fill, phecode, diagnosis_name |
| medication.csv | patid, rx_start_date, rxcui_ing, medication_name |
| laboratory.csv | patid, specimen_date, Class, flag, lab_loinc, result_num, result_unit, norm_range_low, norm_range_high |
| vital.csv | patid, measure_date, ht, wt, systolic, diastolic |

`dx_date_fill` follows the original code’s naming convention for diagnosis
dates: the diagnosis date is used when available, and the admission date is
used when it is missing. Dates use YYYY-MM-DD. Height is
in inches, weight in pounds and blood pressure in mmHg. Laboratory units and
example reference ranges are provided in the CSV.

The six CSV files are ready to use. To regenerate the same dataset with seed 42:

```bash
python toy_example/generate_data.py
```

The tutorial runs locally without patient-data access, credentials or external
medical-service API calls, such as online medication lookup requests. Keep
`toy_example/` inside the repository so the supplied code can locate the original
notebooks and CSV inputs.

## Saved outputs

The notebook saves six files in `toy_example/outputs/` for the currently
selected prediction window:

| File | Contents |
| --- | --- |
| feature_matrix.csv | Feature matrix with patient IDs and labels |
| model_input_train.csv | Training inputs after preprocessing, with IDs and labels |
| model_input_test.csv | Hold-out inputs after preprocessing, with IDs and labels |
| predictions.csv | Hold-out labels and predicted probabilities |
| metrics.csv | Selected window, sample counts, AUROC and average precision |
| rf_model.joblib | Trained RF, age scaler, predictor order, selected parameters and window |

Changing the prediction window and rerunning overwrites these files. Parameter
search results and feature definitions are displayed in the notebook. The
cohort split is already included in `data/cohort.csv`. IDs and labels are
excluded from model predictors. Results illustrate usage on synthetic records.

## Clinical feature examples and terminology sources

- Diagnosis: Phecode 401.1 (essential hypertension) and 250.2 (type 2 diabetes).
  Phecode 250.1 (type 1 diabetes) is recorded only on the index date to test cutoff exclusion.
  Sources: [PheWAS resources](https://phewascatalog.org/phewas/) and
  [MAP paper describing diabetes Phecodes](https://pmc.ncbi.nlm.nih.gov/articles/PMC6798574/).
- Medication: RxNorm ingredient 6809 (metformin), 29046 (lisinopril), 83367 (atorvastatin).
  Sources: [CMS RxNorm code examples](https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/bsapufs/downloads/2010_pd_profiles_puf_datadic_cb.pdf)
  and [NLM RxNav FAQ](https://lhncbc.nlm.nih.gov/RxNav/applications/RxNavFAQ.html).
- Laboratory: [4548-4, hemoglobin A1c](https://loinc.org/4548-4),
  [2345-7, serum/plasma glucose](https://loinc.org/2345-7),
  [2093-3, serum/plasma total cholesterol](https://loinc.org/2093-3).
  Flags are calculated from each simulated result and the example ranges saved
  in the CSV. Those ranges are illustrative; LOINC identifies the test, not its reference range.

Human-readable diagnosis and medication names are included in the inputs;
the notebook displays a dictionary of the resulting predictor columns.

