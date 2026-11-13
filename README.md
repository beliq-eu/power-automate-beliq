# power-automate-beliq

A Microsoft Power Platform **custom connector** for [beliq](https://beliq.eu):
generate, validate, parse, and convert EN 16931 e-invoices (XRechnung, ZUGFeRD,
Factur-X, Peppol BIS, CII, UBL). This is the Power Automate / Power Apps /
Copilot Studio counterpart of the published
[`n8n-nodes-beliq`](https://www.npmjs.com/package/n8n-nodes-beliq) node, built
from the same product model.

beliq owns the API behind this connector, so a Microsoft certification goes
through the **verified publisher** program in Partner Center. The
Independent Publisher program is for connectors to a service the publisher
does not own, so beliq does not use it. The connector is not submitted for certification
yet; [Status and follow-ups](#status-and-follow-ups) says why and lists the
steps.

## Layout

```
Beliq/
  apiDefinition.swagger.json   OpenAPI 2.0 - the connector operations and body schemas
  apiProperties.json           auth (API key + Bearer policy), brand color, publisher
  settings.json                paconn settings (connectorId/environment filled at deploy time)
  icon.png                     connector icon (beliq mark on the brand color)
  icon.svg                     icon source
  README.md                    connector README, the basis of a submission's intro.md
example-flows/                 the two Generate bodies + curl smoke commands
```

## Connector shape

One connector, five actions:

- **Generate e-invoice** -> `POST /v1/generate` (JSON body, returns XML or PDF: a hybrid PDF/A-3 on Factur-X and ZUGFeRD, a visualization with no embedded XML on XRechnung and Peppol BIS)
- **Validate e-invoice** -> `POST /v1/validate` (raw XML/PDF body, returns JSON)
- **Parse e-invoice** -> `POST /v1/parse` (raw XML/PDF body, returns JSON)
- **Convert e-invoice** -> `POST /v1/convert` (raw XML/PDF body, returns the converted document)
- **Check API key** -> `GET /v1/me` (no quota cost)

The Generate body models the core EN 16931 invoice (seller, buyer, lines, tax
summary, payment means, totals) as typed fields, so flow authors get rich field
mapping. Validate / Parse / Convert take the document as the raw request body.

The Generate standard list carries every standard the API accepts. With NLCIUS,
reached through the National profile field, that is every format
`GET https://api.beliq.eu/v1/rulesets` publishes. The convert
source and target lists are shorter because the API's own convert enums are: no
national format is a conversion target. The Validate and Parse format hints
carry auto, CII and UBL only, while the API's enums also name the national
formats. With auto, Validate detects those from the document; Parse reads CII
and UBL only, whatever the hint says. Widening the two enums changes the
definition's shape, and so does naming the rest of the API's Validate response,
such as the badge and ruleset fields. Both wait for the live import under
[Status and follow-ups](#status-and-follow-ups), the first run of the connector
in a tenant.

How deep beliq's check goes differs by format. The connector types no badge:
[`GET /v1/rulesets`](https://docs.beliq.eu/api-reference/rulesets/) (no API key
needed) lists the rule pack, version and badge of each format beliq offers, and
[How verification works](https://docs.beliq.eu/compliance/how-verification-works/)
explains each depth.

## Authentication

Each connection collects only the beliq API key (a `securestring` connection
parameter). A `setheader` policy in `apiProperties.json` builds the
`Authorization: Bearer <key>` header, so users never type the `Bearer ` prefix.

> The policy-based auth is verified by schema (`paconn validate`). Its runtime
> behavior can only be confirmed by creating a real connection in a tenant,
> which is part of the live-import follow-up below. If certification surfaces a
> problem with the per-connection policy reference, the fallback is a plain
> `apiKey` security definition on the `Authorization` header where the user
> pastes `Bearer <key>`.

## Validate

CI runs two offline checks on every push and pull request
(`.github/workflows/ci.yml`):

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt
python scripts/check_connector.py   # definition, properties, example bodies
bash scripts/scrub-check.sh         # no em-dash in published text
```

`scripts/check_connector.py` validates the Swagger 2.0 document, resolves the
paths in `settings.json`, pins the host and scheme, requires a `summary` and a
`description` on every operation, resolves every `$ref` and reports any
definition no operation reaches, checks that the bearer policy reads a
connection parameter that is declared, and validates each `example-flows/*.json`
against the `GenerateInvoice` request schema the connector publishes.

`paconn validate` is the vendor's own check and is worth running before a
submission, but it signs in to Power Platform first and exits 0 when that login
fails, so it cannot gate a pull request:

```bash
pip install paconn
paconn login
paconn validate --api-def Beliq/apiDefinition.swagger.json
```

## Test the bodies

See `example-flows/README.md` for `curl` commands that exercise each operation
against the live API.

## Status and follow-ups

Done: connector definition, properties, icon, READMEs, two Generate example
bodies, and CI that checks all of them offline on every pull request.

Not submitted for certification. A certified connector is reviewed and
deployed by Microsoft, so beliq waits until its API is stable before it
submits. Until then, import the connector as a custom connector. When beliq
submits, the steps are, in this order:

1. Open a Partner Center Seller account and pass its vetting. The Entra
   account behind it needs an email address, or Microsoft rejects the
   certification request.
2. Redraw the icon to Microsoft's verified publisher rules: a square PNG
   between 100 x 100 and 230 x 230 pixels, no rounded corners, an opaque
   background in the brand colour `#fe6019`, and the mark under 70% of the
   height and width. `Beliq/icon.png` is 256 x 256 today, with rounded corners
   on `#e54d0d`.
3. Set `iconBrandColor` in `Beliq/apiProperties.json` to `#fe6019`. Today it is
   `#da3b01`, the colour Microsoft prescribes for independent publishers.
4. Import the connector into a Power Platform environment, call each
   operation successfully at least 10 times against the production host, and
   run the Solution Checker on the connector's solution.
5. Export the connector solution and a second solution with a test flow,
   package both with the Package Deployer, add an `intro.md`, check the result
   with `scripts/validate_package.py`, and submit it in Partner Center behind a
   SAS URI that stays valid for at least 15 days.

Microsoft's certification pages change, so each step starts by reading them
again.

## License

MIT
