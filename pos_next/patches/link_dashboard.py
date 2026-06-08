import frappe, json


def execute():
    ws_name = "dashboard-abdulrahman"

    # Delete old cards/charts references
    frappe.db.sql("DELETE FROM `tabWorkspace Number Card` WHERE parent=%s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent=%s", ws_name)

    # Add Number Cards
    for i, card_name in enumerate(["الأقساط المتأخرة", "الأقساط غير المسددة", "مبيعات اليوم", "مصروفات الشهر"]):
        if frappe.db.exists("Number Card", card_name):
            d = frappe.new_doc("Workspace Number Card")
            d.parent = ws_name
            d.parentfield = "cards"
            d.parenttype = "Workspace"
            d.card_name = card_name
            d.label = card_name
            d.idx = i + 1
            d.db_insert()

    # Add Charts
    for i, chart_name in enumerate(["المبيعات الشهرية", "الأصناف الأكثر مبيعاً"]):
        if frappe.db.exists("Dashboard Chart", chart_name):
            d = frappe.new_doc("Workspace Chart")
            d.parent = ws_name
            d.parentfield = "charts"
            d.parenttype = "Workspace"
            d.chart_name = chart_name
            d.label = chart_name
            d.idx = i + 1
            d.db_insert()

    # Update content to include cards section
    old_content = frappe.db.get_value("Workspace", ws_name, "content") or "[]"
    try:
        content = json.loads(old_content)
    except Exception:
        content = []

    # Add number_card blocks
    card_section = {"id": "cards_hdr", "type": "header", "data": {
        "text": '<span class="h5"><b>📈 مؤشرات الأداء</b></span>', "col": 12
    }}
    if not any(b.get("id") == "cards_hdr" for b in content):
        content.append(card_section)
    for i, card_name in enumerate(["الأقساط المتأخرة", "الأقساط غير المسددة", "مبيعات اليوم", "مصروفات الشهر"]):
        block_id = "nc_" + str(i)
        if not any(b.get("id") == block_id for b in content):
            content.append({"id": block_id, "type": "number_card", "data": {
                "number_card_name": card_name, "col": 3
            }})

    frappe.db.set_value("Workspace", ws_name, "content", json.dumps(content, ensure_ascii=False))
    frappe.db.commit()
    print("✅ Dashboard workspace linked with cards and charts")
