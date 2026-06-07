"""
Installation and Migration hooks for POS Next

This module relies on Frappe's fixture system for:
- Custom fields (custom_field.json)
- Roles (role.json)
- Custom DocPerm (custom_docperm.json)
- Print formats (print_format.json)

The fixtures are defined in hooks.py and synced automatically during install/migrate.
This module handles post-fixture tasks like setting defaults and clearing cache.
"""
import frappe
import logging

# Configure logger
logger = logging.getLogger(__name__)


def after_install():
	"""Hook that runs after app installation"""
	try:
		log_message("POS Next: Running post-install setup", level="info")

		# Setup default print format for POS Profiles
		setup_default_print_format()

		# Create installment system custom fields
		create_installment_custom_fields()

		# Clear cache to ensure changes take effect
		frappe.clear_cache()
		frappe.db.commit()

		log_message("POS Next: Installation completed successfully", level="success")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(
			title="POS Next Installation Error",
			message=frappe.get_traceback()
		)
		log_message(f"POS Next: Installation error - {str(e)}", level="error")
		raise


def after_migrate():
	"""Hook that runs after bench migrate"""
	try:
		# Setup default print format
		setup_default_print_format(quiet=True)

		# Ensure installment custom fields exist
		create_installment_custom_fields(quiet=True)

		# Clear cache
		frappe.clear_cache()
		frappe.db.commit()

		log_message("POS Next: Migration completed successfully", level="success")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(
			title="POS Next Migration Error",
			message=frappe.get_traceback()
		)
		log_message(f"POS Next: Migration error - {str(e)}", level="error")
		raise


def create_installment_custom_fields(quiet=False):
	"""Create custom fields for the installment system on Customer, Item, and Sales Invoice."""
	fields = [
		# --- Customer ---
		{
			"dt": "Customer",
			"fieldname": "custom_full_name_ar",
			"fieldtype": "Data",
			"label": "الاسم الكامل بالعربي",
			"insert_after": "customer_name",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_address_detail",
			"fieldtype": "Small Text",
			"label": "العنوان التفصيلي",
			"insert_after": "custom_full_name_ar",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_mobile",
			"fieldtype": "Data",
			"label": "رقم الهاتف",
			"insert_after": "custom_address_detail",
			"options": "Phone",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_whatsapp",
			"fieldtype": "Data",
			"label": "رقم الواتساب",
			"insert_after": "custom_mobile",
			"options": "Phone",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_id_image",
			"fieldtype": "Attach Image",
			"label": "صورة البطاقة / الهوية",
			"insert_after": "custom_whatsapp",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_national_id",
			"fieldtype": "Data",
			"label": "رقم الهوية الوطنية",
			"insert_after": "custom_id_image",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_payment_type",
			"fieldtype": "Select",
			"label": "نوع الدفع المعتاد",
			"options": "نقدي\nتقسيط\nآجل",
			"insert_after": "custom_national_id",
		},
		{
			"dt": "Customer",
			"fieldname": "custom_notes",
			"fieldtype": "Small Text",
			"label": "ملاحظات",
			"insert_after": "custom_payment_type",
		},
		# --- Item ---
		{
			"dt": "Item",
			"fieldname": "custom_brand",
			"fieldtype": "Data",
			"label": "الماركة / العلامة التجارية",
			"insert_after": "item_name",
		},
		{
			"dt": "Item",
			"fieldname": "custom_model",
			"fieldtype": "Data",
			"label": "الموديل",
			"insert_after": "custom_brand",
		},
		{
			"dt": "Item",
			"fieldname": "custom_color",
			"fieldtype": "Data",
			"label": "اللون",
			"insert_after": "custom_model",
		},
		{
			"dt": "Item",
			"fieldname": "custom_storage",
			"fieldtype": "Data",
			"label": "السعة التخزينية",
			"insert_after": "custom_color",
		},
		{
			"dt": "Item",
			"fieldname": "custom_installment_interest",
			"fieldtype": "Percent",
			"label": "نسبة فائدة التقسيط الافتراضية (%)",
			"insert_after": "custom_storage",
			"default": "0",
			"description": "تُستخدم كقيمة افتراضية عند تقسيط هذا الصنف",
		},
		{
			"dt": "Item",
			"fieldname": "custom_imei",
			"fieldtype": "Data",
			"label": "رقم IMEI (اختياري)",
			"insert_after": "custom_installment_interest",
		},
		# --- Sales Invoice ---
		{
			"dt": "Sales Invoice",
			"fieldname": "custom_payment_mode",
			"fieldtype": "Select",
			"label": "طريقة الدفع",
			"options": "نقدي\nتقسيط\nآجل\nبطاقة",
			"insert_after": "payment_terms_template",
		},
		{
			"dt": "Sales Invoice",
			"fieldname": "custom_installment_plan",
			"fieldtype": "Link",
			"options": "Installment Plan",
			"label": "خطة التقسيط",
			"insert_after": "custom_payment_mode",
			"read_only": 1,
		},
		{
			"dt": "Sales Invoice",
			"fieldname": "custom_down_payment_received",
			"fieldtype": "Currency",
			"label": "الدفعة المقدمة المستلمة",
			"insert_after": "custom_installment_plan",
			"default": "0",
		},
		{
			"dt": "Sales Invoice",
			"fieldname": "custom_customer_whatsapp",
			"fieldtype": "Data",
			"label": "واتساب العميل",
			"insert_after": "custom_down_payment_received",
			"fetch_from": "customer.custom_whatsapp",
			"read_only": 1,
		},
	]

	created = 0
	for f in fields:
		field_name = f["dt"] + "-" + f["fieldname"]
		if not frappe.db.exists("Custom Field", field_name):
			try:
				doc = frappe.get_doc({"doctype": "Custom Field", **f})
				doc.insert(ignore_permissions=True)
				created += 1
			except Exception as e:
				log_message(
					f"Error creating custom field {field_name}: {str(e)}", level="error"
				)

	if not quiet:
		log_message(f"Installment custom fields: {created} created", level="info")


def setup_default_print_format(quiet=False):
	"""
	Set POS Next Receipt as default print format for POS Profiles if not already set.

	Args:
		quiet (bool): If True, suppress detailed logs
	"""
	try:
		# Check if the print format exists
		if not frappe.db.exists("Print Format", "POS Next Receipt"):
			if not quiet:
				log_message("POS Next Receipt print format not found, skipping default setup", level="warning")
			return

		# Get all POS Profiles without a print format
		pos_profiles = frappe.get_all(
			"POS Profile",
			filters={"print_format": ["in", ["", None]]},
			fields=["name"]
		)

		if pos_profiles:
			updated_count = 0
			for profile in pos_profiles:
				try:
					frappe.db.set_value(
						"POS Profile",
						profile.name,
						"print_format",
						"POS Next Receipt",
						update_modified=False
					)
					if not quiet:
						log_message(f"Set default print format for: {profile.name}", level="info", indent=1)
					updated_count += 1
				except Exception as e:
					log_message(f"Error updating POS Profile {profile.name}: {str(e)}", level="error", indent=1)

			if updated_count > 0 and not quiet:
				log_message(f"Updated {updated_count} POS Profile(s) with default print format", level="success")

	except Exception as e:
		log_message(f"Error setting up default print format: {str(e)}", level="error")
		frappe.log_error(
			title="Default Print Format Setup Error",
			message=frappe.get_traceback()
		)


def log_message(message, level="info", indent=0):
	"""
	Standardized logging function with consistent formatting.

	Args:
		message (str): The message to log
		level (str): Log level - info, success, warning, error
		indent (int): Indentation level (0, 1, 2, etc.)
	"""
	indent_str = "  " * indent

	prefixes = {
		"info": "[INFO]",
		"success": "[SUCCESS]",
		"warning": "[WARNING]",
		"error": "[ERROR]",
	}

	prefix = prefixes.get(level, "[INFO]")
	formatted_message = f"{indent_str}{prefix} {message}"

	# Print to console
	print(formatted_message)

	# Also log to frappe logger
	if level == "error":
		logger.error(message)
	elif level == "warning":
		logger.warning(message)
	else:
		logger.info(message)
