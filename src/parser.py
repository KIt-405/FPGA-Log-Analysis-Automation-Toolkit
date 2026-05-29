import re
import pandas as pd
import argparse
import os

def parse_log(file_path):
    print(f"[*] Parsing log file: {file_path}")
    
    log_pattern = re.compile(r"^(INFO|WARNING|ERROR):\s+\[(.*?)\]\s+(.*)$")
    timing_pattern = re.compile(r"WNS=([-\d\.]+)ns")

    parsed_data = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = log_pattern.match(line.strip())
                if match:
                    severity = match.group(1)
                    code = match.group(2)
                    message = match.group(3)
                    
                    wns_match = timing_pattern.search(message)
                    wns_value = float(wns_match.group(1)) if wns_match else None

                    parsed_data.append({
                        "Severity": severity,
                        "Code": code,
                        "Message": message,
                        "WNS (ns)": wns_value
                    })
    except FileNotFoundError:
        print(f"[!] Error: Could not find {file_path}")
        exit(1)
                
    return parsed_data

def analyze_data(raw_data):
    print("[*] Analyzing and aggregating data...")
    df = pd.DataFrame(raw_data)
    
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    issues_df = df[df['Severity'].isin(['WARNING', 'ERROR'])]
    
    # Count occurrences of identical errors/warnings
    summary_df = issues_df.groupby(['Severity', 'Code', 'Message']).size().reset_index(name='Occurrences')
    summary_df = summary_df.sort_values(by=['Severity', 'Occurrences'], ascending=[True, False])
    
    # Isolate negative slack
    timing_failures = df[df['WNS (ns)'].notnull()].sort_values(by='WNS (ns)', ascending=True)
    
    return summary_df, timing_failures

def generate_github_report(summary_df, timing_df, output_dir):
    """Generates a GitHub Dark Mode styled HTML report and a CSV summary."""
    print(f"[*] Generating reports in: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save CSV
    csv_path = os.path.join(output_dir, "log_summary.csv")
    summary_df.to_csv(csv_path, index=False)
    
    # Generate GitHub-styled HTML
    html_path = os.path.join(output_dir, "regression_report.html")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FPGA Regression Report</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                background-color: #0d1117;
                color: #c9d1d9;
                padding: 40px;
                max-width: 1000px;
                margin: 0 auto;
            }}
            h1, h2 {{
                border-bottom: 1px solid #21262d;
                padding-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                margin-bottom: 30px;
                background-color: #161b22;
                border-radius: 6px;
                overflow: hidden;
            }}
            th, td {{
                border: 1px solid #30363d;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #21262d;
                font-weight: 600;
            }}
            .ERROR {{ color: #f85149; font-weight: bold; }}
            .WARNING {{ color: #d29922; }}
        </style>
    </head>
    <body>
        <h1>FPGA Log Analysis Report</h1>
        
        <h2>Critical Timing Violations (WNS)</h2>
        {timing_df[['Code', 'WNS (ns)', 'Message']].to_html(index=False, classes='table') if not timing_df.empty else "<p>No timing violations found.</p>"}

        <h2>Aggregated Warnings & Errors</h2>
        {summary_df.to_html(index=False, classes='table')}
    </body>
    </html>
    """
    
    with open(html_path, "w") as f:
        f.write(html_content)
        
    print(f"[+] Success! Open {html_path} in your browser to view.")

if __name__ == "__main__":
    # Command Line Interface Setup
    parser = argparse.ArgumentParser(description="Parse and analyze FPGA EDA log files.")
    parser.add_argument("--input", required=True, help="Path to the EDA log file (e.g., data/simulation.log)")
    parser.add_argument("--outdir", default="outputs", help="Directory to save the generated reports")
    
    args = parser.parse_args()
    
    # Run the pipeline
    raw_data = parse_log(args.input)
    summary, timing = analyze_data(raw_data)
    generate_github_report(summary, timing, args.outdir)
