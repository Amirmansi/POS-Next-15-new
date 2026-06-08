import frappe


def create_expense_doctypes():
    """Create Expense Entry and Expense Item Line custom doctypes."""
    if not frappe.db.exists("DocType", "Expense Item Line"):
        ct = frappe.get_doc({
            "doctype": "DocType",
            "name": "Expense Item Line",
            "module": "Pos Next",
            "custom": 1,
            "istable": 1,
            "editable_grid": 1,
            "track_changes": 0,
            "fields": [
                {
                    "fieldname": "expense_type",
                    "fieldtype": "Link",
                    "options": "Account",
                    "label": "نوع المصروف",
                    "in_list_view": 1,
                    "columns": 3,
                    "reqd": 1,
                },
                {
                    "fieldname": "description",
                    "fieldtype": "Data",
                    "label": "الوصف / البيان",
                    "in_list_view": 1,
                    "columns": 4,
                },
                {
                    "fieldname": "amount",
                    "fieldtype": "Currency",
                    "label": "المبلغ",
                    "in_list_view": 1,
                    "columns": 2,
                    "reqd": 1,
                },
            ],
        })
        ct.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Expense Item Line child table created")
    else:
        print("⚠ Expense Item Line already exists")

    if not frappe.db.exists("DocType", "Expense Entry"):
        dt = frappe.get_doc({
            "doctype": "DocType",
            "name": "Expense Entry",
            "module": "Pos Next",
            "custom": 1,
            "is_submittable": 1,
            "track_changes": 1,
            "autoname": "naming_series:",
            "fields": [
                {
                    "fieldname": "naming_series",
                    "fieldtype": "Select",
                    "label": "السلسلة",
                    "options": "EXP-.YYYY.-",
                    "default": "EXP-.YYYY.-",
                    "reqd": 1,
                },
                {
                    "fieldname": "posting_date",
                    "fieldtype": "Date",
                    "label": "تاريخ المصروف",
                    "reqd": 1,
                    "default": "Today",
                    "in_list_view": 1,
                },
                {"fieldname": "col1", "fieldtype": "Column Break"},
                {
                    "fieldname": "payment_method",
                    "fieldtype": "Select",
                    "label": "طريقة الدفع",
                    "options": "نقداً\nبنك\nمحفظة إلكترونية\nشيك",
                    "reqd": 1,
                    "default": "نقداً",
                    "in_list_view": 1,
                },
                {
                    "fieldname": "payment_account",
                    "fieldtype": "Link",
                    "options": "Account",
                    "label": "حساب الدفع",
                    "reqd": 1,
                    "depends_on": "eval:doc.payment_method",
                },
                {
                    "fieldname": "sec_payment",
                    "fieldtype": "Section Break",
                    "label": "بيانات المستفيد",
                },
                {
                    "fieldname": "paid_to",
                    "fieldtype": "Data",
                    "label": "المدفوع إليه (اختياري)",
                    "in_list_view": 1,
                },
                {"fieldname": "col2", "fieldtype": "Column Break"},
                {
                    "fieldname": "remarks",
                    "fieldtype": "Small Text",
                    "label": "ملاحظات (اختياري)",
                },
                {
                    "fieldname": "sec_items",
                    "fieldtype": "Section Break",
                    "label": "بنود المصروف",
                },
                {
                    "fieldname": "expense_items",
                    "fieldtype": "Table",
                    "options": "Expense Item Line",
                    "label": "بنود المصروف",
                    "reqd": 1,
                },
                {
                    "fieldname": "sec_totals",
                    "fieldtype": "Section Break",
                    "label": "الإجماليات",
                },
                {
                    "fieldname": "total_amount",
                    "fieldtype": "Currency",
                    "label": "إجمالي المصروفات",
                    "read_only": 1,
                    "in_list_view": 1,
                },
                {"fieldname": "col3", "fieldtype": "Column Break"},
                {
                    "fieldname": "status",
                    "fieldtype": "Select",
                    "label": "الحالة",
                    "options": "مسودة\nمؤكدة\nملغاة",
                    "default": "مسودة",
                    "read_only": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "submit": 1,
                    "cancel": 1,
                    "amend": 1,
                },
                {
                    "role": "Accounts Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "submit": 1,
                    "cancel": 1,
                    "amend": 1,
                },
                {
                    "role": "Accounts User",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "submit": 1,
                },
            ],
        })
        dt.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Expense Entry DocType created")
    else:
        print("⚠ Expense Entry already exists")

def add_custom_field(dt, fieldname, fieldtype, label, opts=None):
    name_key = f"{dt}-{fieldname}"
    if frappe.db.exists("Custom Field", name_key):
        return
    data = {
        "doctype": "Custom Field",
        "dt": dt,
        "fieldname": fieldname,
        "fieldtype": fieldtype,
        "label": label,
    }
    if opts:
        data.update(opts)
    frappe.get_doc(data).insert(ignore_permissions=True)


def hide_field(dt, fieldname):
    name_key = f"{dt}-{fieldname}"
    if frappe.db.exists("Custom Field", name_key):
        frappe.db.set_value("Custom Field", name_key, "hidden", 1)

    ps_name = f"{dt}-{fieldname}-hidden"
    if not frappe.db.exists("Property Setter", ps_name):
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": dt,
            "field_name": fieldname,
            "property": "hidden",
            "value": "1",
            "property_type": "Check",
        }).insert(ignore_permissions=True)


def apply_doc_customizations():
    customer_hide = [
        "customer_type","lead_name","opportunity_name","account_manager",
        "is_internal_customer","represents_company","market_segment",
        "industry","website","language","customer_pos_id","so_required",
        "dn_required","is_frozen","disabled","customer_details",
        "credit_limit_section","payment_terms","loyalty_program",
        "default_currency","tax_id","tax_category","default_sales_partner",
        "sales_team_section",
    ]
    for f in customer_hide:
        try:
            hide_field("Customer", f)
        except Exception:
            pass
    print("✅ Customer fields configured")

    item_hide = [
        "hub_sync_id","hub_warehouse","is_customer_provided_item",
        "customer_items","end_of_life","default_material_request_type",
        "inspection_required_before_purchase","inspection_required_before_delivery",
        "quality_inspection_template","allow_negative_stock",
        "delivered_by_supplier","is_sub_contracted_item",
        "supplier_items","foreign_trade_section","manufacturer_section",
        "max_discount","purchase_uom_conversion_section",
        "has_expiry_date","has_batch_no","create_new_batch_automatically",
        "batch_number_series","retain_sample","sample_quantity",
    ]
    for f in item_hide:
        try:
            hide_field("Item", f)
        except Exception:
            pass
    print("✅ Item fields configured")

    sinv_hide = [
        "is_pos","pos_profile","update_billed_amount_in_sales_order",
        "update_billed_amount_in_delivery_note","scan_barcode",
        "auto_repeat","from_date","to_date","is_debit_note",
        "commission_rate","total_commission","tc_name","terms",
        "letter_head","group_same_items","language","select_print_heading",
        "cash_bank_account","write_off_amount","write_off_account",
        "write_off_cost_center","redeem_loyalty_points","loyalty_points",
        "loyalty_amount","loyalty_program","loyalty_redemption_account",
        "loyalty_redemption_cost_center","contact_person","contact_display",
        "contact_email","contact_mobile","shipping_address_name",
        "shipping_address","dispatch_address_name","dispatch_address",
    ]
    for f in sinv_hide:
        try:
            hide_field("Sales Invoice", f)
        except Exception:
            pass
    print("✅ Sales Invoice fields configured")

    supplier_hide = [
        "lead_time_days","is_internal_supplier","represents_company",
        "market_segment","industry","website","language",
        "default_currency","tax_withholding_category","default_payable_accounts",
        "payment_terms","hold_type","release_date","reason_for_putting_on_hold",
        "on_hold","is_frozen","disabled","supplier_details",
    ]
    for f in supplier_hide:
        try:
            hide_field("Supplier", f)
        except Exception:
            pass
    print("✅ Supplier fields configured")

    pinv_hide = [
        "is_subcontracted","supplier_warehouse","scan_barcode",
        "auto_repeat","from_date","to_date","is_return",
        "return_against","inter_company_invoice_reference",
        "bill_no","bill_date","is_paid","cash_bank_account",
        "write_off_amount","write_off_account","apply_tds",
        "tax_withholding_category","tc_name","terms","letter_head",
        "group_same_items","language","select_print_heading",
        "contact_person","contact_display","contact_email",
    ]
    for f in pinv_hide:
        try:
            hide_field("Purchase Invoice", f)
        except Exception:
            pass
    print("✅ Purchase Invoice fields configured")

    frappe.db.commit()
    print("\n✅ All DocType customizations applied")


def download_image(url, filename):
    try:
        from urllib.request import urlopen
        resp = urlopen(url, timeout=15)
        content = resp.read()
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": content,
            "is_private": 0,
        })
        file_doc.save(ignore_permissions=True)
        return file_doc.file_url
    except Exception as e:
        print(f"  ⚠ Image download failed for {filename}: {e}")
        return None


def create_item_groups():
    groups = [
        "هواتف ذكية", "إكسسوارات الهاتف", "شواحن وكابلات", "سماعات", "باور بانك"
    ]
    for g in groups:
        if not frappe.db.exists("Item Group", g):
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": g,
                "parent_item_group": "All Item Groups",
                "is_group": 0,
            }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("✅ Item Groups created")


def delete_old_items():
    groups = ["هواتف ذكية", "إكسسوارات الهاتف", "شواحن وكابلات", "سماعات", "باور بانك", "All Item Groups"]
    items = frappe.get_all(
        "Item",
        filters={"item_group": ["in", groups]},
        fields=["name"],
    )
    deleted = 0
    for item in items:
        try:
            if frappe.db.count("Stock Ledger Entry", {"item_code": item.name}) == 0:
                frappe.delete_doc("Item", item.name, force=True, ignore_permissions=True)
                deleted += 1
        except Exception as e:
            print(f"  Skip {item.name}: {e}")
    frappe.db.commit()
    print(f"✅ Deleted {deleted} old items")


def create_items():
    ITEM_IMAGES = {
        "smartphone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80",
        "iphone": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&q=80",
        "samsung": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80",
        "earphone": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
        "charger": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&q=80",
        "case": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&q=80",
        "powerbank": "https://images.unsplash.com/photo-1609592806596-b40d7f2f1a82?w=400&q=80",
        "cable": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
    }

    ITEMS = [
        {"item_code":"MOB-IP15-128","item_name":"iPhone 15 — 128GB أسود",
         "item_group":"هواتف ذكية","standard_rate":25000,"valuation_rate":20000,
         "custom_brand":"Apple","custom_model":"iPhone 15","custom_color":"أسود",
         "custom_storage":"128GB","custom_installment_interest":20,
         "img_key":"iphone","opening_qty":5},
        {"item_code":"MOB-IP15-256","item_name":"iPhone 15 — 256GB أبيض",
         "item_group":"هواتف ذكية","standard_rate":28000,"valuation_rate":23000,
         "custom_brand":"Apple","custom_model":"iPhone 15","custom_color":"أبيض",
         "custom_storage":"256GB","custom_installment_interest":20,
         "img_key":"iphone","opening_qty":3},
        {"item_code":"MOB-SAM-S24","item_name":"Samsung Galaxy S24 — 256GB",
         "item_group":"هواتف ذكية","standard_rate":18000,"valuation_rate":14500,
         "custom_brand":"Samsung","custom_model":"Galaxy S24","custom_color":"رمادي",
         "custom_storage":"256GB","custom_installment_interest":25,
         "img_key":"samsung","opening_qty":6},
        {"item_code":"MOB-SAM-A55","item_name":"Samsung Galaxy A55 — 128GB",
         "item_group":"هواتف ذكية","standard_rate":9500,"valuation_rate":7800,
         "custom_brand":"Samsung","custom_model":"Galaxy A55","custom_color":"أزرق",
         "custom_storage":"128GB","custom_installment_interest":30,
         "img_key":"samsung","opening_qty":8},
        {"item_code":"MOB-OPPO-R11","item_name":"OPPO Reno 11 — 256GB",
         "item_group":"هواتف ذكية","standard_rate":11000,"valuation_rate":9000,
         "custom_brand":"OPPO","custom_model":"Reno 11","custom_color":"أسود",
         "custom_storage":"256GB","custom_installment_interest":25,
         "img_key":"smartphone","opening_qty":4},
        {"item_code":"ACC-CASE-IP15","item_name":"كفر حماية iPhone 15 — شفاف",
         "item_group":"إكسسوارات الهاتف","standard_rate":150,"valuation_rate":60,
         "custom_brand":"Generic","img_key":"case","opening_qty":30},
        {"item_code":"ACC-GLASS-IP15","item_name":"جلاس شاشة iPhone 15 — 9H",
         "item_group":"إكسسوارات الهاتف","standard_rate":80,"valuation_rate":25,
         "custom_brand":"Generic","img_key":"case","opening_qty":50},
        {"item_code":"ACC-CASE-S24","item_name":"كفر حماية Samsung S24 — أسود",
         "item_group":"إكسسوارات الهاتف","standard_rate":120,"valuation_rate":45,
         "custom_brand":"Generic","img_key":"case","opening_qty":25},
        {"item_code":"CHR-65W-UC","item_name":"شاحن سريع 65W — USB-C",
         "item_group":"شواحن وكابلات","standard_rate":350,"valuation_rate":180,
         "custom_brand":"Baseus","img_key":"charger","opening_qty":20},
        {"item_code":"CHR-20W-AP","item_name":"شاحن Apple أصلي 20W",
         "item_group":"شواحن وكابلات","standard_rate":280,"valuation_rate":200,
         "custom_brand":"Apple","img_key":"charger","opening_qty":10},
        {"item_code":"CBL-UC-1M","item_name":"كابل USB-C إلى USB-C — 1 متر",
         "item_group":"شواحن وكابلات","standard_rate":80,"valuation_rate":30,
         "custom_brand":"Baseus","img_key":"cable","opening_qty":40},
        {"item_code":"CBL-LIGHT-1M","item_name":"كابل Lightning — 1 متر مضفر",
         "item_group":"شواحن وكابلات","standard_rate":100,"valuation_rate":40,
         "custom_brand":"Baseus","img_key":"cable","opening_qty":35},
        {"item_code":"CHR-WIRELESS","item_name":"شاحن لاسلكي 15W — MagSafe متوافق",
         "item_group":"شواحن وكابلات","standard_rate":320,"valuation_rate":150,
         "custom_brand":"Baseus","img_key":"charger","opening_qty":12},
        {"item_code":"EAR-TWS-PRO","item_name":"سماعة TWS Pro — بلوتوث 5.3",
         "item_group":"سماعات","standard_rate":650,"valuation_rate":300,
         "custom_brand":"Anker","custom_installment_interest":15,
         "img_key":"earphone","opening_qty":15},
        {"item_code":"EAR-WIRED-UC","item_name":"سماعة سلكية USB-C — ستيريو",
         "item_group":"سماعات","standard_rate":120,"valuation_rate":50,
         "custom_brand":"Baseus","img_key":"earphone","opening_qty":20},
        {"item_code":"EAR-SONY-XM5","item_name":"Sony WH-1000XM5 — إلغاء الضوضاء",
         "item_group":"سماعات","standard_rate":4200,"valuation_rate":3400,
         "custom_brand":"Sony","custom_installment_interest":20,
         "img_key":"earphone","opening_qty":3},
        {"item_code":"PWR-20K-BAS","item_name":"باور بانك 20000mAh — شحن سريع",
         "item_group":"باور بانك","standard_rate":550,"valuation_rate":280,
         "custom_brand":"Baseus","img_key":"powerbank","opening_qty":10},
        {"item_code":"PWR-10K-AUK","item_name":"باور بانك 10000mAh — ضغير وخفيف",
         "item_group":"باور بانك","standard_rate":350,"valuation_rate":170,
         "custom_brand":"Anker","img_key":"powerbank","opening_qty":15},
    ]

    company = frappe.defaults.get_global_default("company")
    warehouse = frappe.db.get_value("Warehouse", {"is_group": 0, "company": company}, "name")
    print(f"Company: {company} | Warehouse: {warehouse}")
    created = 0

    for item_data in ITEMS:
        if frappe.db.exists("Item", item_data["item_code"]):
            print(f"  Skip (exists): {item_data['item_code']}")
            continue

        img_key = item_data.pop("img_key", "smartphone")
        opening_qty = item_data.pop("opening_qty", 0)
        img_url = ITEM_IMAGES.get(img_key)
        file_url = None
        if img_url:
            file_url = download_image(img_url, f"{item_data['item_code']}.jpg")

        doc = frappe.get_doc({
            "doctype": "Item",
            "is_stock_item": 1,
            "stock_uom": "Nos",
            "image": file_url,
            **item_data,
        })
        frappe.flags.in_install = True
        try:
            doc.insert(ignore_permissions=True)
        finally:
            frappe.flags.in_install = False

        if opening_qty > 0 and warehouse:
            try:
                se = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Receipt",
                    "company": company,
                    "items": [{
                        "item_code": doc.name,
                        "qty": opening_qty,
                        "t_warehouse": warehouse,
                        "basic_rate": item_data.get("valuation_rate", 0),
                    }],
                })
                frappe.flags.in_install = True
                try:
                    se.insert(ignore_permissions=True)
                finally:
                    frappe.flags.in_install = False
                se.submit()
            except Exception as e:
                print(f"  ⚠ Opening stock for {doc.name}: {e}")

        created += 1
        print(f"  ✅ Created: {doc.name}")

    frappe.db.commit()
    print(f"\n✅ Total items created: {created}")


def create_reports():
    reports = [
        {
            "name": "Installment Dashboard Report",
            "report_type": "Script Report",
            "ref_doctype": "Sales Invoice",
            "module": "Pos Next",
        },
        {
            "name": "Expense Analysis Report",
            "report_type": "Script Report",
            "ref_doctype": "Expense Entry",
            "module": "Pos Next",
        },
        {
            "name": "Stock Balance Mobile Shop",
            "report_type": "Script Report",
            "ref_doctype": "Item",
            "module": "Pos Next",
        },
    ]
    for r in reports:
        if not frappe.db.exists("Report", r["name"]):
            report_doc = {"doctype": "Report", "name": r["name"], "report_name": r["name"], **r}
            frappe.get_doc(report_doc).insert(ignore_permissions=True)
            print(f"✅ Report: {r['name']}")
        else:
            print(f"⚠ Exists: {r['name']}")
    frappe.db.commit()


def create_translation(source, translated, lang="ar", context="Workspace"):
    if not frappe.db.exists("Translation", {"source_text": source, "language": lang, "context": context}):
        frappe.get_doc({
            "doctype": "Translation",
            "language": lang,
            "source_text": source,
            "translated_text": translated,
            "context": context,
        }).insert(ignore_permissions=True)
        frappe.db.commit()


def create_workspace(name, title, translated_title, icon, color, links_data, charts_data=None, cards_data=None):
    if frappe.db.exists("Workspace", name):
        frappe.delete_doc("Workspace", name, force=True, ignore_permissions=True)
    if frappe.db.exists("Workspace", translated_title):
        frappe.delete_doc("Workspace", translated_title, force=True, ignore_permissions=True)

    links = []
    for lnk in links_data:
        links.append({
            "type": lnk.get("type", "Link"),
            "label": lnk["label"],
            "link_type": lnk.get("link_type", "DocType"),
            "link_to": lnk["link_to"],
            "icon": lnk.get("icon", ""),
            "color": lnk.get("color", ""),
            "description": lnk.get("desc", ""),
            "is_query_report": 1 if lnk.get("link_type") == "Report" else 0,
        })

    charts = []
    if charts_data:
        for c in charts_data:
            charts.append({
                "chart_name": c["name"],
                "label": c["label"],
            })

    cards = []
    if cards_data:
        for c in cards_data:
            cards.append({"card_name": c["name"], "label": c["label"]})

    doc = frappe.get_doc({
        "doctype": "Workspace",
        "label": name,
        "title": title,
        "icon": icon,
        "module": "Pos Next",
        "is_standard": 0,
        "public": 1,
        "links": links,
        "charts": charts,
        "number_cards": cards,
        "content": frappe.as_json([
            {"type": "header", "data": {"text": f"<h2>{translated_title}</h2>", "level": 2}},
            {"type": "paragraph", "data": {"text": f"الصفحة الرئيسية للوورك سبيس {translated_title}"}},
        ]),
    })
    doc.insert(ignore_permissions=True)
    create_translation(title, translated_title)
    frappe.db.commit()
    print(f"✅ Workspace: {title} / {translated_title}")
    return doc


def create_workspaces():
    create_workspace(
        name="dashboard-abdulrahman",
        title="Dashboard Abdulrahman Saeed",
        translated_title="لوحة التحكم — م/عبد الرحمن سعيد",
        icon="ti-dashboard",
        color="#1a1a1a",
        links_data=[
            {"label": "فتح واجهة البيع (POS)", "link_to": "point-of-sale", "link_type": "Page", "icon": "ti-device-desktop", "color": "#22c55e"},
            {"label": "الأقساط المتأخرة", "link_to": "Installment Tracking Report", "link_type": "Report", "icon": "ti-alert-triangle", "color": "#ef4444"},
            {"label": "الأقساط المستحقة هذا الشهر", "link_to": "Installment Tracking Report", "link_type": "Report", "icon": "ti-calendar-due", "color": "#f97316"},
            {"label": "تقرير الأرباح والخسائر", "link_to": "Profit and Loss Statement", "link_type": "Report", "icon": "ti-trending-up", "color": "#3b82f6"},
            {"label": "تحليل الأقساط", "link_to": "Installment Dashboard Report", "link_type": "Report", "icon": "ti-chart-donut", "color": "#8b5cf6"},
            {"label": "تقرير المبيعات اليومي", "link_to": "Sales Analytics", "link_type": "Report", "icon": "ti-chart-bar", "color": "#06b6d4"},
        ],
    )
    create_workspace(
        name="sales-abdulrahman",
        title="Sales Abdulrahman Saeed",
        translated_title="المبيعات — م/عبد الرحمن سعيد",
        icon="ti-shopping-cart",
        color="#22c55e",
        links_data=[
            {"label": "واجهة نقطة البيع (POS)", "link_to": "point-of-sale", "link_type": "Page", "icon": "ti-device-desktop", "color": "#22c55e", "desc": "فتح كاشير المبيعات"},
            {"label": "إضافة عميل جديد", "link_to": "Customer", "link_type": "DocType", "icon": "ti-user-plus", "color": "#3b82f6"},
            {"label": "قائمة العملاء", "link_to": "Customer", "link_type": "DocType", "icon": "ti-users", "color": "#3b82f6"},
            {"label": "فواتير المبيعات", "link_to": "Sales Invoice", "link_type": "DocType", "icon": "ti-receipt", "color": "#1a1a1a", "desc": "جميع الفواتير"},
            {"label": "سندات التحصيل", "link_to": "Payment Entry", "link_type": "DocType", "icon": "ti-cash", "color": "#22c55e"},
            {"label": "تقرير تتبع الأقساط", "link_to": "Installment Tracking Report", "link_type": "Report", "icon": "ti-calendar-stats", "color": "#f97316"},
            {"label": "تقرير جمع الأقساط", "link_to": "Installment Collection Report", "link_type": "Report", "icon": "ti-report-money", "color": "#8b5cf6"},
            {"label": "تقرير حالة العملاء", "link_to": "Customer Installment Status", "link_type": "Report", "icon": "ti-user-check", "color": "#06b6d4"},
            {"label": "تحليل المبيعات", "link_to": "Sales Analytics", "link_type": "Report", "icon": "ti-chart-bar", "color": "#3b82f6"},
        ],
    )
    create_workspace(
        name="purchases-abdulrahman",
        title="Purchases and Expenses Abdulrahman Saeed",
        translated_title="المشتريات والمصروفات — م/عبد الرحمن سعيد",
        icon="ti-truck",
        color="#f97316",
        links_data=[
            {"label": "إضافة مورد جديد", "link_to": "Supplier", "link_type": "DocType", "icon": "ti-building-store", "color": "#f97316"},
            {"label": "قائمة الموردين", "link_to": "Supplier", "link_type": "DocType", "icon": "ti-building-store", "color": "#f97316"},
            {"label": "فواتير المشتريات", "link_to": "Purchase Invoice", "link_type": "DocType", "icon": "ti-file-invoice", "color": "#1a1a1a"},
            {"label": "سندات الدفع", "link_to": "Payment Entry", "link_type": "DocType", "icon": "ti-cash", "color": "#ef4444"},
            {"label": "تسجيل مصروف جديد", "link_to": "Expense Entry", "link_type": "DocType", "icon": "ti-file-dollar", "color": "#ef4444", "desc": "مصاريف يومية"},
            {"label": "سجل المصروفات", "link_to": "Expense Entry", "link_type": "DocType", "icon": "ti-list", "color": "#ef4444"},
            {"label": "تقرير المشتريات", "link_to": "Purchase Analytics", "link_type": "Report", "icon": "ti-chart-bar", "color": "#f97316"},
            {"label": "تقرير المصروفات", "link_to": "Expense Analysis Report", "link_type": "Report", "icon": "ti-chart-pie", "color": "#8b5cf6"},
            {"label": "دفتر الأستاذ", "link_to": "General Ledger", "link_type": "Report", "icon": "ti-book", "color": "#3b82f6"},
        ],
    )
    create_workspace(
        name="inventory-abdulrahman",
        title="Inventory Abdulrahman Saeed",
        translated_title="المخزون — م/عبد الرحمن سعيد",
        icon="ti-package",
        color="#8b5cf6",
        links_data=[
            {"label": "إضافة صنف جديد", "link_to": "Item", "link_type": "DocType", "icon": "ti-device-mobile", "color": "#8b5cf6"},
            {"label": "قائمة الأصناف", "link_to": "Item", "link_type": "DocType", "icon": "ti-list", "color": "#8b5cf6"},
            {"label": "المستودعات", "link_to": "Warehouse", "link_type": "DocType", "icon": "ti-building-warehouse", "color": "#3b82f6"},
            {"label": "تحويل مخزون", "link_to": "Stock Entry", "link_type": "DocType", "icon": "ti-transfer", "color": "#f97316", "desc": "نقل بين مستودعات"},
            {"label": "رصيد افتتاحي", "link_to": "Stock Entry", "link_type": "DocType", "icon": "ti-package-import", "color": "#22c55e"},
            {"label": "رصيد المخزون المتاح", "link_to": "Stock Balance", "link_type": "Report", "icon": "ti-chart-bar", "color": "#1a1a1a"},
            {"label": "حركة المخزون", "link_to": "Stock Ledger", "link_type": "Report", "icon": "ti-history", "color": "#f97316"},
            {"label": "تقرير مخزون الموبايلات", "link_to": "Stock Balance Mobile Shop", "link_type": "Report", "icon": "ti-device-mobile", "color": "#8b5cf6"},
            {"label": "تقرير الأصناف منتهية الكمية", "link_to": "Itemwise Recommended Reorder Level", "link_type": "Report", "icon": "ti-alert-circle", "color": "#ef4444"},
        ],
    )
    print("\n✅ All 4 Workspaces created successfully")


def create_dashboard_charts_and_cards():
    if not frappe.db.exists("Dashboard Chart", "مبيعات حسب العميل"):
        frappe.get_doc({
            "doctype": "Dashboard Chart",
            "chart_name": "مبيعات حسب العميل",
            "chart_type": "Group By",
            "document_type": "Sales Invoice",
            "group_by_based_on": "customer",
            "aggregate_function_based_on": "grand_total",
            "number_of_groups": 10,
            "type": "Bar",
            "color": "#3b82f6",
            "filters_json": '[{"fieldname":"docstatus","operator":"=","value":"1"}]',
            "is_public": 1,
        }).insert(ignore_permissions=True)
        print("✅ Chart 1 created")
    else:
        print("⚠ Chart 1 exists")

    if not frappe.db.exists("Dashboard Chart", "المبيعات الشهرية"):
        frappe.get_doc({
            "doctype": "Dashboard Chart",
            "chart_name": "المبيعات الشهرية",
            "chart_type": "Sum",
            "document_type": "Sales Invoice",
            "based_on": "posting_date",
            "time_interval": "Monthly",
            "timespan": "Last Year",
            "value_based_on": "grand_total",
            "type": "Line",
            "color": "#22c55e",
            "filters_json": '[{"fieldname":"docstatus","operator":"=","value":"1"}]',
            "is_public": 1,
        }).insert(ignore_permissions=True)
        print("✅ Chart 2 created")
    else:
        print("⚠ Chart 2 exists")

    if not frappe.db.exists("Dashboard Chart", "المصروفات حسب النوع"):
        frappe.get_doc({
            "doctype": "Dashboard Chart",
            "chart_name": "المصروفات حسب النوع",
            "chart_type": "Group By",
            "document_type": "Expense Entry",
            "group_by_based_on": "payment_method",
            "aggregate_function_based_on": "total_amount",
            "number_of_groups": 8,
            "type": "Donut",
            "color": "#f97316",
            "filters_json": "[]",
            "is_public": 1,
        }).insert(ignore_permissions=True)
        print("✅ Chart 3 created")
    else:
        print("⚠ Chart 3 exists")

    number_cards = [
        {
            "name": "فواتير غير مدفوعة",
            "label": "فواتير غير مدفوعة",
            "document_type": "Sales Invoice",
            "function": "Count",
            "aggregate_function_based_on": "name",
            "filters_json": '[{"fieldname":"outstanding_amount","operator":">","value":"0"},{"fieldname":"docstatus","operator":"=","value":"1"}]',
            "color": "#ef4444",
            "stats_time_interval": "Daily",
        },
        {
            "name": "مبيعات اليوم",
            "label": "مبيعات اليوم",
            "document_type": "Sales Invoice",
            "function": "Sum",
            "aggregate_function_based_on": "grand_total",
            "filters_json": '[{"fieldname":"posting_date","operator":"=","value":"Today"},{"fieldname":"docstatus","operator":"=","value":"1"}]',
            "color": "#22c55e",
            "stats_time_interval": "Daily",
        },
        {
            "name": "عدد المصروفات",
            "label": "عدد المصروفات",
            "document_type": "Expense Entry",
            "function": "Count",
            "aggregate_function_based_on": "name",
            "filters_json": '[{"fieldname":"docstatus","operator":"=","value":"1"}]',
            "color": "#8b5cf6",
            "stats_time_interval": "Monthly",
        },
        {
            "name": "مصروفات الشهر",
            "label": "مصروفات الشهر",
            "document_type": "Expense Entry",
            "function": "Sum",
            "aggregate_function_based_on": "total_amount",
            "filters_json": '[{"fieldname":"docstatus","operator":"=","value":"1"}]',
            "color": "#8b5cf6",
            "stats_time_interval": "Monthly",
        },
    ]
    for card in number_cards:
        if not frappe.db.exists("Number Card", card["name"]):
            frappe.get_doc({"doctype": "Number Card", **card}).insert(ignore_permissions=True)
            print(f"✅ Number Card: {card['name']}")
        else:
            print(f"⚠ Exists: {card['name']}")

    frappe.db.commit()
    print("\n✅ All charts and number cards created")


def link_dashboard_cards_and_charts():
    ws_name = frappe.db.get_value("Workspace", {"label": "dashboard-abdulrahman"}, "name")
    if not ws_name:
        ws_name = frappe.db.get_value("Workspace", {"title": "Dashboard Abdulrahman Saeed"}, "name")
    if not ws_name:
        print("⚠ Dashboard workspace not found")
        return
    ws = frappe.get_doc("Workspace", ws_name)
    ws.set("number_cards", [])
    ws.set("charts", [])

    for card_name in ["فواتير غير مدفوعة", "مبيعات اليوم", "عدد المصروفات", "مصروفات الشهر"]:
        if frappe.db.exists("Number Card", card_name):
            ws.append("number_cards", {"number_card_name": card_name, "label": card_name})

    for chart_name in ["مبيعات حسب العميل", "المبيعات الشهرية", "المصروفات حسب النوع"]:
        if frappe.db.exists("Dashboard Chart", chart_name):
            ws.append("charts", {"chart_name": chart_name, "label": chart_name})

    ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("✅ Dashboard Workspace updated with cards and charts")


def create_expense_entry_client_script():
    SCRIPT = """
frappe.ui.form.on('Expense Entry', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) {
            frm.set_intro(
                '<div style="padding:8px;background:#e3f2fd;border-radius:6px;color:#1565c0;font-weight:700;">' +
                '📝 أضف بنود المصروف في الجدول أدناه ثم احفظ وأرسل لتوليد القيد المحاسبي</div>',
                false
            );
        }
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('📄 عرض القيد المحاسبي', function() {
                frappe.route_options = {"voucher_no": frm.doc.name};
                frappe.set_route("query-report", "General Ledger");
            });
        }
        const colors = {"مسودة":"#f97316","مؤكدة":"#22c55e","ملغاة":"#ef4444"};
        const status = frm.doc.status;
        if (colors[status]) {
            frm.set_df_property("status", "bold", 1);
        }
    },

    payment_method: function(frm) {
        const method_map = {
            "نقداً": "Cash",
            "بنك": "Bank",
            "محفظة إلكترونية": "Cash",
        };
        const account_type = method_map[frm.doc.payment_method];
        if (account_type) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Account",
                    filters: {
                        account_type: account_type,
                        company: frappe.defaults.get_default("company"),
                        is_group: 0,
                    },
                    fields: ["name"],
                    limit: 1,
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value("payment_account", r.message[0].name);
                    }
                },
            });
        }
    }
});

frappe.ui.form.on('Expense Item Line', {
    amount: function(frm, cdt, cdn) {
        calculate_total(frm);
    },
    expense_items_remove: function(frm) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let total = 0;
    (frm.doc.expense_items || []).forEach(row => {
        total += flt(row.amount);
    });
    frm.set_value("total_amount", total);
}
"""

    old = frappe.get_all("Client Script", filters={"dt": "Expense Entry"}, fields=["name"])
    for o in old:
        try:
            frappe.delete_doc("Client Script", o.name, force=True, ignore_permissions=True)
        except Exception:
            pass

    frappe.get_doc({
        "doctype": "Client Script",
        "dt": "Expense Entry",
        "script": SCRIPT,
        "enabled": 1,
        "name": "Expense Entry Smart Script",
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("✅ Expense Entry Client Script created")


def setup_all():
    create_expense_doctypes()
    apply_doc_customizations()
    create_item_groups()
    delete_old_items()
    create_items()
    create_reports()
    create_workspaces()
    create_dashboard_charts_and_cards()
    link_dashboard_cards_and_charts()
    create_expense_entry_client_script()
    print("\n✅ Full setup completed")
