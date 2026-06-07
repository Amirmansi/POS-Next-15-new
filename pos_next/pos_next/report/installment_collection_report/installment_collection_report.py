import urllib.parse

import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": "خطة التقسيط",
			"fieldname": "plan_name",
			"fieldtype": "Link",
			"options": "Installment Plan",
			"width": 160,
		},
		{"label": "العميل", "fieldname": "customer_name", "fieldtype": "Data", "width": 160},
		{"label": "الهاتف / واتساب", "fieldname": "whatsapp", "fieldtype": "Data", "width": 130},
		{
			"label": "رقم الفاتورة",
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 160,
		},
		{"label": "رقم القسط", "fieldname": "installment_number", "fieldtype": "Int", "width": 90},
		{"label": "تاريخ الاستحقاق", "fieldname": "due_date", "fieldtype": "Date", "width": 120},
		{
			"label": "قيمة القسط",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "المدفوع",
			"fieldname": "paid_amount",
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"label": "المتبقي",
			"fieldname": "remaining_amount",
			"fieldtype": "Currency",
			"width": 110,
		},
		{"label": "الحالة", "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": "تذكير واتساب", "fieldname": "whatsapp_btn", "fieldtype": "HTML", "width": 120},
	]


def get_data(filters):
	conditions = "AND s.status != 'مدفوع'"
	values = {}

	if filters.get("from_date"):
		conditions += " AND s.due_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions += " AND s.due_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]
	if filters.get("customer"):
		conditions += " AND ip.customer = %(customer)s"
		values["customer"] = filters["customer"]
	if filters.get("status"):
		conditions += " AND s.status = %(status)s"
		values["status"] = filters["status"]

	rows = frappe.db.sql(
		"""
		SELECT
			ip.name AS plan_name,
			ip.customer_name,
			COALESCE(c.custom_whatsapp, c.custom_mobile, '') AS whatsapp,
			ip.sales_invoice,
			s.installment_number,
			s.due_date,
			s.amount,
			s.paid_amount,
			s.remaining_amount,
			s.status
		FROM `tabInstallment Schedule` s
		JOIN `tabInstallment Plan` ip ON ip.name = s.parent
		JOIN `tabCustomer` c ON c.name = ip.customer
		WHERE ip.docstatus = 1
		{conditions}
		ORDER BY s.due_date ASC
	""".format(
			conditions=conditions
		),
		values=values,
		as_dict=True,
	)

	result = []
	for row in rows:
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
		wa_link = (
			f'https://wa.me/{phone}?text={urllib.parse.quote(msg)}' if phone else "#"
		)
		row["whatsapp_btn"] = (
			f'<a href="{wa_link}" target="_blank" '
			f'style="color:#25D366;font-weight:bold;text-decoration:none;">💬 تذكير</a>'
		)
		result.append(row)

	return result
