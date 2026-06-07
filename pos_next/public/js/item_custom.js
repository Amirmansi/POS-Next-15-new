frappe.ui.form.on("Item", {
	refresh: function (frm) {
		if (!frm.is_new() && frm.doc.custom_brand) {
			frm.set_intro(
				`${frm.doc.custom_brand} ${frm.doc.custom_model || ""} | ${frm.doc.custom_color || ""} | ${frm.doc.custom_storage || ""}`.trim(),
				"blue"
			);
		}
	},
});
