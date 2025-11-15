from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    User, Currency, ChartOfAccount, Customer, Agent, Project,
    LoadingList, LoadingListItem, SalesInvoice, PurchaseInvoice,
    PaymentEntry, JournalEntry, JournalEntryLine, Investor,
    AuditLog, AccountFinance, AccountMetadata,
    AccountGroupHead, AccountGroupMaster
)


# --- User Serializer ---

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    lastLogin = serializers.DateTimeField(source='last_login', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'name',
            'email',
            'role',
            'status',
            'lastLogin',
            'lastPasswordResetAt',
            'tempPasswordLastSetAt',
            'mustChangePassword',
            'first_name',
            'last_name',
            'is_active',
        ]
        read_only_fields = ['lastLogin', 'lastPasswordResetAt', 'tempPasswordLastSetAt']

    def get_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

    def get_status(self, obj):
        return "Active" if obj.is_active else "Inactive"

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


# --- Master Data Serializers ---

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 's_mark']


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'name', 'bank_details']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code', 'name']


class AccountGroupHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroupHead
        fields = ['code', 'srno', 'name', 'type', 'subtype', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AccountGroupMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroupMaster
        fields = [
            'grpcode', 'name', 'type', 'subtype',
            'add_info', 'initial', 'headcode',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ChartOfAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccount
        fields = [
            'id',
            'code',
            'name',
            'account_type',
            'parent',
            'currency',
            'group',
            'is_control',
        ]



class AccountMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountMetadata
        fields = [
            'id', 'account',
            'address_line1', 'address_line2', 'address_line3',
            'city', 'pin_code', 'state', 'country',
            'telephone', 'mobile1', 'mobile2',
            'email', 'website',
            'contact_person1', 'contact_person2',
            'gst_no', 'pan_no',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AccountFinanceSerializer(serializers.ModelSerializer):
    metadata = AccountMetadataSerializer(read_only=True)
    customer_name = serializers.StringRelatedField(source='customer', read_only=True)

    class Meta:
        model = AccountFinance
        fields = [
            'accode', 'grpcode', 'custcode', 'customer', 'customer_name',
            'name', 'init', 'bankinit', 'username',
            'openbal', 'closbal', 'closdc',
            'currbal', 'currdc',
            'currbal_usd', 'currdc_usd',
            'currbal_rmb', 'currdc_rmb',
            'closbal_usd', 'closdc_usd',
            'closbal_rmb', 'closdc_rmb',
            'open_usd', 'open_rmb',
            'dc_usd', 'dc_rmb',
            'curr',
            'added_at', 'edited_at', 'created_at', 'updated_at',
            'is_active',
            'metadata',
        ]
        read_only_fields = ['created_at', 'updated_at']


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = ['id', 'name']


# --- Project Serializer ---

class ProjectSerializer(serializers.ModelSerializer):
    customer_name = serializers.StringRelatedField(source='customer')

    class Meta:
        model = Project
        fields = [
            'id', 'container_number', 'customer', 'customer_name',
            'created_at', 'is_active', 'net_profit'
        ]
        read_only_fields = ['net_profit', 'created_at', 'customer_name']


# --- Loading List Serializers ---

class LoadingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadingListItem
        fields = ['id', 'item_name', 'quantity', 'description']


class LoadingListSerializer(serializers.ModelSerializer):
    items = LoadingListItemSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    customer_name = serializers.StringRelatedField(source='customer')

    class Meta:
        model = LoadingList
        fields = [
            'id', 'status', 'container_number', 'customer', 'customer_name',
            'file', 'created_by', 'submitted_by', 'related_project', 'items'
        ]
        read_only_fields = ['created_by', 'submitted_by', 'related_project']


# --- Journal Entry Serializers ---

class JournalEntryLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntryLine
        fields = [
            'id', 'account', 'currency', 'exchange_rate',
            'debit_foreign', 'credit_foreign'
        ]


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'status', 'project', 'created_by', 'submitted_by',
            'created_at', 'submitted_at', 'notes', 'entry_date', 'lines'
        ]
        read_only_fields = ['created_by', 'submitted_by', 'created_at', 'submitted_at']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        journal_entry = JournalEntry.objects.create(**validated_data)
        for line_data in lines_data:
            JournalEntryLine.objects.create(journal_entry=journal_entry, **line_data)
        return journal_entry


# --- Simple Financial Document Serializers ---

class SalesInvoiceSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    customer_name = serializers.StringRelatedField(source='customer')

    class Meta:
        model = SalesInvoice
        fields = [
            'id', 'status', 'project', 'created_by', 'submitted_by', 'notes',
            'customer', 'customer_name', 'invoice_date', 'due_date',
            'currency', 'exchange_rate', 'total_amount'
        ]
        read_only_fields = ['created_by', 'submitted_by']


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    agent_name = serializers.StringRelatedField(source='agent')

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'status', 'project', 'created_by', 'submitted_by', 'notes',
            'agent', 'agent_name', 'invoice_date', 'currency',
            'exchange_rate', 'total_amount'
        ]
        read_only_fields = ['created_by', 'submitted_by']


class PaymentEntrySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = PaymentEntry
        fields = [
            'id', 'status', 'project', 'created_by', 'submitted_by', 'notes',
            'payment_type', 'party_type', 'customer', 'agent', 'payment_date',
            'currency', 'exchange_rate', 'amount', 'source_account', 'target_account'
        ]
        read_only_fields = ['created_by', 'submitted_by']


# --- Audit Log Serializer (read-only) ---

class AuditLogSerializer(serializers.ModelSerializer):
    user_display = serializers.StringRelatedField(source='user', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_display', 'action',
            'entity_type', 'entity_id', 'changes', 'timestamp', 'details'
        ]
        read_only_fields = fields  # fully read-only
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer placeholder.

    Right now it behaves exactly like the default TokenObtainPairSerializer.
    You can extend it later if you want more data in the response.
    """
    pass
