import os
import yaml
import shutil
from pathlib import Path

OUTPUT_DIR = Path("output/docs/Connectors")


def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)


def title_case(s):
    return s[:1].upper() + s[1:] if s else s


def convert_yaml_to_markdown(yaml_path, out_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    md_lines = []

    # Overview
    title = data.get("title", "Untitled")
    desc = data.get("description", "")
    md_lines.append(f"# {title}\n")
    md_lines.append(f"**Description**: {desc}\n")

    # Inputs
    inputs = data.get("inputs", {}).get("properties", {})
    required = data.get("inputs", {}).get("required", [])
    if inputs:
        md_lines.append("## Inputs\n")
        md_lines.append("| Name | Type | Description | Required |\n|------|------|-------------|----------|")
        for key, value in inputs.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            is_required = "Yes" if key in required else "No"
            md_lines.append(f"| {key} | {dtype} | {desc} | {is_required} |")

    # Outputs
    output = data.get("output", {}).get("properties", {})
    if output:
        md_lines.append("\n## Output Parameters\n")
        md_lines.append("| Name | Type | Description |\n|------|------|-------------|")
        for key, value in output.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    # Write file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def process_connector(connector_dir):
    name = Path(connector_dir).name
    formatted_name = name.replace("t_", "")
    out_root = OUTPUT_DIR / formatted_name

    overview_src = Path(connector_dir) / "docs" / "README.md"
    if overview_src.exists():
        overview_dest = out_root / "overview.md"
        safe_mkdir(out_root)
        shutil.copy(overview_src, overview_dest)

    # Configurations
    config_dir = Path(connector_dir) / "connector" / "config"
    actions_dir = config_dir / "actions"
    assets_dir = config_dir / "assets"

    out_actions = out_root / "Actions"
    out_assets = out_root / "Configurations"
    safe_mkdir(out_actions)
    safe_mkdir(out_assets)

    for yml_file in actions_dir.glob("*.yml"):
        out_file = out_actions / (yml_file.stem + ".md")
        convert_yaml_to_markdown(yml_file, out_file)

    for yml_file in assets_dir.glob("*.yml"):
        out_file = out_assets / (yml_file.stem + ".md")
        convert_yaml_to_markdown(yml_file, out_file)


def main():
    connectors_root = Path(".")
    for item in connectors_root.iterdir():
        if item.is_dir() and (item / "connector").exists():
            process_connector(item)


main()
