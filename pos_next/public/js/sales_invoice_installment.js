// Sales Invoice — تحصيل أقساط شهرية عبر Payment Entry

frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1 || !frm.doc.custom_is_installment_sale) return;

		update_installment_summary(frm);
		render_grid_collect_buttons(frm);

		frm.add_custom_button(
			__("تحصيل قسط شهري"),
			() => open_collect_dialog(frm),
			__("تحصيل")
		);

		const next = get_next_installment(frm);
		if (next) {
			frm.add_custom_button(
				__("تحصيل القسط الحالي") + ` (${format_currency(next.remaining_amount, frm.doc.currency)})`,
				() => collect_installment(frm, next),
				__("تحصيل")
			);
		}
	},

	onload(frm) {
		setup_installment_grid(frm);
	},
});

function setup_installment_grid(frm) {
	if (!frm.fields_dict.custom_installment_schedule) return;
	const grid = frm.fields_dict.custom_installment_schedule.grid;
	grid.cannot_add_rows = true;
	grid.cannot_delete_rows = frm.doc.docstatus === 1;
}

function get_schedule(frm) {
	return frm.doc.custom_installment_schedule || [];
}

function get_next_installment(frm) {
	const today = frappe.datetime.get_today();
	const unpaid = get_schedule(frm)
		.filter((r) => flt(r.remaining_amount) > 0 && r.status !== "مدفوع")
		.sort((a, b) => {
			if (a.due_date === b.due_date) return a.installment_number - b.installment_number;
			return (a.due_date || "") < (b.due_date || "") ? -1 : 1;
		});

	if (!unpaid.length) return null;

	const overdue = unpaid.filter((r) => r.due_date && r.due_date < today);
	return overdue.length ? overdue[0] : unpaid[0];
}

function update_installment_summary(frm) {
	const schedule = get_schedule(frm);
	let total_paid = 0;
	let total_remaining = 0;
	let overdue_count = 0;
	const today = frappe.datetime.get_today();

	schedule.forEach((r) => {
		total_paid += flt(r.paid_amount);
		total_remaining += flt(r.remaining_amount);
		if (r.due_date && r.due_date < today && flt(r.remaining_amount) > 0) overdue_count++;
	});

	const indicator = overdue_count > 0 ? "red" : total_remaining <= 0 ? "green" : "blue";
	const colors = {
		red: { bg: "#ffebee", border: "#b71c1c" },
		blue: { bg: "#e3f2fd", border: "#1565c0" },
		green: { bg: "#e8f5e9", border: "#2e7d32" },
	};
	const c = colors[indicator];

	const html =
		`<div style="display:flex;gap:12px;padding:12px;background:${c.bg};` +
		`border-radius:8px;border:2px solid ${c.border};margin:8px 0;flex-wrap:wrap;direction:rtl;">` +
		`<div style="flex:1;min-width:110px;text-align:center;"><div style="font-size:11px;color:#666;font-weight:700;">إجمالي العقد</div>` +
		`<div style="font-size:18px;font-weight:800;color:#1a1a1a;">${format_currency(frm.doc.custom_installment_total_contract || 0, frm.doc.currency)}</div></div>` +
		`<div style="flex:1;min-width:110px;text-align:center;"><div style="font-size:11px;color:#666;font-weight:700;">القسط الشهري</div>` +
		`<div style="font-size:18px;font-weight:800;color:#3b82f6;">${format_currency(frm.doc.custom_installment_monthly_amount || 0, frm.doc.currency)}</div></div>` +
		`<div style="flex:1;min-width:110px;text-align:center;"><div style="font-size:11px;color:#666;font-weight:700;">المدفوع</div>` +
		`<div style="font-size:18px;font-weight:800;color:#22c55e;">${format_currency(total_paid, frm.doc.currency)}</div></div>` +
		`<div style="flex:1;min-width:110px;text-align:center;"><div style="font-size:11px;color:#666;font-weight:700;">المتبقي</div>` +
		`<div style="font-size:18px;font-weight:800;color:#f97316;">${format_currency(total_remaining, frm.doc.currency)}</div></div>` +
		(overdue_count > 0
			? `<div style="flex:1;min-width:110px;text-align:center;"><div style="font-size:11px;color:#666;font-weight:700;">متأخرة</div>` +
			  `<div style="font-size:18px;font-weight:800;color:#ef4444;">${overdue_count}</div></div>`
			: "") +
		`</div>`;

	frm.set_intro(html, false);
}

function render_grid_collect_buttons(frm) {
	setTimeout(() => {
		const field = frm.fields_dict.custom_installment_schedule;
		if (!field || !field.grid) return;

		const today = frappe.datetime.get_today();
		$(".btn-collect-installment, .btn-paid-installment").remove();

		get_schedule(frm).forEach((row, idx) => {
			const grid_row = field.grid.grid_rows[idx];
			if (!grid_row || !grid_row.row) return;

			const $cell = $(grid_row.row).find('[data-fieldname="remaining_amount"]').last();

			// Show Payment Entry link for rows that have been collected
			if (row.payment_entry) {
				const $pe_btn = $(
					`<a href="/app/payment-entry/${row.payment_entry}" ` +
						`class="btn btn-xs btn-paid-installment" ` +
						`target="_blank" ` +
						`style="margin-top:4px;width:100%;display:block;background:#3b82f6;color:#fff;` +
						`padding:5px 8px;border-radius:6px;font-weight:700;font-size:11px;` +
						`text-align:center;text-decoration:none;">` +
						`📄 ${row.payment_entry}</a>`
				);
				$cell.append($pe_btn);
			}

			// Show collect button for rows with outstanding balance
			if (flt(row.remaining_amount) <= 0 || row.status === "مدفوع") return;

			const is_overdue = row.due_date && row.due_date < today;
			const btn_color = is_overdue ? "#ef4444" : "#22c55e";
			const label = is_overdue
				? `⚠️ تحصيل متأخر ${format_currency(row.remaining_amount, frm.doc.currency)}`
				: `💰 تحصيل ${format_currency(row.remaining_amount, frm.doc.currency)}`;

			const $btn = $(
				`<button type="button" class="btn btn-xs btn-collect-installment" ` +
					`style="margin-top:4px;width:100%;background:${btn_color};color:#fff;border:none;` +
					`padding:6px 8px;border-radius:6px;font-weight:700;font-size:11px;">${label}</button>`
			);

			$btn.on("click", (e) => {
				e.preventDefault();
				e.stopPropagation();
				collect_installment(frm, row);
			});

			$cell.append($btn);
		});
	}, 600);
}

function open_collect_dialog(frm) {
	frappe.call({
		method: "pos_next.api.invoices.get_pending_installments",
		args: { invoice_name: frm.doc.name },
		freeze: true,
		callback(r) {
			if (!r.message || !r.message.installments || !r.message.installments.length) {
				frappe.msgprint({
					title: __("تحصيل الأقساط"),
					indicator: "green",
					message: __("كل الأقساط مدفوعة — مفيش حاجة للتحصيل"),
				});
				return;
			}

			const options = r.message.installments.map((row) => {
				const overdue = row.is_overdue ? " ⚠️ متأخر" : "";
				return {
					label: `قسط ${row.installment_number} — ${row.due_date} — ${format_currency(row.remaining_amount, frm.doc.currency)}${overdue}`,
					value: row.installment_number,
					row,
				};
			});

			const next = options[0].row;
			const d = new frappe.ui.Dialog({
				title: __("تحصيل قسط شهري"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "info",
						options:
							`<div style="direction:rtl;padding:8px 0;font-size:13px;">` +
							`<b>العميل:</b> ${frappe.utils.escape_html(r.message.customer || "")}<br>` +
							`<b>الفاتورة:</b> ${frm.doc.name}</div>`,
					},
					{
						fieldname: "installment_number",
						label: __("اختر القسط"),
						fieldtype: "Select",
						options: options.map((o) => o.label).join("\n"),
						default: options[0].label,
						reqd: 1,
					},
					{
						fieldname: "amount",
						label: __("المبلغ المُحصَّل"),
						fieldtype: "Currency",
						default: next.remaining_amount,
						reqd: 1,
					},
					{
						fieldname: "mode_of_payment",
						label: __("طريقة الدفع"),
						fieldtype: "Link",
						options: "Mode of Payment",
						default: "نقدي",
					},
				],
				primary_action_label: __("إنشاء سند قبض"),
				primary_action(values) {
					const selected = options.find((o) => o.label === values.installment_number);
					if (!selected) {
						frappe.msgprint(__("اختر قسط صحيح"));
						return;
					}
					const amount = flt(values.amount);
					if (amount <= 0 || amount > flt(selected.row.remaining_amount)) {
						frappe.msgprint({ message: __("المبلغ غير صحيح"), indicator: "red" });
						return;
					}
					d.hide();
					create_payment_entry(frm, selected.row, amount, values.mode_of_payment);
				},
			});
			d.show();
		},
	});
}

function collect_installment(frm, row) {
	const remaining = flt(row.remaining_amount);
	if (remaining <= 0) {
		frappe.msgprint(__("القسط ده مدفوع خلاص"));
		return;
	}

	frappe.confirm(
		`<div style="direction:rtl;font-size:14px;">` +
			`<b>تحصيل القسط رقم ${row.installment_number}</b><br>` +
			`المبلغ: <b>${format_currency(remaining, frm.doc.currency)}</b><br>` +
			`تاريخ الاستحقاق: <b>${row.due_date || "-"}</b><br>` +
			`هيتم إنشاء <b>Payment Entry</b> وتحديث جدول الأقساط.</div>`,
		() => {
			frappe.prompt(
				[
					{
						fieldname: "amount_to_collect",
						fieldtype: "Currency",
						label: __("المبلغ المُحصَّل"),
						default: remaining,
						reqd: 1,
					},
					{
						fieldname: "mode_of_payment",
						fieldtype: "Link",
						options: "Mode of Payment",
						label: __("طريقة الدفع"),
						default: "نقدي",
					},
				],
				(values) => {
					const collected = flt(values.amount_to_collect);
					if (collected <= 0 || collected > remaining) {
						frappe.msgprint({ message: __("المبلغ غير صحيح"), indicator: "red" });
						return;
					}
					create_payment_entry(frm, row, collected, values.mode_of_payment);
				},
				__("تحصيل القسط"),
				__("تأكيد")
			);
		}
	);
}

function create_payment_entry(frm, row, amount, mode_of_payment) {
	frappe.call({
		method: "pos_next.api.invoices.create_installment_payment_entry",
		args: {
			invoice_name: frm.doc.name,
			installment_number: row.installment_number,
			amount: amount,
			mode_of_payment: mode_of_payment || null,
		},
		freeze: true,
		freeze_message: __("جارٍ إنشاء سند القبض..."),
		callback(r) {
			if (r.message && r.message.payment_entry) {
				frappe.show_alert(
					{
						message: `✅ تم التحصيل — سند: <a href="/app/payment-entry/${r.message.payment_entry}">${r.message.payment_entry}</a>`,
						indicator: "green",
					},
					7
				);
				frm.reload_doc();
			}
		},
	});
}
