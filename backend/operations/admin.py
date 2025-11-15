from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Currency, ChartOfAccount, Customer, Agent, Project,
    LoadingList, LoadingListItem, SalesInvoice, PurchaseInvoice,
    PaymentEntry, JournalEntry, JournalEntryLine, GeneralLedger,
    CommissionPayable, Investor, InvestorProfitShare,
    AuditLog, AccountFinance, AccountMetadata,
    AccountGroupHead, AccountGroupMaster
)


# --- 1. User Admin ---

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'lastPasswordResetAt', 'tempPasswordLastSetAt', 'mustChangePassword')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )


# --- 2. Master Data Admins ---

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

    def get_readonly_fields(self, request, obj=None):
        """
        When editing an existing currency, lock the 'code' field.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:  # editing existing row
            readonly.append('code')
        return readonly



@admin.register(AccountGroupHead)
class AccountGroupHeadAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'subtype', 'srno')
    search_fields = ('code', 'name')
    list_filter = ('type',)

    def get_readonly_fields(self, request, obj=None):
        """
        Lock 'code' once the head is created.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly.append('code')
        return readonly



@admin.register(AccountGroupMaster)
class AccountGroupMasterAdmin(admin.ModelAdmin):
    list_display = ('grpcode', 'name', 'type', 'subtype', 'headcode')
    search_fields = ('grpcode', 'name')
    list_filter = ('type', 'headcode')

    def get_readonly_fields(self, request, obj=None):
        """
        Lock 'grpcode' once the group is created.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly.append('grpcode')
        return readonly


@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'parent', 'currency', 'group')
    list_filter = ('account_type', 'currency', 'group')
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


# --- 3. Account Finance & Metadata Admin ---

class AccountMetadataInline(admin.StackedInline):
    model = AccountMetadata
    extra = 0
    can_delete = True

class AccountFinanceAdmin(admin.ModelAdmin):
    list_display = (
        'accode', 'name', 'grpcode', 'curr',
        'currbal', 'currbal_usd', 'currbal_rmb', 'is_active'
    )
    list_filter = ('grpcode', 'curr', 'is_active')
    search_fields = ('accode', 'name', 'custcode', 'customer__name')
    inlines = [AccountMetadataInline]

    def get_readonly_fields(self, request, obj=None):
        """
        Lock 'accode' once the record exists.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly.append('accode')
        return readonly



# --- 4. Core Project Admin ---

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('container_number', 'customer', 'is_active', 'created_at', 'net_profit')
    list_filter = ('is_active', 'customer')
    search_fields = ('container_number', 'customer__name')
    readonly_fields = ('created_at', 'net_profit')



# --- 5. Loading List Admin ---

class LoadingListItemInline(admin.TabularInline):
    model = LoadingListItem
    extra = 1


@admin.register(LoadingList)
class LoadingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'container_number', 'customer', 'status', 'created_by', 'submitted_by')
    list_filter = ('status', 'customer', 'created_by')
    search_fields = ('container_number', 'customer__name')
    readonly_fields = ('submitted_by', 'related_project')
    inlines = [LoadingListItemInline]


# --- 6. Financial Document Admins ---

class BaseDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'status', 'created_by', 'submitted_by', 'created_at')
    list_filter = ('status', 'created_at', 'project')
    search_fields = ('id', 'project__container_number')
    readonly_fields = ('created_by', 'submitted_by', 'created_at', 'submitted_at')

    def save_model(self, request, obj, form, change):
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
    model = JournalEntryLine
    extra = 2


@admin.register(JournalEntry)
class JournalEntryAdmin(BaseDocumentAdmin):
    list_display = ('id', 'entry_date', 'project', 'status', 'created_by')
    inlines = [JournalEntryLineInline]


# --- 7. General Ledger (Read-Only) Admin ---

@admin.register(GeneralLedger)
class GeneralLedgerAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_date', 'account', 'project', 'debit_base', 'credit_base', 'currency')
    list_filter = ('transaction_date', 'account', 'project', 'currency')
    search_fields = ('project__container_number', 'account__name')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# --- 8. Other Module Admins ---

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


# --- 9. Audit Log Admin (Read-Only) ---

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity_type', 'entity_id')
    list_filter = ('action', 'entity_type', 'user')
    search_fields = ('entity_type', 'entity_id', 'details')
    readonly_fields = ('user', 'action', 'entity_type', 'entity_id', 'changes', 'timestamp', 'details')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
