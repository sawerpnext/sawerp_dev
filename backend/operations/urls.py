# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router
router = DefaultRouter()

# Register each ViewSet with the router
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'investors', views.InvestorViewSet, basename='investor')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'currencies', views.CurrencyViewSet, basename='currency')
router.register(r'accounts', views.ChartOfAccountViewSet, basename='account')
router.register(r'loading-lists', views.LoadingListViewSet, basename='loadinglist')
router.register(r'sales-invoices', views.SalesInvoiceViewSet, basename='salesinvoice')
router.register(r'purchase-invoices', views.PurchaseInvoiceViewSet, basename='purchaseinvoice')
router.register(r'payment-entries', views.PaymentEntryViewSet, basename='paymententry')
router.register(r'journal-entries', views.JournalEntryViewSet, basename='journalentry')

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Add this new path
    path("users/me/", views.CurrentUserView.as_view(), name="current-user"),

    # This includes all the ViewSet URLs
    path("", include(router.urls)),
]