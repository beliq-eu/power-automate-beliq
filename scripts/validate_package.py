#!/usr/bin/env python3
"""Local pre-submission gate for the Power Platform connector package.zip.

Faithful port of Microsoft's scripts/ConnectorPackageValidator.ps1 structural
checks, so we can validate on Linux (the official .ps1 is Windows-only: it uses
a drive-letter path regex, backslash separators, and DirectoryInfo
stringification that all break under pwsh on Linux). The cert team's Windows run
of the .ps1 stays the authoritative check; this mirrors its logic exactly so a
"PASS" here means a "Validation successful" there.

Usage: validate_package.py <package.zip> [n|y]   (y = AI plugin enabled)
"""
import sys
import zipfile
import io
import xml.etree.ElementTree as ET


def fail(msg):
    print(f"  FAIL: {msg}")


def top_level(names):
    """Return (folders, files) at the root level of a zip namelist."""
    folders, files = set(), []
    for n in names:
        stripped = n.strip("/")
        if not stripped:
            continue
        if "/" in stripped:
            folders.add(stripped.split("/")[0])
        elif n.endswith("/"):
            folders.add(stripped)
        else:
            files.append(stripped)
    return folders, files


def entries_in(names, folder):
    """Immediate children of `folder` in a namelist: (subfolders, files)."""
    prefix = folder.rstrip("/") + "/"
    subfolders, files = set(), []
    for n in names:
        if not n.startswith(prefix):
            continue
        rest = n[len(prefix):]
        if not rest:
            continue
        if "/" in rest.strip("/"):
            subfolders.add(rest.split("/")[0])
        elif rest.endswith("/"):
            subfolders.add(rest.rstrip("/"))
        else:
            files.append(rest)
    return subfolders, files


def node_present(root, tag):
    """PS: node exists AND (HasChildNodes OR Attributes.Count > 0)."""
    for el in root.iter():
        # strip namespace
        local = el.tag.split("}")[-1]
        if local == tag:
            if list(el) or el.attrib:
                return True
    return False


def validate(pkg_path, plugin):
    expected_solutions = 3 if plugin else 2
    print(f"Validating {pkg_path} (plugin={'y' if plugin else 'n'})")
    ok = True

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        # Level 1: root has 0 folders, exactly 1 *.md, exactly 1 *.zip
        folders, files = top_level(names)
        md = [f for f in files if f.lower().endswith(".md")]
        zips = [f for f in files if f.lower().endswith(".zip")]
        if folders:
            fail(f"Level 1: outer zip must contain no folders; found {folders}")
            ok = False
        if len(md) != 1:
            fail(f"Level 1: expected exactly 1 .md (intro.md); found {md}")
            ok = False
        if len(zips) != 1:
            fail(f"Level 1: expected exactly 1 .zip (the .pdpkg.zip); found {zips}")
            ok = False
        if not ok:
            return False
        print(f"  Level 1 OK: {md[0]} + {zips[0]}")

        pdpkg_bytes = outer.read(zips[0])

    with zipfile.ZipFile(io.BytesIO(pdpkg_bytes)) as pdpkg:
        names = pdpkg.namelist()
        # Level 2: exactly 1 folder (files not checked)
        folders, _ = top_level(names)
        if len(folders) != 1:
            fail(f"Level 2: .pdpkg.zip must contain exactly 1 folder "
                 f"(ideally 'PkgAssets'); found {folders}")
            return False
        pkgassets = next(iter(folders))
        print(f"  Level 2 OK: single folder '{pkgassets}'")

        # Level 3: inside that folder, 0 subfolders, exactly N *.zip
        subfolders, files = entries_in(names, pkgassets)
        sol_zips = [f for f in files if f.lower().endswith(".zip")]
        if subfolders:
            fail(f"Level 3: '{pkgassets}' must contain no subfolders; found {subfolders}")
            ok = False
        if len(sol_zips) != expected_solutions:
            fail(f"Level 3: '{pkgassets}' must contain exactly {expected_solutions} "
                 f"solution zips; found {len(sol_zips)}: {sol_zips}")
            ok = False
        if not ok:
            return False
        print(f"  Level 3 OK: {expected_solutions} solution zips: {sol_zips}")

        # Content: categorize each solution zip
        connector_present = flow_present = plugin_present = False
        for sz in sol_zips:
            data = pdpkg.read(f"{pkgassets}/{sz}")
            with zipfile.ZipFile(io.BytesIO(data)) as sol:
                snames = sol.namelist()
                required = ["[Content_Types].xml", "customizations.xml", "solution.xml"]
                root_files = [n for n in snames if "/" not in n.strip("/")]
                missing = [r for r in required if r not in root_files]
                if missing:
                    fail(f"solution '{sz}' missing {missing}")
                    return False
                cust = ET.fromstring(sol.read("customizations.xml"))
                is_conn = node_present(cust, "Connector")
                is_flow = node_present(cust, "Workflows")
                is_plug = node_present(cust, "aicopilot_aiplugin") if plugin else False
                sol_folders, _ = top_level(snames)
                if is_conn and "Connector" not in sol_folders:
                    fail(f"solution '{sz}' has a Connector node but no 'Connector' folder")
                    return False
                if is_flow and ("Workflows" not in sol_folders or "Connector" not in sol_folders):
                    fail(f"solution '{sz}' is a flow solution but missing Connector/Workflows folder")
                    return False
                kind = ("connector" if (is_conn and not is_flow and not is_plug) else
                        "flow" if (is_conn and is_flow and not is_plug) else
                        "plugin" if (is_conn and not is_flow and is_plug) else "UNKNOWN")
                print(f"    - {sz}: Connector={is_conn} Workflows={is_flow} "
                      f"Plugin={is_plug} -> {kind}")
                connector_present = connector_present or kind == "connector"
                flow_present = flow_present or kind == "flow"
                plugin_present = plugin_present or kind == "plugin"

        if not connector_present:
            fail("no valid connector-only solution (Connector node + folder, no Workflows)")
            ok = False
        elif not flow_present:
            fail("no valid flow solution (Connector + Workflows nodes + folders)")
            ok = False
        elif plugin and not plugin_present:
            fail("plugin enabled but no valid plugin solution")
            ok = False

    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    plug = len(sys.argv) > 2 and sys.argv[2].lower() in ("y", "yes")
    result = validate(path, plug)
    print()
    if result:
        print("Validation successful: The package structure is correct.")
        sys.exit(0)
    else:
        print("Validation failed: Invalid package structure.")
        sys.exit(1)
