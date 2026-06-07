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
			"label": "العميل",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{"label": "اسم العميل", "fieldname": "customer_name", "fieldtype": "Data", "width": 160},
		{"label": "الهاتف", "fieldname": "mobile", "fieldtype": "Data", "width": 130},
		{
			"label": "عدد الخطط النشطة",
			"fieldname": "active_plans",
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"label": "إجمالي المديونية",
			"fieldname": "total_debt",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": "إجمالي المدفوع",
			"fieldname": "total_paid",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": "المتأخرات",
			"fieldname": "overdue_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{"label": "حالة العميل", "fieldname": "customer_status", "fieldtype": "Data", "width": 120},
	]


def get_data(filters):
	conditions = "WHERE ip.docstatus = 1 AND ip.plan_status != 'ملغي'"
	values = {}

	if filters.get("customer"):
		conditions += " AND ip.customer = %(customer)s"
		values["customer"] = filters["customer"]
	if filters.get("plan_status"):
		conditions += " AND ip.plan_status = %(plan_status)s"
		values["plan_status"] = filters["plan_status"]

	rows = frappe.db.sql(
		"""
		SELECT
			ip.customer,
			ip.customer_name,
			COALESCE(c.custom_whatsapp, c.custom_mobile, '') AS mobile,
			COUNT(DISTINCT ip.name) AS active_plans,
			SUM(ip.total_remaining) AS total_debt,
			SUM(ip.total_paid) AS total_paid,
			SUM(CASE WHEN ip.plan_status = 'متعثر' THEN ip.total_remaining ELSE 0 END) AS overdue_amount
		FROM `tabInstallment Plan` ip
		JOIN `tabCustomer` c ON c.name = ip.customer
		{conditions}
		GROUP BY ip.customer
		ORDER BY total_debt DESC
	""".format(
			conditions=conditions
		),
		values=values,
		as_dict=True,
	)

	for row in rows:
		if flt(row.overdue_amount) > 0:
			row["customer_status"] = "⚠️ متعثر"
		elif flt(row.total_debt) <= 0:
			row["customer_status"] = "✅ مسدد"
		else:
			row["customer_status"] = "🕐 نشط"

	return rows
