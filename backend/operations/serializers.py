from rest_framework import serializers
from .models import (
    User, Currency, ChartOfAccount, Customer, Agent, Project,
    LoadingList, LoadingListItem, SalesInvoice, PurchaseInvoice,
    PaymentEntry, JournalEntry, JournalEntryLine, Investor
)

# --- User Serializer ---
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model, formatted for the UsersPage DataGrid.
    """
    # Create 'name' from first_name and last_name
    name = serializers.SerializerMethodField()
    
    # Map 'is_active' to 'status'
    status = serializers.SerializerMethodField()
    
    # Django calls it 'last_login', frontend expects 'lastLogin'
    lastLogin = serializers.DateTimeField(source='last_login', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'username',
            'name',          # From get_name
            'email', 
            'role', 
            'status',        # From get_status
            'lastLogin',     # From last_login
            'lastPasswordResetAt', # New field
            'tempPasswordLastSetAt', # New field
            'mustChangePassword',  # New field
            'first_name',    # Include for editing
            'last_name',     # Include for editing
            'is_active',     # Include for editing
        ]
        # Make fields that are built by methods read-only
        read_only_fields = ['lastLogin', 'lastPasswordResetAt', 'tempPasswordLastSetAt']

    def get_name(self, obj):
        # Combine first and last name, or default to username
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

    def get_status(self, obj):
        return "Active" if obj.is_active else "Inactive"

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'VIEWER'),
            is_active=validated_data.get('is_active', True)
        )
        return user

    # --- ADD THIS UPDATE METHOD ---
    def update(self, instance, validated_data):
        """
        Update and return an existing User instance.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        
        # We don't update password here. That's a separate "reset" flow.
        
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

class ChartOfAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccount
        fields = ['id', 'name', 'account_type', 'parent', 'currency']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code', 'name']

class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = ['id', 'name']


# --- Core Project Serializer ---
class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    Includes read-only properties for profitability.
    """
    # Use StringRelatedField to show the customer's name, not just the ID
    customer_name = serializers.StringRelatedField(source='customer')
    
    class Meta:
        model = Project
        fields = [
            'id', 'container_number', 'customer', 'customer_name', 
            'created_at', 'is_active', 'net_profit' # 'net_profit' is your @property
        ]
        read_only_fields = ['net_profit', 'created_at', 'customer_name']


# --- Document Serializers (with nested items) ---

class LoadingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadingListItem
        fields = ['id', 'item_name', 'quantity', 'description']

class LoadingListSerializer(serializers.ModelSerializer):
    """
    Full serializer for LoadingList, including its nested items.
    """
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


class JournalEntryLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntryLine
        fields = [
            'id', 'account', 'currency', 'exchange_rate',
            'debit_foreign', 'credit_foreign'
        ]

class JournalEntrySerializer(serializers.ModelSerializer):
    """
    Full serializer for JournalEntry, including its nested lines.
    """
    lines = JournalEntryLineSerializer(many=True) # Allow writing lines
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'status', 'project', 'created_by', 'submitted_by',
            'created_at', 'submitted_at', 'notes', 'entry_date', 'lines'
        ]
        read_only_fields = ['created_by', 'submitted_by', 'created_at', 'submitted_at']
    
    # We need custom create/update logic to handle the nested 'lines'
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        journal_entry = JournalEntry.objects.create(**validated_data)
        for line_data in lines_data:
            JournalEntryLine.objects.create(journal_entry=journal_entry, **line_data)
        return journal_entry

# --- Simple Document Serializers ---

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