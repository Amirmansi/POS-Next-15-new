frappe.query_reports["Expense Analysis Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("من تاريخ"),
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: __("إلى تاريخ"),
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        },
        {
            fieldname: "payment_method",
            label: __("طريقة الدفع"),
            fieldtype: "Select",
            options: "\nنقداً\nبنك\nمحفظة إلكترونية\nشيك"
        }
    ]
};
