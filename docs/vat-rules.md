# VAT Rules

> Starter VAT rule set for development flow tests.
> Replace with validated legal policy before production use.

---

## Jurisdictions in Scope

| Jurisdiction | Notes |
|-------------|-------|
| DK | Default baseline jurisdiction |
| DE | Cross-border example jurisdiction |

---

## VAT Rates by Country

| Country | Standard Rate | Reduced Rate(s) | Zero Rate | Notes |
|---------|---------------|-----------------|----------|-------|
| DK | 0.25 | none | 0.00 | Base reference for tests |
| DE | 0.19 | 0.07 | 0.00 | Reduced example for books |

---

## B2B vs B2C Rules

### B2B (Business to Business)
- Same-country B2B: apply local standard VAT unless exempt.
- Cross-border B2B with valid `vatNumber`: reverse charge.

### B2C (Business to Consumer)
- Same-country B2C: apply local standard/reduced rate by category.
- Cross-border B2C: apply supplier-country VAT in this starter profile.

---

## Exemptions and Zero-Rated Goods

| Category | Treatment | Jurisdictions | Notes |
|----------|-----------|--------------|-------|
| medical_services | exempt | DK, DE | VAT not charged |
| education_services | exempt | DK, DE | VAT not charged |
| books | reduced | DE | Uses DE 7 percent reduced rate |
| exports_outside_eu | zero-rated | DK, DE | Zero rate for qualifying exports |

---

## Reverse Charge Mechanism

### When it applies
- `customerType` is `B2B`
- `supplierCountry` differs from `customerCountry`
- `vatNumber` is present

### How to calculate
- Set `vatRate` to `0.00`
- Set `vatAmount` to `0`
- Set `isExempt` to `true`
- Set `grossAmount` equal to `netAmount`

### Required fields
- `transactionAmount`
- `customerType`
- `customerCountry`
- `supplierCountry`
- `productCategory`
- `vatNumber`
