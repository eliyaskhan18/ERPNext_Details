frappe.ui.form.on("Stock Entry", "refresh", function(frm) {
    cur_frm.set_query("expense_account", "items", function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var bom_list = [];
        var index = d.idx;
        var expense_account = get_expense_account(d.item_code);
        if (expense_account != null) {
            var expense_account_list = [];
            expense_account_list.push(expense_account);
            return {
                "filters": [
                    ["Account", "name", "in", expense_account_list]
                ]
            }
            refresh_field("expense_account");
            refresh_field("items");
        }
    });

});

function get_expense_account(item_code) {
    var expense_account = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Item",
            filters: {
                item_code: ["=", item_code]
            },

            fieldname: ["expense_account"]
        },
        async: false,

        callback: function(r) {
            if (r.message) {
                expense_account = r.message.expense_account;
            } else {
                expense_account = null;
            }

        } //end of callback fun..
    }); //end of frappe call..
    return expense_account;
}
