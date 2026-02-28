# Layoff Lens

Layoff Lens is an interactive Shiny dashboard designed to help job seekers and data scientists navigate the volatile tech employment landscape. By summarizing workforce trends across major tech companies from 2000 to 2025, the tool allows users to cut through the noise of high hiring numbers to identify companies with true net growth.

## Motivation

Raw hiring data can be misleading. We live in a market where a company might hire 1,000 people while simultaneously laying off 1,200. Layoff Lens safeguards users by visualizing the Net Change and Hire-Layoff Ratio. This allows applicants to prioritize companies with a healthy, expanding environment rather than those simply replacing churned staff, helping them avoid pull-back periods following rapid, unsustainable growth.

## Deployed Dashboards

- [Stable Version](https://019c8d0c-d197-57fd-3fdf-d468eac4c556.share.connect.posit.cloud/)
- [Development Preview](https://019c8d14-1608-8384-81a5-8d19259745d4.share.connect.posit.cloud/)

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
# Create and activate a virtual environment
conda env create -f environment.yml
conda activate layoff-lens

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

Use the Shiny CLI to run the app:

```bash
shiny run --reload src/app.py
```

Ensure "hot reload" is enabled. This allows the app to refresh automatically when you save changes.

Once running, open the link displayed on your terminal to view the dashboard.

## Contributing

Interested in contributing to **LayoffLens**? We welcome pull requests! Please review our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, branch naming conventions, and the process for submitting pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.