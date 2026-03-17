# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Following the [CHANGELOG and Reflection Guidelines](https://github.ubc.ca/mds-2025-26/DSCI_532_viz-2_students/blob/main/milestone1/general_guidelines.md#3-changelog-and-reflection-milestones-24)

## [0.4.0]

### Added

- KPI delta badges showing trend direction (▲/▼) and percentage change from start to end of selected date range
- Info banner on the LLM Chat tab clarifying that sidebar filters do not apply to the chat
- Footer with author names
- CSS flex-reverse on the QueryChat sidebar so the chat input appears at the top

### Changed

- Renamed "Hiring Metric:" selector to "Workforce Trends Metric:"
- KPI value box titles changed from dynamic (`output_text`) to fixed labels ("Hire-Layoff Ratio", "Total Hires", "Total Layoffs")
- KPI values switched from `render.text` to `render.ui` to support rich HTML delta badges
- Removed `.interactive()` from all Altair charts to prevent unintended zoom/scroll behaviour
- Removed chart zoom help text from sidebar
- Resized plots and edited axis labels to be more readable
- Wrapped chart widgets in `overflow:hidden` divs with `fill=False` to eliminate internal scrollbars
- Set LLM Chat `layout_sidebar` to fixed 900px height so the QueryChat panel scrolls internally
- Capped LLM Chat data table card at `max_height="400px"`

### Fixed Issues

- Corrected KPI labels to be more descriptive and accurate
- Fixed LLM visualizations to better reflect QueryChat outputs

## Release Highlight: RAG Knowledge Base

As an advanced feature, we have installed a custom knowledge base for the querychat AI chat interface to help the user get more accurate and relevant responses. This knowledge base includes company aliases, growth definitions, and data reliability definitions. For example, the QueryChat is now better able to understand that "Twitter" refers to "X (Twitter)" and "Google" refers to "Alphabet".

## Collaboration

- Added a custom knowledge base for the querychat AI chat interface to help the user get more accurate and relevant responses.
- Added a dataframe output component to see the filtered dataframe
- Added a data download button that will download the querychat filtered dataframe
- Visual overhaul and QoL improvements

Work was distributed evenly among the team members. We all contributed to the development of the app, but some members took the lead on certain features. We all reviewed each other's code and provided feedback, and all PRs were externally reviewed prior to merging. All team members addressed at least one feedback item, and tested the app locally prior to merging.

### Reflection 0.4.0

Release 0.4.0 addresses all the guidelines listed for Milestone 4 and incorporates or addresses additional feedback from TA, instructor, and our peers.Feedback items were all categorized in terms of priority and addressed accordingly. Critical items concerned issues that directly impacted the user experience and obstructed the user from completing their goals. Minor suggestions or enhancements were labelled as non-critical and addressed as well. Trade-offs were made for feedback items that were too minor, or whose fixes would generate significant complexity or refactoring. These suggestions were mostly an alternative direction for development, and would not significantly improve the user experience or better satisfy our goals.

We also strengthened our tests to ensure these changes are reliable. Our unit tests exercise the get_rendered_text() helper on empty data, typical filtered data, and incorrect argument patterns, confirming that it returns correctly formatted summary strings and raises appropriate errors when misused. In addition, Playwright-based end-to-end tests drive the main Shiny inputs (company selectize and year range slider) under both normal and edge-case configurations, which helps ensure that the core filtering interactions and UI wiring behave as expected after each iteration.

The advanced feature of adding a custom knowledge base for the querychat AI chat interface to help the user get more accurate and relevant responses was a major accomplishment for this release. This knowledge base includes company aliases, growth definitions, and data reliability definitions. The added knowledge base will reinforce QueryChat's utility and make the app more robust.


## [0.3.0]

### Additions

- A querychat AI chat interface
- A dataframe output component to see the filtered dataframe
- At least 2 other output component visualizations that use the querychat filtered dataframe (you can borrow from your original tab) 
- A data download button that will download the querychat filtered dataframe

### Improvements/Fixed Issues

- Addressed all Milestone 2 Feedback (TA and Instructor)
- Relative scale for net change (net_change_pct)
- Add proper notations and format for the number texts
- Change dashboard layout to view plots simultaneously (potentially transpose numbers to the right side)

### Reflection 0.3.0

Based on the work completed so far as per Milestone 3 Guidelines, we have addressed all of the addition items as listed above. We have an AI chat interface which allows us to interact with the filtered data for hiring and layoff trends, alongside a data download button for the querychat filtered dataframe. The other dashboard specific additions are incorporated in `src/app.py` and changes are visible there. We also had certain visual issues for the dashboard that required improvements. By adding these changes, the layout is appropriate for both the user and contributors. These changes include formatting changes, creating new tabs, layout of graphs being accessed, etc.

## [0.2.0]

### Added

- Create an app specification file `m2_spec.md` with job stories, component inventory, reactivity diagram, and calculation details
- A deployment setup is created on Posit Cloud for both the `main` and `dev` branch
- Create `requirements.txt` file with the package dependencies for the dashboard app
- Changes in the M1 sketch in terms of implementable components and optional ones
- Create this `CHANGELOG.md` file to document notable changes

### Changed

- Updated README with the appropriate deployment links for the app
- Implemented all components of the app in `src.py`
- Update job stories from Milestone 1 to match app demands
- Update the component inventory with the functions and descriptions from app
- Updates to `environment.yml` file to match Shiny requirements
- Expand your README to serve two audiences: User and Contributors

### Fixed Issues

- Update the GitHub About section to include the Group Number and the app name
- Transition from improved environment.yml to a pinned requirements.txt for Posit Connect Cloud
- The outputs that were static were changed to reactive as per Milestone 1 Feedback
- Clearly explain the purpose of the app and the curiousity factors

### Reflection 0.2.0

Based on the current state of our app, we have implemented the functions for all job stories and this is a strong foundation for this dashboard. Further contributions and edits will be made over the next couple of milestones to ensure all job stories are appropriately considered and fulfilled. Currently, we have major components for each job story and optional filters as well.

## [0.1.0]

- Repository Creation and Metadata
- Add rough sketch of dashboard
- Create dashboard skeleton
- Add section 4 to proposal
- Add section 1 and 3 to proposal
- Complete Teamwork Contract
- Add CoC and DESCRIPTION
- Add CONTRIBUTING
- Add summary to README
- Add section 2 to the proposal
