frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		if (frm.doc.docstatus === 1 && frm.doc.custom_payment_mode === "تقسيط") {
			if (!frm.doc.custom_installment_plan) {
				frm.add_custom_button(
					__("إنشاء خطة تقسيط"),
					function () {
						frappe.new_doc("Installment Plan", {
							sales_invoice: frm.doc.name,
							customer: frm.doc.customer,
							invoice_amount: frm.doc.grand_total,
						});
					},
					__("التقسيط")
				);
			} else {
				frm.add_custom_button(
					__("عرض خطة التقسيط"),
					function () {
						frappe.set_route("Form", "Installment Plan", frm.doc.custom_installment_plan);
					},
					__("التقسيط")
				);
			}
		}

		if (frm.doc.custom_customer_whatsapp) {
			frm.add_custom_button(__("تواصل واتساب"), function () {
				let phone = frm.doc.custom_customer_whatsapp.replace(/[^0-9]/g, "");
				if (phone.startsWith("0")) phone = "2" + phone;
				let msg = encodeURIComponent(
					`مرحباً ${frm.doc.customer_name}،\n` +
						`نذكركم بفاتورة رقم: ${frm.doc.name}\n` +
						`الإجمالي: ${frappe.format(frm.doc.grand_total, { fieldtype: "Currency" })} ج.م\n` +
						`شكراً لتعاملكم مع متجرنا 🙏`
				);
				window.open(`https://wa.me/${phone}?text=${msg}`, "_blank");
			});
		}
	},

	custom_payment_mode: function (frm) {
		if (frm.doc.custom_payment_mode === "تقسيط") {
			frappe.msgprint({
				title: __("تنبيه"),
				message: __(
					"تم تحديد البيع بالتقسيط. بعد حفظ الفاتورة، قم بإنشاء خطة التقسيط من الزر المخصص."
				),
				indicator: "blue",
			});
		}
	},

	customer: function (frm) {
		if (frm.doc.customer) {
			frappe.db.get_value(
				"Customer",
				frm.doc.customer,
				["custom_whatsapp", "custom_mobile", "custom_payment_type"],
				function (r) {
					if (r) {
						frm.set_value("custom_customer_whatsapp", r.custom_whatsapp || r.custom_mobile);
						if (r.custom_payment_type) {
							frm.set_value("custom_payment_mode", r.custom_payment_type);
						}
					}
				}
			);
		}
	},
});
