"""
Full site setup + demo data for site5.local (mobile shop).
Run: bench --site site5.local execute pos_next.pos_next.doctype.installment_plan.site_setup.run_setup
"""
import frappe


def run_setup():
	frappe.set_user("Administrator")
	log = []

	# ── 1. ERPNext Setup Wizard ───────────────────────────────────────────────
	if not frappe.db.exists("Company", "متجر الموبيلات"):
		from erpnext.setup.setup_wizard.setup_wizard import setup_complete

		args = frappe._dict(
			{
				"language": "Arabic",
				"country": "Egypt",
				"timezone": "Africa/Cairo",
				"currency": "EGP",
				"full_name": "مدير المتجر",
				"email": "admin@mobileshop.local",
				"password": "Admin1234!",
				"company_name": "متجر الموبيلات",
				"company_abbr": "MOB",
				"company_tagline": "محل موبيلات - التقسيط متاح",
				"bank_account": "بنك الموبيلات",
				"fy_start_date": "2026-01-01",
				"fy_end_date": "2026-12-31",
				"chart_of_accounts": "Standard",
				"domain": "Retail",
			}
		)
		frappe.flags.in_setup_wizard = True
		setup_complete(args)
		frappe.flags.in_setup_wizard = False
		frappe.db.commit()
		log.append("✅ ERPNext Setup Wizard completed: متجر الموبيلات")
	else:
		log.append("ℹ️ Company already exists — skipping wizard")

	company_name = "متجر الموبيلات"

	# ── 2. Root Item Group (should already exist after wizard) ────────────────
	actual_root = frappe.db.get_value(
		"Item Group", {"parent_item_group": ("in", ["", None])}, "name"
	) or "All Item Groups"
	log.append(f"ℹ️ Root Item Group: {actual_root}")

	# ── 3. Sub Item Groups ────────────────────────────────────────────────────
	sub_groups = ["هواتف ذكية", "إكسسوارات", "شواحن", "سماعات"]
	for grp in sub_groups:
		if not frappe.db.exists("Item Group", grp):
			frappe.get_doc(
				{
					"doctype": "Item Group",
					"item_group_name": grp,
					"parent_item_group": actual_root,
					"is_group": 0,
				}
			).insert(ignore_permissions=True)
	frappe.db.commit()
	log.append(f"✅ Sub Item Groups: {sub_groups}")

	# ── 4. Items ──────────────────────────────────────────────────────────────
	items_data = [
		# هواتف ذكية
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
			"item_code": "MOB-SAM-S24U",
			"item_name": "Samsung Galaxy S24 Ultra",
			"item_group": "هواتف ذكية",
			"standard_rate": 28000,
			"custom_brand": "Samsung",
			"custom_model": "Galaxy S24 Ultra",
			"custom_color": "تيتانيوم",
			"custom_storage": "512GB",
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
			"item_code": "MOB-IPHONE-15-PRO",
			"item_name": "iPhone 15 Pro",
			"item_group": "هواتف ذكية",
			"standard_rate": 35000,
			"custom_brand": "Apple",
			"custom_model": "iPhone 15 Pro",
			"custom_color": "تيتانيوم طبيعي",
			"custom_storage": "256GB",
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
			"item_code": "MOB-XIAOMI-14",
			"item_name": "Xiaomi 14",
			"item_group": "هواتف ذكية",
			"standard_rate": 15000,
			"custom_brand": "Xiaomi",
			"custom_model": "Xiaomi 14",
			"custom_color": "أسود",
			"custom_storage": "256GB",
			"custom_installment_interest": 22,
		},
		{
			"item_code": "MOB-OPPO-RENO11",
			"item_name": "OPPO Reno 11",
			"item_group": "هواتف ذكية",
			"standard_rate": 11000,
			"custom_brand": "OPPO",
			"custom_model": "Reno 11",
			"custom_color": "أزرق سماوي",
			"custom_storage": "256GB",
			"custom_installment_interest": 28,
		},
		# إكسسوارات
		{
			"item_code": "ACC-CASE-CLEAR",
			"item_name": "كفر حماية شفاف",
			"item_group": "إكسسوارات",
			"standard_rate": 150,
			"custom_brand": "Generic",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "ACC-CASE-LEATHER",
			"item_name": "كفر جلد فاخر",
			"item_group": "إكسسوارات",
			"standard_rate": 380,
			"custom_brand": "Baseus",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "ACC-GLASS-9H",
			"item_name": "جلاس حماية 9H",
			"item_group": "إكسسوارات",
			"standard_rate": 80,
			"custom_brand": "Generic",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "ACC-MAGSAFE-CAR",
			"item_name": "حامل MagSafe للسيارة",
			"item_group": "إكسسوارات",
			"standard_rate": 320,
			"custom_brand": "Baseus",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "ACC-CABLE-USBC",
			"item_name": "كابل USB-C سريع 1م",
			"item_group": "إكسسوارات",
			"standard_rate": 120,
			"custom_brand": "Baseus",
			"custom_installment_interest": 0,
		},
		# شواحن
		{
			"item_code": "CHR-65W-GAN",
			"item_name": "شاحن GaN 65W USB-C",
			"item_group": "شواحن",
			"standard_rate": 450,
			"custom_brand": "Baseus",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "CHR-25W-SAMSUNG",
			"item_name": "شاحن Samsung 25W الأصلي",
			"item_group": "شواحن",
			"standard_rate": 350,
			"custom_brand": "Samsung",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "CHR-WIRELESS-15W",
			"item_name": "شاحن لاسلكي 15W",
			"item_group": "شواحن",
			"standard_rate": 280,
			"custom_brand": "Baseus",
			"custom_installment_interest": 0,
		},
		{
			"item_code": "CHR-BANK-20K",
			"item_name": "باور بانك 20000mAh",
			"item_group": "شواحن",
			"standard_rate": 550,
			"custom_brand": "Anker",
			"custom_installment_interest": 0,
		},
		# سماعات
		{
			"item_code": "EAR-TWS-PRO",
			"item_name": "سماعة بلوتوث TWS Pro",
			"item_group": "سماعات",
			"standard_rate": 650,
			"custom_brand": "Anker",
			"custom_installment_interest": 15,
		},
		{
			"item_code": "EAR-SONY-XM5",
			"item_name": "Sony WH-1000XM5",
			"item_group": "سماعات",
			"standard_rate": 4200,
			"custom_brand": "Sony",
			"custom_model": "WH-1000XM5",
			"custom_color": "أسود",
			"custom_installment_interest": 18,
		},
		{
			"item_code": "EAR-AIRPODS-PRO2",
			"item_name": "Apple AirPods Pro 2",
			"item_group": "سماعات",
			"standard_rate": 5800,
			"custom_brand": "Apple",
			"custom_model": "AirPods Pro 2",
			"custom_installment_interest": 20,
		},
		{
			"item_code": "EAR-WIRED-USBC",
			"item_name": "سماعة سلكية Type-C",
			"item_group": "سماعات",
			"standard_rate": 120,
			"custom_brand": "Baseus",
			"custom_installment_interest": 0,
		},
	]

	created_items = 0
	for item_data in items_data:
		if not frappe.db.exists("Item", item_data["item_code"]):
			doc = frappe.get_doc(
				{
					"doctype": "Item",
					"is_stock_item": 1,
					"stock_uom": "Nos",
					**item_data,
				}
			)
			doc.insert(ignore_permissions=True)
			created_items += 1

	frappe.db.commit()
	log.append(f"✅ Items: {created_items}/{len(items_data)} created")

	# ── 5. Customers ──────────────────────────────────────────────────────────
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
			"custom_notes": "عميل منتظم — يشتري هواتف Samsung",
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
			"custom_notes": "يفضل الدفع نقداً دائماً",
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
			"custom_notes": "تشتري iPhone — تقسيط 12 شهر",
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
			"custom_notes": "تاجر — شراء بالجملة آجل 30 يوم",
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
			"custom_notes": "موظفة حكومة — تقسيط على 6 أشهر",
		},
		{
			"customer_name": "خالد إبراهيم النجار",
			"customer_type": "Individual",
			"custom_full_name_ar": "خالد إبراهيم محمود النجار",
			"custom_address_detail": "طنطا، شارع البحر، عمارة الزهراء",
			"custom_mobile": "01511223344",
			"custom_whatsapp": "01511223344",
			"custom_payment_type": "تقسيط",
			"custom_national_id": "29612051122334",
			"custom_notes": "يشتري لأولاده — تقسيط 3 أشهر",
		},
		{
			"customer_name": "منى عبدالرحمن طه",
			"customer_type": "Individual",
			"custom_full_name_ar": "منى عبدالرحمن محمد طه",
			"custom_address_detail": "الزقازيق، شارع الحرية، برج النور",
			"custom_mobile": "01099887766",
			"custom_whatsapp": "01099887766",
			"custom_payment_type": "نقدي",
			"custom_national_id": "29908157788990",
			"custom_notes": "عميلة جديدة",
		},
		{
			"customer_name": "حسام الدين رضا",
			"customer_type": "Individual",
			"custom_full_name_ar": "حسام الدين محمود رضا",
			"custom_address_detail": "سوهاج، المدينة الجديدة، عمارة الأمل",
			"custom_mobile": "01322334455",
			"custom_whatsapp": "01322334455",
			"custom_payment_type": "تقسيط",
			"custom_national_id": "30005101234567",
			"custom_notes": "مدرس — يدفع مع الراتب",
		},
		{
			"customer_name": "نادية صلاح الدين",
			"customer_type": "Individual",
			"custom_full_name_ar": "نادية صلاح الدين إبراهيم",
			"custom_address_detail": "الفيوم، شارع النيل",
			"custom_mobile": "01466778899",
			"custom_whatsapp": "01466778899",
			"custom_payment_type": "آجل",
			"custom_national_id": "29807222334455",
			"custom_notes": "صاحبة محل هدايا — آجل شهري",
		},
		{
			"customer_name": "عبدالله محمود فتحي",
			"customer_type": "Individual",
			"custom_full_name_ar": "عبدالله محمود فتحي علي",
			"custom_address_detail": "دمياط، ميدان التحرير",
			"custom_mobile": "01588990011",
			"custom_whatsapp": "01588990011",
			"custom_payment_type": "تقسيط",
			"custom_national_id": "29811105566778",
			"custom_notes": "طالب جامعي — يقسط الهاتف",
		},
	]

	created_customers = 0
	for cust_data in customers_data:
		if not frappe.db.exists("Customer", cust_data["customer_name"]):
			doc = frappe.get_doc({"doctype": "Customer", **cust_data})
			doc.insert(ignore_permissions=True)
			created_customers += 1

	frappe.db.commit()
	log.append(f"✅ Customers: {created_customers}/{len(customers_data)} created")

	# ── Write log ─────────────────────────────────────────────────────────────
	with open("/tmp/site_setup_log.txt", "w") as f:
		f.write("\n".join(log) + "\n")
		f.write("\n🎉 SETUP COMPLETE\n")
		f.write("📦 هواتف (7) + إكسسوارات (5) + شواحن (4) + سماعات (4) = 20 صنف\n")
		f.write("👥 10 عملاء متنوعين (تقسيط / نقدي / آجل)\n")
