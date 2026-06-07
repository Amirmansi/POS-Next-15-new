import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, nowdate, flt, get_last_day
from datetime import date


class InstallmentPlan(Document):
	def validate(self):
		self.calculate_totals()
		self.generate_schedule()
		self.update_summary()

	def calculate_totals(self):
		base_amount = flt(self.invoice_amount) - flt(self.down_payment)
		interest = base_amount * flt(self.interest_rate) / 100
		self.total_with_interest = base_amount + interest
		if self.installment_months and int(self.installment_months) > 0:
			self.monthly_installment = round(
				self.total_with_interest / int(self.installment_months), 2
			)

	def generate_schedule(self):
		if not self.first_installment_date or not self.installment_months:
			return

		# Preserve existing paid amounts before regenerating
		existing_paid = {}
		for row in self.schedule:
			if flt(row.paid_amount) > 0:
				existing_paid[row.installment_number] = {
					"paid_amount": flt(row.paid_amount),
					"payment_entry": row.payment_entry,
					"payment_date": row.payment_date,
					"status": row.status,
				}

		self.schedule = []
		start_date = getdate(self.first_installment_date)
		monthly_amount = flt(self.monthly_installment)
		months = int(self.installment_months)

		for i in range(months):
			if self.due_day == "آخر الشهر":
				due = get_last_day(add_months(start_date, i))
			else:
				month_date = add_months(start_date, i)
				try:
					due = date(month_date.year, month_date.month, int(self.due_day))
				except ValueError:
					due = get_last_day(month_date)

			# Last installment absorbs rounding difference
			if i == months - 1:
				paid_so_far = monthly_amount * i
				amount = round(flt(self.total_with_interest) - paid_so_far, 2)
			else:
				amount = monthly_amount

			inst_num = i + 1
			existing = existing_paid.get(inst_num, {})
			paid = flt(existing.get("paid_amount", 0))
			remaining = round(amount - paid, 2)

			if paid >= amount:
				status = "مدفوع"
			elif paid > 0:
				status = "مدفوع جزئياً"
			elif getdate(due) < getdate(nowdate()):
				status = "متأخر"
			else:
				status = "مستحق"

			self.append(
				"schedule",
				{
					"installment_number": inst_num,
					"due_date": due,
					"amount": amount,
					"paid_amount": paid,
					"remaining_amount": max(remaining, 0),
					"status": status,
					"payment_entry": existing.get("payment_entry"),
					"payment_date": existing.get("payment_date"),
				},
			)

	def update_summary(self):
		total_paid = sum(flt(row.paid_amount) for row in self.schedule)
		total_amount = sum(flt(row.amount) for row in self.schedule)
		self.total_paid = total_paid
		self.total_remaining = round(total_amount - total_paid, 2)

		if self.total_remaining <= 0:
			self.plan_status = "مكتمل"
		elif any(
			row.status == "متأخر" and flt(row.remaining_amount) > 0 for row in self.schedule
		):
			self.plan_status = "متعثر"
		elif self.plan_status not in ("ملغي",):
			self.plan_status = "نشط"

	def on_submit(self):
		frappe.db.set_value(
			"Sales Invoice", self.sales_invoice, "custom_installment_plan", self.name
		)
		frappe.db.commit()

	@frappe.whitelist()
	def record_payment(self, installment_number, paid_amount, payment_entry=None):
		"""Record payment against a specific installment."""
		paid_amount = flt(paid_amount)
		installment_number = int(installment_number)

		for row in self.schedule:
			if row.installment_number == installment_number:
				new_paid = flt(row.paid_amount) + paid_amount
				row.paid_amount = new_paid
				row.remaining_amount = max(flt(row.amount) - new_paid, 0)

				if new_paid >= flt(row.amount):
					row.status = "مدفوع"
					row.payment_date = nowdate()
				elif new_paid > 0:
					row.status = "مدفوع جزئياً"

				if payment_entry:
					row.payment_entry = payment_entry
				break

		self.update_summary()
		self.save()
		return {"success": True, "total_remaining": self.total_remaining}
