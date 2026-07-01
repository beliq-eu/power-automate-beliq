# Microsoft Independent Publisher submission

This connector is built and validated. What remains is the Independent
Publisher certification flow with Microsoft. Steps are grouped by who does them.

## Status

- Connector files (`Beliq/`): complete and validated (OpenAPI 2.0).
- `iconBrandColor`: `#da3b01` (the mandatory Independent Publisher color).
- `info.title`: `beliq (Independent Publisher)` (required naming pattern; the
  30-char limit applies to the base name only).
- `x-ms-connector-metadata`: Website, Privacy policy, and Categories set on the
  swagger root (`https://beliq.eu`, `https://beliq.eu/legal/privacy-policy/`,
  `Content and Files;Finance`).
- Support contact: `hello@beliq.eu` in `info.contact`.
- Premium note in `Beliq/README.md` is correct: flows using this connector need
  a Power Automate Premium plan (every custom connector does).

## A. File touch-ups (done)

Title suffixed, connector metadata added, Premium claim corrected, contact and
brand color set. Nothing left here.

When building the submission PR, do NOT copy `Beliq/settings.json` into the
Microsoft repo. It is a local paconn helper, not a submission artifact.

## B. Verified credentials (One Vet) - Tobias only

The submission is bound to a real person's verified identity AND the GitHub
account that opens the PR. Anonymous or generic org accounts do not pass: the
GitHub profile name must match a government-issued ID.

Vendor: AU10TIX. App: Microsoft Authenticator. Time: ~15 min. You have 30 days
to finish once started. The credential is reusable for all future PRs and
expires after 1 year or at ID expiry.

1. Pick the submission GitHub account. Its profile name must match your
   government ID (passport / driver's license), and its registered email must
   be one you monitor. This account can be separate from the build account
   (`beliq-eu`).
2. Install Microsoft Authenticator on your phone.
3. Trigger verification by opening a proposal PR (see step C/D) from that
   account. Microsoft has no standalone "request verification" portal; opening
   the PR is what starts it.
4. Microsoft emails the GitHub-registered address a form. Fill it so the form,
   your GitHub profile, and your government ID all match.
5. You then get an AU10TIX email. Open its link in a private window: enter the
   email PIN, your phone number, photograph your ID, take a selfie.
6. Add the resulting Verified ID to Microsoft Authenticator. Done.

## C. Operation screenshots - Tobias only

Microsoft requires one screenshot per operation showing it working. This
connector has five: Generate e-invoice, Validate e-invoice, Parse e-invoice,
Convert e-invoice, and Check API key.

1. Import `Beliq/apiDefinition.swagger.json` + `Beliq/apiProperties.json` as a
   custom connector in a Power Automate environment with a Premium trial.
2. Connect a beliq API key (Check API key confirms it, no quota cost).
3. Run each operation once. Generate turns a JSON invoice into XML or a hybrid
   PDF; feed that output into Validate, Parse, and Convert (see
   `example-flows/README.md` for the bodies and the chaining).
4. Capture one screenshot of each working. Five total, for the PR body.

## D. The PR - mostly automatable, final click is Tobias

1. From the verified account, fork `microsoft/PowerPlatformConnectors`.
2. Copy `Beliq/` (without `settings.json`) into
   `independent-publisher-connectors/beliq/`.
3. Open the PR. Title: `beliq (Independent Publisher)`. Add label
   `independent-publisher-connector`. Fill the PR template checklist. Paste the
   screenshots into the body.

The documented path opens a `Proposal - beliq (Independent Publisher)` PR first
(this is also the verification trigger in step B), then drops the `Proposal -`
prefix and adds all files when ready.

## E. Review - automatable responses, Tobias relays account actions

Swagger Validator and Breaking Change bots run automatically. A Microsoft
reviewer follows. Average deployment is ~15 business days. Updates must come
from the same publisher account that opened the PR.
