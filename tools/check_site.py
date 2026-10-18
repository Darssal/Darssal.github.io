#!/usr/bin/env python3
"""Check the public site artifact using only the Python standard library.

Diagnostics contain paths, rule names, and line numbers, never matched content.
This intentionally checks site/ only; legacy sources are not deployment inputs.
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ALLOWED_HOSTS = {"github.com", "docs.github.com", "darssal.github.io"}
ALLOWED_SUFFIXES = {
    ".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp",
    ".ico", ".txt", ".xml", ".json", ".webmanifest",
}
TEXT_SUFFIXES = {".html", ".css", ".js", ".svg", ".txt", ".xml", ".json", ".webmanifest"}
REQUIRED_FILES = {"index.html", "styles.css", "404.html", "robots.txt", "sitemap.xml"}
FORBIDDEN_PARTS = {
    ".git", ".github", ".env", "__pycache__", "node_modules", "private",
    "secrets", "credentials", "checkpoints", "datasets", "weights",
}
MAX_FILES = 128
MAX_TEXT_BYTES = 512 * 1024
MAX_ASSET_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
CSS_IMPORT = re.compile(r"@import\s+['\"]([^'\"]+)['\"]", re.I)
SECRET_RULES = {
    "private-key": re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
    "provider-key": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16})\b"),
    "credential-assignment": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*['\"]?[A-Za-z0-9_+/=-]{16,}"),
    "private-machine-path": re.compile(r"(?i)(?:[A-Z]:[\\/](?:Users|program(?:_II)?)[\\/]|/(?:Users|home)/[A-Za-z0-9._-]+/)"),
}


class Page(HTMLParser):
    def __init__(self, checker: "Checker", path: Path):
        super().__init__(convert_charrefs=True)
        self.checker, self.path = checker, path
        self.ids: set[str] = set()
        self.references: list[tuple[str, int]] = []
        self.svg_depth = 0

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        values = dict(attrs)
        if tag == "svg":
            self.svg_depth += 1
        if tag in {"base", "iframe", "object", "embed"}:
            self.checker.fail(self.path, "unsupported-active-element", line)
        if tag == "script" and not values.get("src"):
            self.checker.fail(self.path, "inline-script", line)
        if self.svg_depth and tag in {"script", "foreignobject", "image", "style", "animate", "animatetransform", "set"}:
            self.checker.fail(self.path, "non-static-svg", line)
        for key, value in attrs:
            if key.startswith("on"):
                self.checker.fail(self.path, "event-handler", line)
            if not value:
                continue
            if key == "id":
                if value in self.ids:
                    self.checker.fail(self.path, "duplicate-anchor", line)
                self.ids.add(value)
            if self.svg_depth:
                for match in CSS_URL.finditer(value):
                    if not match.group(2).startswith("#"):
                        self.checker.fail(self.path, "svg-external-resource", line)
                    else:
                        self.references.append((match.group(2), line))
            if key in {"href", "src", "poster", "action", "xlink:href"}:
                if self.svg_depth and key in {"href", "xlink:href"} and not value.startswith("#"):
                    self.checker.fail(self.path, "svg-external-resource", line)
                self.references.append((value, line))
            elif key == "srcset":
                self.references.extend((part.strip().split()[0], line) for part in value.split(",") if part.strip())
            elif key == "style":
                self.references.extend((match.group(2), line) for match in CSS_URL.finditer(value))
        if tag == "meta" and values.get("property", values.get("name", "")) in {"og:image", "twitter:image"}:
            if values.get("content"):
                self.references.append((values["content"], line))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg_depth = max(0, self.svg_depth - 1)


class Checker:
    def __init__(self, root: Path):
        self.site = root / "site"
        self.errors: list[str] = []
        self.files: set[Path] = set()
        self.pages: dict[Path, Page] = {}
        self.svg_ids: dict[Path, set[str]] = {}
        self.references: list[tuple[Path, str, int]] = []

    def fail(self, path: Path, rule: str, line: int = 0):
        try:
            name = "site/" + path.relative_to(self.site).as_posix()
        except ValueError:
            name = "site/"
        self.errors.append(f"{name}:{line}: {rule}")

    def collect(self):
        if not self.site.is_dir() or self.site.is_symlink():
            self.fail(self.site, "missing-or-linked-site-directory")
            return
        total = 0
        for path in sorted(self.site.rglob("*")):
            relative = path.relative_to(self.site)
            if path.is_symlink() or not path.resolve().is_relative_to(self.site.resolve()):
                self.fail(path, "linked-or-outside-artifact")
                continue
            if any(part.lower() in FORBIDDEN_PARTS or part.lower().startswith(".env") for part in relative.parts):
                self.fail(path, "sensitive-path")
            if any(ord(char) < 32 for char in relative.as_posix()):
                self.fail(path, "control-character-in-path")
            if path.is_dir():
                continue
            if not path.is_file():
                self.fail(path, "unsupported-file-type")
                continue
            self.files.add(path)
            size = path.stat().st_size
            total += size
            suffix = path.suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                self.fail(path, "file-type-not-allowed")
                continue
            limit = MAX_TEXT_BYTES if suffix in TEXT_SUFFIXES else MAX_ASSET_BYTES
            if size > limit:
                self.fail(path, "file-size-budget")
                continue
            if suffix not in TEXT_SUFFIXES:
                continue
            try:
                body = path.read_text(encoding="utf-8")
            except UnicodeError:
                self.fail(path, "non-utf8-text")
                continue
            for rule, pattern in SECRET_RULES.items():
                for match in pattern.finditer(body):
                    self.fail(path, rule, body.count("\n", 0, match.start()) + 1)
            self.parse(path, body, suffix)
        for name in sorted(REQUIRED_FILES):
            if self.site / name not in self.files:
                self.fail(self.site / name, "missing-required-file")
        if not any(self.site / f"favicon{suffix}" in self.files for suffix in (".svg", ".ico", ".png")):
            self.fail(self.site / "favicon", "missing-favicon")
        if len(self.files) > MAX_FILES or total > MAX_TOTAL_BYTES:
            self.fail(self.site, "artifact-size-budget")

    def parse(self, path: Path, body: str, suffix: str):
        if suffix == ".html":
            page = Page(self, path)
            try:
                page.feed(body)
                page.close()
            except Exception:
                self.fail(path, "invalid-html")
            self.pages[path] = page
            self.references.extend((path, url, line) for url, line in page.references)
        elif suffix == ".css":
            for pattern, group in ((CSS_URL, 2), (CSS_IMPORT, 1)):
                for match in pattern.finditer(body):
                    # Fragment-only CSS references resolve in the containing document.
                    if not match.group(group).startswith("#"):
                        self.references.append((path, match.group(group), body.count("\n", 0, match.start()) + 1))
        elif suffix in {".svg", ".xml"}:
            if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", body, re.I):
                self.fail(path, "xml-doctype-or-entity")
                return
            try:
                tree = ET.fromstring(body)
            except ET.ParseError:
                self.fail(path, "invalid-xml")
                return
            if suffix == ".svg":
                self.check_svg(path, tree)
            elif path.name == "sitemap.xml":
                for node in tree.iter():
                    if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
                        self.references.append((path, node.text.strip(), 0))
        elif path.name == "robots.txt":
            for line, text in enumerate(body.splitlines(), 1):
                if text.lower().startswith("sitemap:"):
                    self.references.append((path, text.partition(":")[2].strip(), line))

    def check_svg(self, path: Path, tree):
        ids = set()
        for node in tree.iter():
            tag = node.tag.rsplit("}", 1)[-1].lower()
            if tag in {"script", "foreignobject", "image", "animate", "animatetransform", "set"}:
                self.fail(path, "non-static-svg")
            for name, value in node.attrib.items():
                name = name.rsplit("}", 1)[-1].lower()
                if name.startswith("on"):
                    self.fail(path, "svg-event-handler")
                if name == "id":
                    if value in ids:
                        self.fail(path, "duplicate-anchor")
                    ids.add(value)
                if name in {"href", "src"}:
                    if not value.startswith("#"):
                        self.fail(path, "svg-external-resource")
                    else:
                        self.references.append((path, value, 0))
                for match in CSS_URL.finditer(value):
                    if not match.group(2).startswith("#"):
                        self.fail(path, "svg-external-resource")
                    else:
                        self.references.append((path, match.group(2), 0))
            if tag == "style" and node.text:
                # Keep standalone SVG styling in attributes, without CSS imports.
                self.fail(path, "svg-style-element")
        self.svg_ids[path] = ids

    def check_reference(self, source: Path, raw: str, line: int):
        try:
            url = urlsplit(raw.strip())
            host = url.hostname
            port = url.port
        except ValueError:
            self.fail(source, "invalid-url", line)
            return
        if url.scheme or url.netloc:
            if url.scheme != "https" or host not in ALLOWED_HOSTS or url.username or url.password or port not in {None, 443}:
                self.fail(source, "url-not-allowed", line)
                return
            if host != "darssal.github.io":
                return
            target_path = unquote(url.path).lstrip("/")
            target = self.site / target_path
        else:
            decoded = unquote(url.path)
            if "\\" in decoded or "\x00" in decoded:
                self.fail(source, "invalid-local-path", line)
                return
            target = self.site / decoded.lstrip("/") if decoded.startswith("/") else source.parent / decoded
            if not decoded:
                target = source
        target = target.resolve()
        if not target.is_relative_to(self.site.resolve()):
            self.fail(source, "outside-artifact-link", line)
            return
        if target.is_dir():
            target /= "index.html"
        if target not in self.files:
            self.fail(source, "missing-local-target", line)
            return
        if url.fragment:
            ids = self.pages[target].ids if target in self.pages else self.svg_ids.get(target, set())
            if unquote(url.fragment) not in ids:
                self.fail(source, "missing-local-anchor", line)

    def run(self) -> int:
        self.collect()
        for source, url, line in self.references:
            self.check_reference(source, url, line)
        if self.errors:
            for error in sorted(set(self.errors)):
                print(error)
            print(f"FAILED: {len(set(self.errors))} publication finding(s).")
            return 1
        print(f"OK: {len(self.files)} static files; {len(self.references)} URL references; publication boundaries checked.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Repository root (default: this script's repository)")
    args = parser.parse_args()
    return Checker(args.root.resolve()).run()


if __name__ == "__main__":
    raise SystemExit(main())
