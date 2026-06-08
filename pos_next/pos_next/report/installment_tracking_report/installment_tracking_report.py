import urllib.parse
import frappe
from frappe.utils import flt, today, getdate, get_last_day


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


# ── أعمدة التقرير ──────────────────────────────────────────────────────────────

def get_columns():
    return [
        {"label": "العميل",             "fieldname": "customer_name",          "fieldtype": "Data",     "width": 160},
        {"label": "رقم الفاتورة",       "fieldname": "sales_invoice",          "fieldtype": "Link",     "options": "Sales Invoice", "width": 145},
        {"label": "المنتجات",           "fieldname": "items_summary",          "fieldtype": "Data",     "width": 200},
        {"label": "رقم القسط",         "fieldname": "installment_number",     "fieldtype": "Int",      "width": 80},
        {"label": "تاريخ الاستحقاق",   "fieldname": "due_date",               "fieldtype": "Date",     "width": 120},
        {"label": "قيمة القسط",        "fieldname": "amount",                 "fieldtype": "Currency", "width": 115},
        {"label": "المدفوع",            "fieldname": "paid_amount",            "fieldtype": "Currency", "width": 105},
        {"label": "المتبقي",            "fieldname": "remaining_amount",       "fieldtype": "Currency", "width": 105},
        {"label": "أقساط مدفوعة",      "fieldname": "paid_installments",      "fieldtype": "Int",      "width": 105},
        {"label": "أقساط متبقية",      "fieldname": "remaining_installments", "fieldtype": "Int",      "width": 105},
        {"label": "القسط القادم",       "fieldname": "next_due_date",          "fieldtype": "Date",     "width": 120},
        {"label": "أيام التأخر",        "fieldname": "days_overdue",           "fieldtype": "Int",      "width": 90},
        {"label": "الحالة",             "fieldname": "status_html",            "fieldtype": "HTML",     "width": 170},
        {"label": "واتساب",             "fieldname": "whatsapp_btn",           "fieldtype": "HTML",     "width": 115},
    ]


# ── بيانات التقرير ─────────────────────────────────────────────────────────────

def get_data(filters):
    today_date = getdate(today())
    month_start = today_date.replace(day=1)
    month_end   = getdate(get_last_day(today_date))

    sql_cond, values = _build_conditions(filters, today_date, month_start, month_end)

    rows = frappe.db.sql(
        f"""
        SELECT
            si.name                            AS sales_invoice,
            si.customer,
            si.customer_name,
            COALESCE(c.custom_whatsapp, c.custom_mobile, '') AS whatsapp,
            s.installment_number,
            s.due_date,
            s.amount,
            s.paid_amount,
            s.remaining_amount,
            s.status
        FROM `tabInstallment Schedule` s
        JOIN `tabSales Invoice` si ON si.name = s.parent AND s.parenttype = 'Sales Invoice'
        JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.docstatus = 1
          AND si.custom_is_installment_sale = 1
          {sql_cond}
        ORDER BY
            CASE s.status
                WHEN 'متأخر'        THEN 1
                WHEN 'مستحق'        THEN 2
                WHEN 'مدفوع جزئياً' THEN 3
                WHEN 'لم يحن بعد'   THEN 4
                WHEN 'مدفوع'        THEN 5
                ELSE 6
            END,
            s.due_date ASC
        """,
        values,
        as_dict=True,
    )

    if not rows:
        return []

    # جلب ملخص الأصناف لكل فاتورة (دفعة واحدة)
    invoice_names = list({r.sales_invoice for r in rows})
    items_map = _get_items_map(invoice_names)
    counts_map = _get_counts_map(invoice_names)

    result = []
    for row in rows:
        due       = getdate(row.due_date) if row.due_date else today_date
        days_late = max((today_date - due).days, 0) if due < today_date else 0

        smart_status = _smart_status(row, today_date, month_start, month_end)
        status_html  = _render_badge(smart_status)
        wa_btn       = _whatsapp_btn(row, smart_status)

        counts    = counts_map.get(row.sales_invoice, {})
        next_due  = counts.get("next_due")

        result.append({
            "customer_name":          row.customer_name,
            "sales_invoice":          row.sales_invoice,
            "items_summary":          (items_map.get(row.sales_invoice) or "")[:80],
            "installment_number":     row.installment_number,
            "due_date":               row.due_date,
            "amount":                 flt(row.amount),
            "paid_amount":            flt(row.paid_amount),
            "remaining_amount":       flt(row.remaining_amount),
            "paid_installments":      counts.get("paid_count") or 0,
            "remaining_installments": counts.get("remaining_count") or 0,
            "next_due_date":          next_due,
            "days_overdue":           days_late,
            "status_html":            status_html,
            "whatsapp_btn":           wa_btn,
            "_status_type":           smart_status,  # للرسم البياني
        })

    return result


# ── دوال مساعدة ────────────────────────────────────────────────────────────────

def _build_conditions(filters, today_date, month_start, month_end):
    parts, values = [], {}

    if filters.get("customer"):
        parts.append("AND si.customer = %(customer)s")
        values["customer"] = filters["customer"]

    if filters.get("sales_invoice"):
        parts.append("AND si.name = %(sales_invoice)s")
        values["sales_invoice"] = filters["sales_invoice"]

    if filters.get("from_date"):
        parts.append("AND s.due_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        parts.append("AND s.due_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    if filters.get("item_group"):
        parts.append("""
            AND EXISTS (
                SELECT 1 FROM `tabSales Invoice Item` sii
                JOIN `tabItem` it ON it.name = sii.item_code
                WHERE sii.parent = si.name AND it.item_group = %(item_group)s
            )
        """)
        values["item_group"] = filters["item_group"]

    if filters.get("min_remaining"):
        parts.append("AND s.remaining_amount >= %(min_remaining)s")
        values["min_remaining"] = flt(filters["min_remaining"])

    # فلتر خاص: المتأخرون فقط
    if filters.get("overdue_only"):
        parts.append("AND s.due_date < %(today_ov)s AND s.remaining_amount > 0 AND s.status != 'مدفوع'")
        values["today_ov"] = today_date

    # فلتر خاص: مستحق هذا الشهر
    elif filters.get("due_this_month"):
        parts.append("AND s.due_date BETWEEN %(ms)s AND %(me)s")
        values["ms"] = month_start
        values["me"] = month_end

    # فلتر حالة القسط
    elif filters.get("installment_status"):
        st = filters["installment_status"]
        if st == "لم يحن بعد":
            parts.append("AND s.due_date > %(today_f)s AND s.status != 'مدفوع'")
            values["today_f"] = today_date
        elif st == "متأخر":
            parts.append("AND s.due_date < %(today_f)s AND s.remaining_amount > 0 AND s.status != 'مدفوع'")
            values["today_f"] = today_date
        else:
            parts.append("AND s.status = %(st)s")
            values["st"] = st

    else:
        # الافتراضي: إخفاء المدفوعة تماماً
        parts.append("AND s.status != 'مدفوع'")

    return " ".join(parts), values


def _get_items_map(invoice_names):
    if not invoice_names:
        return {}
    rows = frappe.db.sql(
        """
        SELECT parent, GROUP_CONCAT(item_name ORDER BY idx SEPARATOR ' | ') AS items_str
        FROM `tabSales Invoice Item`
        WHERE parent IN %(names)s
        GROUP BY parent
        """,
        {"names": invoice_names},
        as_dict=True,
    )
    return {r.parent: r.items_str for r in rows}


def _get_counts_map(invoice_names):
    if not invoice_names:
        return {}
    rows = frappe.db.sql(
        """
        SELECT
            parent,
            SUM(status = 'مدفوع')                                         AS paid_count,
            SUM(status != 'مدفوع' AND remaining_amount > 0)               AS remaining_count,
            MIN(CASE WHEN status != 'مدفوع' AND remaining_amount > 0
                     THEN due_date END)                                    AS next_due
        FROM `tabInstallment Schedule`
        WHERE parent IN %(names)s AND parenttype = 'Sales Invoice'
        GROUP BY parent
        """,
        {"names": invoice_names},
        as_dict=True,
    )
    return {r.parent: r for r in rows}


def _smart_status(row, today_date, month_start, month_end):
    due       = getdate(row.due_date) if row.due_date else today_date
    remaining = flt(row.remaining_amount)
    paid      = flt(row.paid_amount)
    amount    = flt(row.amount)

    if remaining <= 0 or row.status == "مدفوع":
        return "مدفوع ✅"

    if 0 < paid < amount:
        return "مدفوع جزئياً 🔶"

    if due < today_date:
        days = (today_date - due).days
        if days > 30:
            return f"متأخر جداً ⛔ ({days} يوم)"
        return f"متأخر ⚠️ ({days} يوم)"

    if month_start <= due <= month_end:
        days_left = (due - today_date).days
        if days_left <= 3:
            return f"يستحق خلال {days_left} أيام 🔔"
        return "مستحق هذا الشهر 📅"

    months_left = (due.year - today_date.year) * 12 + (due.month - today_date.month)
    return f"لم يحن بعد ⏳ ({months_left} شهر)"


def _render_badge(status_text):
    if "مدفوع ✅" in status_text:
        bg, color = "#e8f5e9", "#2e7d32"
    elif "مدفوع جزئياً" in status_text:
        bg, color = "#fff3e0", "#e65100"
    elif "متأخر جداً" in status_text:
        bg, color = "#ffebee", "#b71c1c"
    elif "متأخر" in status_text:
        bg, color = "#fff8e1", "#f57f17"
    elif "يستحق خلال" in status_text:
        bg, color = "#fce4ec", "#c62828"
    elif "مستحق هذا الشهر" in status_text:
        bg, color = "#e3f2fd", "#1565c0"
    elif "لم يحن بعد" in status_text:
        bg, color = "#f3e5f5", "#6a1b9a"
    else:
        bg, color = "#f5f5f5", "#616161"

    return (
        f'<span style="background:{bg};color:{color};padding:3px 8px;'
        f'border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap;">'
        f'{status_text}</span>'
    )


def _whatsapp_btn(row, status_text):
    phone = (row.whatsapp or "").replace(" ", "").replace("+", "").replace("-", "")
    if not phone:
        return '<span style="color:#ccc;font-size:11px;">لا يوجد رقم</span>'
    if phone.startswith("0"):
        phone = "2" + phone

    remaining = flt(row.remaining_amount)

    if "متأخر جداً" in status_text:
        msg = (
            f"⛔ تنبيه عاجل — {row.customer_name}\n"
            f"لديك قسط متأخر جداً بقيمة {remaining:,.2f} ج.م\n"
            f"موعد الاستحقاق كان: {row.due_date}\n"
            f"الفاتورة: {row.sales_invoice}\n"
            f"يُرجى السداد فوراً. 🙏"
        )
        btn_color, icon = "#b71c1c", "⛔"
    elif "متأخر" in status_text:
        msg = (
            f"⚠️ تذكير مهم — {row.customer_name}\n"
            f"القسط رقم {row.installment_number} بقيمة {remaining:,.2f} ج.م متأخر.\n"
            f"موعد الاستحقاق: {row.due_date}\n"
            f"الفاتورة: {row.sales_invoice}\n"
            f"نرجو منكم السداد في أقرب وقت. 🙏"
        )
        btn_color, icon = "#f57f17", "⚠️"
    elif "يستحق خلال" in status_text or "مستحق هذا الشهر" in status_text:
        msg = (
            f"📅 تذكير بموعد القسط — {row.customer_name}\n"
            f"القسط رقم {row.installment_number} بقيمة {remaining:,.2f} ج.م\n"
            f"موعد الاستحقاق: {row.due_date}\n"
            f"الفاتورة: {row.sales_invoice}\n"
            f"شكراً لتعاملكم معنا 🙏"
        )
        btn_color, icon = "#1565c0", "📅"
    else:
        msg = (
            f"مرحباً {row.customer_name}،\n"
            f"للاستفسار عن القسط رقم {row.installment_number}\n"
            f"بقيمة {remaining:,.2f} ج.م — الفاتورة: {row.sales_invoice}"
        )
        btn_color, icon = "#25D366", "💬"

    wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
    return (
        f'<a href="{wa_url}" target="_blank" style="'
        f'background:{btn_color};color:white;padding:4px 10px;border-radius:8px;'
        f'font-size:11px;font-weight:700;text-decoration:none;white-space:nowrap;">'
        f'{icon} واتساب</a>'
    )


# ── الرسم البياني ──────────────────────────────────────────────────────────────

def get_chart(data):
    if not data:
        return None

    buckets = {}
    for row in data:
        st = row.get("_status_type", "")
        if "متأخر جداً" in st:
            key = "متأخر جداً"
        elif "متأخر" in st:
            key = "متأخر"
        elif "مدفوع جزئياً" in st:
            key = "مدفوع جزئياً"
        elif "مستحق هذا الشهر" in st or "يستحق خلال" in st:
            key = "مستحق الشهر"
        elif "لم يحن بعد" in st:
            key = "لم يحن بعد"
        elif "مدفوع ✅" in st:
            key = "مدفوع"
        else:
            key = "أخرى"
        buckets[key] = buckets.get(key, 0) + 1

    return {
        "data": {
            "labels": list(buckets.keys()),
            "datasets": [{"values": list(buckets.values())}],
        },
        "type": "donut",
        "colors": ["#b71c1c", "#f57f17", "#ff8f00", "#1565c0", "#6a1b9a", "#2e7d32", "#616161"],
        "height": 200,
    }


# ── الملخص ─────────────────────────────────────────────────────────────────────

def get_summary(data):
    if not data:
        return []

    total_remaining = sum(flt(r.get("remaining_amount", 0)) for r in data)
    overdue_rows    = [r for r in data if "متأخر" in (r.get("_status_type") or "")]
    current_rows    = [r for r in data if "مستحق الشهر" in _bucket(r.get("_status_type") or "")]

    return [
        {"label": "إجمالي المتبقي (ج.م)",       "value": total_remaining,                                         "datatype": "Currency", "indicator": "blue"},
        {"label": "أقساط متأخرة",                "value": len(overdue_rows),                                       "datatype": "Int",      "indicator": "red"},
        {"label": "مبلغ المتأخرات (ج.م)",        "value": sum(flt(r.get("remaining_amount", 0)) for r in overdue_rows), "datatype": "Currency", "indicator": "red"},
        {"label": "مستحق هذا الشهر (ج.م)",       "value": sum(flt(r.get("remaining_amount", 0)) for r in current_rows), "datatype": "Currency", "indicator": "orange"},
    ]


def _bucket(st):
    if "مستحق هذا الشهر" in st or "يستحق خلال" in st:
        return "مستحق الشهر"
    return st
