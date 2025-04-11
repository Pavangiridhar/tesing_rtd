
import os
import yaml
from pathlib import Path

OUTPUT_DIR = Path("output/docs/Connectors")

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def format_markdown_table(headers, rows):
    table = ["| " + " | ".join(headers) + " |"]
    table.append("|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|")
    for row in rows:
        table.append("| " + " | ".join(row) + " |")
    return "\n".join(table)

def convert_yaml_to_markdown(yaml_path, out_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    md = []

    # Title and Description
    title = data.get("title", yaml_path.stem)
    description = data.get("description", "")
    md.append(f"# {title}\n")
    if description:
        md.append(f"**Description**: {description}\n")

    # Endpoint
    method = data.get("meta", {}).get("method", "GET")
    endpoint = data.get("meta", {}).get("endpoint", "")
    if endpoint:
        md.append("## Endpoint")
        md.append(f"- **Method**: `{method}`")
        md.append(f"- **URL**: `{endpoint}`\n")

    # Inputs
    inputs = data.get("inputs", {}).get("properties", {})
    required_inputs = data.get("inputs", {}).get("required", [])
    if inputs:
        md.append("## Inputs")
        rows = []
        for name, prop in inputs.items():
            dtype = prop.get("type", "")
            desc = prop.get("description", "")
            req = "Yes" if name in required_inputs else "No"
            rows.append([name, dtype, desc, req])
        md.append(format_markdown_table(["Name", "Type", "Description", "Required"], rows))

    # Output Example
    example = data.get("output", {}).get("examples")
    if example:
        md.append("\n## Output Example")
        md.append("```json")
        md.append(yaml.dump(example, default_flow_style=False))
        md.append("```")

    # Output Parameters
    output_props = data.get("output", {}).get("properties", {})
    if output_props:
        md.append("\n## Output Parameters")
        rows = []
        for name, prop in output_props.items():
            if name != "response_headers":
                dtype = prop.get("type", "")
                desc = prop.get("description", "")
                rows.append([name, dtype, desc])
        if rows:
            md.append(format_markdown_table(["Name", "Type", "Description"], rows))

    # Response Headers
    headers = output_props.get("response_headers", {}).get("properties", {})
    if headers:
        md.append("\n## Response Headers")
        rows = []
        for name, prop in headers.items():
            dtype = prop.get("type", "")
            desc = prop.get("description", "")
            rows.append([name, dtype, desc])
        md.append(format_markdown_table(["Header", "Type", "Description"], rows))

    # Error Handling
    messages = output_props.get("json_body", {}).get("properties", {}).get("messages", {})
    if messages:
        md.append("\n## Error Handling")
        md.append("The response may include error messages under the `messages` field in the JSON body.")

    # Write to file
    safe_mkdir(out_path.parent)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"[✔] Wrote: {out_path}")
