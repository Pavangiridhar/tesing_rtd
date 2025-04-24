import os
import yaml
import json
import shutil
from pathlib import Path

OUTPUT_DIR = Path("output/docs/Connectors")


def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def convert_yaml_to_markdown(yaml_path, out_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    md_lines = []

    # Title and Description
    title = data.get("title", yaml_path.stem)
    description = data.get("description", "")
    md_lines.append(f"# {title}\n")
    if description:
        md_lines.append(f"**Description**: {description}\n")

    # Endpoint
    endpoint = data.get("meta", {}).get("endpoint", "")
    method = data.get("meta", {}).get("method", "")
    if endpoint or method:
        md_lines.append("## Endpoint\n")
        if endpoint:
            md_lines.append(f"- **URL:** `{endpoint}`")
        if method:
            md_lines.append(f"- **Method:** `{method}`")

    # Inputs
    inputs = data.get("inputs", {}).get("properties", {})
    required = data.get("inputs", {}).get("required", [])
    if inputs:
        has_description = any(inputs[key].get("description") for key in inputs)
        if has_description:
            md_lines.append("## Inputs\n")
            md_lines.append("| Name | Type | Description | Required |")
            md_lines.append("|------|------|-------------|----------|")
            for key, value in inputs.items():
                dtype = value.get("type", "")
                desc = value.get("description", "")
                is_required = "Yes" if key in required else "No"
                md_lines.append(f"| {key} | {dtype} | {desc} | {is_required} |")
        else:
            md_lines.append("## Inputs\n")
            md_lines.append("| Name | Type | Required |")
            md_lines.append("|------|------|----------|")
            for key, value in inputs.items():
                dtype = value.get("type", "")
                is_required = "Yes" if key in required else "No"
                md_lines.append(f"| {key} | {dtype} | {is_required} |")

    # Output section (only if there's an output example or output parameters)
    output = data.get("output", {})
    output_props = output.get("properties", {})
    example = output.get("examples") or output.get("example")
    if output_props or example:
        md_lines.append("## Output\n")

    # Output Example
    if example:
        md_lines.append("### Example\n")
        md_lines.append("```json")
        try:
            md_lines.append(json.dumps(example, indent=2))
        except TypeError:
            md_lines.append(str(example))
        md_lines.append("```")

    # Output Parameters
    output_fields = [key for key in output_props if key != "response_headers"]
    if output_fields:
        has_description = any(output_props[key].get("description") for key in output_fields)
        md_lines.append("### Output Parameters\n")
        if has_description:
            md_lines.append("| Name | Type | Description |")
            md_lines.append("|------|------|-------------|")
            for key in output_fields:
                dtype = output_props[key].get("type", "")
                desc = output_props[key].get("description", "")
                md_lines.append(f"| {key} | {dtype} | {desc} |")
        else:
            md_lines.append("| Name | Type |")
            md_lines.append("|------|------|")
            for key in output_fields:
                dtype = output_props[key].get("type", "")
                md_lines.append(f"| {key} | {dtype} |")

    # Response Headers
    headers = output_props.get("response_headers", {}).get("properties", {})
    if headers:
        has_desc = any(headers[key].get("description") for key in headers)
        md_lines.append("## Response Headers\n")
        if has_desc:
            md_lines.append("| Header | Type | Description |")
            md_lines.append("|--------|------|-------------|")
            for key, value in headers.items():
                dtype = value.get("type", "")
                desc = value.get("description", "")
                md_lines.append(f"| {key} | {dtype} | {desc} |")
        else:
            md_lines.append("| Header | Type |")
            md_lines.append("|--------|------|")
            for key, value in headers.items():
                dtype = value.get("type", "")
                md_lines.append(f"| {key} | {dtype} |")

    # Error Handling (optional, only if present in schema)
    json_body = output_props.get("json_body", {}).get("properties", {})
    messages = json_body.get("messages", {}).get("items", {}).get("properties", {})
    if messages:
        md_lines.append("## Error Handling\n")
        md_lines.append("### Common Error Responses\n")
        md_lines.append("| Status Code | Message | Description | Example |")
        md_lines.append("|-------------|---------|-------------|---------|")
        md_lines.append("| 400 | Bad Request | The request was invalid or cannot be processed. | Invalid search ID or parameters. |")
        md_lines.append("| 401 | Unauthorized | Missing or incorrect authentication. | Invalid API token. |")
        md_lines.append("| 403 | Forbidden | Access to the resource is denied. | No permissions for search. |")
        md_lines.append("| 404 | Not Found | The requested item does not exist. | Search ID not found. |")
        md_lines.append("| 500 | Internal Server Error | A server error occurred. | Unexpected failure in Splunk. |")

        md_lines.append("\n### Error Example\n")
        md_lines.append("```json")
        md_lines.append(json.dumps({
            "messages": [
                {"type": "ERROR", "text": "Search ID not found."}
            ],
            "status_code": 404,
            "reason": "Not Found"
        }, indent=2))
        md_lines.append("```")

    # Write to file
    safe_mkdir(out_path.parent)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[✔] Wrote: {out_path}")

def process_connector(connector_dir):
    connector_name = Path(connector_dir).name
    print(f"🔧 Processing connector: {connector_name}")

    out_root = OUTPUT_DIR / connector_name
    overview_src = Path(connector_dir) / "docs" / "README.md"

    # Write overview as 00_overview.md so it's always first
    if overview_src.exists():
        safe_mkdir(out_root)
        overview_dest = out_root / "00_overview.md"
        shutil.copy(overview_src, overview_dest)
        print(f"[✔] Copied 00_overview.md for {connector_name}")

    actions_dir = Path(connector_dir) / "connector" / "config" / "actions"
    configs_dir = Path(connector_dir) / "connector" / "config" / "assets"

    out_actions = out_root / "Actions"
    out_configs = out_root / "Configurations"
    safe_mkdir(out_actions)
    safe_mkdir(out_configs)

    for yml in sorted(list(actions_dir.glob("*.yml")) + list(actions_dir.glob("*.yaml"))):
        out_md = out_actions / f"{yml.stem}.md"
        convert_yaml_to_markdown(yml, out_md)

    for yml in sorted(list(configs_dir.glob("*.yml")) + list(configs_dir.glob("*.yaml"))):
        out_md = out_configs / f"{yml.stem}.md"
        convert_yaml_to_markdown(yml, out_md)

def main():
    for item in sorted(Path(".").iterdir()):
        if item.is_dir() and (item / "connector").exists():
            process_connector(item)
   
if __name__ == "__main__":
    main()
