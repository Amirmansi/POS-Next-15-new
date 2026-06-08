import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ExpenseEntry(Document):

    def validate(self):
        self.calculate_total()
        self.validate_payment_account()

    def calculate_total(self):
        total = sum(flt(row.amount) for row in self.expense_items or [])
        self.total_amount = total

    def validate_payment_account(self):
        if not self.payment_account:
            company = frappe.defaults.get_global_default("company")
            cash = frappe.get_all(
                "Account",
                filters={"account_type": "Cash", "company": company, "is_group": 0},
                fields=["name"],
                limit=1,
            )
            if cash:
                self.payment_account = cash[0].name

    def on_submit(self):
        self.status = "مؤكدة"
        self.make_gl_entries()

    def on_cancel(self):
        self.status = "ملغاة"
        self.cancel_gl_entries()

    def make_gl_entries(self):
        from frappe.accounts.general_ledger import make_gl_entries

        company = frappe.defaults.get_global_default("company")
        cost_center = frappe.db.get_value("Company", company, "cost_center")

        gl_entries = []
        for row in self.expense_items or []:
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": row.expense_type,
                        "debit": flt(row.amount),
                        "debit_in_account_currency": flt(row.amount),
                        "against": self.payment_account,
                        "remarks": row.description or self.remarks or self.name,
                        "cost_center": cost_center,
                    },
                    company=company,
                )
            )

        gl_entries.append(
            self.get_gl_dict(
                {
                    "account": self.payment_account,
                    "credit": flt(self.total_amount),
                    "credit_in_account_currency": flt(self.total_amount),
                    "against": ", ".join(r.expense_type for r in self.expense_items or []),
                    "remarks": f"سداد مصروفات — {self.name}",
                    "cost_center": cost_center,
                },
                company=company,
            )
        )

        make_gl_entries(gl_entries)

    def cancel_gl_entries(self):
        from frappe.accounts.general_ledger import make_reverse_gl_entries

        make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
