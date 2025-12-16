
> Column names may need minor adjustment depending on your site export.  

### Required mapping / resource files
The pipeline expects several resource files in the repo root (or update the paths in notebooks):
- `ADRD_dx_med_codes.csv` (AD/ADRD diagnosis codes + anti-dementia medication codes)
- `icd2phecode.csv` (ICD → Phecode mapping)
- `Collected_lab_tests_for_ADRD_evaluation_M_online.xlsx` (lab selection/metadata)

---

## Quickstart (recommended notebook order)

1. **Data extraction and cleaning**
   - Run `data_preprocessing.ipynb`

2. **Cohort construction + case-control matching**
   - Run `cohort_preprocessing.ipynb`

3. **Feature preprocessing for different EHR data types**
   - Run `feature preprocessing.ipynb`

4. **Feature matrix construction based on different prediction windows**
   - Run `feature_construction_for_prediction_window.ipynb`

5. **Evaluation**
   - Choose one of:
     - `evaluation_direct_parad.ipynb`
     - `evaluation_finetune_parad.ipynb`
     - `evaluation_retrain_parad.ipynb`

---

## Key configuration knobs

Most notebooks expose a few important parameters near the top:
- `hold_out_portion` (e.g., `0.5` for 50% hold-out)
- matching `ratio` (e.g., `10` for 1:10 case-control)
- prediction windows (commonly `[10, 5, 2, 1, 0]` where `0` represents “1-day”)
- site list
---

## Environment / dependencies

The core stack is:
- Python 3.10 
- `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `seaborn`
- `tqdm`, `dill`
- `plotnine` (optional, for ggplot-style figures)
- `patchworklib` (optional, for figure composition)

You can start with:
```bash
pip install numpy pandas scikit-learn matplotlib seaborn tqdm dill plotnine patchworklib
