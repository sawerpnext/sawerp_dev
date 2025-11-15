from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User
from django.test import TestCase
from .models import (
    Currency, Customer,
    AccountGroupHead, AccountGroupMaster,
    AccountFinance, AccountMetadata
)


class AccountModelsTestCase(TestCase):
    def setUp(self):
        self.inr = Currency.objects.create(code='INR', name='Indian Rupee')
        self.head = AccountGroupHead.objects.create(
            code='ASSET',
            srno=1,
            name='Assets',
            type='Asset'
        )
        self.group = AccountGroupMaster.objects.create(
            grpcode='BANK',
            name='Bank Accounts',
            type='Asset',
            headcode=self.head
        )
        self.customer = Customer.objects.create(
            name='Test Customer',
            s_mark='S-MARK-1'
        )

    def test_account_finance_and_metadata_link(self):
        acc = AccountFinance.objects.create(
            accode='ACC-001',
            grpcode=self.group,
            custcode='LEG-001',
            customer=self.customer,
            name='Test Account',
            curr=self.inr
        )

        meta = AccountMetadata.objects.create(
            account=acc,
            address_line1='Line 1',
            city='Mumbai',
            pin_code='400001',
            email='test@example.com'
        )

        self.assertEqual(acc.metadata.city, 'Mumbai')
        self.assertEqual(meta.account.accode, 'ACC-001')


class AuthFlowTests(APITestCase):
    """
    Simple smoke tests for token auth and the /api/users/me/ endpoint.

    Why this exists:
    - To quickly catch if authentication or basic API wiring breaks.
    - To give you a very fast "does it still work?" check after changes.
    """

    def setUp(self):
        """
        Create a test user we can use to log in and get a token.
        """
        self.username = "testuser"
        self.password = "testpassword123"

        # Use the custom User model's create_user helper.
        self.user = User.objects.create_user(
            username=self.username,
            email="testuser@example.com",
            password=self.password,
        )

    def test_obtain_token_and_get_current_user(self):
        """
        1. Get a token from /api/token-auth/.
        2. Call /api/users/me/ with that token.
        3. Check that we get 200 OK and the correct username.
        """
        # 1) Get token
        token_url = reverse("api_token_auth")
        response = self.client.post(
            token_url,
            {"username": self.username, "password": self.password},
            format="json",
        )

        # Response should be 200 and contain a "token" key
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

        token = response.data["token"]

        # 2) Use the token to call /api/users/me/
        # REST framework TokenAuthentication expects header: "Authorization: Token <token>"
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me_url = "/api/users/me/"
        response = self.client.get(me_url)

        # 3) Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.username)
from decimal import Decimal
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from .models import (
    User,
    Currency,
    Customer,
    Project,
    ChartOfAccount,
    SalesInvoice,
    GeneralLedger,
)
from .posting import submit_document


class PostingPipelineTests(TestCase):
    """
    Basic end-to-end test for:
    SalesInvoice -> submit_document -> GeneralLedger -> Project.net_profit
    """

    def setUp(self):
        # Base user
        self.user = User.objects.create_user(
            username="tester",
            password="test-password",
        )

        # Base currency
        self.inr = Currency.objects.create(code="INR", name="Indian Rupee")

        # Chart of Accounts needed by the posting rules
        self.ar_account = ChartOfAccount.objects.create(
            name="Accounts Receivable",
            account_type="Asset",
            parent=None,
            currency=self.inr,
        )
        self.revenue_account = ChartOfAccount.objects.create(
            name="Freight Income",
            account_type="Income",
            parent=None,
            currency=self.inr,
        )

        # Simple customer + project
        self.customer = Customer.objects.create(
            name="Test Customer",
            s_mark="TEST-SMARK",
        )
        self.project = Project.objects.create(
            container_number="CONT-001",
            customer=self.customer,
        )

    def test_sales_invoice_submission_posts_to_ledger_and_updates_project_profit(self):
        invoice = SalesInvoice.objects.create(
            project=self.project,
            customer=self.customer,
            invoice_date=date(2025, 1, 1),
            due_date=date(2025, 1, 15),
            currency=self.inr,
            exchange_rate=Decimal("1.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        # Submit the invoice using the shared helper
        submit_document(invoice, self.user)

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "Submitted")

        # Fetch GL rows for this invoice
        ct = ContentType.objects.get_for_model(SalesInvoice)
        gl_rows = GeneralLedger.objects.filter(
            content_type=ct,
            object_id=invoice.pk,
        ).order_by("id")

        self.assertEqual(gl_rows.count(), 2)

        ar_row = gl_rows[0]
        revenue_row = gl_rows[1]

        # Debit row: Accounts Receivable
        self.assertEqual(ar_row.account, self.ar_account)
        self.assertEqual(ar_row.debit_base, Decimal("1000.00"))
        self.assertEqual(ar_row.credit_base, Decimal("0"))
        self.assertEqual(ar_row.debit_foreign, Decimal("1000.00"))
        self.assertEqual(ar_row.credit_foreign, Decimal("0"))
        self.assertEqual(ar_row.project, self.project)

        # Credit row: Freight Income
        self.assertEqual(revenue_row.account, self.revenue_account)
        self.assertEqual(revenue_row.credit_base, Decimal("1000.00"))
        self.assertEqual(revenue_row.debit_base, Decimal("0"))
        self.assertEqual(revenue_row.credit_foreign, Decimal("1000.00"))
        self.assertEqual(revenue_row.debit_foreign, Decimal("0"))
        self.assertEqual(revenue_row.project, self.project)

        # Project.net_profit should now equal the revenue (Income credit)
        self.assertEqual(self.project.net_profit, Decimal("1000.00"))
