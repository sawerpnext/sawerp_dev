from django.test import TestCase
from django.core.management import call_command

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
            1. Get a JWT access token from /api/token/.
            2. Call /api/users/me/ with that token.
            3. Check that we get 200 OK and the correct username.
            """
            # 1) Get JWT token pair
            token_url = reverse("token_obtain_pair")  # name from operations/urls.py
            response = self.client.post(
                token_url,
                {"username": self.username, "password": self.password},
                format="json",
            )

            # Response should be 200 and contain an "access" key
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("access", response.data)

            access_token = response.data["access"]

            # 2) Use the access token to call /api/users/me/
            # JWT expects header: "Authorization: Bearer <access_token>"
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
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
        # Make sure COA and currencies exist in the test DB
        # --reset is safe here because this is a fresh test database.
        call_command("seed_coa", reset=True)

        # Base user
        self.user = User.objects.create_user(
            username="tester",
            password="test-password",
        )

        # Base currency used on the invoice
        # (seed_coa also creates INR, but we keep this simple.)
        self.inr = Currency.objects.get(code="INR")

        # Chart of Accounts needed by the posting rules
        # Now fetched by code, not created by hand.
        self.ar_account = ChartOfAccount.objects.get(code="AR_INR")
        self.revenue_account = ChartOfAccount.objects.get(code="FREIGHT_INCOME")

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




######PHASE 4

from django.core.management import call_command
from django.test import TestCase

from operations.models import ChartOfAccount


class SeedCoaTests(TestCase):
    def setUp(self):
        """
        Before each test:
        - reset and reseed the chart of accounts using the seed_coa command.
        """
        call_command("seed_coa", reset=True)

    def test_core_accounts_exist(self):
        """
        Check that key multi-currency accounts are created by seed_coa.
        """

        # Accounts Receivable per currency
        for code, currency_code in [("AR_INR", "INR"), ("AR_USD", "USD"), ("AR_RMB", "RMB")]:
            self.assertTrue(
                ChartOfAccount.objects.filter(
                    code=code,
                    account_type="Asset",
                    currency__code=currency_code,
                ).exists(),
                msg=f"Missing AR account {code}",
            )

        # Accounts Payable per currency
        for code, currency_code in [("AP_INR", "INR"), ("AP_USD", "USD"), ("AP_RMB", "RMB")]:
            self.assertTrue(
                ChartOfAccount.objects.filter(
                    code=code,
                    account_type="Liability",
                    currency__code=currency_code,
                ).exists(),
                msg=f"Missing AP account {code}",
            )

        # Funds with Agent (INR, USD, RMB)
        for code, currency_code in [
            ("FUNDS_AGENT_INR", "INR"),
            ("FUNDS_AGENT_USD", "USD"),
            ("FUNDS_AGENT_RMB", "RMB"),
        ]:
            self.assertTrue(
                ChartOfAccount.objects.filter(
                    code=code,
                    account_type="Asset",
                    currency__code=currency_code,
                ).exists(),
                msg=f"Missing Funds with Agent account {code}",
            )

        # Income / Expense core accounts
        self.assertTrue(
            ChartOfAccount.objects.filter(
                code="FREIGHT_INCOME",
                account_type="Income",
                currency__code="INR",
            ).exists(),
            msg="Missing Freight Income account",
        )
        self.assertTrue(
            ChartOfAccount.objects.filter(
                code="FREIGHT_CHARGES",
                account_type="Expense",
                currency__code="INR",
            ).exists(),
            msg="Missing Freight Charges account",
        )
