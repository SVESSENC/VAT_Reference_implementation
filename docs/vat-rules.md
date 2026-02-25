# VAT Rules

> **This is the source of truth for all VAT calculation logic.**
> Paste this entire document into any agent session working on the engine or VAT calculation code.
> Do not implement VAT logic that contradicts or extends beyond what is documented here.

---

## Jurisdictions in Scope

> TBD — list the countries or regions this implementation covers.

| Jurisdiction | Notes |
|-------------|-------|
| TBD | |

---

## VAT Rates by Country

> TBD — document the standard, reduced, and zero rates per jurisdiction.

| Country | Standard Rate | Reduced Rate(s) | Zero Rate | Notes |
|---------|-------------|----------------|----------|-------|
| TBD | | | | |

---

## B2B vs B2C Rules

> TBD — describe how VAT treatment differs between business and consumer transactions.

### B2B (Business to Business)
- TBD

### B2C (Business to Consumer)
- TBD

---

## Exemptions and Zero-Rated Goods

> TBD — list product categories or transaction types that are exempt or zero-rated.

| Category | Treatment | Jurisdictions | Notes |
|----------|-----------|--------------|-------|
| TBD | | | |

---

## Reverse Charge Mechanism

> TBD — describe when and how reverse charge applies (typically cross-border B2B).

### When it applies
- TBD

### How to calculate
- TBD

### Required fields
- TBD (see also `docs/data-contracts.md` for the `vatNumber` field)
