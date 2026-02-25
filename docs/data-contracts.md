# Data Contracts

> **This is the source of truth for all data shapes across the system.**
> Paste this entire document into every agent session before generating engine or API code.
> No agent should invent, rename, or restructure fields without team discussion and an update to this document.

---

## VAT Calculation Input

The input object passed to the VAT engine for every calculation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transactionAmount` | `number` | Yes | The net transaction amount before VAT, in the transaction currency. |
| `customerType` | `"B2B" \| "B2C"` | Yes | Whether the customer is a business or a consumer. Affects VAT treatment. |
| `customerCountry` | `string` | Yes | ISO 3166-1 alpha-2 country code of the customer (e.g. `"DE"`, `"GB"`). |
| `supplierCountry` | `string` | Yes | ISO 3166-1 alpha-2 country code of the supplier. |
| `productCategory` | `string` | Yes | Category of the product or service. Used to determine VAT rate and exemptions. |
| `vatNumber` | `string \| null` | No | Customer's VAT registration number. Required for reverse charge scenarios. |

---

## VAT Calculation Output

The output object returned by the VAT engine after a calculation.

| Field | Type | Description |
|-------|------|-------------|
| `netAmount` | `number` | The transaction amount before VAT (mirrors input `transactionAmount`). |
| `vatAmount` | `number` | The VAT amount calculated. |
| `vatRate` | `number` | The VAT rate applied as a decimal (e.g. `0.20` for 20%). |
| `grossAmount` | `number` | Total amount including VAT (`netAmount + vatAmount`). |
| `jurisdiction` | `string` | The jurisdiction whose rules were applied (ISO country code or region code). |
| `isExempt` | `boolean` | Whether the transaction is VAT-exempt. If `true`, `vatAmount` will be `0`. |
| `invoiceLine` | `string` | Human-readable summary line suitable for display on an invoice. |

---

## API Endpoints

> TBD — to be defined once the API layer is scoped.

| Method | Path | Request Body | Response Body | Notes |
|--------|------|-------------|--------------|-------|
| TBD | | | | |
