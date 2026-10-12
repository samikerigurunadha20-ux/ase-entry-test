import json
import urllib.request
import urllib.error
from urllib.parse import quote


def get_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def main():
    with open("requirements.txt", "r", encoding="utf-8") as file:
        requirements = [
            line.strip()
            for line in file
            if line.strip()
        ]

    dependencies_checked = len(requirements)
    packages_not_on_pypi = 0
    versions_not_on_pypi = 0
    releases = []

    for requirement in requirements:
        package, version = requirement.split("==", 1)

        package_url = (
            f"https://pypi.org/pypi/{quote(package)}/json"
        )

        package_data = get_json(package_url)

        if package_data is None:
            packages_not_on_pypi += 1
            continue

        version_url = (
            f"https://pypi.org/pypi/"
            f"{quote(package)}/{quote(version)}/json"
        )

        version_data = get_json(version_url)

        if version_data is None:
            versions_not_on_pypi += 1
            continue

        files = version_data["urls"]

        if files:
            upload_time = files[0]["upload_time"]
            releases.append(
                (upload_time, package, version)
            )

    print(f"Dependencies checked: {dependencies_checked}")
    print(f"Packages not on PyPI: {packages_not_on_pypi}")
    print(f"Versions not on PyPI: {versions_not_on_pypi}")

    if releases:
        oldest = min(releases, key=lambda x: x[0])
        upload_time, package, version = oldest
        year = upload_time[:4]

        print(
            f"Oldest pinned release: "
            f"{package}=={version} ({year})"
        )
    else:
        print("Oldest pinned release: None")


if __name__ == "__main__":
    main()