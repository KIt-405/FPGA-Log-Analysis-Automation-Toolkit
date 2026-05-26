import re
import pandas as pd

def parse_log(file_path):
    # These regex patterns look for standard EDA log formats
    # Example match: "WARNING: [Synth 8-3331] design unisim has unconnected port"
    log_pattern = re.compile(r"^(INFO|WARNING|ERROR):\s+\[(.*?)\]\s+(.*)$")
    
    # Specific pattern to catch timing violations (WNS - Worst Negative Slack)
    timing_pattern = re.compile(r"WNS=([-\d\.]+)ns")

    parsed_data = []

    with open(file_path, 'r') as file:
        for line in file:
            match = log_pattern.match(line.strip())
            if match:
                severity = match.group(1)
                code = match.group(2)
                message = match.group(3)
                
                # Check if this line contains a timing violation
                wns_match = timing_pattern.search(message)
                wns_value = float(wns_match.group(1)) if wns_match else None

                parsed_data.append({
                    "Severity": severity,
                    "Code": code,
                    "Message": message,
                    "WNS (ns)": wns_value
                })
                
    return parsed_data

# Test the parser
raw_data = parse_log('simulation.log')
print(f"Extracted {len(raw_data)} events.")
