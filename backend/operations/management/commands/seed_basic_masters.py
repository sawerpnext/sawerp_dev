from django.core.management.base import BaseCommand
from django.db import transaction

from operations.models import (
    Currency,
    AccountGroupHead,
    AccountGroupMaster,
    ChartOfAccount,
)


class Command(BaseCommand):
    help = "Seed basic currencies, account groups, and chart of accounts for the ERP Shipping project."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding basic currencies..."))
        inr, _ = Currency.objects.get_or_create(code="INR", defaults={"name": "Indian Rupee"})
        usd, _ = Currency.objects.get_or_create(code="USD", defaults={"name": "US Dollar"})
        rmb, _ = Currency.objects.get_or_create(code="RMB", defaults={"name": "Chinese Yuan"})

        self.stdout.write(self.style.SUCCESS("Currencies ensured: INR, USD, RMB."))

        self.stdout.write(self.style.SUCCESS("Seeding AccountGroupHead rows..."))
        heads_data = [
            {"code": "ASSET", "srno": 10, "name": "Assets", "type": "Asset"},
            {"code": "LIAB", "srno": 20, "name": "Liabilities", "type": "Liability"},
            {"code": "INC", "srno": 30, "name": "Income", "type": "Income"},
            {"code": "EXP", "srno": 40, "name": "Expenses", "type": "Expense"},
            {"code": "EQUITY", "srno": 50, "name": "Equity", "type": "Equity"},
        ]

        heads = {}
        for data in heads_data:
            head, _ = AccountGroupHead.objects.get_or_create(
                code=data["code"],
                defaults={
                    "srno": data["srno"],
                    "name": data["name"],
                    "type": data["type"],
                },
            )
            heads[data["code"]] = head
        self.stdout.write(self.style.SUCCESS("AccountGroupHead rows ensured."))

        self.stdout.write(self.style.SUCCESS("Seeding AccountGroupMaster rows..."))
        groups_data = [
            # Assets
            {
                "grpcode": "BANK_INR",
                "name": "Bank Accounts - INR",
                "type": "Asset",
                "subtype": "Bank",
                "headcode": "ASSET",
            },
            {
                "grpcode": "BANK_USD",
                "name": "Bank Accounts - USD",
                "type": "Asset",
                "subtype": "Bank",
                "headcode": "ASSET",
            },
            {
                "grpcode": "BANK_RMB",
                "name": "Bank Accounts - RMB",
                "type": "Asset",
                "subtype": "Bank",
                "headcode": "ASSET",
            },
            {
                "grpcode": "AR",
                "name": "Accounts Receivable",
                "type": "Asset",
                "subtype": "Receivable",
                "headcode": "ASSET",
            },
            # Liabilities
            {
                "grpcode": "AP",
                "name": "Accounts Payable",
                "type": "Liability",
                "subtype": "Payable",
                "headcode": "LIAB",
            },
            # Income
            {
                "grpcode": "FREIGHT_INC",
                "name": "Freight Income",
                "type": "Income",
                "subtype": "Operating Income",
                "headcode": "INC",
            },
            # Expenses
            {
                "grpcode": "FREIGHT_EXP",
                "name": "Freight Charges",
                "type": "Expense",
                "subtype": "Operating Expense",
                "headcode": "EXP",
            },
        ]

        groups = {}
        for data in groups_data:
            head = heads[data["headcode"]]
            group, _ = AccountGroupMaster.objects.get_or_create(
                grpcode=data["grpcode"],
                defaults={
                    "name": data["name"],
                    "type": data["type"],
                    "subtype": data.get("subtype"),
                    "headcode": head,
                },
            )
            groups[data["grpcode"]] = group
        self.stdout.write(self.style.SUCCESS("AccountGroupMaster rows ensured."))

        self.stdout.write(self.style.SUCCESS("Seeding ChartOfAccount rows..."))
        chart_data = [
            # Bank / Cash accounts per currency
            {
                "name": "Bank Account - INR",
                "account_type": "Asset",
                "group": "BANK_INR",
                "currency": inr,
            },
            {
                "name": "Bank Account - USD",
                "account_type": "Asset",
                "group": "BANK_USD",
                "currency": usd,
            },
            {
                "name": "Bank Account - RMB",
                "account_type": "Asset",
                "group": "BANK_RMB",
                "currency": rmb,
            },
            # Receivables / Payables
            {
                "name": "Accounts Receivable",
                "account_type": "Asset",
                "group": "AR",
                "currency": inr,
            },
            {
                "name": "Accounts Payable",
                "account_type": "Liability",
                "group": "AP",
                "currency": inr,
            },
            # Income / Expense
            {
                "name": "Freight Income",
                "account_type": "Income",
                "group": "FREIGHT_INC",
                "currency": inr,
            },
            {
                "name": "Freight Charges",
                "account_type": "Expense",
                "group": "FREIGHT_EXP",
                "currency": inr,
            },
        ]

        for data in chart_data:
            group = groups[data["group"]]
            ChartOfAccount.objects.get_or_create(
                name=data["name"],
                account_type=data["account_type"],
                group=group,
                defaults={
                    "parent": None,
                    "currency": data["currency"],
                },
            )

        self.stdout.write(self.style.SUCCESS("ChartOfAccount rows ensured."))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
