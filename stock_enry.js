frappe.ui.form.on("Sales Order", "refresh", function(frm) {
    cur_frm.set_query("control_bom", "items", function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
	var bom_list = [];
	var index = d.idx;
        bom_list = getControlBOMList(d.item_code);
        return {
            "filters": [
                ["BOM", "name", "in", bom_list]
            ]
        }
        refresh_field("control_bom");
        refresh_field("items");
        console.log("control_bom :" + bom_list);
    });

});

function getControlBOMList(item_code){
var bomList = [];
frappe.call({
        	method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_bom_list_for_so",
            args: {
                "item_code": item_code,
            },
	    async: false,
            callback: function(r) {
                console.log("Length" + r.message.length);
                for (var i = 0; i < r.message.length; i++) {
                    bomList.push(r.message[i].name);
                    console.log("bomList" + bomList);
                }
            }
        });
return bomList;
}

