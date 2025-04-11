import os
import yaml
import shutil
from pathlib import Path

OUTPUT_DIR = Path("output/docs/Connectors")
SUMMARY_FILE = Path("output/docs/summary.md")

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def convert_yaml_to_markdown(yaml_path, out_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    md_lines = []

    title = data.get("title", yaml_path.stem)
    description = data.get("description", "")
    md_lines.append(f"# {title}\n")
    if description:
        md_lines.append(f"**Description**: {description}\n")

    endpoint = data.get("meta", {}).get("endpoint", "")
    method = data.get("meta", {}).get("method", "")
    if endpoint or method:
        md_lines.append("## Endpoint\n")
        if endpoint:
            md_lines.append(f"- **URL:** `{endpoint}`")
        if method:
            md_lines.append(f"- **Method:** `{method}`")

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

    md_lines.append("## Output\n")

    example = data.get("output", {}).get("example")
    if example:
        md_lines.append("### Example\n")
        md_lines.append("```json")
        md_lines.append(yaml.dump(example, default_flow_style=False))
        md_lines.append("```")

    output = data.get("output", {}).get("properties", {})
    if output:
        md_lines.append("### Output Parameters\n")
        md_lines.append("| Name | Type | Description |")
        md_lines.append("|------|------|-------------|")
        for key, value in output.items():
            if key == "response_headers":
                continue
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    headers = output.get("response_headers", {}).get("properties", {})
    if headers:
        md_lines.append("## Response Headers\n")
        md_lines.append("| Header | Type | Description |")
        md_lines.append("|--------|------|-------------|")
        for key, value in headers.items():
            dtype = value.get("type", "")
            desc = value.get("description", "")
            md_lines.append(f"| {key} | {dtype} | {desc} |")

    json_body = output.get("json_body", {}).get("properties", {})
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
        md_lines.append("{")
        md_lines.append("  \"messages\": [")
        md_lines.append("    {")
        md_lines.append("      \"type\": \"ERROR\",")
        md_lines.append("      \"text\": \"Search ID not found.\"")
        md_lines.append("    }")
        md_lines.append("  ],")
        md_lines.append("  \"status_code\": 404,")
        md_lines.append("  \"reason\": \"Not Found\"")
        md_lines.append("}")
        md_lines.append("```")

    safe_mkdir(out_path.parent)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[✔] Wrote: {out_path}")

def process_connector(connector_dir):
    connector_name = Path(connector_dir).name
    print(f"🔧 Processing connector: {connector_name}")

    out_root = OUTPUT_DIR / connector_name
    overview_src = Path(connector_dir) / "docs" / "README.md"

    if overview_src.exists():
        safe_mkdir(out_root)
        overview_dest = out_root / "overview.md"
        shutil.copy(overview_src, overview_dest)
        print(f"[✔] Copied overview.md for {connector_name}")

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

def generate_summary_flat():
    print("📘 Generating flat summary.md")
    lines = ["# Connectors"]
    for connector in sorted(OUTPUT_DIR.iterdir()):
        if not connector.is_dir():
            continue
        lines.append(f"- **{connector.name}**")
        overview = connector / "overview.md"
        if overview.exists():
            lines.append(f"  - [Overview](Connectors/{connector.name}/overview.md)")

        configs = connector / "Configurations"
        if configs.exists():
            for md_file in sorted(configs.glob("*.md")):
                lines.append(f"  - [Configurations: {md_file.stem}](Connectors/{connector.name}/Configurations/{md_file.name})")

        actions = connector / "Actions"
        if actions.exists():
            for md_file in sorted(actions.glob("*.md")):
                lines.append(f"  - [Actions: {md_file.stem}](Connectors/{connector.name}/Actions/{md_file.name})")

    safe_mkdir(SUMMARY_FILE.parent)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[✔] Wrote: {SUMMARY_FILE}")

def main():
    for item in sorted(Path(".").iterdir()):
        if item.is_dir() and (item / "connector").exists():
            process_connector(item)
    generate_summary_flat()

if __name__ == "__main__":
    main()
