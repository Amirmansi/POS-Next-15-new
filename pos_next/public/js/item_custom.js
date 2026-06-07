// Item Form - Mobile Shop UX
// Shows only essential fields for a mobile/electronics shop

frappe.ui.form.on("Item", {
    refresh: function(frm) {
        // Essential fields for a mobile shop
        var essential_fields = [
            "item_name", "item_code", "item_group", "brand",
            "custom_brand", "custom_model", "custom_color", "custom_storage",
            "custom_imei", "custom_installment_interest", "custom_company",
            "description", "image",
            "standard_rate", "valuation_rate",
            "is_stock_item", "opening_stock",
            "default_warehouse"
        ];

        // Hide fields not in the essential list
        frm.fields.forEach(function(field) {
            if (
                !essential_fields.includes(field.df.fieldname) &&
                field.df.fieldtype !== "Section Break" &&
                field.df.fieldtype !== "Column Break" &&
                field.df.fieldtype !== "Tab Break"
            ) {
                frm.toggle_display(field.df.fieldname, false);
            }
        });

        // Show a summary intro line with device specs
        if (!frm.is_new() && frm.doc.custom_brand) {
            frm.set_intro(
                `${frm.doc.custom_brand} ${frm.doc.custom_model || ""} | ${frm.doc.custom_color || ""} | ${frm.doc.custom_storage || ""}`.trim(),
                "blue"
            );
        }
    },
});
