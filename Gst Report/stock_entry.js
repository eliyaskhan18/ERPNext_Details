frappe.ui.form.on("Stock Entry", "purpose", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var purpose = d.purpose;
    console.log("purpose--------" + purpose);

    frappe.call({
        method: "erpnext.stock.doctype.stock_entry.stock_entry.match_item_code",
        args: {
            "purpose": purpose
        },
        async: false,

        callback: function(r) {
            console.log("stock expense account ----------" + JSON.stringify(r.message));
            var users_expensse = r.message;
            if (users_expensse != undefined) {
                var expence_purpose = r.message[0].purpose;
                var expense_account = r.message[0].expense_account;
                console.log("in if expence_purpose---------------" + expence_purpose);
                if (purpose == expence_purpose) {
                    $.each(cur_frm.doc.items || [], function(i, item) {
                        console.log("expence_account------------" + expense_account);
                        item.expense_account = "";
                        item.expense_account = expense_account;
                    });

                }

            } else {
                $.each(cur_frm.doc.items || [], function(i, item) {

                    item.expense_account = "";
                })
            }
            refresh_field("items");
            refresh_field("expense_account");
        }
    })
});
