import argparse
import glob
import importlib.util
import io
import json
import os
import sys

import requests
import yaml
from connector_definition_runner import Runner

IPC_API_URI = os.getenv("IPC_API_URI", "")
IPC_API_TOKEN = os.getenv("IPC_API_TOKEN", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="The connector action to run")
    args = parser.parse_args()
    # check if action has an override script
    glob_path = "./**/{}.py".format(args.action)
    action_override = glob.glob(glob_path, recursive=True)
    connector_override = glob.glob("./**/runner_override.py", recursive=True)
    asset, inputs = _load_asset_and_inputs()
    asset_schema, action_schema = _load_schemas(asset, args.action)
    inputs["files"] = parse_form_data(action_schema, inputs)
    http_proxy = os.getenv("http_proxy") or asset.get("http_proxy", None)
    if action_override and len(action_override) == 1:
        spec = importlib.util.spec_from_file_location("module.name", action_override[0])
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        RunnerClass = mod.RunnerOverride
    elif connector_override and len(connector_override) == 1:
        spec = importlib.util.spec_from_file_location(
            "module.name", connector_override[0]
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        RunnerClass = mod.RunnerOverride
    else:
        RunnerClass = Runner

    runner = RunnerClass(asset=asset, asset_schema=asset_schema, http_proxy=http_proxy)

    resp = runner.run(inputs=inputs, action_schema=action_schema)
    resp = handle_output_files(resp, action_schema)
    print("::set-output ", json.dumps(resp, indent=None), "", sep="")


def _load_asset_and_inputs():
    raw_inputs = sys.stdin.read()
    if not raw_inputs:
        raw_inputs = "{}"
    inputs = json.loads(raw_inputs)
    asset = {}
    asset_keys = [
        "url",
        "client_id",
        "client_secret",
        "scope",
        "verify_ssl",
        "http_proxy",
        "oauth2_username",
        "oauth2_password",
        "token_url",
        "client_id",
        "client_secret",
        "scope",
        "verify_ssl",
        "http_proxy",
        "username",
        "password",
        "verify_ssl",
        "http_proxy",
    ]
    for k in inputs.keys():
        if k in asset_keys:
            asset[k] = inputs[k]
    for k in asset.keys():
        del inputs[k]

    return asset, inputs


def _get_asset_name(asset):
    if {"username", "password"} <= set(asset):
        return "http_basic"
    elif {"token"} <= set(asset):
        return "http_bearer"
    elif {"oauth2_username", "oauth2_password"} <= set(asset):
        return "oauth2_password"
    elif {"client_secret", "client_id"} <= set(asset):
        return "oauth2_client_credentials"
    else:
        # apikey does not have any pre-defined asset parameters, so we cannot
        #  distinguish it from "no auth" until we try to pull the manifest.
        #  The runner handles that
        return "apikey"


def _load_schemas(asset, action_name):

    asset_name = _get_asset_name(asset)

    manifests = glob.glob("./**/*.yaml", recursive=True)
    asset_manifest = {}
    action_manifest = {}
    for manifest in manifests:
        # All Swimlane connector schemas should have schema property.
        try:
            schema = yaml.safe_load(open(manifest).read())
            schema_type = schema["schema"]
            if (
                asset_name
                and schema_type in ["asset/1"]
                and schema["name"] == asset_name
            ):
                asset_manifest = schema

            if schema_type in ["action/1"] and schema["name"] == action_name:
                action_manifest = schema
        except Exception:
            pass

    return asset_manifest, action_manifest


def get_file(file_id):
    """Gets the file content from the file associated with the file_id provided
    and returns a ByteIO object with the file content.
    """
    get_url = f"{IPC_API_URI}/files/{file_id}"
    params = {"token": IPC_API_TOKEN}
    res = requests.get(get_url, params=params)
    return io.BytesIO(res.content)


def is_attachment(manifest):
    """Checks if the current property is an attachment"""
    return (
        manifest["type"] == "array"
        and manifest["items"].get("contentDisposition") == "attachment"
    ) or manifest.get("contentDisposition") == "attachment"


def parse_file_object(file_object, field_name):
    file_data = get_file(file_object["file"])
    form_entry = (field_name, (file_object["file_name"], file_data))
    return form_entry


def lookup_attachments(manifest):
    """Returns a list of properties"""
    return [k for k, v in manifest["properties"].items() if is_attachment(v)]


def parse_form_data(manifest, data):
    output = parse_form_data_old(manifest, data)
    output.extend(parse_form_data_new(manifest, data))
    return output


def parse_form_data_old(manifest, data):
    files = []
    attachment_fields = lookup_attachments(manifest["inputs"])
    for attachment_field in attachment_fields:

        file_data = data.get(attachment_field)
        if file_data is None:
            continue

        file_manifest = manifest["inputs"]["properties"][attachment_field]

        if file_manifest["type"] == "array":

            file_manifest = file_manifest["items"]["properties"]
            for attachment in file_data:
                files.extend(parse_file_object(attachment, file_manifest))

        else:
            files.extend(parse_file_object(file_data, file_manifest["properties"]))

    return files


def parse_form_data_new(manifest, data):
    files = []
    for form_field, field_value in data.get("Images", {}).items():
        field_manifest = (
            manifest["inputs"]["properties"]
            .get("Images", {})
            .get("properties", {})
            .get(form_field)
        )
        if field_manifest and is_attachment(field_manifest):
            if isinstance(field_value, list):
                for attachment in field_value:
                    files.append(parse_file_object(attachment, form_field))
            else:
                files.append(parse_file_object(field_value, form_field))
        else:
            if isinstance(list, field_value):
                for value in field_value:
                    files.append((form_field, value))
            else:
                files.append((form_field, field_value))

    return files


def handle_output_files(output, action_schema):
    if "file" in output:
        post_url = f"{IPC_API_URI}/files"
        params = {"token": IPC_API_TOKEN}
        upload = [
            (
                "files",
                (
                    output["file"][0]["filename"],
                    output["file"][0]["file_data"],
                    "multipart/form-data",
                ),
            )
        ]
        res = requests.post(post_url, files=upload, params=params)
        output["file"] = res.json()
    return output


if __name__ == "__main__":
    main()
