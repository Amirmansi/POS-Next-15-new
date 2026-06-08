# Copyright (c) 2025, BrainWise and contributors

import frappe
from frappe.utils import cint, flt, today


def update_installment_on_payment(doc, method=None):
	"""Update Installment Schedule rows when a Payment Entry is submitted."""
	if doc.payment_type != "Receive":
		return

	# Skip down payment PEs — they are not linked to any monthly installment row
	if doc.reference_no and doc.reference_no.endswith("-DP"):
		return

	for ref in doc.get("references") or []:
		if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
			continue

		si_name = ref.reference_name
		allocated = flt(ref.allocated_amount)
		if allocated <= 0:
			continue

		try:
			si = frappe.get_doc("Sales Invoice", si_name)
		except frappe.DoesNotExistError:
			continue

		if not si.get("custom_is_installment_sale"):
			continue

		inst_num = None
		if frappe.db.has_column("Payment Entry", "custom_installment_number"):
			inst_num = frappe.db.get_value("Payment Entry", doc.name, "custom_installment_number")
		if not inst_num and doc.reference_no and "-Q" in doc.reference_no:
			try:
				inst_num = cint(doc.reference_no.rsplit("-Q", 1)[-1])
			except Exception:
				inst_num = None
		target_row = None

		if inst_num is not None:
			for row in si.get("custom_installment_schedule") or []:
				if cint(row.installment_number) == cint(inst_num) and flt(row.remaining_amount) > 0:
					target_row = row
					break

		if not target_row:
			for row in sorted(
				si.get("custom_installment_schedule") or [],
				key=lambda r: (r.due_date or "", r.installment_number or 0),
			):
				if flt(row.remaining_amount) > 0:
					target_row = row
					break

		if not target_row:
			continue

		new_paid = flt(target_row.paid_amount) + allocated
		new_remaining = max(0, flt(target_row.amount) - new_paid)
		if new_remaining <= 0.01:
			new_status = "مدفوع"
		elif new_paid > 0:
			new_status = "مدفوع جزئياً"
		else:
			new_status = "مستحق"

		frappe.db.set_value(
			"Installment Schedule",
			target_row.name,
			{
				"paid_amount": new_paid,
				"remaining_amount": new_remaining,
				"status": new_status,
				"payment_entry": doc.name,
				"payment_date": doc.posting_date or today(),
			},
			update_modified=False,
		)

		si.reload()
		total_paid = sum(flt(r.paid_amount) for r in si.custom_installment_schedule)
		total_remaining = sum(flt(r.remaining_amount) for r in si.custom_installment_schedule)

		if frappe.db.has_column("Sales Invoice", "custom_total_paid_installments"):
			frappe.db.set_value(
				"Sales Invoice",
				si_name,
				{
					"custom_total_paid_installments": total_paid,
					"custom_installment_remaining": total_remaining,
				},
				update_modified=False,
			)
