from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# --- 1. Custom User Model ---
# We extend the default User to add our specific roles

class User(AbstractUser):
    class Role(models.TextChoices):
        CREATOR = 'CREATOR', 'Creator'
        REVIEWER = 'REVIEWER', 'Reviewer'
        ADMIN = 'ADMIN', 'Admin'
        VIEWER = 'VIEWER', 'Viewer'

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.VIEWER
    )
    # Extra password tracking fields
    lastPasswordResetAt = models.DateTimeField(null=True, blank=True)
    tempPasswordLastSetAt = models.DateTimeField(null=True, blank=True)
    mustChangePassword = models.BooleanField(default=False)


# --- 2. Master Data: Currency & Chart of Accounts ---

class Currency(models.Model):
    # Example: INR, USD, RMB
    code = models.CharField(max_length=3, unique=True, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.code


class ChartOfAccount(models.Model):
    """
    Main Chart of Accounts table.
    - account_type: high-level type (Asset, Liability, etc.)
    - parent: for tree structure (Assets > Bank Accounts > HDFC Bank INR)
    - currency: one currency per account (or empty for generic heads)
    - group: link to accounting group (for reporting/COA structure)
    """
    ACCOUNT_TYPES = (
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Equity', 'Equity'),
    )

    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    currency = models.ForeignKey(
        Currency,
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    # NEW: link to detailed group master (Phase 2)
    group = models.ForeignKey(
        'AccountGroupMaster',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='chart_accounts'
    )

    def __str__(self):
        return self.name


# --- 3. Audit Log (from Audit_log / Log table) ---

class AuditLog(models.Model):
    """
    Single table for auditing all system actions:
    - who did what
    - on which entity
    - when
    - what changed (JSON diff)
    """
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('submit', 'Submit'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who performed the action. Null for system actions."
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50, help_text="Model name, e.g. 'Customer', 'AccountFinance'.")
    entity_id = models.BigIntegerField(help_text="Primary key of the affected row.")
    changes = models.JSONField(null=True, blank=True, help_text="JSON diff of old vs new values.")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True, help_text="Extra info like IP, request id, etc.")

    class Meta:
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} {self.action} {self.entity_type}({self.entity_id})"


# --- 4. Account Group Head & Master (Grphead / Grpmast) ---

class AccountGroupHead(models.Model):
    """
    High-level COA heads:
    - Asset
    - Liability
    - Income
    - Expense
    - Equity
    """
    HEAD_TYPE_CHOICES = (
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Equity', 'Equity'),
    )

    code = models.CharField(max_length=50, primary_key=True)
    srno = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=HEAD_TYPE_CHOICES)
    subtype = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Group Head"
        verbose_name_plural = "Account Group Heads"

    def __str__(self):
        return self.name


class AccountGroupMaster(models.Model):
    """
    Detailed account groups (e.g., 'Bank Accounts', 'Funds with Agent - USD').
    """
    TYPE_CHOICES = AccountGroupHead.HEAD_TYPE_CHOICES

    grpcode = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    subtype = models.CharField(max_length=50, null=True, blank=True)
    add_info = models.TextField(null=True, blank=True)
    initial = models.CharField(max_length=10, null=True, blank=True)

    headcode = models.ForeignKey(
        AccountGroupHead,
        on_delete=models.PROTECT,
        related_name='groups'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Group"
        verbose_name_plural = "Account Groups"

    def __str__(self):
        return self.name


# --- 5. Parties: Customer & Agent ---

class Customer(models.Model):
    name = models.CharField(max_length=255)
    # s_mark is a unique tag used in the loading list and for mapping
    s_mark = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Agent(models.Model):
    name = models.CharField(max_length=255)
    # Flexible structure for per-currency bank details
    bank_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


# --- 6. Account Finance & Metadata (Account_fin / Account_info) ---

class AccountFinance(models.Model):
    """
    Core financial info for an account/party.
    Includes balances in INR, USD, RMB.
    """
    DC_CHOICES = (
        ('D', 'Debit'),
        ('C', 'Credit'),
    )

    # Primary key
    accode = models.CharField(max_length=50, primary_key=True)

    # Group (was grpcode in legacy, now FK to AccountGroupMaster)
    grpcode = models.ForeignKey(
        AccountGroupMaster,
        on_delete=models.PROTECT,
        related_name='accounts',
        help_text="Account group (e.g., Bank, Debtors, Funds with Agent)."
    )

    # Optional link to Customer and legacy code
    custcode = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Legacy customer code (for migration)."
    )
    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='account_finance',
        help_text="Linked customer, if this account is for a customer."
    )

    name = models.CharField(max_length=255)
    init = models.CharField(max_length=10, null=True, blank=True, help_text="Initials.")
    bankinit = models.CharField(max_length=10, null=True, blank=True, help_text="Bank initials.")
    username = models.CharField(max_length=150, null=True, blank=True, unique=True)

    # Opening / closing balances in INR
    openbal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closbal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closdc = models.CharField(max_length=1, choices=DC_CHOICES, default='C')

    # Current balances in INR
    currbal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currdc = models.CharField(max_length=1, choices=DC_CHOICES, default='C')

    # USD balances
    currbal_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currdc_usd = models.CharField(max_length=1, choices=DC_CHOICES, default='C', null=True, blank=True)

    # RMB balances
    currbal_rmb = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currdc_rmb = models.CharField(max_length=1, choices=DC_CHOICES, default='C', null=True, blank=True)

    # Closing balances in USD/RMB
    closbal_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closdc_usd = models.CharField(max_length=1, choices=DC_CHOICES, default='C', null=True, blank=True)
    closbal_rmb = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closdc_rmb = models.CharField(max_length=1, choices=DC_CHOICES, default='C', null=True, blank=True)

    # Opening foreign balances
    open_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    open_rmb = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    dc_usd = models.CharField(max_length=1, choices=DC_CHOICES, default='C', null=True, blank=True)
    dc_rmb = models.CharField(max_length=1, choices=DC_CHOICES, default='C', null=True, blank=True)

    # Default currency
    curr = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        default='INR'
    )

    added_at = models.DateTimeField(null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft-delete flag
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['grpcode']),
            models.Index(fields=['currbal', 'currbal_usd', 'currbal_rmb']),
        ]
        verbose_name = "Account Finance"
        verbose_name_plural = "Account Finance"

    def __str__(self):
        return f"{self.accode} - {self.name}"


class AccountMetadata(models.Model):
    """
    Non-financial metadata for an account:
    address, contacts, GST, PAN, etc.
    1:1 with AccountFinance.
    """
    account = models.OneToOneField(
        AccountFinance,
        on_delete=models.CASCADE,
        related_name='metadata'
    )

    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    address_line3 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=20, blank=True, null=True)

    # NOTE: In the Word doc this was a FK to a State table.
    # For now we keep it as free text to keep things simple.
    state = models.CharField(max_length=100, blank=True, null=True)

    country = models.CharField(max_length=100, default='India')
    telephone = models.CharField(max_length=50, blank=True, null=True)
    mobile1 = models.CharField(max_length=50, blank=True, null=True)
    mobile2 = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    contact_person1 = models.CharField(max_length=255, blank=True, null=True)
    contact_person2 = models.CharField(max_length=255, blank=True, null=True)
    gst_no = models.CharField(max_length=50, blank=True, null=True)
    pan_no = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['gst_no']),
            models.Index(fields=['email']),
            models.Index(fields=['city', 'account']),
        ]
        verbose_name = "Account Metadata"
        verbose_name_plural = "Account Metadata"

    def __str__(self):
        return f"Metadata for {self.account_id}"


# --- 7. Core Project (Container) Model ---

class Project(models.Model):
    """Represents a single Container and its profitability."""
    container_number = models.CharField(max_length=100, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.container_number

    # --- Profitability Reporting ---

    def get_total_revenue(self):
        """Sum of all 'Income' postings in the ledger for this project (base currency)."""
        return GeneralLedger.objects.filter(
            project=self,
            account__account_type='Income'
        ).aggregate(total=Sum('credit_base'))['total'] or 0

    def get_total_expenses(self):
        """Sum of all 'Expense' postings in the ledger for this project (base currency)."""
        return GeneralLedger.objects.filter(
            project=self,
            account__account_type='Expense'
        ).aggregate(total=Sum('debit_base'))['total'] or 0

    @property
    def net_profit(self):
        """Profit = Total Income Credits - Total Expense Debits."""
        return self.get_total_revenue() - self.get_total_expenses()


# --- 8. Operational Document (Loading List) ---

class LoadingList(models.Model):
    STATUS_CHOICES = (('Draft', 'Draft'), ('Submitted', 'Submitted'))

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    container_number = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    file = models.FileField(upload_to='loading_lists/', null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='loading_lists'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='submitted_loading_lists'
    )

    related_project = models.OneToOneField(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"LL-{self.id} ({self.container_number})"


class LoadingListItem(models.Model):
    loading_list = models.ForeignKey(
        LoadingList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)


# --- 9. Base Document for Financial Docs ---

class BaseDocument(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Cancelled', 'Cancelled'),
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_%(class)ss'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='submitted_%(class)ss'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


# --- 10. Specific Financial Documents ---

class SalesInvoice(BaseDocument):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    invoice_date = models.DateField()
    due_date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)  # In foreign currency


class PurchaseInvoice(BaseDocument):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT)
    invoice_date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)  # In foreign currency


class PaymentEntry(BaseDocument):
    """For simple payments/receipts, e.g., Customer pays invoice."""
    PAYMENT_TYPE = (('Receive', 'Receive'), ('Pay', 'Pay'))
    PARTY_TYPE = (('Customer', 'Customer'), ('Agent', 'Agent'))

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE)
    party_type = models.CharField(max_length=10, choices=PARTY_TYPE)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.PROTECT)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.PROTECT)

    payment_date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # In foreign currency

    source_account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.PROTECT,
        related_name='debit_payments'
    )
    target_account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.PROTECT,
        related_name='credit_payments'
    )


class JournalEntry(BaseDocument):
    """
    For complex, multi-line entries like:
    - Agent Advance Payment
    - Agent Currency Conversion
    - Internal Bank Transfers
    """
    entry_date = models.DateField()

    def __str__(self):
        return f"JV-{self.id}"


class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.ForeignKey(ChartOfAccount, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)

    debit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @property
    def debit_base(self):
        return self.debit_foreign * self.exchange_rate

    @property
    def credit_base(self):
        return self.credit_foreign * self.exchange_rate


# --- 11. General Ledger ---

class GeneralLedger(models.Model):
    account = models.ForeignKey(ChartOfAccount, on_delete=models.PROTECT)
    transaction_date = models.DateField(db_index=True)

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True
    )

    debit_base = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_base = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    debit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=["project", "account"]),
            models.Index(fields=["account", "transaction_date"]),
        ]
        verbose_name_plural = "General Ledger"


# --- 12. Other Modules ---

class CommissionPayable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_paid = models.BooleanField(default=False)


class Investor(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class InvestorProfitShare(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    investor = models.ForeignKey(Investor, on_delete=models.PROTECT)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    profit_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
