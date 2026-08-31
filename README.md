# power-automate-beliq

A Microsoft Power Platform **custom connector** for [beliq](https://beliq.eu):
generate, validate, parse, and convert EN 16931 e-invoices (XRechnung, ZUGFeRD,
Factur-X, Peppol BIS, CII, UBL). This is the Power Automate / Power Apps /
Copilot Studio counterpart of the published
[`n8n-nodes-beliq`](https://www.npmjs.com/package/n8n-nodes-beliq) node, built
from the same product model.

It targets the Microsoft **Independent Publisher** program, so the layout under
`Beliq/` matches the
[microsoft/PowerPlatformConnectors](https://github.com/microsoft/PowerPlatformConnectors)
`independent-publisher-connectors/<Name>/` convention.

## Layout

```
Beliq/
  apiDefinition.swagger.json   OpenAPI 2.0 - the connector operations and body schemas
  apiProperties.json           auth (API key + Bearer policy), brand color, publisher
  settings.json                paconn settings (connectorId/environment filled at deploy time)
  icon.png                     connector icon (beliq mark on the brand color)
  icon.svg                     icon source
  README.md                    connector README (ships with the IP submission)
example-flows/                 the two Generate bodies + curl smoke commands
```

## Connector shape

One connector, five actions:

- **Generate e-invoice** -> `POST /v1/generate` (JSON body, returns XML or hybrid PDF)
- **Validate e-invoice** -> `POST /v1/validate` (raw XML/PDF body, returns JSON)
- **Parse e-invoice** -> `POST /v1/parse` (raw XML/PDF body, returns JSON)
- **Convert e-invoice** -> `POST /v1/convert` (raw XML/PDF body, returns the converted document)
- **Check API key** -> `GET /v1/me` (no quota cost)

The Generate body models the core EN 16931 invoice (seller, buyer, lines, tax
summary, payment means, totals) as typed fields, so flow authors get rich field
mapping. Validate / Parse / Convert take the document as the raw request body.

The format option lists are the live, publicly-offered subset of the beliq
coverage manifest in `beliq-types`. They are kept in sync with the `n8n-nodes-beliq`
node; provisional formats are withheld from the dropdowns.

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

Not done yet (tracked as follow-ups):

- Live import into a Power Automate environment, create a connection, run the
  operations, and capture screenshots.
- Smoke-test the bodies against the live API once a key and the production
  endpoint are available.
- Independent Publisher submission PR to `microsoft/PowerPlatformConnectors`
  (PR titled "beliq (Independent Publisher)"; the README must include
  screenshots of operations succeeding in flows).
