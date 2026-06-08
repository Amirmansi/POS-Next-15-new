frappe.query_reports["Stock Balance Mobile Shop"] = {
    filters: [
        {
            fieldname: "item_group",
            label: __("مجموعة الأصناف"),
            fieldtype: "Link",
            options: "Item Group"
        },
        {
            fieldname: "warehouse",
            label: __("المستودع"),
            fieldtype: "Link",
            options: "Warehouse"
        }
    ]
};
