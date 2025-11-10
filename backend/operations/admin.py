from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Currency, ChartOfAccount, Customer, Agent, Project,
    LoadingList, LoadingListItem, SalesInvoice, PurchaseInvoice,
    PaymentEntry, JournalEntry, JournalEntryLine, GeneralLedger,
    CommissionPayable, Investor, InvestorProfitShare
)

# --- 1. User Admin ---

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Registers the custom User model.
    We add the 'role' field to the display and fieldsets.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )


# --- 2. Master Data Admins ---

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'parent', 'currency')
    list_filter = ('account_type', 'currency')
    search_fields = ('name', 'parent__name')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 's_mark')
    search_fields = ('name', 's_mark')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# --- 3. Core Project Admin ---

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('container_number', 'customer', 'is_active', 'created_at')
    list_filter = ('is_active', 'customer')
    search_fields = ('container_number', 'customer__name')
    readonly_fields = ('created_at',)


# --- 4. Operational Document (Loading List) Admin ---

class LoadingListItemInline(admin.TabularInline):
    """Allows editing Items from within the LoadingList admin page."""
    model = LoadingListItem
    extra = 1  # Show 1 empty form

@admin.register(LoadingList)
class LoadingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'container_number', 'customer', 'status', 'created_by', 'submitted_by')
    list_filter = ('status', 'customer', 'created_by')
    search_fields = ('container_number', 'customer__name')
    readonly_fields = ('submitted_by', 'related_project')
    inlines = [LoadingListItemInline]


# --- 5. Financial Document Admins ---
# We use a base class to share common readonly fields and filters

class BaseDocumentAdmin(admin.ModelAdmin):
    """Shared admin config for all financial documents."""
    list_display = ('id', 'project', 'status', 'created_by', 'submitted_by', 'created_at')
    list_filter = ('status', 'created_at', 'project')
    search_fields = ('id', 'project__container_number')
    readonly_fields = ('created_by', 'submitted_by', 'created_at', 'submitted_at')
    
    def save_model(self, request, obj, form, change):
        """Automatically set the creator on first save."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SalesInvoice)
class SalesInvoiceAdmin(BaseDocumentAdmin):
    list_display = ('id', 'customer', 'project', 'total_amount', 'currency', 'status', 'invoice_date')
    search_fields = ('id', 'project__container_number', 'customer__name')
    list_filter = ('status', 'customer', 'currency', 'invoice_date')

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(BaseDocumentAdmin):
    list_display = ('id', 'agent', 'project', 'total_amount', 'currency', 'status', 'invoice_date')
    search_fields = ('id', 'project__container_number', 'agent__name')
    list_filter = ('status', 'agent', 'currency', 'invoice_date')

@admin.register(PaymentEntry)
class PaymentEntryAdmin(BaseDocumentAdmin):
    list_display = ('id', 'payment_type', 'party_type', 'amount', 'currency', 'status', 'payment_date')
    search_fields = ('id', 'project__container_number', 'customer__name', 'agent__name')
    list_filter = ('status', 'payment_type', 'party_type', 'currency')

class JournalEntryLineInline(admin.TabularInline):
    """Allows editing Lines from within the JournalEntry admin page."""
    model = JournalEntryLine
    extra = 2 # Show 2 empty forms (for debit/credit)

@admin.register(JournalEntry)
class JournalEntryAdmin(BaseDocumentAdmin):
    list_display = ('id', 'entry_date', 'project', 'status', 'created_by')
    inlines = [JournalEntryLineInline]


# --- 6. General Ledger (Read-Only) Admin ---

@admin.register(GeneralLedger)
class GeneralLedgerAdmin(admin.ModelAdmin):
    """
    The General Ledger should be immutable from the admin.
    It's a report, not a data entry form.
    """
    list_display = ('id', 'transaction_date', 'account', 'project', 'debit_base', 'credit_base', 'currency')
    list_filter = ('transaction_date', 'account', 'project', 'currency')
    search_fields = ('project__container_number', 'account__name')
    
    # --- Make it Read-Only ---
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False


# --- 7. Other Module Admins ---

@admin.register(CommissionPayable)
class CommissionPayableAdmin(admin.ModelAdmin):
    list_display = ('project', 'employee', 'amount', 'is_paid')
    list_filter = ('is_paid', 'employee')
    search_fields = ('project__container_number', 'employee__username')

@admin.register(InvestorProfitShare)
class InvestorProfitShareAdmin(admin.ModelAdmin):
    list_display = ('project', 'investor', 'share_percentage', 'profit_amount')
    list_filter = ('investor',)
    search_fields = ('project__container_number', 'investor__name')