from LanZouAPI import  lanzou_parse
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
def upurl():
    print("1")
