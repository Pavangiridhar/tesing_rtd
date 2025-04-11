import os
import yaml
import shutil
from pathlib import Path

OUTPUT_DIR = Path("output/docs/Connectors")

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def title_case(s):
    return s[0].upper() + s[1:] if s else s

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

    # Inputs
    inputs = data.get("inputs", {}).get("properties", {})
    required_inputs = data.get("inputs", {}).get("required", [])
    if inputs:
        md_lines.append("## Inputs\n")
        md_lines.append("| Name | Type | Description | Required |")
        md_lines.append("|------|------|-------------|----------|")
        for key, val in inputs.items():
            dtype = val.get("type", "")
            desc = val.get("description", "")
            is_required = "Yes" if key in required_inputs else "No"
            md_lines.append(f"| {key} | {dtype} | {desc} | {is_required} |")

    # Output Example
    example = data.get("output", {}).get("examples")
    if example:
        md_lines.append("\n## Output Example\n")
        md_lines.append("```json")
        md_lines.append(yaml.dump(example, default_flow_style=False))
        md_lines.append("```\n")

    # Output Parameters
    outputs = data.get("output", {}).get("properties", {})
    if outputs:
        md_lines.append("\n## Output Parameters\n")
        md_lines.append("| Name | Type | Description |")
        md_lines.append("|------|------|-------------|")
        for key, val in outputs.items():
            if key == "response_headers":  # handled separately
                continue
            dtype = val.get("type", "")
            desc = val.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    # Response Headers
    headers = outputs.get("response_headers", {}).get("properties", {})
    if headers:
        md_lines.append("\n## Response Headers\n")
        md_lines.append("| Header | Type | Description |")
        md_lines.append("|--------|------|-------------|")
        for key, val in headers.items():
            dtype = val.get("type", "")
            desc = val.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    # Error Handling
    error_msgs = outputs.get("json_body", {}).get("properties", {}).get("messages", {})
    if error_msgs:
        md_lines.append("\n## Error Handling\n")
        md_lines.append("The response may include error messages under the `messages` field in the JSON body.")

    # Write file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def process_connector(connector_dir):
    name = Path(connector_dir).name
    out_root = OUTPUT_DIR / name
    overview_src = Path(connector_dir) / "docs" / "README.md"

    # Overview
    if overview_src.exists():
        safe_mkdir(out_root)
        shutil.copy(overview_src, out_root / "overview.md")

    # Actions and Configurations
    config_dir = Path(connector_dir) / "connector" / "config"
    actions_dir = config_dir / "actions"
    assets_dir = config_dir / "assets"

    out_actions = out_root / "Actions"
    out_configs = out_root / "Configurations"
    safe_mkdir(out_actions)
    safe_mkdir(out_configs)

    for yml in actions_dir.glob("*.yml"):
        convert_yaml_to_markdown(yml, out_actions / f"{yml.stem}.md")

    for yml in assets_dir.glob("*.yml"):
        convert_yaml_to_markdown(yml, out_configs / f"{yml.stem}.md")


def main():
    found_any = False
    for item in Path(".").iterdir():
        if item.is_dir():
            print(f"Checking {item}")
            if (item / "connector").exists():
                print(f"Processing connector: {item}")
                process_connector(item)
                found_any = True
    if not found_any:
        print("No valid connector directories found.")

if __name__ == "__main__":
    main()
