############################################################################################################

@frappe.whitelist()
def make_draft_mode(name):
	name = json.dumps(name)
	name = ast.literal_eval(name)
	print "raw_material_list------------"+name
	    
	item_list = frappe.db.sql("""select * 
	from `tabPurchase Order` where name=%s""",(name), as_dict=1)
	print "item_list-----------------",item_list
	title = ""
	owner = ""
	taxes_and_charges = ""
	company = ""
	supplier = ""
	schedule_date = ""
	stock_req = ""
	supplier_address =""
	address_display = ""
	busyvoucherno = ""
	item_lines_to_print = 0
	project = ""
	additional_discount_percentage = 0
	remark = ""
	material_req = ""
	for i in range(0, len(item_list)):
		title = item_list[i]["title"]
		owner = item_list[i]["owner"]
		taxes_and_charges = item_list[i]["taxes_and_charges"]
		company = item_list[i]["company"]
		docstatus = item_list[i]["docstatus"]
		supplier = item_list[i]["supplier"]
		schedule_date = item_list[i]["schedule_date"]
		stock_req =  item_list[i]["stock_req"]
		supplier_address = item_list[i]["supplier_address"]
		address_display = item_list[i]["address_display"]
		apply_discount_on = item_list[i]["apply_discount_on"]
		if item_list[i]["busyvoucherno"] != None:
			busyvoucherno =  item_list[i]["busyvoucherno"]
		item_lines_to_print = item_list[i]["item_lines_to_print"]
		additional_discount_percentage = item_list[i]["additional_discount_percentage"]
		project = item_list[i]["project"]
		if item_list[i]["tracking_no"] != None:
			remark = item_list[i]["tracking_no"]
		if item_list[i]["tracking_no"] != None:
			material_req = item_list[i]["material_request"]
	paymennt = frappe.db.sql("""select due_date from `tabPayment Schedule` where parent=%s""",(name), as_dict=1)
	due_date = paymennt[0]["due_date"]
	#print "due_date---------",due_date
	purchase_items = frappe.db.sql("""select * from `tabPurchase Order Item` where parent=%s""",(name), as_dict=1)
	print "purchase_items------------",purchase_items
	purchase_taxes = frappe.db.sql("""select * from `tabPurchase Taxes and Charges` where parent=%s""",(name), as_dict=1)
	
	required_date = datetime.now()
	doctype = "Purchase Order"
	doctype_item = "Purchase Order Item"
	docstatus = 0
	return_doc = ""
	innerJson_transfer = " "
	innertaxesJson_transfer = ""
	OuterJson_Transfer = {
		"doctype": "Purchase Order",
		"title" : title,
		"creation" : required_date,
		"owner" : owner,
		"taxes_and_charges" :taxes_and_charges,
		"company" : company,
		"due_date" : due_date,
		"docstatus" :docstatus,
		"supplier" : supplier,
		"schedule_date" :schedule_date,
		"stock_req" : stock_req,
		"supplier_address" :supplier_address,
		"address_display" :address_display,
		"apply_discount_on" :apply_discount_on,
		"additional_discount_percentage" :additional_discount_percentage,
		"busyvoucherno" : busyvoucherno,
		"item_lines_to_print" : item_lines_to_print,
		"project" : project,
		"tracking_no" : remark,
		"material_request" : material_req,
		"items":[],
		"taxes":[]
		}

	for data in purchase_items:
		item_code = data['item_code']
		received_qty = data['received_qty']
		target_warehouse = data['warehouse']
		last_purchase_price = data["last_purchase_rate"]
		parentfield = data["parentfield"]
		qty_as_per_stock_uom = data['stock_qty']
		rate = data['rate']
		pending_qty = qty_as_per_stock_uom-received_qty
		innerJson_transfer = {
			"item_code": item_code,
			"doctype": "Purchase Order Item",
			"qty": pending_qty,
			"schedule_date": required_date,
			"last_purchase_price" : last_purchase_price,
			"parentfield" : parentfield,
			"warehouse":target_warehouse,
			"qty_as_per_stock_uom":qty_as_per_stock_uom,
			"rate":rate
		}
		#print "innerJson_transfer-----------",innerJson_transfer
		OuterJson_Transfer["items"].append(innerJson_transfer)
	for data in purchase_taxes:
		charge_type = data['charge_type']
		account_head = data['account_head']
		rate = data['rate']
		tax_amount = data["tax_amount"]
		description = data["description"]
		cost_center= data["cost_center"]
		innertaxesJson_transfer = {
			"charge_type" : charge_type,
			"account_head":account_head,
			"rate":rate,
			"tax_amount": tax_amount,
			"description" :description,
			"cost_center" :cost_center
		}
		OuterJson_Transfer["taxes"].append(innertaxesJson_transfer)
	doc = frappe.new_doc("Purchase Order")
	doc.update(OuterJson_Transfer)
	doc.save()
	return_doc = doc.doctype
	if return_doc:
		return return_doc 
	
