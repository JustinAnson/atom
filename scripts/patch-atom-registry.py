#!/usr/bin/env python3
"""Patch package.json and package-lock.json for dead atom.io registry.

atom.io was sunset in 2022; bundled package URLs must point at GitHub tarballs
and integrity hashes must be removed for those entries.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOM_RE = re.compile(
    r'https://(?:www\.)?atom\.io/api/packages/([^/]+)/versions/([^/]+)/tarball'
)


def github_tarball(name, version):
    return f'https://codeload.github.com/atom/{name}/tar.gz/v{version}'


def needs_patch(text):
    return 'atom.io/api/packages' in text


def patch_package_json(path):
    with open(path) as f:
        data = json.load(f)
    changed = False
    for key, value in list(data.get('dependencies', {}).items()):
        if isinstance(value, str) and 'atom.io/api/packages' in value:
            match = ATOM_RE.search(value)
            if match:
                data['dependencies'][key] = github_tarball(match.group(1), match.group(2))
                changed = True
    if changed:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
    return changed


def patch_obj(obj):
    if isinstance(obj, dict):
        version = obj.get('version', '')
        if isinstance(version, str) and 'atom.io/api/packages' in version:
            match = ATOM_RE.search(version)
            if match:
                obj['version'] = github_tarball(match.group(1), match.group(2))
                obj.pop('integrity', None)
                obj.pop('resolved', None)
        for value in obj.values():
            patch_obj(value)
    elif isinstance(obj, list):
        for item in obj:
            patch_obj(item)


def patch_package_lock(path):
    with open(path) as f:
        data = json.load(f)
    before = json.dumps(data)
    patch_obj(data)
    after = json.dumps(data)
    if before != after:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        return True
    return False


def main():
    pkg = ROOT / 'package.json'
    lock = ROOT / 'package-lock.json'
    if not needs_patch(pkg.read_text()) and not needs_patch(lock.read_text()):
        print('atom.io registry patch not needed')
        return 0
    changed = patch_package_json(pkg) or patch_package_lock(lock)
    print('Patched atom.io registry URLs' if changed else 'No changes made')
    return 0


if __name__ == '__main__':
    sys.exit(main())
