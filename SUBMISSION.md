# Microsoft Independent Publisher submission

This connector is built and validated. What remains is the Independent Publisher
certification flow with Microsoft. Steps are grouped by who does them.

## Status

- Connector files (`Beliq/`): complete and validated (OpenAPI 2.0). Offline gate
  `scripts/check_connector.py` passes; `scripts/scrub-check.sh` (no em-dash) passes.
- `info.title`: `beliq`. IP connectors use the BASE name only; Microsoft appends
  "(Independent Publisher)" at certification. Do not put the suffix in `info.title`
  (0 of 15 sampled merged IP connectors carry it). The suffix belongs on the PR title
  and in `publisher`/`stackOwner`, not the swagger title.
- `iconBrandColor`: `#da3b01` (the mandatory Independent Publisher color).
- `x-ms-connector-metadata`: Website, Privacy policy, Categories set on the swagger root
  (`https://beliq.eu`, `https://beliq.eu/legal/privacy-policy/`, `Content and Files;Finance`).
- Support contact: `hello@beliq.eu` in `info.contact`. This is also the address the
  verified-credentials form is sent to (see B), so keep that inbox monitored.
- `api.beliq.eu` is live; a real key works. `paconn validate` was run 2026-07-01 and
  reported "Swagger certification succeeded with warnings" (the two warnings are expected,
  see F). Note `paconn validate` signs into Power Platform first and exits 0 when that
  login fails, so a green run is only evidence when the Entra login actually succeeded.
- Reusable Microsoft setup already stands up (2026-07-01): a dedicated Entra tenant, a
  work/school account `connectors@<tenant>.onmicrosoft.com`, and a Power Apps Developer
  Plan environment. Personal Microsoft accounts are rejected for connector work
  (AADSTS500200 / 50020). `paconn` is installed in the local `.venv`.

## A. File touch-ups (done)

Title set to the base name `beliq`, connector metadata added, Premium claim corrected,
contact and brand color set. Nothing left here.

When building the submission PR, do NOT copy `Beliq/settings.json` into the Microsoft
repo. It is a local paconn helper, not a submission artifact. The icon is also not
committed (see D).

## B. Verified credentials (OneVet / AU10TIX) - Tobias only

The submission is bound to a real person's verified identity AND the GitHub account that
opens the PR. Anonymous or generic org accounts do not pass: the GitHub profile name must
match a government-issued ID.

Account: `blue-d3v` (profile name matches the government ID). This same account completed
OneVet verification for the PolyDoc IP connector. Whether that credential carries over to
a second connector is not established, so do not treat this gate as pre-cleared: **when
the proposal PR is open, ask the reviewer directly whether the existing verified
credential applies to this connector.** Be ready to run it again if not.

Vendor: AU10TIX. App: Microsoft Authenticator. Time: ~15 min. The window is 30 days once
started, and it is easy to lose: PolyDoc's first form expired unfilled and cost ~2 weeks.

1. `blue-d3v` must have a **public, monitored email** set on its GitHub profile, and
   `info.contact` in the swagger is `hello@beliq.eu`: the verification form is sent to the
   swagger contact address, so `hello@beliq.eu` must be watched.
2. Install Microsoft Authenticator on your phone.
3. Trigger verification by opening the proposal PR (see C/D). Microsoft has no standalone
   "request verification" portal; opening the PR is what starts it.
4. Microsoft emails a form. Fill it so the form, your GitHub profile, and your government
   ID all match.
5. You then get an AU10TIX email. Open its link in a private window: enter the email PIN,
   your phone number, photograph your ID, take a selfie.
6. Add the resulting Verified ID to Microsoft Authenticator. Done.

## C. Operation screenshots - Tobias only

Microsoft requires one screenshot per operation showing it working. This connector has
five: Generate e-invoice, Validate e-invoice, Parse e-invoice, Convert e-invoice, and
Check API key.

Use a `blq_test_` sandbox key for this (create one at
`https://dashboard.beliq.eu/api-keys`, pick Test). It is free, never decrements the live
quota, and the connector behaves identically; the only difference is an invisible
specimen marker on the output bytes, which does not show in a screenshot of a 200.

1. Import `Beliq/apiDefinition.swagger.json` + `Beliq/apiProperties.json` as a custom
   connector in a Power Automate environment with a Premium trial.
2. Connect the sandbox key (Check API key confirms it, no quota cost).
3. Run each operation once. Generate turns a JSON invoice into XML or a hybrid PDF; feed
   that output into Validate, Parse, and Convert (see `example-flows/README.md` for the
   bodies and the chaining).
4. Capture one screenshot of each working. Five total, for the PR body.

GitHub has no API to upload images into a PR (drag-drop only). Drag-drop the screenshots
into the PR body in the browser as `blue-d3v`, or commit them somewhere with a public raw
URL first and reference them.

## D. The PR - mostly automatable, final click is Tobias

1. From `blue-d3v`, fork `microsoft/PowerPlatformConnectors`.
2. Into `independent-publisher-connectors/beliq/`, commit exactly **five files**:
   - `apiDefinition.swagger.json`
   - `apiProperties.json`
   - `readme.md` (lowercase; rename from `Beliq/README.md`)
   - `intro.md` (see F; a short package intro, reuse the README summary)
   - `package.zip` (the solution-export artifact from F)

   Do NOT commit `settings.json`, `icon.png`, or `icon.svg`. The icon is not part of the
   IP folder (of 465 merged IP folders only 2 carry `icon.png`); `iconBrandColor` in
   `apiProperties.json` is what the program mandates. `icon.png` is still used locally by
   `paconn create` (F), just not committed to the Microsoft repo.
3. Open the PR. Title: `beliq (Independent Publisher)`. Add label
   `independent-publisher-connector`. Fill the PR template checklist. Paste the five
   screenshots into the body.

The documented path opens a `Proposal - beliq (Independent Publisher)` PR first (this is
also the verification trigger in B), then drops the `Proposal -` prefix when ready.

`package.zip` is a **committed file in the folder, not a comment attachment.** Attaching
it as a comment gets bounced ("attach as part of the PR artifacts") and only clears once
it is committed alongside `intro.md`. Commit it from the start. (Upstream folders more
often name it `connectorPackage.zip`; a plain `package.zip` also passes.)

## E. Review - automatable responses, Tobias relays account actions

Swagger Validator and Breaking Change bots run automatically. A Microsoft reviewer
follows, and the cert team comments `certify-connector` to start certification. Budget
~6-8 weeks end to end, with reviewer round-trips of 5-14 days each (Microsoft's nominal
"~15 business days" understates it). Every follow-up push and reply must come from
`blue-d3v`, the account that opened the PR.

## F. The package.zip requirement

`package.zip` is a hard, current IP gate. It is a solution-export artifact, committed into
the connector folder (see D). A flat `paconn download` (apiDefinition / apiProperties /
settings / icon) does NOT satisfy it.

Exact structure (this is what Microsoft's `ConnectorPackageValidator.ps1` checks;
`scripts/validate_package.py` is a faithful Linux port, run as
`validate_package.py package.zip n`, `n` = no AI plugin):

- Outer zip: EXACTLY one `intro.md` + one `.zip` (the Package Deployer `.pdpkg.zip`).
  No folders, nothing else.
- That inner `.pdpkg.zip`: one folder (`PkgAssets`) + env files (`.xml` / `.dll` / `.pdb`)
  - a genuine Package Deployer package.
- `PkgAssets`: EXACTLY two solution zips (no plugin), no subfolders.
- Each solution zip contains `[Content_Types].xml`, `customizations.xml`, `solution.xml`
  - a real Dataverse solution export.
- One solution = **Connector only** (`customizations.xml` has a `Connector` node + a
  matching `Connector` folder).
- The other = **Connector + Workflows**: a TEST CLOUD FLOW that uses the connector
  (`Workflows` node + folder). The validator REJECTS a connector-only package - the flow
  solution is mandatory.

Because `info.title` is already `beliq` (5 chars), the created connector's displayName is
`beliq`, well under the hard Dataverse 30-char limit. (PolyDoc hit `0x80040216
"Connector name cannot be longer than 30 characters"` with a 31-char suffixed title, and
displayName is immutable, so it had to recreate the connector. Starting at `beliq` avoids
that.)

### F.1 Produce the two solution zips (Tobias, browser)

1. Use a **Dataverse-enabled** Power Platform environment (the Developer Plan env used for
   the screenshots ships a database).
2. `paconn login` (device-code, `connectors@<tenant>.onmicrosoft.com`), then push the
   connector:
   `paconn create -e <ENV> -d Beliq/apiDefinition.swagger.json -p Beliq/apiProperties.json -i Beliq/icon.png`.
   It creates the connector (displayName `beliq`), then crashes at the local
   `settings.json` overwrite prompt with a NoTTY error - the connector already exists at
   that point.
3. Maker portal: add the custom connector to a new solution ("beliq Connector"), export
   **Unmanaged** -> connector-only solution zip.
4. Maker portal: create a second solution ("beliq Flow"), add the connector AND author a
   trivial cloud flow inside it (manual trigger -> GenerateInvoice), export **Unmanaged**
   -> flow solution zip. The flow solution MUST contain BOTH the connector and the flow.
5. Give the two zips distinct filenames.

### F.2 Build package.zip (agent-doable once the two zips exist)

Tooling pins (latest pac/pwsh are broken on Linux with "DotnetToolSettings.xml not
found"). Installed to `~/.dotnet`: dotnet SDK 8.0.422, pac 1.43.6, pwsh 7.4.7. Every
pac/dotnet/pwsh call needs:

```
export DOTNET_ROOT=$HOME/.dotnet
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH
```

With the two solution zips in hand:

```
mkdir pkg && cd pkg
pac package init --outputDirectory .
dotnet add package Microsoft.NETFramework.ReferenceAssemblies   # lets net472 compile on Linux
pac package add-solution --path <beliq_Connector.zip>
pac package add-solution --path <beliq_Flow.zip>
dotnet publish -c Release          # NOT build/pack; the .pdpkg.zip is emitted AfterTargets=Publish
# -> bin/Release/<proj>.<ver>.pdpkg.zip
```

Then assemble and validate:

```
# in a clean dir holding only intro.md + the .pdpkg.zip, both at root, no folders:
zip package.zip intro.md <proj>.<ver>.pdpkg.zip
python3 scripts/validate_package.py package.zip n
# expect: "Validation successful: The package structure is correct."
```

Commit `package.zip` + `intro.md` into `independent-publisher-connectors/beliq/` (D).

### F.3 The two `paconn validate` warnings (expected, left as-is)

- `produces` MIME types `application/xml` / `application/pdf` are "not supported" per the
  validator's json/text/form allowlist. They are the honest content types for a document
  download, and beliq's API strictly checks Content-Type (xml / pdf / octet-stream, sniffs
  `%PDF-`), so rewriting `consumes`/`produces` to a "supported" type blind would make the
  live API reject the call. Leave them.
- Each operation has "more than one response with specified schema" because 4xx/5xx are
  documented alongside 200. The 4xx/5xx docs are useful; the warning is informational.
