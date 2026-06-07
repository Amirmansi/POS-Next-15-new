"""
Demo data script for the installment system.
Run from bench console:
    bench --site site5.local console
    exec(open('apps/pos_next/pos_next/pos_next/doctype/installment_plan/installment_demo_data.py').read())
"""
import frappe

frappe.set_user("Administrator")

# ── Item Groups ──────────────────────────────────────────────────────────────
for grp in ["هواتف ذكية", "إكسسوارات", "شواحن", "سماعات"]:
	if not frappe.db.exists("Item Group", grp):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": grp,
				"parent_item_group": "All Item Groups",
				"is_group": 0,
			}
		).insert(ignore_permissions=True)

frappe.db.commit()
print("✅ Item Groups created")

# ── Items ─────────────────────────────────────────────────────────────────────
items_data = [
	{
		"item_code": "MOB-SAM-S24",
		"item_name": "Samsung Galaxy S24",
		"item_group": "هواتف ذكية",
		"standard_rate": 18000,
		"custom_brand": "Samsung",
		"custom_model": "Galaxy S24",
		"custom_color": "أسود",
		"custom_storage": "256GB",
		"custom_installment_interest": 25,
	},
	{
		"item_code": "MOB-IPHONE-15",
		"item_name": "iPhone 15",
		"item_group": "هواتف ذكية",
		"standard_rate": 25000,
		"custom_brand": "Apple",
		"custom_model": "iPhone 15",
		"custom_color": "أزرق",
		"custom_storage": "128GB",
		"custom_installment_interest": 20,
	},
	{
		"item_code": "MOB-SAM-A55",
		"item_name": "Samsung Galaxy A55",
		"item_group": "هواتف ذكية",
		"standard_rate": 9500,
		"custom_brand": "Samsung",
		"custom_model": "Galaxy A55",
		"custom_color": "أخضر",
		"custom_storage": "128GB",
		"custom_installment_interest": 30,
	},
	{
		"item_code": "ACC-CASE-01",
		"item_name": "كفر حماية شفاف",
		"item_group": "إكسسوارات",
		"standard_rate": 150,
		"custom_brand": "Generic",
		"custom_installment_interest": 0,
	},
	{
		"item_code": "ACC-GLASS-01",
		"item_name": "جلاس حماية للشاشة",
		"item_group": "إكسسوارات",
		"standard_rate": 80,
		"custom_brand": "Generic",
		"custom_installment_interest": 0,
	},
	{
		"item_code": "CHR-65W-01",
		"item_name": "شاحن سريع 65W USB-C",
		"item_group": "شواحن",
		"standard_rate": 350,
		"custom_brand": "Baseus",
		"custom_installment_interest": 0,
	},
	{
		"item_code": "CHR-WIRELESS-01",
		"item_name": "شاحن لاسلكي 15W",
		"item_group": "شواحن",
		"standard_rate": 280,
		"custom_brand": "Baseus",
		"custom_installment_interest": 0,
	},
	{
		"item_code": "EAR-BT-01",
		"item_name": "سماعة بلوتوث TWS Pro",
		"item_group": "سماعات",
		"standard_rate": 650,
		"custom_brand": "Anker",
		"custom_installment_interest": 15,
	},
	{
		"item_code": "EAR-WIRED-01",
		"item_name": "سماعة سلكية Type-C",
		"item_group": "سماعات",
		"standard_rate": 120,
		"custom_brand": "Baseus",
		"custom_installment_interest": 0,
	},
]

for item_data in items_data:
	if not frappe.db.exists("Item", item_data["item_code"]):
		doc = frappe.get_doc({"doctype": "Item", "is_stock_item": 1, "stock_uom": "Nos", **item_data})
		doc.insert(ignore_permissions=True)

frappe.db.commit()
print(f"✅ Items created: {len(items_data)}")

# ── Customers ─────────────────────────────────────────────────────────────────
customers_data = [
	{
		"customer_name": "أحمد محمد السيد",
		"customer_type": "Individual",
		"custom_full_name_ar": "أحمد محمد السيد عبدالله",
		"custom_address_detail": "القاهرة، شارع الجيش، عمارة 12، شقة 3",
		"custom_mobile": "01012345678",
		"custom_whatsapp": "01012345678",
		"custom_payment_type": "تقسيط",
		"custom_national_id": "29901011234567",
	},
	{
		"customer_name": "محمد علي إبراهيم",
		"customer_type": "Individual",
		"custom_full_name_ar": "محمد علي إبراهيم حسن",
		"custom_address_detail": "الإسكندرية، سموحة، برج النيل، الدور 5",
		"custom_mobile": "01198765432",
		"custom_whatsapp": "01198765432",
		"custom_payment_type": "نقدي",
		"custom_national_id": "29805152345678",
	},
	{
		"customer_name": "فاطمة خالد العمري",
		"customer_type": "Individual",
		"custom_full_name_ar": "فاطمة خالد محمود العمري",
		"custom_address_detail": "الجيزة، الدقي، شارع التحرير، رقم 45",
		"custom_mobile": "01554433221",
		"custom_whatsapp": "01554433221",
		"custom_payment_type": "تقسيط",
		"custom_national_id": "30003030987654",
	},
	{
		"customer_name": "عمر أحمد القاضي",
		"customer_type": "Individual",
		"custom_full_name_ar": "عمر أحمد محمد القاضي",
		"custom_address_detail": "المنصورة، شارع الجمهورية، برج السلام، شقة 8",
		"custom_mobile": "01067890123",
		"custom_whatsapp": "01067890123",
		"custom_payment_type": "آجل",
		"custom_national_id": "29712285678901",
	},
	{
		"customer_name": "سارة حسن الشافعي",
		"customer_type": "Individual",
		"custom_full_name_ar": "سارة حسن محمود الشافعي",
		"custom_address_detail": "أسيوط، شارع الكورنيش، عمارة المروة، شقة 6",
		"custom_mobile": "01234567890",
		"custom_whatsapp": "01234567890",
		"custom_payment_type": "تقسيط",
		"custom_national_id": "30108106789012",
	},
]

for cust_data in customers_data:
	if not frappe.db.exists("Customer", cust_data["customer_name"]):
		doc = frappe.get_doc({"doctype": "Customer", **cust_data})
		doc.insert(ignore_permissions=True)

frappe.db.commit()
print(f"✅ Customers created: {len(customers_data)}")
print("\n🎉 البيانات التجريبية جاهزة على site5.local")
