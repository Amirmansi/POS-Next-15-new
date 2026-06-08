import frappe


def execute():
    SCRIPT = r"""
frappe.ui.form.on('Expense Entry', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) {
            frm.set_intro(
                '<div style="padding:10px;background:#e3f2fd;border-radius:6px;' +
                'color:#1565c0;font-weight:700;border-right:4px solid #1565c0;">' +
                'أضف بنود المصروف ثم احفظ وأرسل لتوليد القيد المحاسبي</div>',
                false
            );
        }
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('عرض القيد المحاسبي', function() {
                frappe.route_options = {"voucher_no": frm.doc.name};
                frappe.set_route("query-report", "General Ledger");
            });
        }
    },

    payment_method: function(frm) {
        var method_map = {
            "نقداً": "Cash",
            "بنك": "Bank",
            "محفظة إلكترونية": "Cash"
        };
        var account_type = method_map[frm.doc.payment_method];
        if (account_type) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Account",
                    filters: {
                        account_type: account_type,
                        company: frappe.defaults.get_default("company"),
                        is_group: 0
                    },
                    fields: ["name"],
                    limit: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value("payment_account", r.message[0].name);
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Expense Item Line', {
    amount: function(frm) {
        var total = 0;
        (frm.doc.expense_items || []).forEach(function(row) {
            total += flt(row.amount);
        });
        frm.set_value("total_amount", total);
    },
    expense_items_remove: function(frm) {
        var total = 0;
        (frm.doc.expense_items || []).forEach(function(row) {
            total += flt(row.amount);
        });
        frm.set_value("total_amount", total);
    }
});
"""

    for old in frappe.get_all("Client Script", filters={"dt": "Expense Entry"}, fields=["name"]):
        frappe.delete_doc("Client Script", old.name, force=True)

    doc = frappe.get_doc({
        "doctype": "Client Script",
        "dt": "Expense Entry",
        "script": SCRIPT,
        "enabled": 1,
        "name": "Expense Entry Smart Script"
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Done - Expense Entry Client Script created")
