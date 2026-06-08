import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "posting_date", "label": _("التاريخ"), "fieldtype": "Date", "width": 110},
        {"fieldname": "name", "label": _("رقم السجل"), "fieldtype": "Link", "options": "Expense Entry", "width": 140},
        {"fieldname": "expense_type", "label": _("نوع المصروف"), "fieldtype": "Link", "options": "Account", "width": 200},
        {"fieldname": "description", "label": _("البيان"), "fieldtype": "Data", "width": 200},
        {"fieldname": "payment_method", "label": _("طريقة الدفع"), "fieldtype": "Data", "width": 120},
        {"fieldname": "amount", "label": _("المبلغ"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "paid_to", "label": _("المدفوع إليه"), "fieldtype": "Data", "width": 150},
    ]


def get_data(filters):
    conditions = "WHERE ee.docstatus = 1"
    if filters.get("from_date"):
        conditions += f" AND ee.posting_date >= {frappe.db.escape(filters[from_date])}"
    if filters.get("to_date"):
        conditions += f" AND ee.posting_date <= {frappe.db.escape(filters[to_date])}"
    if filters.get("payment_method"):
        conditions += f" AND ee.payment_method = {frappe.db.escape(filters[payment_method])}"

    query = f"""
        SELECT
            ee.posting_date,
            ee.name,
            eil.expense_type,
            eil.description,
            ee.payment_method,
            eil.amount,
            ee.paid_to
        FROM `tabExpense Entry` ee
        INNER JOIN `tabExpense Item Line` eil ON eil.parent = ee.name
        {conditions}
        ORDER BY ee.posting_date DESC, ee.name
    """
    return frappe.db.sql(query, as_dict=True)
