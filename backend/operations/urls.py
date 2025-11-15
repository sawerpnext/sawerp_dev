from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'investors', views.InvestorViewSet, basename='investor')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'currencies', views.CurrencyViewSet, basename='currency')

router.register(r'account-group-heads', views.AccountGroupHeadViewSet, basename='accountgrouphead')
router.register(r'account-groups', views.AccountGroupMasterViewSet, basename='accountgroup')
router.register(r'accounts', views.ChartOfAccountViewSet, basename='account')
router.register(r'account-finance', views.AccountFinanceViewSet, basename='accountfinance')
router.register(r'account-metadata', views.AccountMetadataViewSet, basename='accountmetadata')

router.register(r'loading-lists', views.LoadingListViewSet, basename='loadinglist')
router.register(r'sales-invoices', views.SalesInvoiceViewSet, basename='salesinvoice')
router.register(r'purchase-invoices', views.PurchaseInvoiceViewSet, basename='purchaseinvoice')
router.register(r'payment-entries', views.PaymentEntryViewSet, basename='paymententry')
router.register(r'journal-entries', views.JournalEntryViewSet, basename='journalentry')

router.register(r'audit-logs', views.AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", views.CurrentUserView.as_view(), name="current-user"),
    path("", include(router.urls)),
]
