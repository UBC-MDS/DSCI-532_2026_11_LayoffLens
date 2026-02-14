# Layoff Lens

This is a Shiny Dashboard that aims to give data scientists and related interest groups the tools necessary to summarize workforce trends in 25 major companies and how it has changed from their respective beginning point in the data to 2025. Such tools such as company selection or industry filtering allow the dashboard to display certain companies that the user is interested in.

(Project title and 3-4 sentence summary).

## Local Development

To run the dashboard locally, follow these steps:

### Clone the Repository

```bash
git clone https://github.com/UBC-MDS/DSCI-532_2026_11_LayoffLens.git
cd DSCI-532_2026_11_LayoffLens
```

### Set Up the Environment

Ensure you have `conda` or `mamba` installed.

```bash
conda env create -f environment.yml
conda activate layoff-lens
```

### Run the Dashboard

Navigate to the source directory and run the app script:

```bash
python src/app.py
```

Once running, open your browser and go to [this link](http://127.0.0.1:8050/) to view the skeleton dashboard.
