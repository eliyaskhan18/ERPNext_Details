
//js code

frappe.ui.form.on("Item", "before_save", function(frm, cdt, cdn) {
	  var d = locals[cdt][cdn];
	console.log("i am in ---------")
	var item_details = fun();
	});
function fun(){
	 frappe.call({
        method: "erpnext.stock.doctype.item.item.for_item_code",
        args: { 
        },
        async: false,
        callback: function(r) {
		if (r.message){
		console.log("hello --------------"+JSON.stringify(r.message.length));
		var item_code_length = r.message.length;
		console.log("item_code_length-------"+item_code_length);
		var going_add = item_code_length +1;
		var str = "" + going_add
		var pad = "0000"
		var ans = pad.substring(0, pad.length - str.length) + str
		console.log("ans---------"+ans);
		cur_frm.doc.item_code = "FI- "+ans;
		cur_frm.refresh_field("item_code");
		cur_frm.refresh();
		frappe.validated = false;
		}
		else{
		var going_add = 1 ;
		var str = "" + going_add
		var pad = "0000"
		var ans = pad.substring(0, pad.length - str.length) + str
		cur_frm.doc.item_code = "FI- "+ans;
		cur_frm.refresh_field("item_code");
		cur_frm.refresh();
		frappe.validated = false;
		}
        }
    });
}


//python code

@frappe.whitelist()
def for_item_code():
	item_code_details = frappe.db.sql("""select item_code from `tabItem` where item_code LIKE ('%FI-%')""",as_dict=1)
	return item_code_details
