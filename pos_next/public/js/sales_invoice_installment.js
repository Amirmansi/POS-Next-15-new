// Sales Invoice - Installment Management JS
// Adds a "تحصيل قسط" button in the Installment Schedule child table
// and hides non-essential fields for a mobile shop workflow

frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {
        // Only on submitted installment invoices
        if (frm.doc.docstatus !== 1 || !frm.doc.custom_is_installment_sale) return;

        // Refresh the child table to show collection buttons
        frm.fields_dict["custom_installment_schedule"].grid.refresh();
    },

    onload: function(frm) {
        setup_installment_grid(frm);
    },
});

frappe.ui.form.on("Installment Schedule", {
    form_render: function(frm, cdt, cdn) {
        var row = frappe.get_doc(cdt, cdn);
        var wrapper = frm.fields_dict["custom_installment_schedule"].grid.get_field("status");

        // Only show on submitted docs
        if (frm.doc.docstatus !== 1 || !frm.doc.custom_is_installment_sale) return;
        if (row.status === "مدفوع") return;

        var today = frappe.datetime.get_today();
        var is_due = row.due_date <= today;

        // Find the first unpaid installment
        var schedule = frm.doc.custom_installment_schedule || [];
        var unpaid = schedule.filter(r => r.status !== "مدفوع").sort((a, b) => a.installment_number - b.installment_number);
        var is_next = unpaid.length > 0 && unpaid[0].name === row.name;

        if (!is_due && !is_next) return;

        // Add collect button
        var grid_row = frm.fields_dict["custom_installment_schedule"].grid.grid_rows_by_docname[cdn];
        if (!grid_row || grid_row.$row.find(".btn-collect-installment").length) return;

        var $btn = $(`
            <button class="btn btn-xs btn-success btn-collect-installment"
                style="margin-top:4px; font-weight:bold; font-size:12px; padding:3px 10px;">
                💰 تحصيل قسط ${row.installment_number}
            </button>
        `);

        $btn.on("click", function(e) {
            e.stopPropagation();
            collect_installment(frm, row);
        });

        grid_row.$row.find(".data-row").append($btn);
    }
});

function setup_installment_grid(frm) {
    if (!frm.fields_dict["custom_installment_schedule"]) return;

    var grid = frm.fields_dict["custom_installment_schedule"].grid;
    grid.cannot_add_rows = true;
    grid.cannot_delete_rows = frm.doc.docstatus === 1;
}

function collect_installment(frm, row) {
    var remaining = flt(row.remaining_amount);
    if (remaining <= 0) {
        frappe.msgprint(__("هذا القسط مدفوع بالفعل"));
        return;
    }

    frappe.confirm(
        `<b>تحصيل القسط رقم ${row.installment_number}</b><br>
         المبلغ: <b>${format_currency(remaining, frm.doc.currency)}</b><br>
         الفاتورة: <b>${frm.doc.name}</b><br><br>
         هل تريد إنشاء سند تحصيل؟`,
        function() {
            create_payment_entry(frm, row, remaining);
        }
    );
}

function create_payment_entry(frm, row, amount) {
    frappe.call({
        method: "pos_next.api.invoices.create_installment_payment_entry",
        args: {
            invoice_name: frm.doc.name,
            installment_number: row.installment_number,
            amount: amount,
        },
        freeze: true,
        freeze_message: __("جارٍ إنشاء سند التحصيل..."),
        callback: function(r) {
            if (r.message && r.message.payment_entry) {
                frappe.show_alert({
                    message: `تم إنشاء سند التحصيل: <b>${r.message.payment_entry}</b>`,
                    indicator: "green"
                }, 5);
                frm.reload_doc();
            }
        }
    });
}
