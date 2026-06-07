frappe.query_reports["Installment Collection Report"] = {
	filters: [
		{
			fieldname: "from_date",
			fieldtype: "Date",
			label: __("من تاريخ"),
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "to_date",
			fieldtype: "Date",
			label: __("إلى تاريخ"),
			default: frappe.datetime.add_months(frappe.datetime.get_today(), 1),
		},
		{
			fieldname: "customer",
			fieldtype: "Link",
			options: "Customer",
			label: __("العميل"),
		},
		{
			fieldname: "status",
			fieldtype: "Select",
			label: __("الحالة"),
			options: "\nمستحق\nمتأخر\nمدفوع جزئياً",
		},
	],
};
