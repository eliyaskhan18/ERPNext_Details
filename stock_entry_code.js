frappe.ui.form.on("Stock Entry Detail", {
    item_code: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var item_code = d.item_code;
	
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
				console.log("expense_account-------"+r.message);
			  if (r.message) {
				var expense_account = "";
			      expense_account = r.message.expense_account;
			    console.log("expense_account-------"+expense_account);
			  $.each(cur_frm.doc.items || [], function(i, item) {
				item._default_expense_account = expense_account;
			});
			refresh_field("items");
			  }
		}//end of callback fun..
	   });//end of frappe call..
	
    }
});

