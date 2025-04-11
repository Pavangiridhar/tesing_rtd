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
    print(f"🔄 Converting: {yaml_path} -> {out_path}")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    md_lines = []

    title = data.get("title", yaml_path.stem)
    desc = data.get("description", "")
    md_lines.append(f"# {title}\n")
    if desc:
        md_lines.append(f"**Description**: {desc}\n")

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

    example = data.get("output", {}).get("example")
    if example:
        md_lines.append("\n## Output Example\n")
        md_lines.append("```json")
        md_lines.append(yaml.dump(example, default_flow_style=False))
        md_lines.append("```\n")

    output = data.get("output", {}).get("properties", {})
    if output:
        md_lines.append("\n## Output Parameters\n")
        md_lines.append("| Name | Type | Description |")
        md_lines.append("|------|------|-------------|")
        for key, value in output.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    headers = output.get("response_headers", {}).get("properties", {})
    if headers:
        md_lines.append("\n## Response Headers\n")
        md_lines.append("| Header | Type | Description |")
        md_lines.append("|--------|------|-------------|")
        for key, value in headers.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    if output.get("json_body", {}).get("properties", {}).get("messages"):
        md_lines.append("\n## Error Handling\n")
        md_lines.append("The response may include error messages under the `messages` field in the JSON body.")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def process_connector(connector_dir):
    connector_name = Path(connector_dir).name
    out_root = OUTPUT_DIR / connector_name
    print(f"\n📦 Processing connector: {connector_name}")

    overview_src = Path(connector_dir) / "docs" / "README.md"
    if overview_src.exists():
        print("📄 Copying overview.md")
        safe_mkdir(out_root)
        shutil.copy(overview_src, out_root / "overview.md")
    else:
        print("⚠️ overview.md not found.")

    config_dir = Path(connector_dir) / "connector" / "config"
    actions_dir = config_dir / "actions"
    assets_dir = config_dir / "assets"

    out_actions = out_root / "Actions"
    out_configs = out_root / "Configurations"
    safe_mkdir(out_actions)
    safe_mkdir(out_configs)

    print(f"📁 Looking for actions in {actions_dir}")
    if actions_dir.exists():
        for yml in actions_dir.glob("*.yml"):
            print(f"  ✅ Found action: {yml.name}")
            convert_yaml_to_markdown(yml, out_actions / f"{yml.stem}.md")
    else:
        print("❌ Actions directory not found.")

    print(f"📁 Looking for configurations in {assets_dir}")
    if assets_dir.exists():
        for yml in assets_dir.glob("*.yml"):
            print(f"  ✅ Found config: {yml.name}")
            convert_yaml_to_markdown(yml, out_configs / f"{yml.stem}.md")
    else:
        print("❌ Configurations directory not found.")


def main():
    for item in Path(".").iterdir():
        if item.is_dir() and (item / "connector").exists():
            process_connector(item)


if __name__ == "__main__":
    main()
