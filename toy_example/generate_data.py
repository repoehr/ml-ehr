"""Generate deterministic, entirely synthetic processed EHR tables (no real records)."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def main():
    out = Path(__file__).resolve().parent / 'data'
    out.mkdir(exist_ok=True)
    rng = np.random.default_rng(42)
    cohort, demo, dx, rx, lab, vital = [], [], [], [], [], []
    for i in range(120):
        pid = 900001 + i
        label = int(i < 40)
        cohort.append([pid, '2020-01-01', label])
        birth = pd.Timestamp(f'{int(rng.integers(1935,1960))}-06-15')
        age = round((pd.Timestamp('2020-01-01') - birth).days / 365.25, 3)
        demo.append([pid, birth.strftime('%Y-%m-%d'), age,
                     ['Female', 'Male'][i % 2],
                     ['White', 'Black or African American', 'Asian', 'Other'][i % 4],
                     ['Not Hispanic or Latino', 'Hispanic or Latino'][int(i % 5 == 0)]])
        # All subjects have >11 years of history. Labels are simulated,
        # not inferred from diagnostic codes or a clinical case definition.
        for date in ['2008-01-01', '2014-01-01', '2018-01-01']:
            dx.append([pid, date, '401.1', 'Essential hypertension'])
            if rng.random() < (0.65 if label else 0.35):
                dx.append([pid, date, '250.2', 'Type 2 diabetes'])
            ingredient = 6809 if rng.random() < (0.6 if label else 0.4) else 29046
            rx.append([pid, date, ingredient, 'metformin' if ingredient == 6809 else 'lisinopril'])
            if rng.random() < 0.4:
                rx.append([pid, date, 83367, 'atorvastatin'])
            for loinc, name, unit, low, high, mean, sd in [
                ('4548-4', 'hemoglobin_a1c', '%', 4.0, 5.6, 5.8, 1.0),
                ('2345-7', 'glucose', 'mg/dL', 70, 110, 105, 30),
                ('2093-3', 'total_cholesterol', 'mg/dL', 100, 200, 185, 40)]:
                value = round(max(0.1, rng.normal(mean, sd)), 2)
                flag = 'ablow' if value < low else 'abhigh' if value > high else 'nor'
                lab.append([pid, date, name, flag, loinc, value, unit, low, high])
            # inches and pounds, following the existing BMI implementation.
            vital.append([pid, date, 66, int(rng.integers(120,190)), int(rng.integers(105,150)), int(rng.integers(65,95))])
        # Type 1 diabetes occurs only on the index date: cutoff exclusion probe.
        dx.append([pid, '2020-01-01', '250.1', 'Type 1 diabetes'])
    tables = {
        'cohort': (cohort, ['patid','INDEX_DATE','label']),
        'demographics': (demo, ['patid','birth_date','age','sex','race','ethnicity']),
        'diagnosis': (dx, ['patid','dx_date_fill','phecode','diagnosis_name']),
        'medication': (rx, ['patid','rx_start_date','rxcui_ing','medication_name']),
        'laboratory': (lab, ['patid','specimen_date','Class','flag','lab_loinc','result_num','result_unit','norm_range_low','norm_range_high']),
        'vital': (vital, ['patid','measure_date','ht','wt','systolic','diastolic']),
    }
    cohort_df = pd.DataFrame(cohort, columns=['patid', 'INDEX_DATE', 'label'])
    train_ids, _ = train_test_split(cohort_df.patid, test_size=0.3,
                                    stratify=cohort_df.label, random_state=42)
    cohort_df['split'] = np.where(cohort_df.patid.isin(train_ids), 'train', 'hold_out_test')
    tables['cohort'] = (cohort_df.values.tolist(), cohort_df.columns.tolist())
    for name, (rows, columns) in tables.items():
        pd.DataFrame(rows, columns=columns).to_csv(out / f'{name}.csv', index=False)
    print(f'Wrote {len(tables)} synthetic CSV tables to {out}')


if __name__ == '__main__':
    main()
