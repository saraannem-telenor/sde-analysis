# SDE Analysis

## Setting Up the Environment

To run this project, it's recommended to use a Python virtual environment to manage dependencies.
It has been run using python3.9.1

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the environment

```bash
source venv/bin/activate
```

### 3. Install required packages

```bash
pip install -r requirements.txt
```

---

## Data Preprocessing

The data preprocessing is done in the following notebooks:

- `preprocess_statkraft_cerra.ipynb`: Handles preprocessing for the Statkraft CERRA dataset.
- `preprocess_real.ipynb`: Handles preprocessing for the real-world dataset.
- `preprocess_altimetri.ipynb`: Performs additional preprocessing on altimetri data to extract elevation information.

These notebooks clean, format, and prepare the data for analysis.


---

## Data Analysis

The main analysis is performed in:

- `analysing_statkraft_cerra.ipynb`

This notebook contains visualizations, comparisons, and insights based on the preprocessed datasets.

---



