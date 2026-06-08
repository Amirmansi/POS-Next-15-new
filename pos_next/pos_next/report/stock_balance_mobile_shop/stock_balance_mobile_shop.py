import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "item_code", "label": _("كود الصنف"), "fieldtype": "Link", "options": "Item", "width": 140},
        {"fieldname": "item_name", "label": _("اسم الصنف"), "fieldtype": "Data", "width": 220},
        {"fieldname": "item_group", "label": _("المجموعة"), "fieldtype": "Link", "options": "Item Group", "width": 140},
        {"fieldname": "warehouse", "label": _("المستودع"), "fieldtype": "Link", "options": "Warehouse", "width": 140},
        {"fieldname": "actual_qty", "label": _("الكمية الفعلية"), "fieldtype": "Float", "width": 110},
        {"fieldname": "valuation_rate", "label": _("سعر التكلفة"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "stock_value", "label": _("قيمة المخزون"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "standard_rate", "label": _("سعر البيع"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "expected_profit", "label": _("الربح المتوقع"), "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters):
    mobile_groups = ["هواتف ذكية", "إكسسوارات الهاتف", "شواحن وكابلات", "سماعات", "باور بانك"]
    group_list = ", ".join([frappe.db.escape(g) for g in mobile_groups])

    conditions = f"WHERE i.item_group IN ({group_list}) AND i.disabled = 0 AND b.actual_qty != 0"
    if filters.get("item_group"):
        conditions = f"WHERE i.item_group = {frappe.db.escape(filters[item_group])} AND i.disabled = 0 AND b.actual_qty != 0"
    if filters.get("warehouse"):
        conditions += f" AND b.warehouse = {frappe.db.escape(filters[warehouse])}"

    query = f"""
        SELECT
            i.item_code,
            i.item_name,
            i.item_group,
            b.warehouse,
            b.actual_qty,
            b.valuation_rate,
            b.stock_value,
            i.standard_rate,
            (b.actual_qty * (i.standard_rate - b.valuation_rate)) as expected_profit
        FROM `tabItem` i
        INNER JOIN `tabBin` b ON b.item_code = i.item_code
        {conditions}
        ORDER BY i.item_group, i.item_code
    """
    return frappe.db.sql(query, as_dict=True)
