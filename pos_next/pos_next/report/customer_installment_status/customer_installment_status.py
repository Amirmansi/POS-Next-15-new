import frappe
from frappe.utils import flt, today, getdate


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "العميل", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "اسم العميل", "fieldname": "customer_name", "fieldtype": "Data", "width": 160},
        {"label": "الهاتف", "fieldname": "mobile", "fieldtype": "Data", "width": 130},
        {"label": "عدد الفواتير المقسطة", "fieldname": "invoice_count", "fieldtype": "Int", "width": 120},
        {"label": "الأقساط الإجمالية", "fieldname": "total_installments", "fieldtype": "Int", "width": 110},
        {"label": "إجمالي التعاقد", "fieldname": "total_contract", "fieldtype": "Currency", "width": 140},
        {"label": "إجمالي المدفوع", "fieldname": "total_paid", "fieldtype": "Currency", "width": 130},
        {"label": "إجمالي المتبقي", "fieldname": "total_remaining", "fieldtype": "Currency", "width": 130},
        {"label": "أقساط متأخرة", "fieldname": "overdue_count", "fieldtype": "Int", "width": 110},
        {"label": "مبلغ المتأخرات", "fieldname": "overdue_amount", "fieldtype": "Currency", "width": 120},
        {"label": "حالة العميل", "fieldname": "customer_status", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    cond = "WHERE si.docstatus = 1 AND si.custom_is_installment_sale = 1"
    values = {}

    if filters.get("customer"):
        cond += " AND si.customer = %(customer)s"
        values["customer"] = filters["customer"]
    if filters.get("customer_status"):
        pass  # Applied after fetching

    today_str = today()

    rows = frappe.db.sql(
        """
        SELECT
            si.customer,
            si.customer_name,
            COALESCE(c.custom_whatsapp, c.custom_mobile, '') AS mobile,
            COUNT(DISTINCT si.name) AS invoice_count,
            COUNT(s.name) AS total_installments,
            SUM(si.custom_installment_total_contract) AS total_contract,
            SUM(s.paid_amount) AS total_paid,
            SUM(s.remaining_amount) AS total_remaining,
            SUM(CASE WHEN s.due_date < %(today)s AND s.status != 'مدفوع' THEN 1 ELSE 0 END) AS overdue_count,
            SUM(CASE WHEN s.due_date < %(today)s AND s.status != 'مدفوع' THEN s.remaining_amount ELSE 0 END) AS overdue_amount
        FROM `tabSales Invoice` si
        JOIN `tabInstallment Schedule` s ON s.parent = si.name AND s.parenttype = 'Sales Invoice'
        JOIN `tabCustomer` c ON c.name = si.customer
        {cond}
        GROUP BY si.customer
        ORDER BY total_remaining DESC
        """.format(cond=cond),
        {**values, "today": today_str},
        as_dict=True,
    )

    status_filter = filters.get("customer_status")
    result = []
    for row in rows:
        if flt(row.total_remaining) <= 0:
            row["customer_status"] = "✅ مسدد"
        elif flt(row.overdue_amount) > 0:
            row["customer_status"] = "⚠️ متعثر"
        else:
            row["customer_status"] = "🕐 نشط"

        if status_filter and row["customer_status"] != status_filter:
            continue
        result.append(row)

    return result
