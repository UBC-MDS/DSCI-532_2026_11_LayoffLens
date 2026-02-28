# Milestone 2 - App Specification

## Job Stories

| # | Story | Status | Notes |
|---|-----------|--------|-------|
| 1 | As a job seeker, I want to visualize the distribution of hiring across all the major tech companies to assess where my application efforts would be most fruitful. | ✅ Implemented | Using the Sidebar filters to isolate specific company trends. |
| 2 | When I search a company, I want to know if they're downsizing or laying off workers so that I can devote less time applying there. | ✅ Implemented | Visualized via the line chart with distinct styles for hires vs layoffs. |
| 3 | As an applicant, I want to view the companies with a hiring:layoff ratio to determine which companies seem to be growing their team. | ✅ Implemented | Displayed as a real-time KPI in the dashboard value box. |
| 3 | As an researcher, I want to be able to reset my search filters to quickly view other features. | ✅ Implemented | *Optional Complexity* Created a reset button to clear filters |

## Component Inventory

| ID | Type | Shiny widget/renderer | Depends on | Job Story |
|----|------|----------------------|------------|-----------|
| company | Input | ui.input_selectize() | — | #1, #2, #3 |
| year | Input | ui.input_slider() | — | #1, #2, #3 |
| hiring_metric | Input | ui.input_select() | — | #1 |
| filtered_df | Expression | @reactive.calc | company, year | #1, #2, #3 |
| company_trend_plot | Output | @render_altair | filtered_df | #1, #2 |
| hire_layoff_ratio | Output | @render.text | filtered_df | #3 |
| reset_ui | Effect | @reactive.effect | - | #4 |

## Reactivity Diagram

```mermaid
flowchart TD
  %% Inputs
  A[/company/] 
  B[/year/]

  %% Reactive Expressions
  F{{filtered_df}}

  %% Outputs
  P1([company_trend_plot])
  P2([hire_layoff_ratio])

  %% Connections
  A --> F
  B --> F
  F --> P1
  F --> P2
  ```

## Calculation Details

### 1 `filtered_df`:

- Depends on: `input.company` and `input.year`.
- Transformation: Extracts the list of selected companies from the selectize input and the start/end years from the slider. It then subsets the master dataset to include only rows that match both criteria.
- Consumers: `plot_trends` and `hire_layoff_ratio`.
