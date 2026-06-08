import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"fieldname": "customer", "label": _("العميل"), "fieldtype": "Link", "options": "Customer", "width": 180},
        {"fieldname": "total_invoices", "label": _("عدد الفواتير"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_amount", "label": _("إجمالي المبلغ"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "paid_amount", "label": _("المسدد"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "remaining_amount", "label": _("المتبقي"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "overdue_count", "label": _("أقساط متأخرة"), "fieldtype": "Int", "width": 120},
        {"fieldname": "next_due_date", "label": _("أقرب موعد"), "fieldtype": "Date", "width": 120},
    ]


def get_data(filters):
    conditions = "WHERE si.docstatus = 1"
    if filters.get("customer"):
        conditions += f" AND si.customer = {frappe.db.escape(filters[customer])}"

    query = f"""
        SELECT
            si.customer,
            COUNT(DISTINCT si.name) as total_invoices,
            SUM(si.grand_total) as total_amount,
            SUM(si.grand_total - si.outstanding_amount) as paid_amount,
            SUM(si.outstanding_amount) as remaining_amount,
            COUNT(CASE WHEN sch.due_date < CURDATE() AND sch.status != مدفوع THEN 1 END) as overdue_count,
            MIN(CASE WHEN sch.status != مدفوع THEN sch.due_date END) as next_due_date
        FROM `tabSales Invoice` si
        LEFT JOIN `tabPOS Installment Schedule` sch ON sch.parent = si.name
        {conditions}
        GROUP BY si.customer
        HAVING remaining_amount > 0
        ORDER BY overdue_count DESC, remaining_amount DESC
        LIMIT 100
    """
    return frappe.db.sql(query, as_dict=True)
