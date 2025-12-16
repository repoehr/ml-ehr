
> Column names may need minor adjustment depending on your site export.  

### Required mapping / resource files
The pipeline expects several resource files in the repo root (or update the paths in notebooks):
- `ADRD_dx_med_codes.csv` (AD/ADRD diagnosis codes + anti-dementia medication codes)
- `icd2phecode.csv` (ICD → Phecode mapping)
- `Collected_lab_tests_for_ADRD_evaluation_M_online.xlsx` (lab selection/metadata)

---

## Quickstart (recommended notebook order)

1. **Data cleaning**
   - Run `data_preprocessing.ipynb`
   - Verify the `EHR/*_*_all.pkl` outputs exist.

2. **Cohort + matching**
   - Run `cohort_preprocessing.ipynb`
   - This creates `Middle/`, `Middle/splits/`, and `PSM_results/`.

3. **Feature preprocessing**
   - Run `feature preprocessing.ipynb`
   - This creates processed domain-level tables in `MiddleFeatures/`.

4. **Feature matrix construction**
   - Run `feature_construction_for_prediction_window.ipynb`
   - This produces matched/unmatched matrices used by evaluation.

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
- prediction windows (commonly `[10, 5, 2, 1, 0]` where `0` may represent “1-day”)
- site list: `['wcm', 'columbia', 'montefiore', 'mshs', 'nyu']`

---

## Environment / dependencies

The core stack is:
- Python 3.9+ (tested with common scientific Python stacks)
- `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `seaborn`
- `tqdm`, `dill`
- `plotnine` (optional, for ggplot-style figures)
- `patchworklib` (optional, for figure composition)

You can start with:
```bash
pip install numpy pandas scikit-learn matplotlib seaborn tqdm dill plotnine patchworklib
