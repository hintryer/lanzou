def run_update(template: str, variables: dict) -> str:
    config = load_json(json_path)
    final_result = {}

    item_list=jsonpath.findall("$.autoupdate..~", config)
    for item in item_list:
        value=jsonpath.findall(f"$.autoupdate..{item}", config)
        final_result[item] = value.format(**config)
    config.update(final_result)
    save_json(config,json_path)   
    return final_result                

    
    return template.format(**variables)

def run_checkver(json_path):
    config = load_json(json_path)
    final_result = {}

    matches = jsonpath.finditer("$.checkver", config)
    for match in matches:
        item_list=jsonpath.findall(f"{match.path}..~", config)
        for item in item_list:
            if item != "apiurl":
                expr=jsonpath.findall(f"{match.path}..{item}", config)
                apiurl=jsonpath.findall(f"{match.path}..apiurl", config)
                data=fetch_data(apiurl[0])
                
                final_result[item] = extract_value(data,expr[0])
    config.update(final_result)
    save_json(config,json_path)   
    return final_result
# ====================== .NET 示例 ======================
url_tpl = "https://builds.dotnet.microsoft.com/dotnet/Runtime/{version}/dotnet-runtime-{version}-win-x64.exe"
vars = {
    "name": "",
    "category": "运行库",
    "version": "3.23",
    "description": ".NET 9 Runtime",
    "homepage": "https://dotnet.microsoft.com/",
    "url": "",
    "checkver": [
        {
            "apiurl": "https://raw.githubusercontent.com/dotnet/core/main/release-notes/releases-index.json",
            "version": "$.releases-index[?(@.channel-version=='9.0')].latest-release"
        }
    ],
    "autoupdate": {
        "url": "https://builds.dotnet.microsoft.com/dotnet/Runtime/$version/dotnet-runtime-$version-win-x64.exe"
    }
}
print(substitute(url_tpl, vars))