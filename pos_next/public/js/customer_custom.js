// Customer Form - Mobile Shop UX
// Shows only essential fields; provides installment report shortcuts and WhatsApp button

frappe.ui.form.on("Customer", {
    refresh: function(frm) {
        // Hide non-essential sections for mobile shop workflow
        var essential_fields = [
            "customer_name", "customer_type", "customer_group", "territory",
            "custom_mobile", "custom_whatsapp", "custom_address_detail",
            "custom_full_name_ar", "custom_national_id", "custom_id_image",
            "custom_payment_type", "custom_notes"
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

        if (!frm.is_new()) {
            frm.add_custom_button(__("أقساطه المستحقة"), function() {
                frappe.set_route("query-report", "Installment Collection Report", {
                    customer: frm.doc.name,
                });
            });

            frm.add_custom_button(__("حالة التقسيط"), function() {
                frappe.set_route("query-report", "Customer Installment Status", {
                    customer: frm.doc.name,
                });
            });

            if (frm.doc.custom_whatsapp) {
                frm.add_custom_button(__("واتساب"), function() {
                    let phone = frm.doc.custom_whatsapp.replace(/[^0-9]/g, "");
                    if (phone.startsWith("0")) phone = "2" + phone;
                    window.open(`https://wa.me/${phone}`, "_blank");
                });
            }
        }
    },

    custom_mobile: function(frm) {
        if (!frm.doc.custom_whatsapp && frm.doc.custom_mobile) {
            frm.set_value("custom_whatsapp", frm.doc.custom_mobile);
        }
    },
});
