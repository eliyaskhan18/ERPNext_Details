@frappe.whitelist()
def for_item_code():
	item_code_details = frappe.db.sql("""select name,current from `tabSeries` where name='FI-'""",as_dict=1)
	return item_code_details


@frappe.whitelist()
def series_update(current_num,name):
	updated = frappe.db.sql("""UPDATE `tabSeries` SET current = '"""+current_num+"""' where name = %s""",(name),as_dict=1)
	return updated


//////////js code

frappe.ui.form.on("Item", "before_save", function(frm, cdt, cdn) {
    if (frm.doc.__islocal) {
        var d = locals[cdt][cdn];
        console.log("i am in ---------")
        var item_details = fun();
    }
});

function fun() {
    frappe.call({
        method: "erpnext.stock.doctype.item.item.for_item_code",
        args: {},
        async: false,
        callback: function(r) {
            if (r.message) {
                console.log("hello --------------" + JSON.stringify(r.message));
                var name = r.message[0].name;
                var current = r.message[0].current
                var current_num = current + 1;
                console.log("item_code_length-------" + current + "  " + name);
                var str = "" + current_num;
                var pad = "0000";
                var ans = pad.substring(0, pad.length - str.length) + str;
                console.log("ans---------" + ans);
                var going_add = name + "" + ans;
                cur_frm.refresh();
                cur_frm.doc.item_code = going_add;
                cur_frm.refresh_field("item_code");
                cur_frm.refresh();
                console.log("before call----------current_num--" + current_num);
                console.log("before call----------name--" + name);
                frappe.ui.form.on("Item", "after_save", function(frm, cdt, cdn) {
                    update_function(current_num, name);
                });
            }
        }
    });
}

function update_function(current_num, name) {
    console.log("inside--function--current_num1----------" + typeof current_num);
    console.log("inside--function----name1----------" + typeof name);
    frappe.call({
        method: "erpnext.stock.doctype.item.item.series_update",
        args: {
            "current_num": current_num,
            "name": name
        },
        async: false,
        callback: function(r) {}
    });
}
