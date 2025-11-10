from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    User, Currency, ChartOfAccount, Customer, Agent, Project,
    LoadingList, SalesInvoice, PurchaseInvoice,
    PaymentEntry, JournalEntry, Investor
)
from .serializers import (
    UserSerializer, CurrencySerializer, ChartOfAccountSerializer, CustomerSerializer,
    AgentSerializer, ProjectSerializer, LoadingListSerializer, SalesInvoiceSerializer,
    PurchaseInvoiceSerializer, PaymentEntrySerializer, JournalEntrySerializer,
    InvestorSerializer
)

# --- Base ViewSet for Auto-Setting Creator ---

class BaseDocumentViewSet(viewsets.ModelViewSet):
    """
    A base viewset for all financial and operational documents.
    It automatically sets the 'created_by' field to the current user
    on creation.
    """
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set the creator to the logged-in user."""
        serializer.save(created_by=self.request.user)

# --- ViewSets for Each Model ---

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for Users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # You might change this to IsAdminUser

class CustomerViewSet(viewsets.ModelViewSet):
    """API endpoint for Customers."""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class AgentViewSet(viewsets.ModelViewSet):
    """API endpoint for Agents."""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

class InvestorViewSet(viewsets.ModelViewSet):
    """API endpoint for Investors."""
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [IsAuthenticated]

class CurrencyViewSet(viewsets.ModelViewSet):
    """API endpoint for Currencies."""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]

class ChartOfAccountViewSet(viewsets.ModelViewSet):
    """API endpoint for the Chart of Accounts."""
    queryset = ChartOfAccount.objects.all()
    serializer_class = ChartOfAccountSerializer
    permission_classes = [IsAuthenticated]

class ProjectViewSet(viewsets.ModelViewSet):
    """API endpoint for Projects."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

# --- Document ViewSets (using the Base class) ---

class LoadingListViewSet(BaseDocumentViewSet):
    """API endpoint for Loading Lists."""
    queryset = LoadingList.objects.all()
    serializer_class = LoadingListSerializer

class SalesInvoiceViewSet(BaseDocumentViewSet):
    """API endpoint for Sales Invoices."""
    queryset = SalesInvoice.objects.all()
    serializer_class = SalesInvoiceSerializer

class PurchaseInvoiceViewSet(BaseDocumentViewSet):
    """API endpoint for Purchase Invoices."""
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer

class PaymentEntryViewSet(BaseDocumentViewSet):
    """API endpoint for Payment Entries."""
    queryset = PaymentEntry.objects.all()
    serializer_class = PaymentEntrySerializer

class JournalEntryViewSet(BaseDocumentViewSet):
    """API endpoint for Journal Entries."""
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer

class CurrentUserView(APIView):
    """
    An endpoint to get the current authenticated user's details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return the user's data.
        """
        # request.user is automatically set by TokenAuthentication
        serializer = UserSerializer(request.user)
        return Response(serializer.data)