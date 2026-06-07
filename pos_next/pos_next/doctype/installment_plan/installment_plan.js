frappe.ui.form.on("Installment Plan", {
	refresh: function (frm) {
		frm.add_custom_button(__("إعادة حساب الجدول"), function () {
			frm.save().then(() => {
				frappe.show_alert({ message: __("تم إعادة حساب الجدول بنجاح"), indicator: "green" });
				frm.reload_doc();
			});
		});

		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("تسجيل دفعة"), function () {
				_show_payment_dialog(frm);
			});
		}

		_update_intro(frm);
	},

	interest_rate: (frm) => frm.trigger("recalculate"),
	installment_months: (frm) => frm.trigger("recalculate"),
	down_payment: (frm) => frm.trigger("recalculate"),
	invoice_amount: (frm) => frm.trigger("recalculate"),
	first_installment_date: (frm) => frm.trigger("recalculate"),
	due_day: (frm) => frm.trigger("recalculate"),

	recalculate: function (frm) {
		if (!frm.doc.invoice_amount || !frm.doc.installment_months) return;
		let base = flt(frm.doc.invoice_amount) - flt(frm.doc.down_payment || 0);
		let interest = (base * flt(frm.doc.interest_rate || 0)) / 100;
		let total = base + interest;
		let monthly = Math.round((total / frm.doc.installment_months) * 100) / 100;
		frm.set_value("total_with_interest", total);
		frm.set_value("monthly_installment", monthly);
		_update_intro(frm);
	},
});

function _update_intro(frm) {
	if (!frm.doc.total_with_interest) return;
	let color = frm.doc.plan_status === "متعثر" ? "red" : frm.doc.plan_status === "مكتمل" ? "green" : "blue";
	frm.set_intro(
		`💰 الإجمالي: <b>${_fmt(frm.doc.total_with_interest)} ج.م</b> &nbsp;|&nbsp; ` +
			`📅 القسط الشهري: <b>${_fmt(frm.doc.monthly_installment)} ج.م</b> &nbsp;|&nbsp; ` +
			`✅ المدفوع: <b>${_fmt(frm.doc.total_paid)} ج.م</b> &nbsp;|&nbsp; ` +
			`⏳ المتبقي: <b>${_fmt(frm.doc.total_remaining)} ج.م</b>`,
		color
	);
}

function _fmt(val) {
	return parseFloat(val || 0).toLocaleString("ar-EG", { minimumFractionDigits: 2 });
}

function _show_payment_dialog(frm) {
	// Build pending installments list
	let pending = (frm.doc.schedule || []).filter(
		(r) => r.status !== "مدفوع" && parseFloat(r.remaining_amount) > 0
	);
	if (!pending.length) {
		frappe.msgprint(__("لا توجد أقساط متبقية"));
		return;
	}

	let options = pending.map(
		(r) =>
			`قسط ${r.installment_number} — تاريخ: ${r.due_date} — متبقي: ${_fmt(r.remaining_amount)} ج.م`
	);

	let d = new frappe.ui.Dialog({
		title: __("تسجيل دفعة قسط"),
		fields: [
			{
				label: __("القسط"),
				fieldname: "installment_number",
				fieldtype: "Select",
				options: pending.map((r) => r.installment_number).join("\n"),
				reqd: 1,
			},
			{
				label: __("المبلغ المدفوع"),
				fieldname: "paid_amount",
				fieldtype: "Currency",
				reqd: 1,
			},
			{
				label: __("سند القبض (اختياري)"),
				fieldname: "payment_entry",
				fieldtype: "Link",
				options: "Payment Entry",
			},
		],
		primary_action_label: __("تسجيل"),
		primary_action(values) {
			frappe.call({
				method: "record_payment",
				doc: frm.doc,
				args: {
					installment_number: values.installment_number,
					paid_amount: values.paid_amount,
					payment_entry: values.payment_entry,
				},
				callback(r) {
					if (!r.exc) {
						frappe.show_alert({ message: __("تم تسجيل الدفعة بنجاح"), indicator: "green" });
						frm.reload_doc();
					}
				},
			});
			d.hide();
		},
	});
	d.show();
}
