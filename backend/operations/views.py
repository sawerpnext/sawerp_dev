from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action


from .models import (
    User, Currency, ChartOfAccount, Customer, Agent, Project,
    LoadingList, SalesInvoice, PurchaseInvoice,
    PaymentEntry, JournalEntry, Investor,
    AuditLog, AccountFinance, AccountMetadata,
    AccountGroupHead, AccountGroupMaster
)
from .serializers import (
    UserSerializer, CurrencySerializer, ChartOfAccountSerializer, CustomerSerializer,
    AgentSerializer, ProjectSerializer, LoadingListSerializer, SalesInvoiceSerializer,
    PurchaseInvoiceSerializer, PaymentEntrySerializer, JournalEntrySerializer,
    InvestorSerializer, AuditLogSerializer, AccountFinanceSerializer,
    AccountMetadataSerializer, AccountGroupHeadSerializer, AccountGroupMasterSerializer
)

from .posting import submit_document
# --- Base ViewSet for Documents (sets created_by) ---

class BaseDocumentViewSet(viewsets.ModelViewSet):
    """
    Common behaviour for all document ViewSets that inherit from BaseDocument:
    - Auto-fill created_by on create
    - Provide /submit/ action to post into the General Ledger
    """
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """
        Submit this document:

        - Moves status from Draft -> Submitted
        - Creates GeneralLedger rows using the posting service
        - Returns the updated document
        """
        document = self.get_object()
        submit_document(document, request.user)
        serializer = self.get_serializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)



# --- Core Master Data ViewSets ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]


class InvestorViewSet(viewsets.ModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [IsAuthenticated]


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]


class AccountGroupHeadViewSet(viewsets.ModelViewSet):
    queryset = AccountGroupHead.objects.all()
    serializer_class = AccountGroupHeadSerializer
    permission_classes = [IsAuthenticated]


class AccountGroupMasterViewSet(viewsets.ModelViewSet):
    queryset = AccountGroupMaster.objects.all()
    serializer_class = AccountGroupMasterSerializer
    permission_classes = [IsAuthenticated]


class ChartOfAccountViewSet(viewsets.ModelViewSet):
    queryset = ChartOfAccount.objects.all()
    serializer_class = ChartOfAccountSerializer
    permission_classes = [IsAuthenticated]


class AccountFinanceViewSet(viewsets.ModelViewSet):
    queryset = AccountFinance.objects.select_related('grpcode', 'customer', 'curr')
    serializer_class = AccountFinanceSerializer
    permission_classes = [IsAuthenticated]


class AccountMetadataViewSet(viewsets.ModelViewSet):
    queryset = AccountMetadata.objects.select_related('account')
    serializer_class = AccountMetadataSerializer
    permission_classes = [IsAuthenticated]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


# --- Document ViewSets ---

class LoadingListViewSet(BaseDocumentViewSet):
    queryset = LoadingList.objects.all()
    serializer_class = LoadingListSerializer


class SalesInvoiceViewSet(BaseDocumentViewSet):
    queryset = SalesInvoice.objects.all()
    serializer_class = SalesInvoiceSerializer


class PurchaseInvoiceViewSet(BaseDocumentViewSet):
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer


class PaymentEntryViewSet(BaseDocumentViewSet):
    queryset = PaymentEntry.objects.all()
    serializer_class = PaymentEntrySerializer


class JournalEntryViewSet(BaseDocumentViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer


# --- Audit Log View (read-only) ---

class AuditLogViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]


# --- Current User Helper ---

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
