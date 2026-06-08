import frappe, json

def execute():
    OWNER = "م/عبد الرحمن سعيد"

    def ins_sc(ws, label, t, lt, color, idx):
        d = frappe.new_doc("Workspace Shortcut")
        d.parent = ws; d.parentfield = "shortcuts"; d.parenttype = "Workspace"
        d.label = label; d.type = t; d.link_to = lt; d.color = color; d.idx = idx
        d.db_insert()

    def ins_lnk(ws, label, lt, lto, onb, idx):
        d = frappe.new_doc("Workspace Link")
        d.parent = ws; d.parentfield = "links"; d.parenttype = "Workspace"
        d.label = label; d.link_type = lt; d.link_to = lto
        d.is_query_report = 1 if lt == "Report" else 0
        d.hidden = 0; d.onboard = onb; d.idx = idx
        d.db_insert()

    def rebuild(ws_name, ws_title, scs, lnks):
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent=%s", ws_name)
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent=%s", ws_name)
        [ins_sc(ws_name, s[0], s[1], s[2], s[3] if len(s)>3 else "", i+1) for i, s in enumerate(scs)]
        [ins_lnk(ws_name, l[0], l[1], l[2], l[3] if len(l)>3 else 0, i+1) for i, l in enumerate(lnks)]
        content = [{"id":"hdr","type":"header","data":{"text":"<span class=\"h4\"><b>"+ws_title+"</b></span>","col":12}}]
        [content.append({"id":"sc"+str(i),"type":"shortcut","data":{"shortcut_name":s[0],"col":3}}) for i, s in enumerate(scs)]
        frappe.db.set_value("Workspace", ws_name, {"title": ws_title, "content": json.dumps(content, ensure_ascii=False)})
        print(f"  ✅ {ws_name}: {len(scs)}sc {len(lnks)}lnk")

    rebuild("dashboard-abdulrahman", "📊 لوحة التحكم — "+OWNER,
        scs=[
            ("فتح واجهة البيع","Page","pos_next","green"),
            ("تقرير المبيعات اليومي","Report","Sales Analytics",""),
            ("الأرباح والخسائر","Report","Profit and Loss Statement",""),
            ("الأقساط المستحقة","Report","Installment Tracking Report",""),
            ("الأقساط المتأخرة","Report","Installment Tracking Report","red"),
            ("تحليل الأقساط","Report","Installment Dashboard Report",""),
        ],
        lnks=[
            ("فتح واجهة البيع (POS)","Page","pos_next",1),
            ("الأقساط المتأخرة","Report","Installment Tracking Report",0),
            ("الأقساط المستحقة هذا الشهر","Report","Installment Tracking Report",0),
            ("تقرير الأرباح والخسائر","Report","Profit and Loss Statement",0),
            ("تحليل الأقساط","Report","Installment Dashboard Report",0),
            ("تقرير المبيعات اليومي","Report","Sales Analytics",0),
        ]
    )

    rebuild("sales-abdulrahman", "💰 المبيعات — "+OWNER,
        scs=[
            ("واجهة نقطة البيع","Page","pos_next","green"),
            ("إضافة عميل جديد","DocType","Customer","blue"),
            ("قائمة العملاء","DocType","Customer",""),
            ("فواتير المبيعات","DocType","Sales Invoice",""),
            ("سندات التحصيل","DocType","Payment Entry",""),
            ("تقرير حالة العملاء","Report","Customer Installment Status",""),
            ("تقرير تتبع الأقساط","Report","Installment Tracking Report",""),
            ("تقرير جمع الأقساط","Report","Installment Collection Report",""),
            ("تحليل المبيعات","Report","Sales Analytics",""),
        ],
        lnks=[
            ("واجهة نقطة البيع (POS)","Page","pos_next",1),
            ("إضافة عميل جديد","DocType","Customer",1),
            ("قائمة العملاء","DocType","Customer",0),
            ("فواتير المبيعات","DocType","Sales Invoice",0),
            ("سندات التحصيل","DocType","Payment Entry",0),
            ("تقرير حالة العملاء","Report","Customer Installment Status",0),
            ("تقرير تتبع الأقساط","Report","Installment Tracking Report",0),
            ("تقرير جمع الأقساط","Report","Installment Collection Report",0),
            ("تحليل المبيعات","Report","Sales Analytics",0),
        ]
    )

    rebuild("purchases-abdulrahman", "🛒 المشتريات والمصروفات — "+OWNER,
        scs=[
            ("إضافة مورد جديد","DocType","Supplier",""),
            ("قائمة الموردين","DocType","Supplier",""),
            ("فواتير المشتريات","DocType","Purchase Invoice",""),
            ("تسجيل مصروف جديد","DocType","Expense Entry","red"),
            ("سجل المصروفات","DocType","Expense Entry",""),
            ("سندات الدفع","DocType","Payment Entry",""),
            ("تقرير المشتريات","Report","Purchase Analytics",""),
            ("تقرير المصروفات","Report","Expense Analysis Report",""),
            ("دفتر الأستاذ","Report","General Ledger",""),
        ],
        lnks=[
            ("إضافة مورد جديد","DocType","Supplier",1),
            ("قائمة الموردين","DocType","Supplier",0),
            ("فواتير المشتريات","DocType","Purchase Invoice",0),
            ("تسجيل مصروف جديد","DocType","Expense Entry",1),
            ("سجل المصروفات","DocType","Expense Entry",0),
            ("سندات الدفع","DocType","Payment Entry",0),
            ("تقرير المشتريات","Report","Purchase Analytics",0),
            ("تقرير المصروفات","Report","Expense Analysis Report",0),
            ("دفتر الأستاذ","Report","General Ledger",0),
        ]
    )

    rebuild("inventory-abdulrahman", "🏪 المخزون — "+OWNER,
        scs=[
            ("إضافة صنف جديد","DocType","Item",""),
            ("قائمة الأصناف","DocType","Item",""),
            ("المستودعات","DocType","Warehouse",""),
            ("تحويل مخزون","DocType","Stock Entry",""),
            ("رصيد افتتاحي","DocType","Stock Entry",""),
            ("رصيد المخزون","Report","Stock Balance",""),
            ("حركة المخزون","Report","Stock Ledger",""),
            ("مخزون الموبايلات","Report","Stock Balance Mobile Shop",""),
            ("الأصناف المنتهية","Report","Itemwise Recommended Reorder Level","red"),
        ],
        lnks=[
            ("إضافة صنف جديد","DocType","Item",1),
            ("قائمة الأصناف","DocType","Item",0),
            ("المستودعات","DocType","Warehouse",0),
            ("تحويل مخزون","DocType","Stock Entry",0),
            ("رصيد افتتاحي","DocType","Stock Entry",0),
            ("رصيد المخزون المتاح","Report","Stock Balance",0),
            ("حركة المخزون","Report","Stock Ledger",0),
            ("تقرير مخزون الموبايلات","Report","Stock Balance Mobile Shop",0),
            ("تقرير الأصناف منتهية الكمية","Report","Itemwise Recommended Reorder Level",0),
        ]
    )

    frappe.db.commit()
    print("✅ All 4 Workspaces rebuilt successfully")
