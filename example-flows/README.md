# Example flows

These files are the **request bodies** for the **Generate e-invoice** action.
They double as the payloads used to smoke-test the connector against the live
API.

| File | Operation | Use case |
| --- | --- | --- |
| `1-generate-xrechnung.json` | Generate e-invoice | An EN 16931 invoice generated as XRechnung XML. |
| `2-generate-facturx-pdf.json` | Generate e-invoice | The same invoice generated as a Factur-X hybrid PDF, with `verify` enabled. |

The **Validate**, **Parse**, and **Convert** actions take a raw XML or PDF
document as the body rather than JSON. The easiest source of a valid document
is the output of **Generate e-invoice**: run the XRechnung body above, then
feed the returned XML into Validate, Parse, or Convert. The `curl` block below
runs that whole chain end to end.

## Using one in a flow

1. Add the **beliq** **Generate e-invoice** action to your flow.
2. Map the fields from the matching JSON file. **Standard**, **Output**, and
   the **Invoice** object are the main inputs.
3. Pass the action output (binary file content) to a downstream step, for
   example **Create file** (OneDrive / SharePoint / Blob) or an email
   attachment.

For Validate / Parse / Convert, map a raw document into the **Document** body,
for example the file content from a **Get file content** step or the output of
a preceding **Generate** action.

## Testing the bodies directly

The same bodies work against the API with `curl`. Generate and Convert return
the document; Validate and Parse return JSON.

```bash
# Generate XRechnung XML
curl -sS -D - -o invoice.xml \
  -H "Authorization: Bearer $BELIQ_API_KEY" \
  -H "Content-Type: application/json" \
  --data @1-generate-xrechnung.json \
  https://api.beliq.eu/v1/generate

# Generate a Factur-X hybrid PDF
curl -sS -D - -o invoice.pdf \
  -H "Authorization: Bearer $BELIQ_API_KEY" \
  -H "Content-Type: application/json" \
  --data @2-generate-facturx-pdf.json \
  https://api.beliq.eu/v1/generate

# Validate the generated XML
curl -sS \
  -H "Authorization: Bearer $BELIQ_API_KEY" \
  -H "Content-Type: application/xml" \
  --data-binary @invoice.xml \
  "https://api.beliq.eu/v1/validate?format=auto"

# Parse the generated XML into structured JSON
curl -sS \
  -H "Authorization: Bearer $BELIQ_API_KEY" \
  -H "Content-Type: application/xml" \
  --data-binary @invoice.xml \
  "https://api.beliq.eu/v1/parse?format=auto"

# Convert the XML to UBL
curl -sS -D - -o invoice-ubl.xml \
  -H "Authorization: Bearer $BELIQ_API_KEY" \
  -H "Content-Type: application/xml" \
  --data-binary @invoice.xml \
  "https://api.beliq.eu/v1/convert?targetFormat=ubl"
```
