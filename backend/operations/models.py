# backend/api/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum, F, Q
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
    # The default 'username', 'password', 'email', etc. are all inherited
    lastPasswordResetAt = models.DateTimeField(null=True, blank=True)
    tempPasswordLastSetAt = models.DateTimeField(null=True, blank=True)
    mustChangePassword = models.BooleanField(default=False)

# --- 2. Master Data ---

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, primary_key=True) # INR, USD, RMB
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.code

class ChartOfAccount(models.Model):
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
    # For accounts like 'Funds with Agent - USD'
    currency = models.ForeignKey(
        Currency, 
        null=True, 
        blank=True, 
        on_delete=models.PROTECT
    )
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)
    # The 's.mark' you requested, must be unique
    s_mark = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Agent(models.Model):
    name = models.CharField(max_length=255)
    # JSONField is perfect for flexible multi-currency bank details
    bank_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

# --- 3. Core Project (Container) Model ---

class Project(models.Model):
    """ Represents a single Container and its profitability """
    container_number = models.CharField(max_length=100, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.container_number

    # --- Profitability Reporting ---
    # These methods query the GeneralLedger for real-time profit
    
    def get_total_revenue(self):
        """ Sums all 'Income' postings in the ledger for this project (in base currency) """
        return GeneralLedger.objects.filter(
            project=self,
            account__account_type='Income'
        ).aggregate(total=Sum('credit_base'))['total'] or 0

    def get_total_expenses(self):
        """ Sums all 'Expense' postings in the ledger for this project (in base currency) """
        return GeneralLedger.objects.filter(
            project=self,
            account__account_type='Expense'
        ).aggregate(total=Sum('debit_base'))['total'] or 0

    @property
    def net_profit(self):
        """ 
        Revenue is a Credit, Expense is a Debit.
        Profit = Total Credits (Income) - Total Debits (Expense)
        """
        return self.get_total_revenue() - self.get_total_expenses()


# --- 4. Operational Document (Loading List) ---
# This is NOT a financial doc. Its job is to CREATE a Project.

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
        null=True, blank=True, 
        on_delete=models.PROTECT, 
        related_name='submitted_loading_lists'
    )
    
    # This link is set when the Reviewer "Submits" this document
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


# --- 5. Financial Document Base ---
# An abstract model to handle the Draft/Submit workflow for ALL financial docs

class BaseDocument(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'), 
        ('Submitted', 'Submitted'), 
        ('Cancelled', 'Cancelled')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Draft')
    
    # This is the "financial dimension" link
    project = models.ForeignKey(
        Project, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='created_%(class)ss' # e.g., created_journalentrys
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, 
        on_delete=models.PROTECT, 
        related_name='submitted_%(class)ss'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


# --- 6. Specific Financial Documents ---
# These all inherit the Draft/Submit status from BaseDocument

class SalesInvoice(BaseDocument):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    invoice_date = models.DateField()
    due_date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2) # In foreign currency
    
    # On submit, this will post to GeneralLedger:
    # Debit:  Accounts Receivable (Asset)
    # Credit: Sales (Income) <--- This entry gets the project tag

class PurchaseInvoice(BaseDocument):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT)
    invoice_date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2) # In foreign currency
    
    # On submit, this will post to GeneralLedger:
    # Debit:  Freight Expense (Expense) <--- This entry gets the project tag
    # Credit: Accounts Payable - Agent (Liability)

class PaymentEntry(BaseDocument):
    """ For simple payments/receipts, e.g., Customer pays invoice """
    PAYMENT_TYPE = (('Receive', 'Receive'), ('Pay', 'Pay'))
    PARTY_TYPE = (('Customer', 'Customer'), ('Agent', 'Agent'))
    
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE)
    party_type = models.CharField(max_length=10, choices=PARTY_TYPE)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.PROTECT)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.PROTECT)
    
    payment_date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    amount = models.DecimalField(max_digits=15, decimal_places=2) # In foreign currency
    
    # e.g., Pay FROM 'HDFC Bank INR' TO 'Accounts Payable - Agent'
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
    
    # On submit, this will post to GeneralLedger:
    # Debit:  source_account
    # Credit: target_account

class JournalEntry(BaseDocument):
    """ 
    The most powerful document. For complex, multi-line entries like:
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
    
    # Amounts in the specified foreign currency
    debit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    @property
    def debit_base(self):
        """ Converts foreign debit to base currency """
        return self.debit_foreign * self.exchange_rate

    @property
    def credit_base(self):
        """ Converts foreign credit to base currency """
        return self.credit_foreign * self.exchange_rate


# --- 7. THE GENERAL LEDGER ---
# This is the FINAL, immutable table of all transactions.
# All reports are built from this table.
# Entries are created here ONLY when a document is 'Submitted'.

class GeneralLedger(models.Model):
    account = models.ForeignKey(ChartOfAccount, on_delete=models.PROTECT)
    transaction_date = models.DateField(db_index=True)
    
    # --- This is the key to your profitability report ---
    project = models.ForeignKey(
        Project, 
        null=True, 
        blank=True, 
        on_delete=models.PROTECT,
        db_index=True
    )
    
    # Amounts in the BASE currency (e.g., INR)
    debit_base = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_base = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Original amounts in the FOREIGN currency
    debit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_foreign = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    
    # Generic link back to the source document (SalesInvoice, JournalEntry, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=["project", "account"]),
            models.Index(fields=["account", "transaction_date"]),
        ]
        verbose_name_plural = "General Ledger"


# --- 8. Other Modules ---

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
    # This would be calculated and stored after a project is closed
    profit_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)