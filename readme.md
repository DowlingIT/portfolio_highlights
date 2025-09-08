
# Project Overview

This repository contains a curated collection of professional materials and project highlights. Due to the proprietary nature of much of the content, only sanitized summaries and select case study highlights are included. The purpose of this repository is to showcase relevant experience, support case studies, and provide examples for GitHub contributions, while ensuring all sensitive or confidential information is excluded.

**Connect on LinkedIn:** [Jeremy Dowling](https://www.linkedin.com/in/jeremy-dowling-8ab7579/)

## Case Study Formatting

Case studies in this repository are structured to be compatible with Pandoc, allowing for seamless conversion to Word documents (.docx) as needed.

## Git Contribution Scripts

Most projects were not tracked with github, so the common public contribution information that many like to look at are not readily available.  This repository includes PowerShell scripts for generating information about Git contributions.  

- `GitMetrics.ps1`: Summarizes overall contribution metrics for a repository.
- `GitMetricsByDate.ps1`: Generates contribution metrics for a specified date range.

**Usage:**

1. Open PowerShell and change directory to the target repository:
	```powershell
	cd path\to\your\repo
	```
2. Copy and run the scripts from the `scripts` folder:
	```powershell
	..\GitMetrics.ps1
	..\GitMetricsByDate.ps1 -StartDate "2020-04-01" -EndDate "2021-04-01"
	```


