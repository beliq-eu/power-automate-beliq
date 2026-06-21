# beliq

[beliq](https://beliq.eu) is an EU e-invoicing compliance API. It generates,
validates, parses, and converts EN 16931 invoices against authority-pinned,
nightly-drift-checked rules. beliq produces and checks the compliant document;
transmission, archiving, and tax-authority reporting stay with your access
point.

## Publisher

beliq

## Prerequisites

You need a beliq account and an API key. The free tier is enough to evaluate
the connector. No Power Automate premium license is required to use a custom
connector (unlike the generic HTTP action).

## Obtaining credentials

1. Sign in at [dashboard.beliq.eu](https://dashboard.beliq.eu).
2. Open **API Keys** and create a key.
3. When you create the connection, paste the key into **beliq API key**. Paste
   only the key; the connector adds the `Bearer ` prefix for you.

Use **Check API key** (no quota cost) to confirm the connection works.

## Supported operations

| Operation | What it does |
| --- | --- |
| **Generate e-invoice** | Build a compliant e-invoice from a structured EN 16931 invoice object. Returns the XML, or a hybrid PDF (Factur-X / ZUGFeRD) when Output is PDF. |
| **Validate e-invoice** | Check a raw XML or PDF e-invoice against the authority-pinned rules. Returns a structured result with errors and warnings. |
| **Parse e-invoice** | Read a raw XML or PDF e-invoice into a structured invoice object. |
| **Convert e-invoice** | Convert a raw XML or PDF e-invoice between formats within the EN 16931 family. |
| **Check API key** | Return the account, plan, and quota context for the calling key. Does not consume quota. |

### Formats

Generate targets **XRechnung**, **ZUGFeRD**, **Factur-X**, and **Peppol BIS**.
Convert moves between **CII**, **UBL**, **ZUGFeRD**, **Factur-X**, **XRechnung**,
and **Peppol BIS**. Validate and parse accept **CII** and **UBL** syntaxes, or
auto-detect from the document.

### Input and output

- **Generate** takes a JSON invoice body and returns the document as binary file
  content. Pass the output to a downstream step, for example **Create file**
  (OneDrive / SharePoint / Blob) or an email attachment.
- **Validate**, **Parse**, and **Convert** take the raw document as the request
  body (XML or PDF file content). Map the file content from a previous step, for
  example **Get file content**. The engine detects XML versus PDF from the
  content. Validate and Parse return JSON; Convert returns the converted document
  as binary file content.

## Known issues and limitations

- The **Generate** and **Convert** responses are declared as a binary file.
  Convert echoes the detected source and target formats in the
  `X-Source-Format` and `X-Target-Format` response headers.
- E-invoices follow EN 16931. At minimum provide a due date or payment terms
  (rule BR-CO-25), the seller VAT ID when a line uses VAT category `S`, and
  consistent totals (net + tax = gross). With **Verify** enabled, a document
  that fails validation returns an error.
- The connector models the core EN 16931 invoice fields. Country-specific
  extensions are accepted by the API but are not surfaced as typed fields.

## Authentication

Each connection collects only the beliq API key (a `securestring` connection
parameter). A `setheader` policy in `apiProperties.json` builds the
`Authorization: Bearer <key>` header, so users never type the `Bearer ` prefix.

## Deployment instructions

This connector is a standard Power Platform custom connector
(`apiDefinition.swagger.json` + `apiProperties.json` + `icon.png`). Deploy it
with the Power Platform Connectors CLI:

```bash
# one-time login
paconn login

# validate the definition
paconn validate --api-def apiDefinition.swagger.json

# create the connector in the selected environment
paconn create --api-def apiDefinition.swagger.json \
  --api-prop apiProperties.json --icon icon.png
```

You can also import `apiDefinition.swagger.json` directly from the Power Automate
maker portal (**Data > Custom connectors > New custom connector > Import an
OpenAPI file**).
