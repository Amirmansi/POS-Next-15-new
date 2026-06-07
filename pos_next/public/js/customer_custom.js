frappe.ui.form.on("Customer", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("أقساطه المستحقة"), function () {
				frappe.set_route("query-report", "Installment Collection Report", {
					customer: frm.doc.name,
				});
			});

			frm.add_custom_button(__("حالة التقسيط"), function () {
				frappe.set_route("query-report", "Customer Installment Status", {
					customer: frm.doc.name,
				});
			});

			if (frm.doc.custom_whatsapp) {
				frm.add_custom_button(__("واتساب"), function () {
					let phone = frm.doc.custom_whatsapp.replace(/[^0-9]/g, "");
					if (phone.startsWith("0")) phone = "2" + phone;
					window.open(`https://wa.me/${phone}`, "_blank");
				});
			}
		}
	},

	custom_mobile: function (frm) {
		if (!frm.doc.custom_whatsapp && frm.doc.custom_mobile) {
			frm.set_value("custom_whatsapp", frm.doc.custom_mobile);
		}
	},
});
