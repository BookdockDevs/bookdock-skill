"""Validate the Bookdock Agent Skill and optionally build its release archive."""

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

import yaml


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "bookdock"
API_REFERENCE = SKILL / "references" / "external-api.md"
VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}")


def check_frontmatter(tag: str) -> str:
    markdown = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", markdown, re.DOTALL)
    if not frontmatter:
        raise ValueError("SKILL.md must start with YAML frontmatter")

    fields = yaml.safe_load(frontmatter.group(1))
    if not isinstance(fields, dict) or fields.get("name") != SKILL.name:
        raise ValueError("The Skill name must match its directory")
    description = fields.get("description")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        raise ValueError("The Skill description must be 1–1024 characters")
    metadata = fields.get("metadata")
    if not isinstance(metadata, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in metadata.items()
    ):
        raise ValueError("Skill metadata must be a mapping of string keys to string values")
    version = metadata.get("version", "")
    if not VERSION.fullmatch(version):
        raise ValueError("metadata.version must be a quoted MAJOR.MINOR.PATCH version")
    if tag and tag != f"v{version}":
        raise ValueError(f"Tag {tag!r} does not match metadata.version {version!r}")
    return version


def read_release_notes(version: str) -> str:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    sections = re.split(r"^##[ \t]+", changelog, flags=re.MULTILINE)[1:]
    heading = re.compile(rf"\[{re.escape(version)}\](?:[ \t]+-[ \t]+\d{{4}}-\d{{2}}-\d{{2}})?")
    notes = []
    for section in sections:
        title, _, body = section.partition("\n")
        if heading.fullmatch(title.rstrip()):
            notes.append(body.strip())

    if len(notes) != 1 or not notes[0]:
        raise ValueError(f"CHANGELOG.md must contain one non-empty section for {version}")
    return notes[0] + "\n"


def check_api_reference() -> None:
    snapshot = json.loads((ROOT / "tests" / "bookdock-api.json").read_text(encoding="utf-8"))
    endpoints = {}
    for line in API_REFERENCE.read_text(encoding="utf-8").splitlines():
        row = re.fullmatch(r"\| `([A-Z]+ /api/v1/[^ `]+)` \| ([^|]+) \| .* \|", line)
        if row:
            endpoint, scope = row.groups()
            if endpoint in endpoints:
                raise ValueError(f"Duplicate endpoint in API reference: {endpoint}")
            endpoints[endpoint] = None if scope == "Any valid Bookdock access token" else scope.strip("`")

    expected = snapshot["endpoints"]
    for endpoint in sorted(expected.keys() | endpoints.keys()):
        if endpoint not in expected or endpoint not in endpoints or endpoints[endpoint] != expected[endpoint]:
            raise ValueError(
                f"API reference differs from {snapshot['source']} at {endpoint}: "
                f"expected {expected.get(endpoint, 'no route')!r}, found {endpoints.get(endpoint, 'no route')!r}"
            )


def check_documents(shell: str | None) -> None:
    readmes = [ROOT / "README.md", ROOT / "README.en.md"]
    for document in [*readmes, ROOT / "CHANGELOG.md", *sorted(SKILL.rglob("*.md"))]:
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^()\s]+)\)", text):
            link = urlsplit(target)
            if link.path and not link.scheme and not link.netloc:
                path = (document.parent / unquote(link.path)).resolve()
                if not path.is_relative_to(ROOT) or not path.exists():
                    raise ValueError(f"Invalid local link in {document.relative_to(ROOT)}: {target}")
        if shell:
            for snippet in re.findall(r"^```sh\n(.*?)^```$", text, re.MULTILINE | re.DOTALL):
                subprocess.run([shell, "--noprofile", "--norc", "-n"], input=snippet.encode("utf-8"), check=True)


def build_archive(destination: Path) -> None:
    entries = {"bookdock/LICENSE": (ROOT / "LICENSE").read_bytes()}
    for document in sorted(SKILL.rglob("*.md")):
        name = document.relative_to(SKILL.parent).as_posix()
        entries[name] = document.read_bytes()

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    with ZipFile(destination) as archive:
        if archive.testzip() or {name: archive.read(name) for name in archive.namelist()} != entries:
            raise ValueError(f"Archive contents do not match the Skill files: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="", help="Require this release tag to match metadata.version")
    parser.add_argument("--bash", help="Bash executable to use for syntax checking Markdown examples")
    parser.add_argument("--output", type=Path, help="Path for the optional ZIP archive")
    parser.add_argument("--release-notes", type=Path, help="Write the current changelog section to this file")
    args = parser.parse_args()
    try:
        version = check_frontmatter(args.tag)
        notes = read_release_notes(version)
        check_api_reference()
        check_documents(args.bash)
        if args.output:
            build_archive(args.output)
        if args.release_notes:
            args.release_notes.parent.mkdir(parents=True, exist_ok=True)
            args.release_notes.write_text(notes, encoding="utf-8", newline="\n")
    except (OSError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Skill check failed: {error}\n")
    print(f"Validated bookdock {version}" + (f" and packaged {args.output}" if args.output else ""))


if __name__ == "__main__":
    main()
