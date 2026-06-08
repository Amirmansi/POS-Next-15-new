import frappe


def execute():
    charts = [
        {
            "chart_name": "المبيعات الشهرية",
            "chart_type": "Sum",
            "document_type": "Sales Invoice",
            "based_on": "posting_date",
            "time_interval": "Monthly",
            "timespan": "Last Year",
            "value_based_on": "grand_total",
            "type": "Line",
            "color": "#22c55e",
            "filters_json": '[{"fieldname":"docstatus","operator":"=","value":1}]',
        },
        {
            "chart_name": "الأصناف الأكثر مبيعاً",
            "chart_type": "Group By",
            "document_type": "Sales Invoice Item",
            "parent_document_type": "Sales Invoice",
            "group_by_based_on": "item_name",
            "aggregate_function_based_on": "qty",
            "number_of_groups": 10,
            "type": "Bar",
            "color": "#3b82f6",
            "filters_json": "[]",
        },
    ]

    for chart in charts:
        chart_name = chart["chart_name"]
        if frappe.db.exists("Dashboard Chart", chart_name):
            frappe.delete_doc("Dashboard Chart", chart_name, force=True, ignore_permissions=True)
        doc = frappe.get_doc({"doctype": "Dashboard Chart", "is_public": 1, **chart})
        doc.insert(ignore_permissions=True)
        print("  ✅ Chart: " + chart_name)

    frappe.db.commit()
    print("✅ Charts done")
