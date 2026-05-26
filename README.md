# FPGA-Log-Analysis-Automation-Toolkit

A Python-based automation toolkit designed to parse, aggregate, and analyze FPGA simulation and synthesis logs from EDA-style workflows. 

## Features
* **Regex Parsing:** Extracts severe events (Errors/Warnings) and critical timing violations (WNS) from standard EDA text logs.
* **Pandas Aggregation:** Groups recurring failure patterns to prevent log-bloat and accelerate root-cause debugging.
* **Automated Reporting:** Generates a GitHub-styled HTML regression dashboard and structured CSV outputs.

## Project Structure
```text
fpga-log-analyzer/
├── data/
│   └── simulation.log        # Mock EDA output for testing
├── src/
│   └── fpga_parser.py        # Main logic (Parsing, Pandas, HTML output)
├── outputs/                  # Auto-generated reports (CSV/HTML)
└── README.md                 # Project documentation
