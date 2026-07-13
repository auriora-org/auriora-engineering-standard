#!/usr/bin/env python3
"""Validate AES repo: markdown links, anchors, requirement ID uniqueness."""
import os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", ".claude")]
    for f in filenames:
        if f.endswith(".md"):
            md_files.append(os.path.join(dirpath, f))

def github_anchor(heading):
    a = heading.strip().lower()
    a = re.sub(r"[^\w\- ]", "", a)
    a = a.replace(" ", "-")
    return a

anchors = {}   # file -> set of anchors
for path in md_files:
    text = open(path, encoding="utf-8").read()
    heads = re.findall(r"^#{1,6}\s+(.+)$", text, re.M)
    aset = set()
    counts = collections.Counter()
    for h in heads:
        h = re.sub(r"[`*]", "", h)
        base = github_anchor(h)
        n = counts[base]
        counts[base] += 1
        aset.add(base if n == 0 else f"{base}-{n}")
    anchors[path] = aset

errors = []
link_re = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
for path in md_files:
    text = open(path, encoding="utf-8").read()
    # strip fenced code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    for label, target in link_re.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            frag, fpath = target[1:], path
        else:
            parts = target.split("#", 1)
            rel = parts[0]
            frag = parts[1] if len(parts) > 1 else None
            fpath = os.path.normpath(os.path.join(os.path.dirname(path), rel))
            if not os.path.exists(fpath):
                errors.append(f"BROKEN LINK  {os.path.relpath(path, ROOT)} -> {target}")
                continue
        if frag is not None and fpath.endswith(".md"):
            if frag not in anchors.get(fpath, set()):
                errors.append(f"BROKEN ANCHOR {os.path.relpath(path, ROOT)} -> {target}")

# requirement ID uniqueness (definitions = headings "### AES-XXX-NNN:"
# plus table-row definitions "| AES-XXX-NNN |", e.g. fixed historical decisions)
req_defs = collections.defaultdict(list)
for path in md_files:
    text = open(path, encoding="utf-8").read()
    for m in re.finditer(r"^###\s+(AES-[A-Z]+-\d{3}):", text, re.M):
        req_defs[m.group(1)].append(os.path.relpath(path, ROOT))
    for m in re.finditer(r"^\|\s*(AES-[A-Z]+-\d{3})\s*\|", text, re.M):
        req_defs[m.group(1)].append(os.path.relpath(path, ROOT))
for rid, locs in sorted(req_defs.items()):
    if len(locs) > 1:
        errors.append(f"DUPLICATE REQ ID {rid}: {locs}")

# retired requirement IDs are registered in docs/document-index.md;
# expand `AES-XXX-NNN` – `AES-XXX-MMM` ranges into individual IDs
retired = set()
index_path = os.path.join(ROOT, "docs", "document-index.md")
if os.path.exists(index_path):
    itext = open(index_path, encoding="utf-8").read()
    for m in re.finditer(r"`(AES-[A-Z]+-)(\d{3})`\s*[–-]\s*`(?:AES-[A-Z]+-)?(\d{3})`", itext):
        prefix, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        for n in range(lo, hi + 1):
            retired.add(f"{prefix}{n:03d}")
    for m in re.finditer(r"`(AES-[A-Z]+-\d{3})`", itext):
        retired.add(m.group(1))

# referenced requirement IDs that are neither defined nor retired
refs = set()
for path in md_files:
    text = open(path, encoding="utf-8").read()
    for m in re.finditer(r"\bAES-[A-Z]+-\d{3}\b", text):
        refs.add(m.group(0))
undefined = sorted(r for r in refs if r not in req_defs and r not in retired)
for r in undefined:
    errors.append(f"REFERENCED BUT UNDEFINED REQ ID: {r}")

print(f"files: {len(md_files)}, requirement IDs defined: {len(req_defs)}")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("ALL CHECKS PASSED")
