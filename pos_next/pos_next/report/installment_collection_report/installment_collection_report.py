import urllib.parse
import frappe
from frappe import _
from frappe.utils import flt, today, getdate


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "رقم الفاتورة", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 160},
        {"label": "العميل", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 140},
        {"label": "اسم العميل", "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": "الهاتف / واتساب", "fieldname": "whatsapp", "fieldtype": "Data", "width": 130},
        {"label": "رقم القسط", "fieldname": "installment_number", "fieldtype": "Int", "width": 90},
        {"label": "تاريخ الاستحقاق", "fieldname": "due_date", "fieldtype": "Date", "width": 120},
        {"label": "قيمة القسط", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "المدفوع", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 110},
        {"label": "المتبقي", "fieldname": "remaining_amount", "fieldtype": "Currency", "width": 110},
        {"label": "الحالة", "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": "عدد الأشهر", "fieldname": "months", "fieldtype": "Int", "width": 90},
        {"label": "القسط الشهري", "fieldname": "monthly_amount", "fieldtype": "Currency", "width": 120},
        {"label": "تذكير واتساب", "fieldname": "whatsapp_btn", "fieldtype": "HTML", "width": 130},
    ]


def get_data(filters):
    conditions = "AND s.parenttype = 'Sales Invoice'"
    values = {}

    # Status filter - default: show pending/overdue only
    status_filter = filters.get("status")
    if status_filter:
        conditions += " AND s.status = %(status)s"
        values["status"] = status_filter
    else:
        conditions += " AND s.status != 'مدفوع'"

    if filters.get("from_date"):
        conditions += " AND s.due_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND s.due_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]
    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters["customer"]
    if filters.get("sales_invoice"):
        conditions += " AND si.name = %(sales_invoice)s"
        values["sales_invoice"] = filters["sales_invoice"]

    rows = frappe.db.sql(
        """
        SELECT
            si.name AS sales_invoice,
            si.customer,
            si.customer_name,
            COALESCE(c.custom_whatsapp, c.custom_mobile, '') AS whatsapp,
            s.installment_number,
            s.due_date,
            s.amount,
            s.paid_amount,
            s.remaining_amount,
            s.status,
            si.custom_installment_months AS months,
            si.custom_installment_monthly_amount AS monthly_amount
        FROM `tabInstallment Schedule` s
        JOIN `tabSales Invoice` si ON si.name = s.parent
        JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.docstatus = 1
          AND si.custom_is_installment_sale = 1
          {conditions}
        ORDER BY s.due_date ASC, si.name ASC
        """.format(conditions=conditions),
        values,
        as_dict=True,
    )

    result = []
    today_date = getdate(today())
    for row in rows:
        # Mark overdue
        if row.status == "مستحق" and row.due_date and getdate(row.due_date) < today_date:
            row.status = "متأخر"
            frappe.db.set_value(
                "Installment Schedule", {"parent": row.sales_invoice, "installment_number": row.installment_number},
                "status", "متأخر", update_modified=False
            )

        phone = (row.whatsapp or "").replace(" ", "").replace("+", "").replace("-", "")
        if phone.startswith("0"):
            phone = "2" + phone

        msg = (
            f"مرحباً {row.customer_name}،\n"
            f"نذكركم بموعد سداد القسط رقم {row.installment_number}\n"
            f"المبلغ المستحق: {flt(row.remaining_amount):.2f} ج.م\n"
            f"تاريخ الاستحقاق: {row.due_date}\n"
            f"الفاتورة: {row.sales_invoice}\n"
            f"شكراً لتعاملكم مع متجرنا 🙏"
        )
        wa_link = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}" if phone else "#"
        row["whatsapp_btn"] = (
            f'<a href="{wa_link}" target="_blank" style="color:#25D366;font-weight:bold;text-decoration:none;">💬 تذكير</a>'
        )
        result.append(row)

    return result
