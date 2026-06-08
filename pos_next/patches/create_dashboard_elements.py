import frappe


def execute():
    cards = [
        {
            "name": "الأقساط المتأخرة",
            "label": "أقساط متأخرة",
            "document_type": "Installment Schedule",
            "parent_document_type": "Sales Invoice",
            "function": "Count",
            "aggregate_function_based_on": "name",
            "filters_json": '[{"fieldname":"status","operator":"=","value":"Overdue"}]',
            "color": "#ef4444",
        },
        {
            "name": "الأقساط غير المسددة",
            "label": "أقساط غير مسددة",
            "document_type": "Installment Schedule",
            "parent_document_type": "Sales Invoice",
            "function": "Count",
            "aggregate_function_based_on": "name",
            "filters_json": '[{"fieldname":"remaining_amount","operator":">","value":0}]',
            "color": "#f97316",
        },
        {
            "name": "مبيعات اليوم",
            "label": "مبيعات اليوم",
            "document_type": "Sales Invoice",
            "function": "Sum",
            "aggregate_function_based_on": "grand_total",
            "filters_json": '[{"fieldname":"posting_date","operator":"=","value":"Today"},{"fieldname":"docstatus","operator":"=","value":1}]',
            "color": "#22c55e",
        },
        {
            "name": "مصروفات الشهر",
            "label": "مصروفات الشهر",
            "document_type": "Expense Entry",
            "function": "Sum",
            "aggregate_function_based_on": "total_amount",
            "filters_json": '[{"fieldname":"docstatus","operator":"=","value":1}]',
            "color": "#8b5cf6",
        },
    ]

    for card in cards:
        if frappe.db.exists("Number Card", card["name"]):
            frappe.delete_doc("Number Card", card["name"], force=True, ignore_permissions=True)
        doc = frappe.get_doc({"doctype": "Number Card", "is_public": 1, **card})
        doc.insert(ignore_permissions=True)
        print("  ✅ Number Card: " + card["name"])

    charts = [
        {
            "name": "المبيعات الشهرية",
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
            "name": "الأصناف الأكثر مبيعاً",
            "chart_type": "Group By",
            "document_type": "Sales Invoice Item",
            "group_by_based_on": "item_name",
            "aggregate_function_based_on": "qty",
            "number_of_groups": 10,
            "type": "Bar",
            "color": "#3b82f6",
            "filters_json": "[]",
        },
    ]

    for chart in charts:
        if frappe.db.exists("Dashboard Chart", chart["name"]):
            frappe.delete_doc("Dashboard Chart", chart["name"], force=True, ignore_permissions=True)
        doc = frappe.get_doc({"doctype": "Dashboard Chart", "is_public": 1, **chart})
        doc.insert(ignore_permissions=True)
        print("  ✅ Dashboard Chart: " + chart["name"])

    frappe.db.commit()
    print("✅ Done - dashboard elements created")
