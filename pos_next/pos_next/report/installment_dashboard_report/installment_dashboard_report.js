frappe.query_reports["Installment Dashboard Report"] = {
    filters: [
        {
            fieldname: "customer",
            label: __("العميل"),
            fieldtype: "Link",
            options: "Customer"
        }
    ]
};
