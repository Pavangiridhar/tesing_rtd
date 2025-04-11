import os
import yaml
import shutil
from pathlib import Path

OUTPUT_DIR = Path("output/docs/Connectors")


def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)


def convert_yaml_to_markdown(yaml_path, out_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    md_lines = []

    # Title and description
    title = data.get("title", yaml_path.stem)
    description = data.get("description", "")
    md_lines.append(f"# {title}\n")
    if description:
        md_lines.append(f"**Description**: {description}\n")

    # Inputs
    inputs = data.get("inputs", {}).get("properties", {})
    required = data.get("inputs", {}).get("required", [])
    if inputs:
        md_lines.append("## Inputs\n")
        md_lines.append("| Name | Type | Description | Required |")
        md_lines.append("|------|------|-------------|----------|")
        for key, value in inputs.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            is_required = "Yes" if key in required else "No"
            md_lines.append(f"| {key} | {dtype} | {desc} | {is_required} |")

    # Output Example
    example = data.get("output", {}).get("example")
    if example:
        md_lines.append("\n## Output Example\n")
        md_lines.append("```json")
        md_lines.append(yaml.dump(example, default_flow_style=False))
        md_lines.append("```\n")

    # Output Parameters
    output = data.get("output", {}).get("properties", {})
    if output:
        md_lines.append("\n## Output Parameters\n")
        md_lines.append("| Name | Type | Description |")
        md_lines.append("|------|------|-------------|")
        for key, value in output.items():
            if key == "response_headers":
                continue
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    # Response Headers
    headers = output.get("response_headers", {}).get("properties", {})
    if headers:
        md_lines.append("\n## Response Headers\n")
        md_lines.append("| Header | Type | Description |")
        md_lines.append("|--------|------|-------------|")
        for key, value in headers.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    # Error Handling
    if output.get("json_body", {}).get("properties", {}).get("messages"):
        md_lines.append("\n## Error Handling\n")
        md_lines.append("The response may include error messages under the `messages` field in the JSON body.")

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

    # Copy overview
    if overview_src.exists():
        safe_mkdir(out_root)
        shutil.copy(overview_src, out_root / "overview.md")
        print(f"[✔] Copied overview.md for {connector_name}")

    # Convert YAMLs
    actions_dir = Path(connector_dir) / "connector" / "config" / "actions"
    configs_dir = Path(connector_dir) / "connector" / "config" / "assets"

    out_actions = out_root / "Actions"
    out_configs = out_root / "Configurations"
    safe_mkdir(out_actions)
    safe_mkdir(out_configs)

    for yml in actions_dir.glob("*.yml"):
        out_file = out_actions / f"{yml.stem}.md"
        convert_yaml_to_markdown(yml, out_file)

    for yml in configs_dir.glob("*.yml"):
        out_file = out_configs / f"{yml.stem}.md"
        convert_yaml_to_markdown(yml, out_file)


def main():
    root = Path(".")
    for item in root.iterdir():
        if item.is_dir() and (item / "connector").exists():
            process_connector(item)


if __name__ == "__main__":
    main()
