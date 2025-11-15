# Backend Master Data (Phase 2)

## New Models

### AccountGroupHead
- High-level heads: Asset, Liability, Income, Expense, Equity.
- Fields: code, name, type, subtype.

### AccountGroupMaster
- Detailed groups under heads.
- Example: grpcode=BANK, name="Bank Accounts", type="Asset", headcode="ASSET".

### AccountFinance
- Financial balances per account/party.
- Key fields:
  - accode (PK)
  - grpcode (FK to AccountGroupMaster)
  - customer (FK to Customer)
  - curr (FK to Currency)
  - INR balances: openbal, closbal, currbal, closdc, currdc
  - USD/RMB balances: currbal_usd, currbal_rmb, etc.
- Editable via:
  - Admin: "Account Finance"
  - API: `/api/account-finance/`

### AccountMetadata
- 1:1 with AccountFinance (field: account).
- Contact + address fields: address_line1/2/3, city, state, country, mobile1/2, email, website, gst_no, pan_no.
- Editable via:
  - Admin inline under Account Finance.
  - API: `/api/account-metadata/`

### AuditLog
- Logs actions like create/edit/delete/submit.
- Currently read-only; will be filled later via signals.
- API: `/api/audit-logs/` (GET only).

## API Endpoints (Phase 2)

- `GET/POST /api/account-group-heads/`
- `GET/POST /api/account-groups/`
- `GET/POST /api/account-finance/`
- `GET/POST /api/account-metadata/`
- `GET /api/audit-logs/`
