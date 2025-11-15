from pathlib import Path
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.management import call_command

from operations.models import (
    Currency,
    AccountGroupHead,
    AccountGroupMaster,
    ChartOfAccount,
    GeneralLedger,
    PaymentEntry,
    JournalEntryLine,
)


class Command(BaseCommand):
    help = "Seed currencies, account groups, and chart of accounts from fixtures/coa_skeleton.json."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing COA (and groups) before seeding. Dev-only.",
        )

    
    
    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset"]

        if reset:
    # Safety: do not reset if ledger or dependent docs exist
            if GeneralLedger.objects.exists() or PaymentEntry.objects.exists() or JournalEntryLine.objects.exists():
                raise CommandError(
                    "Cannot use --reset while there are GeneralLedger, PaymentEntry, "
                    "or JournalEntryLine rows. Clear them first in dev."
                )

            # Important: only delete ChartOfAccount rows.
            # Do NOT delete AccountGroupMaster or AccountGroupHead because they are
            # linked via PROTECT from AccountFinance and others.
            self.stdout.write(self.style.WARNING("Deleting existing ChartOfAccount entries..."))
            ChartOfAccount.objects.all().delete()


        # 1) Ensure currencies
        self._ensure_currencies()

        # 2) Ensure group heads and groups
        heads = self._ensure_group_heads()
        groups = self._ensure_groups(heads)

        # 3) Load fixture JSON
        fixture_path = Path(__file__).resolve().parents[2] / "fixtures" / "coa_skeleton.json"
        if not fixture_path.exists():
            raise CommandError(f"Fixture file not found: {fixture_path}")

        with fixture_path.open("r", encoding="utf-8") as f:
            raw_accounts = json.load(f)

        # 4) Map currencies
        currencies = {c.code: c for c in Currency.objects.all()}

        # 5) Create/update COA from fixture
        accounts_by_code = {}

        for row in raw_accounts:
            code = row["code"]
            name = row["name"]
            account_type = row["account_type"]
            group_code = row.get("group_code")
            currency_code = row.get("currency_code")
            parent_code = row.get("parent_code")
            is_control = row.get("is_control", False)

            parent = accounts_by_code.get(parent_code) if parent_code else None
            group = groups.get(group_code) if group_code else None
            currency = currencies.get(currency_code) if currency_code else None

            account, created = ChartOfAccount.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "account_type": account_type,
                    "parent": parent,
                    "group": group,
                    "currency": currency,
                    "is_control": is_control,
                },
            )
            accounts_by_code[code] = account

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(accounts_by_code)} ChartOfAccount rows."))

    # --- Helpers --------------------------------------------------------

    def _ensure_currencies(self):
        data = [
            ("INR", "Indian Rupee"),
            ("USD", "US Dollar"),
            ("RMB", "Chinese Yuan"),
        ]
        for code, name in data:
            Currency.objects.get_or_create(code=code, defaults={"name": name})
        self.stdout.write(self.style.SUCCESS("Currencies ensured (INR, USD, RMB)."))

    def _ensure_group_heads(self):
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
        return heads

    def _ensure_groups(self, heads):
        groups_data = [
            # Bank groups
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
            # Receivables / Payables
            {
                "grpcode": "AR",
                "name": "Accounts Receivable",
                "type": "Asset",
                "subtype": "Receivable",
                "headcode": "ASSET",
            },
            {
                "grpcode": "AP",
                "name": "Accounts Payable",
                "type": "Liability",
                "subtype": "Payable",
                "headcode": "LIAB",
            },
            # Funds with Agent
            {
                "grpcode": "FUNDS_AGENT",
                "name": "Funds with Agent",
                "type": "Asset",
                "subtype": "Agent Funds",
                "headcode": "ASSET",
            },
            # Income / Expense
            {
                "grpcode": "FREIGHT_INC",
                "name": "Freight Income",
                "type": "Income",
                "subtype": "Operating Income",
                "headcode": "INC",
            },
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
                    "subtype": data["subtype"],
                    "headcode": head,
                },
            )
            groups[data["grpcode"]] = group

        self.stdout.write(self.style.SUCCESS("AccountGroupMaster rows ensured."))
        return groups
