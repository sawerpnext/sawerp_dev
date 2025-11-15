from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from .models import (
    ChartOfAccount,
    GeneralLedger,
    SalesInvoice,
    PurchaseInvoice,
    PaymentEntry,
    JournalEntry,
    JournalEntryLine,
    AuditLog,
)

# --- Special Chart of Account codes used in posting ---

ACCOUNT_CODE_AR_BY_CURRENCY = {
    "INR": "AR_INR",
    "USD": "AR_USD",
    "RMB": "AR_RMB",
}

ACCOUNT_CODE_AP_BY_CURRENCY = {
    "INR": "AP_INR",
    "USD": "AP_USD",
    "RMB": "AP_RMB",
}

ACCOUNT_CODE_FREIGHT_INCOME = "FREIGHT_INCOME"
ACCOUNT_CODE_FREIGHT_CHARGES = "FREIGHT_CHARGES"


def _get_account_by_code(code: str) -> ChartOfAccount:
    """
    Helper to fetch a ChartOfAccount by its internal code (e.g. AR_INR, FREIGHT_INCOME).
    """
    try:
        return ChartOfAccount.objects.get(code=code)
    except ChartOfAccount.DoesNotExist as exc:
        raise ValueError(
            f"Missing ChartOfAccount with code='{code}'. "
            f"Run 'python manage.py seed_coa' to create it."
        ) from exc

# 

def _create_gl_entry(
    *,
    account,
    transaction_date,
    project,
    debit_base: Decimal = Decimal("0"),
    credit_base: Decimal = Decimal("0"),
    debit_foreign: Decimal = Decimal("0"),
    credit_foreign: Decimal = Decimal("0"),
    currency,
    source_object,
) -> GeneralLedger:
    """
    Create a single GeneralLedger row pointing back to the source document.
    """
    if debit_base and credit_base:
        raise ValueError("A ledger row cannot have both debit_base and credit_base non-zero.")

    content_type = ContentType.objects.get_for_model(source_object.__class__)

    return GeneralLedger.objects.create(
        account=account,
        transaction_date=transaction_date,
        project=project,
        debit_base=debit_base,
        credit_base=credit_base,
        debit_foreign=debit_foreign,
        credit_foreign=credit_foreign,
        currency=currency,
        content_type=content_type,
        object_id=source_object.pk,
    )


def _assert_balanced(rows):
    """
    Ensure that all rows together satisfy: total debits == total credits.
    """
    total_debits = sum((row.debit_base for row in rows), Decimal("0"))
    total_credits = sum((row.credit_base for row in rows), Decimal("0"))

    if total_debits != total_credits:
        raise ValueError(f"Ledger not balanced: debits={total_debits}, credits={total_credits}")

def post_sales_invoice(invoice: SalesInvoice):
    """
    Post a SalesInvoice to the General Ledger.

    Logic (multi-currency):
    - DR Accounts Receivable - <currency> (Asset)
    - CR Freight Income (Income)

    Example:
    - If invoice.currency = USD, use AR_USD.
    - Base (INR) amounts go into debit_base/credit_base.
    - Foreign (USD/RMB) amounts go into debit_foreign/credit_foreign.
    """
    base_amount = invoice.total_amount * invoice.exchange_rate

    currency_code = invoice.currency.code
    try:
        ar_code = ACCOUNT_CODE_AR_BY_CURRENCY[currency_code]
    except KeyError:
        raise ValueError(f"No AR account code configured for currency '{currency_code}'.")

    ar_account = _get_account_by_code(ar_code)
    revenue_account = _get_account_by_code(ACCOUNT_CODE_FREIGHT_INCOME)

    rows = []

    # DR Accounts Receivable - <currency>
    rows.append(
        _create_gl_entry(
            account=ar_account,
            transaction_date=invoice.invoice_date,
            project=invoice.project,
            debit_base=base_amount,
            debit_foreign=invoice.total_amount,
            currency=invoice.currency,
            source_object=invoice,
        )
    )

    # CR Freight Income
    rows.append(
        _create_gl_entry(
            account=revenue_account,
            transaction_date=invoice.invoice_date,
            project=invoice.project,
            credit_base=base_amount,
            credit_foreign=invoice.total_amount,
            currency=invoice.currency,
            source_object=invoice,
        )
    )

    _assert_balanced(rows)
    return rows


def post_purchase_invoice(pi: PurchaseInvoice):
    """
    Post a PurchaseInvoice to the General Ledger.

    Logic (multi-currency):
    - DR Freight Charges (Expense)
    - CR Accounts Payable - <currency> (Liability)
    """
    base_amount = pi.total_amount * pi.exchange_rate

    currency_code = pi.currency.code
    try:
        ap_code = ACCOUNT_CODE_AP_BY_CURRENCY[currency_code]
    except KeyError:
        raise ValueError(f"No AP account code configured for currency '{currency_code}'.")

    expense_account = _get_account_by_code(ACCOUNT_CODE_FREIGHT_CHARGES)
    ap_account = _get_account_by_code(ap_code)

    rows = []

    # DR Freight Charges
    rows.append(
        _create_gl_entry(
            account=expense_account,
            transaction_date=pi.invoice_date,
            project=pi.project,
            debit_base=base_amount,
            debit_foreign=pi.total_amount,
            currency=pi.currency,
            source_object=pi,
        )
    )

    # CR Accounts Payable - <currency>
    rows.append(
        _create_gl_entry(
            account=ap_account,
            transaction_date=pi.invoice_date,
            project=pi.project,
            credit_base=base_amount,
            credit_foreign=pi.total_amount,
            currency=pi.currency,
            source_object=pi,
        )
    )

    _assert_balanced(rows)
    return rows


def post_payment_entry(pe: PaymentEntry):
    """
    Post a PaymentEntry to the General Ledger.

    Very simple rule:
    - Money moves from source_account -> target_account
    - DR target_account
    - CR source_account

    The PAYMENT_TYPE and PARTY_TYPE are for information/validation only.
    """
    base_amount = pe.amount * pe.exchange_rate

    rows = []

    rows.append(
        _create_gl_entry(
            account=pe.target_account,
            transaction_date=pe.payment_date,
            project=pe.project,
            debit_base=base_amount,
            debit_foreign=pe.amount,
            currency=pe.currency,
            source_object=pe,
        )
    )

    rows.append(
        _create_gl_entry(
            account=pe.source_account,
            transaction_date=pe.payment_date,
            project=pe.project,
            credit_base=base_amount,
            credit_foreign=pe.amount,
            currency=pe.currency,
            source_object=pe,
        )
    )

    _assert_balanced(rows)
    return rows


def post_journal_entry(je: JournalEntry):
    """
    Post a JournalEntry to the General Ledger.

    Each JournalEntryLine becomes one GL row:
    - debit_base / credit_base come from the line's properties.
    """
    rows = []

    for line in je.lines.all():
        if not line.debit_foreign and not line.credit_foreign:
            # Skip completely empty lines
            continue

        rows.append(
            _create_gl_entry(
                account=line.account,
                transaction_date=je.entry_date,
                project=je.project,
                debit_base=line.debit_base,
                credit_base=line.credit_base,
                debit_foreign=line.debit_foreign,
                credit_foreign=line.credit_foreign,
                currency=line.currency,
                source_object=je,
            )
        )

    if not rows:
        raise ValueError("JournalEntry has no lines with non-zero amounts.")

    _assert_balanced(rows)
    return rows


@transaction.atomic
def submit_document(document, user):
    """
    Common submit helper for all BaseDocument children.

    Steps:
    1. Check status is Draft.
    2. Check we have not already posted ledger rows for this document.
    3. Call the correct posting function.
    4. Mark document as Submitted and stamp submitted_by / submitted_at.
    5. Write an AuditLog row.
    """
    if document.status != "Draft":
        raise ValueError("Only documents in 'Draft' status can be submitted.")

    content_type = ContentType.objects.get_for_model(document.__class__)
    existing = GeneralLedger.objects.filter(
        content_type=content_type,
        object_id=document.pk,
    )
    if existing.exists():
        raise ValueError("This document already has GeneralLedger rows and cannot be submitted again.")

    # Dispatch to the right posting function
    if isinstance(document, SalesInvoice):
        rows = post_sales_invoice(document)
    elif isinstance(document, PurchaseInvoice):
        rows = post_purchase_invoice(document)
    elif isinstance(document, PaymentEntry):
        rows = post_payment_entry(document)
    elif isinstance(document, JournalEntry):
        rows = post_journal_entry(document)
    else:
        raise ValueError(f"Unsupported document type for submit: {document.__class__.__name__}")

    # Move status Draft -> Submitted
    old_status = document.status
    document.status = "Submitted"
    document.submitted_by = user
    document.submitted_at = timezone.now()
    document.save(update_fields=["status", "submitted_by", "submitted_at"])

    # Simple audit log entry
    AuditLog.objects.create(
        user=user,
        action="submit",
        entity_type=document.__class__.__name__,
        entity_id=document.pk,
        changes={"status": [old_status, "Submitted"]},
        details=f"Document submitted and {len(rows)} GeneralLedger rows created.",
    )

    return document
