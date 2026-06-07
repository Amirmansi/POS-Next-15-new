frappe.query_reports["Customer Installment Status"] = {
	filters: [
		{
			fieldname: "customer",
			fieldtype: "Link",
			options: "Customer",
			label: __("العميل"),
		},
		{
			fieldname: "plan_status",
			fieldtype: "Select",
			label: __("حالة الخطة"),
			options: "\nنشط\nمكتمل\nمتعثر",
		},
	],
};
