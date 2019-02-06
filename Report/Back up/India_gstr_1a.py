# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate
from frappe import _, msgprint
from datetime import datetime
import datetime
from datetime import date, timedelta
import calendar
import dateutil.parser
import time
import math
import json
import ast
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	return IndiaGstr1A(filters).run()
class IndiaGstr1A(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.data = []
		self.columns = []
		self.invoice_id = ""
		self.item_code = ""
		self.tax_data = []
		self.tax_details = []
		self.customer_address = ""
		self.company_address = ""
		if self.filters.fetch_days_data is not None:
			self.filters.from_date = self.filters.temp_from_date
			self.filters.to_date = self.filters.temp_to_date
	def run(self):
		if self.filters.get("type_of_business") == "B2B":
			sales = self.sales_invoice_details()
			columns = self.get_columns_b2b()
			sales_count = self.sales_invoice_counts()
			total_bill_gstin = 0
			total_invoice = 0
			total_taxable_vlaue = 0.0
			total_invoice_value = 0.0
			total_cess_amount = 0.0
			total_cess = 0.0
			invoice_map = {}
			for sale in sales_count:
				amended_from = sale.amended_from
				total_bill_gstin = sale.bill_gstin
				total_invoice = sale.invoice_to
			invoice_map = get_business_type_details(sales)
			for_total = self.sales_invoice_counts()
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					billing_address_gstin = map_data["mapped_items"][map_d]["billing_address_gstin"]
					customer_address = map_data["mapped_items"][map_d]["customer_address"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					reverse_charge = map_data["mapped_items"][map_d]["reverse_charge"]
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					manual_serial_number =map_data["mapped_items"][map_d]["manual_serial_number"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					
					if amended_from is None:
						total_taxable_vlaue = total_taxable_vlaue + tot_net_amount
						total_invoice_value = total_invoice_value +grand_total
						self.data.append([billing_address_gstin,customer_address,invoice_no,manual_serial_number,
							posting_date,grand_total,place_of_supply,reverse_charge,"",
							invoice_type,ecommerce_gstin,rate_of_tax,tot_net_amount,""])
			self.data.append(["","","","","",""])
			self.data.append(["Total","","","","",total_invoice_value,"","","","","","",total_taxable_vlaue,total_cess])
		
		elif self.filters.get("type_of_business") == "B2BA":
			invoice_map = {}
			columns = self.get_columns_b2ba()
			sales_detail = self.sales_invoice_details()
			sales_count = self.sales_invoice_count()
			total_bill_gstin = 0
			total_invoice = 0
			total_taxable_vlaue = 0.0
			total_invoice_value = 0.0
			total_cess_amount = 0.0
			for sale in sales_count:
				amended_from = sale.amended_from
				total_bill_gstin = sale.bill_gstin
				total_invoice = sale.invoice_to
			invoice_map = get_business_type_details(sales_detail)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					billing_address_gstin = map_data["mapped_items"][map_d]["billing_address_gstin"]
					customer_address = map_data["mapped_items"][map_d]["customer_address"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					reverse_charge = map_data["mapped_items"][map_d]["reverse_charge"]
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					modified = map_data["mapped_items"][map_d]["modified"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					manual_serial_number =map_data["mapped_items"][map_d]["manual_serial_number"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					if amended_from is not None:
						total_taxable_vlaue = total_taxable_vlaue + tot_net_amount
						total_invoice_value = total_invoice_value +grand_total
					if amended_from is not None:
						self.data.append([billing_address_gstin,customer_address,amended_from,manual_serial_number,
							posting_date,invoice_no,modified,grand_total,place_of_supply,reverse_charge,"",
							invoice_type,ecommerce_gstin,rate_of_tax,tot_net_amount,""])	
			self.data.append(["","","","","",""])
			self.data.append(["Total","","","","","","",total_invoice_value,"","","","","","",
					total_taxable_vlaue,total_cess_amount])
		
		elif self.filters.get("type_of_business") == "B2CL":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_b2bl()
			sales_b = self.sales_invoice_b2bl()
			invoice_map = get_business_type_details(sales_b)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					amended_from =  map_data["mapped_items"][map_d]["amended_from"]
					self.customer_address = map_data["mapped_items"][map_d]["customer_address"]
					self.company_address = map_data["mapped_items"][map_d]["company_address"]
					grand_total = map_data["mapped_items"][map_d]["grand_total"]
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					if amended_from is None:
						if grand_total > float(b2c_limit) and address_details != gst_state_number:
							grand_total_invoice = grand_total_invoice + invoice_grand_total
							grand_total_taxable = grand_total_taxable + tot_net_amount
							self.data.append([invoice_no,
								posting_date,invoice_grand_total,place_of_supply,""
								,rate_of_tax,tot_net_amount,"",ecommerce_gstin])
			self.data.append(["","","","",""])
			self.data.append(["Total","",grand_total_invoice,"","","",grand_total_taxable,grand_total_cess,""])

		elif self.filters.get("type_of_business") == "B2CLA":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_b2bla()
			sales_b = self.sales_invoice_b2bl()
			invoice_map = get_business_type_details(sales_b)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					modified_date = map_data["mapped_items"][map_d]["modified"]
					self.customer_address = map_data["mapped_items"][map_d]["customer_address"]
					self.company_address = map_data["mapped_items"][map_d]["company_address"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					grand_total = map_data["mapped_items"][map_d]["grand_total"]
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					if amended_from is not None:
						if grand_total > float(b2c_limit) and address_details != gst_state_number:
							grand_total_invoice = grand_total_invoice + invoice_grand_total
							grand_total_taxable = grand_total_taxable + tot_net_amount
							self.data.append([amended_from,posting_date,place_of_supply,invoice_no,
								modified_date,invoice_grand_total,""
								,rate_of_tax,tot_net_amount,"",ecommerce_gstin])

			self.data.append(["","","","",""])
			self.data.append(["Total","","","","",grand_total_invoice,"","",grand_total_taxable,grand_total_cess,""])	
		elif self.filters.get("type_of_business") == "B2CS":
			invoice_map = {}
			grand_total_taxable = 0.0
			grand_invoice_total = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_b2bcs()
			sales_b = self.sales_invoice_b2bl()
			invoice_map = get_unique_state_list(sales_b)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					grand_total = map_data["mapped_items"][map_d]["grand_total"]
					self.customer_address = map_data["mapped_items"][map_d]["customer_address"]
					self.company_address = map_data["mapped_items"][map_d]["company_address"]
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					customer_type = map_data["mapped_items"][map_d]["customer_type"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					grand_invoice_total += invoice_grand_total
					grand_total_taxable = grand_total_taxable + tot_net_amount
					self.data.append([customer_type,place_of_supply,invoice_grand_total,""
					,rate_of_tax,tot_net_amount,"",ecommerce_gstin])
			self.data.append(["","","","",""])
			self.data.append(["Total","",grand_invoice_total,"",grand_total_taxable,grand_total_cess,""])	

		elif self.filters.get("type_of_business") == "B2CSA":
			columns = self.get_columns_b2bcsa()
			invoice_map = {}
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			now = datetime.datetime.now()
			current_year = now.year
			sales_b = self.sales_invoice_b2bl()
			invoice_map = get_unique_state_list_amended(sales_b)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					grand_total = map_data["mapped_items"][map_d]["grand_total"]
					self.customer_address = map_data["mapped_items"][map_d]["customer_address"]
					self.company_address = map_data["mapped_items"][map_d]["company_address"]
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					customer_type = map_data["mapped_items"][map_d]["customer_type"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					rand_total_taxable = grand_total_taxable + tot_net_amount
					self.data.append([str(current_year)+"-"+str(current_year+1),posting_date,
					place_of_supply,customer_type,""
					,rate_of_tax,tot_net_amount,"",ecommerce_gstin])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","","",grand_total_taxable,grand_total_cess,""])	
		elif self.filters.get("type_of_business") == "CDNR":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_cdnr()
			sale_return = self.sales_invoice_cdrn()
			invoice_map = get_business_type_details(sale_return)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					modified_date = map_data["mapped_items"][map_d]["modified"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					port_code = map_data["mapped_items"][map_d]["port_code"]
					shipping_bill_number = map_data["mapped_items"][map_d]["shipping_bill_number"]
					shipping_bill_date = map_data["mapped_items"][map_d]["shipping_bill_date"]
					export_type = map_data["mapped_items"][map_d]["export_type"]
					self.customer_name = map_data["mapped_items"][map_d]["customer_name"]
					is_return = map_data["mapped_items"][map_d]["is_return"]
					self.return_against = map_data["mapped_items"][map_d]["return_against"]
					billing_address_gstin = map_data["mapped_items"][map_d]["billing_address_gstin"]
					customer_address = map_data["mapped_items"][map_d]["customer_address"]
					payment_entry = self.get_Advance_Payment_details()
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					document_type = ""
					if payment_entry is not None:
						for payment in payment_entry:
							payment_number = payment.name
							payment_date = payment.posting_date
							payment_date = payment_date.strftime('%d-%m-%Y')	
					else:
						payment_number = invoice_no
						payment_date = posting_date
					return_sales_details = self.sale_invoice_again_return()
					for return_sale in return_sales_details:
						credit_invoice_id = return_sale.name
						creadit_return_date = return_sale.posting_date
						creadit_return_date = creadit_return_date.strftime('%d-%m-%Y')
						document_type = "C"
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					if amended_from is None:
						grand_total_invoice = grand_total_invoice + invoice_grand_total
						grand_total_taxable = grand_total_taxable + tot_net_amount
						self.data.append([billing_address_gstin,customer_address,payment_number,
							payment_date,credit_invoice_id,creadit_return_date,
							document_type,place_of_supply,invoice_grand_total,""
							,rate_of_tax,tot_net_amount,"",pre_gst])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","","","","",grand_total_invoice,"","",grand_total_taxable,grand_total_cess,""])	
		elif self.filters.get("type_of_business") == "CDNR-A":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_cdnra()
			sale_return = self.sales_invoice_cdrn()
			invoice_map = get_business_type_details(sale_return)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					modified_date = map_data["mapped_items"][map_d]["modified"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					port_code = map_data["mapped_items"][map_d]["port_code"]
					shipping_bill_number = map_data["mapped_items"][map_d]["shipping_bill_number"]
					shipping_bill_date = map_data["mapped_items"][map_d]["shipping_bill_date"]
					export_type = map_data["mapped_items"][map_d]["export_type"]
					self.customer_name = map_data["mapped_items"][map_d]["customer_name"]
					is_return = map_data["mapped_items"][map_d]["is_return"]
					self.return_against = map_data["mapped_items"][map_d]["return_against"]
					billing_address_gstin = map_data["mapped_items"][map_d]["billing_address_gstin"]
					customer_address = map_data["mapped_items"][map_d]["customer_address"]
					payment_entry = self.get_Advance_Payment_details()
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					document_type = ""
					if payment_entry is not None:
						for payment in payment_entry:
							payment_number = payment.name
							payment_date = payment.posting_date
							payment_date = payment_date.strftime('%d-%m-%Y')
					else:
						
						payment_number = invoice_no
						payment_date = posting_date
					return_sales_details = self.sale_invoice_again_return()
					for return_sale in return_sales_details:
						credit_invoice_id = return_sale.name
						creadit_return_date = return_sale.posting_date
						creadit_return_date = creadit_return_date.strftime('%d-%m-%Y')
						document_type = "C"
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					if amended_from is not None:
						grand_total_invoice = grand_total_invoice + invoice_grand_total
						grand_total_taxable = grand_total_taxable + tot_net_amount
						self.data.append([billing_address_gstin,customer_address,amended_from,
							modified_date,payment_number,
							payment_date,credit_invoice_id,creadit_return_date,
							document_type,place_of_supply,invoice_grand_total,""
							,rate_of_tax,tot_net_amount,"",pre_gst])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","","","","","","",grand_total_invoice,"","",
					grand_total_taxable,grand_total_cess,""])	
			
		elif self.filters.get("type_of_business") == "EXPORT":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_exp()
			sales_b = self.sales_invoice_exp()
			invoice_map = get_business_type_details(sales_b)
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					modified_date = map_data["mapped_items"][map_d]["modified"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					port_code = map_data["mapped_items"][map_d]["port_code"]
					shipping_bill_number = map_data["mapped_items"][map_d]["shipping_bill_number"]
					shipping_bill_date = map_data["mapped_items"][map_d]["shipping_bill_date"]
					export_type = map_data["mapped_items"][map_d]["export_type"]
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					grand_total_invoice = grand_total_invoice + invoice_grand_total
					grand_total_taxable = grand_total_taxable + tot_net_amount
					self.data.append([export_type,invoice_no,posting_date,invoice_grand_total,
						port_code,shipping_bill_number,shipping_bill_date,""
						,rate_of_tax,tot_net_amount,""])
			self.data.append(["","","","",""])
			self.data.append(["Total","","",grand_total_invoice,"","","","","",grand_total_taxable,grand_total_cess])

		elif self.filters.get("type_of_business") == "EXEMP":
			invoice_map = {}
			grand_total_nill = 0.0
			grand_total_non = 0.0
			grand_total_exmp = 0.0
			columns = self.get_columns_exemp()
			expemted_items_details = self.sales_invoice_item_expem()
			invoice_map = sales_exepted_nill(expemted_items_details)
			for exem in invoice_map:
				exempt_details = invoice_map[exem]
				item_name = exempt_details.item_name
				non_net_amount = exempt_details.non_net_amount
				exempt_net_amount = exempt_details.exempt_net_amount
				nill_net_amount = exempt_details.nill_net_amount
				india_gst_item_status = exempt_details.india_gst_item_status
				grand_total_nill = grand_total_nill + nill_net_amount
				grand_total_non = grand_total_non + non_net_amount
				grand_total_exmp = grand_total_exmp + exempt_net_amount
				self.data.append([item_name,nill_net_amount,exempt_net_amount,non_net_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total",grand_total_nill,grand_total_exmp,grand_total_non])
		elif self.filters.get("type_of_business") == "HSN":
			grand_total_value = 0.0
			grand_total_net_amount = 0.0
			grand_total_central = 0.0
			grand_total_integrated = 0.0
			grand_total_state = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_hsn()
			hsn_code_uqc_details = self.hsn_code_uqc_code()
			hsn_uqc_unique = get_hsn_uqc_list(hsn_code_uqc_details)
			description = ""
			for unique_hsn in hsn_uqc_unique:
				hsn_detials = hsn_uqc_unique[unique_hsn]
				self.gst_hsn_code = hsn_detials.gst_hsn_code
				description_of_hsn = self.gst_hsn_doc()
				for desc in description_of_hsn:
					if self.gst_hsn_code == desc.name:
						description =  desc.description
				self.uom = hsn_detials.uom
				uqc_details = self.gst_uqc_doc()
				if uqc_details is not None:
					for uqc in uqc_details:
						uqc_code = uqc.uqc_code
						quantity = uqc.quantity
					uqc_name = uqc_code+"-"+quantity
				else:
					uqc_name = "OTH-OTHER"
				net_amount = hsn_detials.net_amount
				state_tax_amount = hsn_detials.state_tax_amount
				integrated_tax_amount = hsn_detials.integrated_tax_amount
				total_value_tax = net_amount*hsn_detials.tax_rate/100
				total_value = total_value_tax+net_amount
				grand_total_value = grand_total_value + total_value
				grand_total_net_amount = grand_total_net_amount + net_amount
				qty = hsn_detials.qty
				central_tax_amount = hsn_detials.central_tax_amount
				grand_total_central = grand_total_central + central_tax_amount
				grand_total_integrated = grand_total_integrated + integrated_tax_amount
				grand_total_state = grand_total_state + state_tax_amount
				self.data.append([self.gst_hsn_code,description,uqc_name,qty,total_value,
					net_amount,integrated_tax_amount,central_tax_amount,state_tax_amount])
			self.data.append(["","","","",""])
			
			self.data.append(["Total","","","",grand_total_value,grand_total_net_amount,grand_total_integrated,grand_total_central,
						grand_total_state,grand_total_cess])

		elif self.filters.get("type_of_business") == "AT":
			columns = self.get_columns_at()
			entry_sales = self.payment_and_sales()
			unique_payment = unique_payment_entry(entry_sales)
			cess_amount = 0.0
			Total_gross_amount = 0.0
			total_rate_amount = 0.0
			total_advance_paid = 0.0
			for entry in unique_payment:
				entry_detials = unique_payment[entry]
				for entry_d in range(0,len(entry_detials["mapped_items"])):
					invoice_no = entry_detials["mapped_items"][entry_d]["invoice_id"]
					place_of_supply = entry_detials["mapped_items"][entry_d]["place_of_supply"]
					payment_total_amount = entry_detials["mapped_items"][entry_d]["payment_total_amount"]
					advance_paid = entry_detials["mapped_items"][entry_d]["advance_paid"]
					rate_taxe_d =  entry_detials["mapped_items"][entry_d]["tax_rate"]
					additional_discount =  entry_detials["mapped_items"][entry_d]["additional_discount_percentage"]
					net_amount =  entry_detials["mapped_items"][entry_d]["net_amount"]
					grand_total =  entry_detials["mapped_items"][entry_d]["grand_total"]
					igst_tax =  entry_detials["mapped_items"][entry_d]["igst_rate"]
					sgst_tax =  entry_detials["mapped_items"][entry_d]["sgst_rate"]
					cgst_tax =  entry_detials["mapped_items"][entry_d]["cgst_rate"]
					igst_net = net_amount * igst_tax / 100
					sgst_net = net_amount * sgst_tax / 100
					cgst_net = net_amount * cgst_tax / 100
					total_rate = net_amount *(100-additional_discount)/100 * payment_total_amount/grand_total * rate_taxe_d
					total_rate_amount = total_rate_amount + total_rate
					Total_gross_amount = Total_gross_amount + payment_total_amount
					total_advance_paid = total_advance_paid + advance_paid
					self.data.append([invoice_no,place_of_supply,advance_paid,"",total_rate,
					payment_total_amount,cess_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","",total_advance_paid,"",total_rate_amount,Total_gross_amount,cess_amount])
		elif self.filters.get("type_of_business") == "ATA":
			columns = self.get_columns_ata()
			entry_sales_amended = self.payment_and_sales_amended()
			unique_payment_amended = unique_payment_entry_can_amen(entry_sales_amended)
			now = datetime.datetime.now()
			current_year = now.year
			cess_amount = 0.0
			Total_gross_amount = 0.0
			total_rate_amount = 0.0
			total_advance_paid = 0.0
			for entry in unique_payment_amended:
				entry_detials = unique_payment_amended[entry]
				for entry_d in range(0,len(entry_detials["mapped_items"])):
					invoice_no = entry_detials["mapped_items"][entry_d]["invoice_id"]
					place_of_supply = entry_detials["mapped_items"][entry_d]["place_of_supply"]
					payment_total_amount = entry_detials["mapped_items"][entry_d]["payment_total_amount"]
					advance_paid = entry_detials["mapped_items"][entry_d]["advance_paid"]
					rate_taxe_d =  entry_detials["mapped_items"][entry_d]["tax_rate"]
					amended_from = entry_detials["mapped_items"][entry_d]["sales_amended_from"]
					creation_date = entry_detials["mapped_items"][entry_d]["creation_date"]
					additional_discount =  entry_detials["mapped_items"][entry_d]["additional_discount_percentage"]
					net_amount =  entry_detials["mapped_items"][entry_d]["net_amount"]
					grand_total =  entry_detials["mapped_items"][entry_d]["grand_total"]
					total_rate = net_amount *(100-additional_discount)/100 * payment_total_amount/grand_total * rate_taxe_d
					total_rate = round(total_rate)
					total_rate_amount = total_rate_amount + total_rate
					Total_gross_amount = Total_gross_amount + payment_total_amount
					total_advance_paid = total_advance_paid + advance_paid
					self.data.append([invoice_no,str(current_year)+ " - "+str(current_year+1),
					creation_date, place_of_supply,advance_paid,"",total_rate,payment_total_amount,cess_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","",total_advance_paid,"",total_rate_amount,Total_gross_amount,cess_amount])
		elif self.filters.get("type_of_business") == "ATADJ":
			columns = self.get_columns_atadj()
			atadj_sales = self.sales_order_sales_invoice()
			atadj_sales_unique = unique_order_invoice(atadj_sales)
			for entry in atadj_sales_unique:
				entry_detials = atadj_sales_unique[entry]
				for entry_d in range(0,len(entry_detials["mapped_items"])):
					invoice_id = entry_detials["mapped_items"][entry_d]["invoice_id"]
					place_of_supply = entry_detials["mapped_items"][entry_d]["place_of_supply"]
					payment_total_amount = entry_detials["mapped_items"][entry_d]["payment_total_amount"]
					allocated_amount = entry_detials["mapped_items"][entry_d]["allocated_amount"]
					rate_taxe_d =  entry_detials["mapped_items"][entry_d]["tax_rate"]
					gstin = entry_detials["mapped_items"][entry_d]["gstin"]
					creation_date = entry_detials["mapped_items"][entry_d]["posting_date"]
					payment_id =  entry_detials["mapped_items"][entry_d]["payment_id"]
					net_amount =  entry_detials["mapped_items"][entry_d]["net_amount"]
					customer_address =  entry_detials["mapped_items"][entry_d]["customer_address"]
					igst_amount = net_amount * tax_rate/100
					

		elif self.filters.get("type_of_business") == "ATADJA":
			columns = self.get_columns_ata()
		return columns, self.data
		
	def get_columns_b2b(self):
		return [
			_("GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Manual Serial Number") + "::150",
			_("Invoice date") + "::150",
			_("Invoice Value") + "::180",
			_("Place Of Supply") + "::150",
			_("Reverse Charge") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Invoice Type") + "::150",
			_("E-Commerce GSTIN") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::160", 
			_("Cess Amount") + "::120"
		
		]
	def get_columns_b2ba(self):
		return [
			_("GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Original Invoice Number") + ":Link/Sales Invoice:150",
			_("Manual Serial Number") + "::150",
			_("Original Invoice date") + "::150",
			_("Revised Invoice Number") + ":Link/Sales Invoice:150",
			_("Revised Invoice date") + "::150",
			_("Invoice Value") + "::180",
			_("Place Of Supply") + "::150",
			_("Reverse Charge") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Invoice Type") + "::150",
			_("E-Commerce GSTIN") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::160", 
			_("Cess Amount") + "::120"
		
		]
	def get_columns_b2bl(self):
		return [
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Invoice date") + "::150",
			_("Invoice Value") + "::150",
			_("Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::180",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]
	def get_columns_b2bla(self):
		return [
			_("Original Invoice Number") + ":Link/Sales Invoice:150",
			_("Original Invoice date") + "::150",
			_("Original Place Of Supply") + "::150",
			_("Revised Invoice Number") + ":Link/Sales Invoice:150",
			_("Revised Invoice date") + "::150",
			_("Invoice Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::180",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]
	def get_columns_b2bcs(self):
		return [
			_("Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]
	def get_columns_b2bcsa(self):
		return [
			_("Financial Year") + "::150",
			_("Original Month") + "::150",
			_("Type ") + "::150",
			_("Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]
	def get_columns_exp(self):
		return [
			_(" Export Type") + "::150",
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Invoice date ") + "::150",
			_("Invoice Value ") + "::150",
			_("Port Code") + "::150",
			_("Shipping Bill Number") + "::150",
			_("Shipping Bill Date") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150"
			
		
		]
	def get_columns_cdnr(self):
		return [
			_(" GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Invoice/Advance Receipt Number") + "::150",
			_("Invoice/Advance Receipt date") + "::150",
			_("Note/Refund Voucher Number ") + ":Link/Sales Invoice:150",
			_("Note/Refund Voucher date") + "::150",
			_("Document Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Note/Refund Voucher Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("Pre GST") + "::150"
		
		
		]
	def get_columns_cdnra(self):
		return [
			_(" GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Original Note/Refund Voucher Number ") + ":Link/Sales Invoice:150",
			_("Original Note/Refund Voucher date") + "::150",
			_("Original Invoice/Advance Receipt Number") + "::150",
			_("Original Invoice/Advance Receipt date") + "::150",
			_("Revised Note/Refund Voucher Number ") + ":Link/Sales Invoice:150",
			_("Revised Note/Refund Voucher date") + "::150",
			_("Document Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Note/Refund Voucher Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("Pre GST") + "::150"
		
		
		]
	def get_columns_exemp(self):
		return [
			_("Description") + ":Link/Item:250",
			_("Nil Rated Supplies") + "::150",
			_("Exempted(other than nil rated/non GST supply)") + "::250",
			_("Non-GST Supplies") + "::150"
		]
	def get_columns_hsn(self):
		return [
			_("HSN") + "::150",
			_("Description") + "::250",
			_("UQC ") + "::150",
			_("Total Quantity") + "::150",
			_("Total Value") + "::150",
			_("Taxable Value") + "::150",
			_("Integrated Tax Amount") + "::150",
			_("Central Tax Amount") + "::150",
			_("State/UT Tax Amount") + "::150",
			_("Cess Amount") + "::150"
			
		]
	def get_columns_at(self):
		return [
			_("Date") + "::150",
			_("Voucher No.") + ":Link/Payment Entry:150",
			_("GSTIN No.") + "::250",
			_("Party ") + "::150",
			_("Place of Supply") + "::150",
			_("Reference No.") + ":Link/Sales Order:150",
			_("Rate") + "::150",
			_("Advance Received") + "::150",
			_("Advance Adjusted") + "::250",
			_("Advance Pending ") + "::150",
			_("Taxable Amount") + "::150",
			_("IGST Amt") + "::150",
			_("CGST Amt") + "::150",
			_("SGST Amt") + "::150"
		
		]
	def get_columns_ata(self):
		return [
			_("Sales Order Number") + ":Link/Sales Order:150",
			_("Financial Year") + "::150",
			_("Original Month") + "::250",
			_("Original Place Of Supply") + "::150",
			_("Invoice Value") + "::150",
			_("Applicable % of Tax Rate") + "::250",
			_("Rate ") + "::150",
			_("Gross Advance Received") + "::150",
			_("Cess Amount") + "::150"
			
		]
	def get_columns_atadj(self):
		return [
			_("Date") + "::150",
			_("Voucher No.") + ":Link/Payment Entry:150",
			_("GSTIN No.") + "::250",
			_("Party ") + "::150",
			_("Place of Supply") + "::150",
			_("Reference No.") + ":Link/Sales Order:150",
			_("Rate") + "::150",
			_("Advance Received") + "::150",
			_("Advance Pending ") + "::150",
			_("Advance Adjusted") + "::150",
			_("IGST Amt") + "::150",
			_("CGST Amt") + "::150",
			_("SGST Amt") + "::150"
		
		]

	
	def sales_invoice_details(self):
		sales_invoice = frappe.db.sql("""select si.billing_address_gstin,si.customer_address,si.name,si.customer_name,
					si.posting_date,si.place_of_supply,si.is_return,si.return_against,si.manual_serial_number,
					si.reverse_charge,si.invoice_type,si.ecommerce_gstin,si.posting_date,si.amended_from,
					si.modified,si.grand_total,si.company_address,c.customer_type
					from `tabSales Invoice` si, `tabCustomer` c
					where si.posting_date >= %s AND si.posting_date <= %s AND si.invoice_type = "Regular"
			 		AND c.customer_type = "Company" AND si.customer_name = c.customer_name 
					AND si.docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)

		return sales_invoice

	def sales_invoice_b2bl(self):
		sales_invoice_b = frappe.db.sql("""select si.billing_address_gstin,si.customer_address,si.name,si.customer_name,
					si.posting_date,si.place_of_supply,si.is_return,si.return_against,si.manual_serial_number,
					si.reverse_charge,si.invoice_type,si.ecommerce_gstin,si.posting_date,si.amended_from,
					si.modified,si.grand_total,si.company_address,c.customer_type
					from `tabSales Invoice` si, `tabCustomer` c
					where si.posting_date >= %s AND si.posting_date <= %s AND si.invoice_type = "Regular"
			 		AND c.customer_type = "Individual" AND si.customer_name = c.customer_name AND si.is_return = 0
					AND si.docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)
		return sales_invoice_b
	def sales_invoice_exp(self):
		sales_invoice_ex = frappe.db.sql("""select billing_address_gstin,customer_address,name,customer_name
					posting_date,place_of_supply,port_code,shipping_bill_number,shipping_bill_date,
					export_type,reverse_charge,invoice_type,ecommerce_gstin,posting_date,amended_from,
					modified,grand_total,company_address,is_return,return_against
					from `tabSales Invoice`
					where posting_date >= %s AND posting_date <= %s AND invoice_type = "Export"
					AND docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)
		return sales_invoice_ex

	def sales_invoice_cdrn(self):
		sales_invoice_cd = frappe.db.sql("""select billing_address_gstin,customer_address,name,customer_name,
					posting_date,place_of_supply,port_code,shipping_bill_number,shipping_bill_date,
					export_type,reverse_charge,invoice_type,ecommerce_gstin,posting_date,amended_from,
					modified,grand_total,company_address,is_return,return_against
					from `tabSales Invoice`
					where posting_date >= %s AND posting_date <= %s AND is_return = 1
					AND docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)
		return sales_invoice_cd

	def sales_invoice_item_expem(self):
		exempt_item = frappe.db.sql(""" select sii.name,si.parent,si.item_name,si.item_code,si.net_amount,i.india_gst_item_status 
					from `tabSales Invoice` sii, `tabSales Invoice Item` si , `tabItem` i 
					where sii.name = si.parent AND si.item_code = i.name 
					AND i.india_gst_item_status IN ("Nil Rated Item","Exempt Item","Non-GST Item") 
					AND sii.posting_date >= %s AND sii.posting_date <=%s
				 	AND sii.docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)
		
		return exempt_item
	def hsn_code_uqc_code(self):
		hsn_uqc = frappe.db.sql(""" select s.name,si.item_name,si.item_code,si.net_amount,si.uom,si.qty,si.gst_hsn_code
					from `tabSales Invoice` s, `tabSales Invoice Item` si
					where s.name = si.parent AND s.posting_date >= %s AND s.posting_date <= %s""",
					(self.filters.from_date,self.filters.to_date), as_dict = 1)
		return hsn_uqc

	def sale_invoice_again_return(self):
		return_sales = frappe.db.sql("""select name,posting_date from `tabSales Invoice` where name = %s""",(self.return_against), as_dict = 1)
		return return_sales

	def sales_invoice_counts(self):
		sales_in = frappe.db.sql("""select count(billing_address_gstin) as bill_gstin, count(name) as invoice_to,amended_from 
					from `tabSales Invoice` 
					where posting_date >= %s AND posting_date <= %s AND amended_from is NULL AND docstatus = 1
					
 					AND customer_name IN (select customer_name from `tabCustomer` where customer_type = "Company")""",(self.filters.from_date,self.filters.to_date), as_dict = 1)

		return sales_in
	def sales_invoice_count(self):
		sales_in_c = frappe.db.sql("""select count(billing_address_gstin) as bill_gstin, count(name) as invoice_to 
					from `tabSales Invoice` 
					where posting_date >= %s AND posting_date <= %s  AND docstatus = 1
					AND NOT amended_from = "NULL"
 					AND customer_name IN (select customer_name from `tabCustomer` where customer_type = "Company")""",(self.filters.from_date,self.filters.to_date), as_dict = 1)

		return sales_in_c
	
	def gst_hsn_doc(self):
		hsn_doc = frappe.db.sql("""select name,description from `tabGST HSN Code` where  name = %s""",(self.gst_hsn_code), as_dict = 1)
		return hsn_doc

	def gst_uqc_doc(self):
		uqc_doc = frappe.db.sql("""select uqc_code,quantity from `tabUQC Item` where erpnext_uom_link = %s""",(self.uom), as_dict = 1)
		return uqc_doc

	def get_Advance_Payment_details(self):
		if self.customer_name:
			payment_data = frappe.get_list("Payment Entry", {"party_name":self.customer_name},
			["paid_amount","name","creation","party_name","posting_date"])
			return payment_data
		else:
			return None

	def get_contact_details(self):
		
		gst_state_number =""
		if self.customer_address:
			gst_state_number = frappe.db.get_value('Address',self.customer_address,
			['gst_state_number'])
		return gst_state_number

	def address_gst_number(self):
		company_gst_state_number = ""
		address_detail = frappe.get_list("Address",["address_type","gst_state_number","name"])
		for itrate_address in address_detail:
			name = itrate_address.name
			if name == self.company_address:
				company_gst_state_number  = itrate_address.gst_state_number
		return company_gst_state_number

	def payment_and_sales(self):
		temp_from_time = " 00:00:00"
		temp_to_time = " 23:59:59"
		tmp_from_date = str(self.filters.from_date)+ (temp_from_time)
		tmp_to_date = str(self.filters.to_date)+(temp_to_time)
		payment_sale = frappe.db.sql(""" select so.name,so.advance_paid,pr.parent,pr.allocated_amount,ad.state,so.amended_from
						,soi.item_code,soi.net_amount,so.additional_discount_percentage,so.grand_total
						from `tabSales Order` so, `tabPayment Entry Reference` pr, `tabAddress` ad,
						`tabPayment Entry` pe, `tabSales Order Item` soi
						where so.name = pr.reference_name AND so.customer_address = ad.name AND 
						pe.name = pr.parent AND pe.amended_from is NULL AND so.name = soi.parent
						AND so.creation >= %s AND so.creation <= %s AND so.amended_from is NULL AND so.docstatus = 1
						""",(tmp_from_date,tmp_to_date), as_dict = 1)
		
		return payment_sale

	def payment_and_sales_amended(self):
		temp_from_time = " 00:00:00"
		temp_to_time = " 23:59:59"
		tmp_from_date = str(self.filters.from_date)+ (temp_from_time)
		tmp_to_date = str(self.filters.to_date)+(temp_to_time)
		payment_sale_amend = frappe.db.sql(""" select pe.name,per.parent,per.allocated_amount,so.name,so.amended_from
						as sales_amended,pe.amended_from as payment_amended,so.advance_paid,
						so.docstatus as sales_doc,pe.docstatus as payment_doc,pe.creation,
						soi.item_code,soi.net_amount,so.additional_discount_percentage,so.grand_total,ad.state
						from `tabPayment Entry` pe , `tabPayment Entry Reference` per, `tabSales Order` so 
						, `tabSales Order Item` soi , `tabAddress` ad
						where pe.name = per.parent AND so.name = per.reference_name AND so.name = soi.parent AND
						 so.customer_address = ad.name AND
						so.docstatus IN (1,2) AND pe.docstatus IN (1,2) AND so.creation >= %s AND so.creation <= %s
						""",(tmp_from_date,tmp_to_date), as_dict = 1)
		return payment_sale_amend
	def sales_order_sales_invoice(self):
		temp_from_time = " 00:00:00"
		temp_to_time = " 23:59:59"
		tmp_from_date = str(self.filters.from_date)+ (temp_from_time)
		tmp_to_date = str(self.filters.to_date)+(temp_to_time)
		order_invoice = frappe.db.sql("""select so.name as sales_order,so.grand_total as order_total,ad.state,ad.gstin
						,si.name as sales_invoice,si.grand_total as invoice_total,so.creation,so.customer_address,
						sii.item_code,sii.net_amount,pr.parent,pr.allocated_amount,pr.reference_name,
						si.amended_from as sales_amended,pe.amended_from as payment_amended
						from `tabSales Order` so, `tabSales Invoice` si, `tabSales Invoice Item` sii, 
						`tabPayment Entry Reference` pr, `tabPayment Entry` pe, `tabAddress` ad
						where so.name = si.sales_order AND si.name = pr.reference_name AND sii.parent = si.name 
						AND so.creation >= %s AND so.creation <= %s AND ad.name = so.customer_address AND
						pr.parent = pe.name AND pe.amended_from is NULL AND so.amended_from is NULL"""
						,(tmp_from_date,tmp_to_date), as_dict = 1)
		return order_invoice

def sales_account_tax(invoice_id):
	if invoice_id:
		account_tax = frappe.db.sql("""select account_head,rate,item_wise_tax_detail 
							from `tabSales Taxes and Charges`
							where parent = %s """
							,(invoice_id),as_dict =1)
	return account_tax

def sales_item_details(invoice_id):
	if invoice_id:
		invoice_item = frappe.db.sql("""select item_code,net_amount,qty,rate 
						from `tabSales Invoice Item` 
						where parent = %s"""
						,(invoice_id), as_dict = 1)
			
	return invoice_item

def sales_item_details_order(invoice_id):
	if invoice_id:
		invoice_item = frappe.db.sql("""select item_code,net_amount,qty,rate 
						from `tabSales Order Item` 
						where parent = %s"""
						,(invoice_id), as_dict = 1)
			
	return invoice_item

def sales_tax(item_code,invoice_id):
	items = frappe.db.sql("""select si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type 
					from `tabSales Invoice Item` si, `tabItem Tax` it 
					where si.item_code = '"""+item_code+"""' AND 
					si.parent = '"""+invoice_id+"""' AND it.parent = si.item_code 
					AND it.tax_type LIKE ('%IGST%') """, as_dict = 1)
	return items
def sales_tax_so(item_code,invoice_id):
	if item_code:
		items = frappe.db.sql("""select si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type 
					from `tabSales Order Item` si, `tabItem Tax` it 
					where si.item_code = %s AND si.parent = %s AND it.parent = si.item_code 
					""",(item_code,invoice_id), as_dict = 1)
	return items

def sales_tax_hsn(item_code,invoice_id):
	
	if item_code:
		items_hsn = frappe.db.sql("""select si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type 
					from `tabSales Invoice Item` si, `tabItem Tax` it
					where si.item_code = %s AND si.parent = %s AND it.parent = si.item_code 
					""",(item_code,invoice_id), as_dict = 1)
	return items_hsn

def sales_taxe_rate_details(invoice_id):
	taxe_rate_data = frappe.db.sql("""select parent,rate,account_head 
					from `tabSales Taxes and Charges` 
					where  parent = %s""",(invoice_id), as_dict = 1)
	return taxe_rate_data

def sales_order_details(invoice_id):
	sales_order = frappe.db.sql("""select so.name,ad.state from `tabSales Order` so , `tabAddress` ad
					 where so.customer_address = ad.name AND so.name = %s""",(invoice_id), as_dict = 1)
	return sales_order
def get_contact_details(customer_address):
	gst_state_number =""
	if customer_address:
		gst_state_number = frappe.db.get_value('Address',customer_address,
		['gst_state_number'])
	return gst_state_number

def address_gst_number(company_address):
	company_gst_state_number = ""
	address_detail = frappe.get_list("Address",["address_type","gst_state_number","name"])
	for itrate_address in address_detail:
		name = itrate_address.name
		if name == company_address:
			company_gst_state_number  = itrate_address.gst_state_number
	return company_gst_state_number

def get_business_type_details(sales):
	invoice_map = {}
	for seles_data in sales:
		amended_from = seles_data.amended_from
		invoice_id = seles_data.name
		billing_address_gstin = seles_data.billing_address_gstin
		customer_address = seles_data.customer_address
		place_of_supply = seles_data.place_of_supply
		reverse_charge = seles_data.reverse_charge
		invoice_type = seles_data.invoice_type
		customer_name = seles_data.customer_name
		ecommerce_gstin = seles_data.ecommerce_gstin
		posting_date = seles_data.posting_date
		posting_date = posting_date.strftime('%d-%m-%Y')
		grand_total = seles_data.grand_total
		company_address = seles_data.company_address
		customer_type = seles_data.customer_type
		port_code = seles_data.port_code
		shipping_bill_number = seles_data.shipping_bill_number
		shipping_bill_date = seles_data.shipping_bill_date
		if shipping_bill_date is not None:
			shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
		export_type = seles_data.export_type
		is_return = seles_data.is_return
		return_against = seles_data.return_against
		manual_serial_number = seles_data.manual_serial_number
		account_head = ""
		modified = seles_data.modified
		modified = modified.date()
		modified = modified.strftime('%d-%m-%Y')
		amended_from = seles_data.amended_from
		sales_item = sales_item_details(invoice_id)
		for item in sales_item:
			item_code = item.item_code
			item_net_amount = item.net_amount
			tax_data = sales_tax(item_code,invoice_id)
			print "tax_data--------------",tax_data
			sales_invoice_tax_data = sales_account_tax(invoice_id)
			tax_rate_list = []
			if len(tax_data) != 0:
				for data in tax_data:
					tax_rate = data.tax_rate
					print "tax_rate------------",tax_rate
					net_amount = data.net_amount
					key = invoice_id
					if key in invoice_map:
				    		item_entry = invoice_map[key]
						mapped_items_list = item_entry["mapped_items"]
						new_list = []
						for mapped_items in mapped_items_list:
					    		tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if tax_rate in data_rate:
						    	for items in mapped_items_list:
						   		 if float(tax_rate) == float(items["tax_rate"]):
						    			qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (net_amount)
						else :
							new_list.append({
									"tax_rate": tax_rate,
									"net_amount": net_amount,
									"invoice_id": key,
									"billing_address_gstin": billing_address_gstin,
									"customer_address": customer_address,
									"place_of_supply": place_of_supply,
									"reverse_charge": reverse_charge,
									"invoice_type": invoice_type,
									"posting_date": posting_date,
									"ecommerce_gstin": ecommerce_gstin,
									"modified":modified,
									"amended_from":amended_from,
									"grand_total":grand_total,
									"company_address":company_address,
									"customer_type":customer_type,
									"port_code":port_code,
									"shipping_bill_number":shipping_bill_number,
									"shipping_bill_date":shipping_bill_date,
									"export_type":export_type,
									"customer_name":customer_name,
									"is_return":is_return,
									"return_against":return_against,
									"manual_serial_number":manual_serial_number
								    })
							item_entry["mapped_items"] = mapped_items_list + new_list
					else :
						item_list = []
						item_list.append({
							"tax_rate": tax_rate,
							"net_amount": net_amount,
							"invoice_id": key,
							"billing_address_gstin": billing_address_gstin,
							"customer_address": customer_address,
							"place_of_supply": place_of_supply,
							"reverse_charge": reverse_charge,
							"invoice_type": invoice_type,
				    			"posting_date": posting_date,
							"ecommerce_gstin": ecommerce_gstin,
							"modified":modified,
							"amended_from":amended_from,
							"grand_total":grand_total,
							"company_address":company_address,
							"customer_type":customer_type,
							"port_code":port_code,
							"shipping_bill_number":shipping_bill_number,
							"shipping_bill_date":shipping_bill_date,
							"export_type":export_type,
							"customer_name":customer_name,
							"is_return":is_return,
							"return_against":return_against,
							"manual_serial_number":manual_serial_number
						})
						invoice_map[key] = frappe._dict({
						    "mapped_items": item_list
						})
			else:
				sales_tax_rate = 0
				total_amount = 0.0
				if len(sales_invoice_tax_data) != 0:
					for invoice_tax_data in sales_invoice_tax_data:
						account_head = invoice_tax_data.account_head
						item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
						converted = ast.literal_eval(item_wise_tax_detail)
						if item_code in converted:
							details = converted[item_code]
							if "SGST" in account_head or "CGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
							
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
					if invoice_id in invoice_map:
						item_entry = invoice_map[invoice_id]
						mapped_items_list = item_entry["mapped_items"]
						for mapped_items in mapped_items_list:
							tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if sales_tax_rate in data_rate:
							for items in mapped_items_list:
								if float(sales_tax_rate) == float(items["tax_rate"]):
									qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (item_net_amount)
						else:
							mapped_items_list.append({
										"tax_rate": sales_tax_rate, 
								  		"net_amount": item_net_amount,
								                "invoice_id": invoice_id,
										"billing_address_gstin":billing_address_gstin,
										"customer_address":customer_address,
										"place_of_supply":place_of_supply,
										"reverse_charge":reverse_charge,
										"invoice_type":invoice_type,
										"posting_date":posting_date,
										"ecommerce_gstin":ecommerce_gstin,
										"modified":modified,
										"amended_from":amended_from,
										"grand_total":grand_total,
										"company_address":company_address,
										"customer_type":customer_type,
										"port_code":port_code,
										"shipping_bill_number":shipping_bill_number,
										"shipping_bill_date":shipping_bill_date,
										"export_type":export_type,
										"customer_name":customer_name,
										"is_return":is_return,
										"return_against":return_against,
										"manual_serial_number":manual_serial_number
										})
							item_entry["mapped_items"] = mapped_items_list
					else:
						item_list = []
						item_list.append({
								"tax_rate": sales_tax_rate, 
								"net_amount": item_net_amount,
								"invoice_id": invoice_id,
								"billing_address_gstin":billing_address_gstin,
								"customer_address":customer_address,
								"place_of_supply":place_of_supply,
								"reverse_charge":reverse_charge,
								"invoice_type":invoice_type,
								"posting_date":posting_date,
								"ecommerce_gstin":ecommerce_gstin,
								"modified":modified,
								"amended_from":amended_from,
								"grand_total":grand_total,
								"company_address":company_address,
								"customer_type":customer_type,
								"port_code":port_code,
								"shipping_bill_number":shipping_bill_number,
								"shipping_bill_date":shipping_bill_date,
								"export_type":export_type,
								"customer_name":customer_name,
								"is_return":is_return,
								"return_against":return_against,
								"manual_serial_number":manual_serial_number
								})
						invoice_map[invoice_id] = frappe._dict({"mapped_items": item_list})
	return invoice_map
def get_unique_state_list(sales):
	invoice_map = {}
	for seles_data in sales:
		amended_from = seles_data.amended_from
		if amended_from is None:
			invoice_id = seles_data.name
			billing_address_gstin = seles_data.billing_address_gstin
			customer_address = seles_data.customer_address
			place_of_supply = seles_data.place_of_supply
			reverse_charge = seles_data.reverse_charge
			invoice_type = seles_data.invoice_type
			customer_name = seles_data.customer_name
			ecommerce_gstin = seles_data.ecommerce_gstin
			posting_date = seles_data.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			grand_total = seles_data.grand_total
			company_address = seles_data.company_address
			customer_type = seles_data.customer_type
			port_code = seles_data.port_code
			shipping_bill_number = seles_data.shipping_bill_number
			shipping_bill_date = seles_data.shipping_bill_date
			if shipping_bill_date is not None:
				shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
			export_type = seles_data.export_type
			is_return = seles_data.is_return
			return_against = seles_data.return_against
			account_head = ""
			modified = seles_data.modified
			modified = modified.date()
			modified = modified.strftime('%d-%m-%Y')
			amended_from = seles_data.amended_from
			b2c_limit = frappe.db.get_value('GST Settings',customer_address,'b2c_limit')
			gst_state_number = get_contact_details(customer_address)
			address_details = address_gst_number(company_address)
			if (grand_total <= float(b2c_limit) and address_details != gst_state_number)\
			or (grand_total <= float(b2c_limit) and address_details == gst_state_number) \
			or (grand_total >= float(b2c_limit) and address_details == gst_state_number): 
				sales_item = sales_item_details(invoice_id)
				for item in sales_item:
					item_code = item.item_code
					item_net_amount = item.net_amount
					tax_data = sales_tax(item_code,invoice_id)
					sales_invoice_tax_data = sales_account_tax(invoice_id)
					tax_rate_list = []
					if len(tax_data) != 0:
						for data in tax_data:
							tax_rate = data.tax_rate
							net_amount = data.net_amount
							key = place_of_supply
							if key in invoice_map:
						    		item_entry = invoice_map[key]
								mapped_items_list = item_entry["mapped_items"]
								new_list = []
								for mapped_items in mapped_items_list:
							    		tax_rate_list.append(mapped_items["tax_rate"])
									data_rate = list(set(tax_rate_list))
								if tax_rate in data_rate:
								    	for items in mapped_items_list:
								   		if float(tax_rate) == float(items["tax_rate"]):
								    			qty_temp = items["net_amount"]
											items["net_amount"] = (qty_temp) + (net_amount)
								else :
									new_list.append({
											"tax_rate": tax_rate,
											"net_amount": net_amount,
											"billing_address_gstin": billing_address_gstin,
											"customer_address": customer_address,
											"place_of_supply": key,
											"reverse_charge": reverse_charge,
											"invoice_type": invoice_type,
											"posting_date": posting_date,
											"ecommerce_gstin": ecommerce_gstin,
											"modified":modified,
											"amended_from":amended_from,
											"grand_total":grand_total,
											"company_address":company_address,
											"customer_type":customer_type,
											"port_code":port_code,
											"shipping_bill_number":shipping_bill_number,
											"shipping_bill_date":shipping_bill_date,
											"export_type":export_type,
											"customer_name":customer_name,
											"is_return":is_return,
											"return_against":return_against
									
										    })
									item_entry["mapped_items"] = mapped_items_list + new_list
							else :
								item_list = []
								item_list.append({
									"tax_rate": tax_rate,
									"net_amount": net_amount,
									"billing_address_gstin": billing_address_gstin,
									"customer_address": customer_address,
									"place_of_supply": key,
									"reverse_charge": reverse_charge,
									"invoice_type": invoice_type,
									"posting_date": posting_date,
									"ecommerce_gstin": ecommerce_gstin,
									"modified":modified,
									"amended_from":amended_from,
									"grand_total":grand_total,
									"company_address":company_address,
									"customer_type":customer_type,
									"port_code":port_code,
									"shipping_bill_number":shipping_bill_number,
									"shipping_bill_date":shipping_bill_date,
									"export_type":export_type,
									"customer_name":customer_name,
									"is_return":is_return,
									"return_against":return_against
								})
								invoice_map[key] = frappe._dict({
								    "mapped_items": item_list
								})
					else:
						sales_tax_rate = 0
						total_amount = 0.0
						if len(sales_invoice_tax_data) != 0:
							for invoice_tax_data in sales_invoice_tax_data:
								account_head = invoice_tax_data.account_head
								item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
								converted = ast.literal_eval(item_wise_tax_detail)
								if item_code in converted:
									details = converted[item_code]
									if "SGST" in account_head or "CGST" in account_head:
										sales_tax_rate = sales_tax_rate + details[0]
							
									elif "IGST" in account_head:
										sales_tax_rate = details[0]
							if place_of_supply in invoice_map:
								item_entry = invoice_map[place_of_supply]
						
								mapped_items_list = item_entry["mapped_items"]
								for mapped_items in mapped_items_list:
									tax_rate_list.append(mapped_items["tax_rate"])
									data_rate = list(set(tax_rate_list))
								if sales_tax_rate in data_rate:
									for items in mapped_items_list:
										if float(sales_tax_rate) == float(items["tax_rate"]):
											qty_temp = items["net_amount"]
											items["net_amount"] = (qty_temp) + (item_net_amount)
								else:
									mapped_items_list.append({
												"tax_rate": sales_tax_rate, 
										  		"net_amount": item_net_amount,
												"billing_address_gstin":billing_address_gstin,
												"customer_address":customer_address,
												"place_of_supply":place_of_supply,
												"reverse_charge":reverse_charge,
												"invoice_type":invoice_type,
												"posting_date":posting_date,
												"ecommerce_gstin":ecommerce_gstin,
												"modified":modified,
												"amended_from":amended_from,
												"grand_total":grand_total,
												"company_address":company_address,
												"customer_type":customer_type,
												"port_code":port_code,
												"shipping_bill_number":shipping_bill_number,
												"shipping_bill_date":shipping_bill_date,
												"export_type":export_type,
												"customer_name":customer_name,
												"is_return":is_return,
												"return_against":return_against
												})
									item_entry["mapped_items"] = mapped_items_list
							else:
								item_list = []
								item_list.append({
										"tax_rate": sales_tax_rate, 
										"net_amount": item_net_amount,
										"billing_address_gstin":billing_address_gstin,
										"customer_address":customer_address,
										"place_of_supply":place_of_supply,
										"reverse_charge":reverse_charge,
										"invoice_type":invoice_type,
										"posting_date":posting_date,
										"ecommerce_gstin":ecommerce_gstin,
										"modified":modified,
										"amended_from":amended_from,
										"grand_total":grand_total,
										"company_address":company_address,
										"customer_type":customer_type,
										"port_code":port_code,
										"shipping_bill_number":shipping_bill_number,
										"shipping_bill_date":shipping_bill_date,
										"export_type":export_type,
										"customer_name":customer_name,
										"is_return":is_return,
										"return_against":return_against
										})
								invoice_map[place_of_supply] = frappe._dict({"mapped_items": item_list})	
	return invoice_map
def get_unique_state_list_amended(sales):
	invoice_map = {}
	for seles_data in sales:
		amended_from = seles_data.amended_from
		if amended_from is not None:
			invoice_id = seles_data.name
			billing_address_gstin = seles_data.billing_address_gstin
			customer_address = seles_data.customer_address
			place_of_supply = seles_data.place_of_supply
			reverse_charge = seles_data.reverse_charge
			invoice_type = seles_data.invoice_type
			customer_name = seles_data.customer_name
			ecommerce_gstin = seles_data.ecommerce_gstin
			posting_date = seles_data.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			grand_total = seles_data.grand_total
			company_address = seles_data.company_address
			customer_type = seles_data.customer_type
			port_code = seles_data.port_code
			shipping_bill_number = seles_data.shipping_bill_number
			shipping_bill_date = seles_data.shipping_bill_date
			if shipping_bill_date is not None:
				shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
			export_type = seles_data.export_type
			is_return = seles_data.is_return
			return_against = seles_data.return_against
			account_head = ""
			modified = seles_data.modified
			modified = modified.date()
			modified = modified.strftime('%d-%m-%Y')
			amended_from = seles_data.amended_from
			b2c_limit = frappe.db.get_value('GST Settings',customer_address,'b2c_limit')
			gst_state_number = get_contact_details(customer_address)
			address_details = address_gst_number(company_address)
			if (grand_total <= float(b2c_limit) and address_details != gst_state_number)\
			or (grand_total <= float(b2c_limit) and address_details == gst_state_number) \
			or (grand_total >= float(b2c_limit) and address_details == gst_state_number): 
				sales_item = sales_item_details(invoice_id)
				for item in sales_item:
					item_code = item.item_code
					item_net_amount = item.net_amount
					tax_data = sales_tax(item_code,invoice_id)
					sales_invoice_tax_data = sales_account_tax(invoice_id)
					tax_rate_list = []
					if len(tax_data) != 0:
						for data in tax_data:
							tax_rate = data.tax_rate
							net_amount = data.net_amount
							key = place_of_supply
							if key in invoice_map:
						    		item_entry = invoice_map[key]
								mapped_items_list = item_entry["mapped_items"]
								new_list = []
								for mapped_items in mapped_items_list:
							    		tax_rate_list.append(mapped_items["tax_rate"])
									data_rate = list(set(tax_rate_list))
								if tax_rate in data_rate:
								    	for items in mapped_items_list:
								   		if float(tax_rate) == float(items["tax_rate"]):
								    			qty_temp = items["net_amount"]
											items["net_amount"] = (qty_temp) + (net_amount)
								else :
									new_list.append({
											"tax_rate": tax_rate,
											"net_amount": net_amount,
											"billing_address_gstin": billing_address_gstin,
											"customer_address": customer_address,
											"place_of_supply": key,
											"reverse_charge": reverse_charge,
											"invoice_type": invoice_type,
											"posting_date": posting_date,
											"ecommerce_gstin": ecommerce_gstin,
											"modified":modified,
											"amended_from":amended_from,
											"grand_total":grand_total,
											"company_address":company_address,
											"customer_type":customer_type,
											"port_code":port_code,
											"shipping_bill_number":shipping_bill_number,
											"shipping_bill_date":shipping_bill_date,
											"export_type":export_type,
											"customer_name":customer_name,
											"is_return":is_return,
											"return_against":return_against
									
										    })
									item_entry["mapped_items"] = mapped_items_list + new_list
							else :
								item_list = []
								item_list.append({
									"tax_rate": tax_rate,
									"net_amount": net_amount,
									"billing_address_gstin": billing_address_gstin,
									"customer_address": customer_address,
									"place_of_supply": key,
									"reverse_charge": reverse_charge,
									"invoice_type": invoice_type,
									"posting_date": posting_date,
									"ecommerce_gstin": ecommerce_gstin,
									"modified":modified,
									"amended_from":amended_from,
									"grand_total":grand_total,
									"company_address":company_address,
									"customer_type":customer_type,
									"port_code":port_code,
									"shipping_bill_number":shipping_bill_number,
									"shipping_bill_date":shipping_bill_date,
									"export_type":export_type,
									"customer_name":customer_name,
									"is_return":is_return,
									"return_against":return_against
								})
								invoice_map[key] = frappe._dict({
								    "mapped_items": item_list
								})
					else:
						sales_tax_rate = 0
						total_amount = 0.0
						if len(sales_invoice_tax_data) != 0:
							for invoice_tax_data in sales_invoice_tax_data:
								account_head = invoice_tax_data.account_head
								item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
								converted = ast.literal_eval(item_wise_tax_detail)
								if item_code in converted:
									details = converted[item_code]
									if "SGST" in account_head or "CGST" in account_head:
										sales_tax_rate = sales_tax_rate + details[0]
							
									elif "IGST" in account_head:
										sales_tax_rate = details[0]
							if place_of_supply in invoice_map:
								item_entry = invoice_map[place_of_supply]
						
								mapped_items_list = item_entry["mapped_items"]
								for mapped_items in mapped_items_list:
									tax_rate_list.append(mapped_items["tax_rate"])
									data_rate = list(set(tax_rate_list))
								if sales_tax_rate in data_rate:
									for items in mapped_items_list:
										if float(sales_tax_rate) == float(items["tax_rate"]):
											qty_temp = items["net_amount"]
											items["net_amount"] = (qty_temp) + (item_net_amount)
								else:
									mapped_items_list.append({
												"tax_rate": sales_tax_rate, 
										  		"net_amount": item_net_amount,
												"billing_address_gstin":billing_address_gstin,
												"customer_address":customer_address,
												"place_of_supply":place_of_supply,
												"reverse_charge":reverse_charge,
												"invoice_type":invoice_type,
												"posting_date":posting_date,
												"ecommerce_gstin":ecommerce_gstin,
												"modified":modified,
												"amended_from":amended_from,
												"grand_total":grand_total,
												"company_address":company_address,
												"customer_type":customer_type,
												"port_code":port_code,
												"shipping_bill_number":shipping_bill_number,
												"shipping_bill_date":shipping_bill_date,
												"export_type":export_type,
												"customer_name":customer_name,
												"is_return":is_return,
												"return_against":return_against
												})
									item_entry["mapped_items"] = mapped_items_list
							else:
								item_list = []
								item_list.append({
										"tax_rate": sales_tax_rate, 
										"net_amount": item_net_amount,
										"billing_address_gstin":billing_address_gstin,
										"customer_address":customer_address,
										"place_of_supply":place_of_supply,
										"reverse_charge":reverse_charge,
										"invoice_type":invoice_type,
										"posting_date":posting_date,
										"ecommerce_gstin":ecommerce_gstin,
										"modified":modified,
										"amended_from":amended_from,
										"grand_total":grand_total,
										"company_address":company_address,
										"customer_type":customer_type,
										"port_code":port_code,
										"shipping_bill_number":shipping_bill_number,
										"shipping_bill_date":shipping_bill_date,
										"export_type":export_type,
										"customer_name":customer_name,
										"is_return":is_return,
										"return_against":return_against
										})
								invoice_map[place_of_supply] = frappe._dict({"mapped_items": item_list})	
	return invoice_map
def sales_exepted_nill(exempted_items):
	payment_tax = {}
	item_unieq_name1 = []
	item_unieq_name2 = []
	item_unieq_name3 = []
	for exempt in exempted_items:
		india_gst_item_status = exempt.india_gst_item_status
		if str(india_gst_item_status) == "Nil Rated Item":
			item_name = exempt.item_name
			net_amount = exempt.net_amount
			exempt_net_amount = 0.0
			non_net_amount = 0.0
			key = item_name
			if key in payment_tax:						
				item_entry = payment_tax[key]
				item_unieq_name1.append(item_entry["item_name"])
				uniue_name = list(set(item_unieq_name1))
				if item_name in uniue_name:
					if item_name == item_entry["item_name"]:
						qty_temp = item_entry["nill_net_amount"]
						item_entry["nill_net_amount"] = (qty_temp) + (net_amount)
				else:
					payment_tax[key] = frappe._dict({
						"item_name": key, 
						"nill_net_amount": net_amount,
						"india_gst_item_status":india_gst_item_status,
						"non_net_amount":non_net_amount,
						"exempt_net_amount":exempt_net_amount
						})
			else:
				payment_tax[key] = frappe._dict({
					"item_name": key, 
					"nill_net_amount": net_amount,
					"india_gst_item_status":india_gst_item_status,
					"non_net_amount":non_net_amount,
					"exempt_net_amount":exempt_net_amount
					})		
		elif str(india_gst_item_status) == "Exempt Item":
			item_name = exempt.item_name
			net_amount = exempt.net_amount
			non_net_amount = 0.0
			nill_net_amount = 0.0
			key = item_name
			if key in payment_tax:						
				item_entry = payment_tax[key]
				item_unieq_name2.append(item_entry["item_name"])
				uniue_name = list(set(item_unieq_name2))
				if item_name in uniue_name:
					if item_name == item_entry["item_name"]:
						qty_temp = item_entry["exempt_net_amount"]
						item_entry["exempt_net_amount"] = (qty_temp) + (net_amount)
				else:
					payment_tax[key] = frappe._dict({
						"item_name": key, 
						"exempt_net_amount": net_amount,
						"india_gst_item_status":india_gst_item_status,
						"non_net_amount":non_net_amount,
						"nill_net_amount":nill_net_amount
						})
			else:
				payment_tax[key] = frappe._dict({
					"item_name": key, 
					"exempt_net_amount": net_amount,
					"india_gst_item_status":india_gst_item_status,
					"non_net_amount":non_net_amount,
					"nill_net_amount":nill_net_amount
					})
			
		elif str(india_gst_item_status) == "Non-GST Item":
			item_name = exempt.item_name
			net_amount = exempt.net_amount
			exempt_net_amount = 0.0
			nill_net_amount = 0.0
			key = item_name
			if key in payment_tax:						
				item_entry = payment_tax[key]
				item_unieq_name3.append(item_entry["item_name"])
				uniue_name = list(set(item_unieq_name3))
				if item_name in uniue_name:
					if item_name == item_entry["item_name"]:
						qty_temp = item_entry["non_net_amount"]
						item_entry["non_net_amount"] = (qty_temp) + (net_amount)
				else:
					payment_tax[key] = frappe._dict({
						"item_name": key, 
						"non_net_amount": net_amount,
						"india_gst_item_status":india_gst_item_status,
						"exempt_net_amount":exempt_net_amount,
						"non_net_amount":non_net_amount
						})
			else:
				payment_tax[key] = frappe._dict({
					"item_name": key, 
					"non_net_amount": net_amount,
					"india_gst_item_status":india_gst_item_status,
					"exempt_net_amount":exempt_net_amount,
					"nill_net_amount":nill_net_amount
					})

	
	return payment_tax
def get_hsn_uqc_list(sales):
	invoice_map = {}
	item_tax_rate = 0.0
	integrated_tax_amount = 0.0
	central_tax_amount = 0.0
	state_tax_amount = 0.0
	total_value = 0.0
	for seles_data in sales:
		invoice_id = seles_data.name
		item_name = seles_data.itme_name
		item_code = seles_data.item_code
		net_amount = seles_data.net_amount
		gst_hsn_code = seles_data.gst_hsn_code
		uom = seles_data.uom
		qty = seles_data.qty
		tax_data = sales_tax_hsn(item_code,invoice_id)
		sales_invoice_tax_data = sales_account_tax(invoice_id)
		tax_rate_list = []
		if gst_hsn_code is not None:
			if len(tax_data) != 0:
				for data in tax_data:
					tax_rate = data.tax_rate
					tax_type = data.tax_type
					key = gst_hsn_code
					if "SGST" in tax_type or "CGST" in tax_type:
						if  "SGST" in tax_type:
							state_tax_amount = net_amount * data.tax_rate/100
						elif "CGST" in tax_type:
							central_tax_amount = net_amount * data.tax_rate/100
					elif "IGST" in tax_type:
						
						item_tax_rate = data.tax_rate
						integrated_tax_amount = net_amount * data.tax_rate/100
				if key in invoice_map:
				    	item_entry = invoice_map[key]
					qty_temp = item_entry["net_amount"]
					qty_count = item_entry["qty"]
					item_entry["net_amount"] = (qty_temp) + (net_amount)
					item_entry["qty"] = (qty_count) + (qty)
				else :
				
					invoice_map[key] = frappe._dict({
							"tax_rate": item_tax_rate,
							"net_amount": net_amount,
							"gst_hsn_code": key,
							"state_tax_amount":state_tax_amount,
							"central_tax_amount":central_tax_amount,
							"integrated_tax_amount":integrated_tax_amount,
							"uom":uom,
							"qty":qty,
							"item_code":item_code
							})
			else:
				sales_tax_rate = 0
				total_amount = 0.0
				if len(sales_invoice_tax_data) != 0:
					for invoice_tax_data in sales_invoice_tax_data:
						account_head = invoice_tax_data.account_head
						item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
						converted = ast.literal_eval(item_wise_tax_detail)
						if item_code in converted:
							details = converted[item_code]
							if "SGST" in account_head or "CGST" in account_head:
								if "SGST" in account_head:
									sales_tax_rate = sales_tax_rate + details[0]
									state_tax_amount = state_tax_amount * details[0]/100
								elif  "CGST" in account_head:
									sales_tax_rate = sales_tax_rate + details[0]
									central_tax_amount = central_tax_amount * details[0]/100
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
								integrated_tax_amount = net_amount * details[0]/100
							
					if gst_hsn_code in invoice_map:
						item_entry = invoice_map[gst_hsn_code]
					
						qty_temp = item_entry["net_amount"]
						qty_count = item_entry["qty"]
						item_entry["net_amount"] = (qty_temp) + (net_amount)
						item_entry["qty"] = (qty_count) + (qty)
					else:
						invoice_map[gst_hsn_code] = frappe._dict({
							"tax_rate": sales_tax_rate,
							"net_amount": net_amount,
							"gst_hsn_code": gst_hsn_code,
							"state_tax_amount":state_tax_amount,
							"central_tax_amount":central_tax_amount,
							"integrated_tax_amount":integrated_tax_amount,
							"uom":uom,
							"qty":qty,
							"item_code":item_code
							})	
	return invoice_map
def unique_payment_entry(entry_sales):
	invoice_map = {}
	for seles_data in entry_sales:
		invoice_id = seles_data.name
		payment_total_amount = seles_data.allocated_amount
		advance_paid = seles_data.advance_paid
		grand_total = seles_data.grand_total
		place_of_supply = seles_data.state
		item_code = seles_data.item_code
		net_amount = seles_data.net_amount
		additional_discount_percentage = seles_data.additional_discount_percentage
		sales_item = sales_item_details_order(invoice_id)
		tax_data = sales_tax_so(item_code,invoice_id)
		sales_invoice_tax_data = sales_account_tax(invoice_id)
		tax_rate_list = []
		if len(tax_data) != 0:
			for data in tax_data:
				tax_rate = data.tax_rate
				net_amount = data.net_amount
				tax_type = data.tax_type
				tax_rate = 0
				igst_rate = 0
				cgst_rate = 0
				sgst_rate = 0
				if "IGST" in tax_type:
					tax_rate = data.tax_rate
					igst_rate = data.tax_rate
				elif "SGST" in tax_type:
					tax_rate += data.tax_rate
					sgst_rate = data.tax_rate
				elif "CGST" in tax_type:
					tax_rate += data.tax_rate
					cgst_rate = data.tax_rate
					
				key = invoice_id
				if key in invoice_map:
			    		item_entry = invoice_map[key]
					mapped_items_list = item_entry["mapped_items"]
					new_list = []
					for mapped_items in mapped_items_list:
				    		tax_rate_list.append(mapped_items["tax_rate"])
						data_rate = list(set(tax_rate_list))
					if tax_rate in data_rate:
					    	for items in mapped_items_list:
					   		if float(tax_rate) == float(items["tax_rate"]):
					    			qty_temp = items["net_amount"]
								items["net_amount"] = (qty_temp) + (net_amount)
					else :
						new_list.append({
								"tax_rate": tax_rate,
								"net_amount" :net_amount,
								"place_of_supply": place_of_supply, 
								"payment_total_amount": payment_total_amount,
								"invoice_id":key,
								"advance_paid":advance_paid,
								"additional_discount_percentage":additional_discount_percentage,
								"grand_total":grand_total,
								"igst_rate":igst_rate,
								"sgst_rate":sgst_rate,
								"cgst_rate":cgst_rate
									
								    })
						item_entry["mapped_items"] = mapped_items_list + new_list
				else :
					item_list = []
					item_list.append({
							"tax_rate": tax_rate,
							"net_amount" :net_amount,
							"place_of_supply": place_of_supply, 
							"payment_total_amount": payment_total_amount,
							"invoice_id":key,
							"advance_paid":advance_paid,
							"additional_discount_percentage":additional_discount_percentage,
							"grand_total":grand_total,
							"igst_rate":igst_rate,
							"sgst_rate":sgst_rate,
							"cgst_rate":cgst_rate
						})
					invoice_map[key] = frappe._dict({
						    "mapped_items": item_list
						})
		else:
			sales_tax_rate = 0
			total_amount = 0.0
			igst_rate = 0
			cgst_rate = 0
			sgst_rate = 0
			if len(sales_invoice_tax_data) != 0:
				for invoice_tax_data in sales_invoice_tax_data:
					account_head = invoice_tax_data.account_head
					item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
					converted = ast.literal_eval(item_wise_tax_detail)
					if item_code in converted:
						details = converted[item_code]
						if "SGST" in account_head:
							sales_tax_rate = sales_tax_rate + details[0]
							sgst_rate = details[0]
						elif "CGST" in account_head:
							sales_tax_rate = sales_tax_rate + details[0]
							cgst_rate = details[0]
						elif "IGST" in account_head:
							sales_tax_rate = details[0]
							igst_rate = details[0]
				if invoice_id in invoice_map:
					item_entry = invoice_map[invoice_id]
					mapped_items_list = item_entry["mapped_items"]
					for mapped_items in mapped_items_list:
						tax_rate_list.append(mapped_items["tax_rate"])
						data_rate = list(set(tax_rate_list))
					if sales_tax_rate in data_rate:
						for items in mapped_items_list:
							if float(sales_tax_rate) == float(items["tax_rate"]):
								qty_temp = items["net_amount"]
								items["net_amount"] = (qty_temp) + (net_amount)
					else:
						mapped_items_list.append({
									"tax_rate": sales_tax_rate, 
							  		"net_amount": net_amount,
									"place_of_supply": place_of_supply, 
									"payment_total_amount": payment_total_amount,
									"invoice_id":invoice_id,
									"advance_paid":advance_paid,
									"additional_discount_percentage":additional_discount_percentage,
									"grand_total":grand_total,
									"igst_rate":igst_rate,
									"sgst_rate":sgst_rate,
									"cgst_rate":cgst_rate
									})
						item_entry["mapped_items"] = mapped_items_list
				else:
					item_list = []
					item_list.append({
							"tax_rate": sales_tax_rate, 
							"net_amount": net_amount,
							"place_of_supply": place_of_supply, 
							"payment_total_amount": payment_total_amount,
							"invoice_id":invoice_id,
							"advance_paid":advance_paid,
							"additional_discount_percentage":additional_discount_percentage,
							"grand_total":grand_total,
							"igst_rate":igst_rate,
							"sgst_rate":sgst_rate,
							"cgst_rate":cgst_rate
							})
					invoice_map[invoice_id] = frappe._dict({"mapped_items": item_list})	
	return invoice_map
def unique_payment_entry_can_amen(entry_sales):
	invoice_map = {}
	for seles_data in entry_sales:
		sales_amended_from = seles_data.sales_amended
		sales_doc = seles_data.sales_doc
		payment_doc = seles_data.payment_doc
		payment_amended_from = seles_data.payment_amended
		if payment_amended_from is not None:
			invoice_id = seles_data.name
			payment_total_amount = seles_data.allocated_amount
			advance_paid = seles_data.advance_paid
			grand_total = seles_data.grand_total
			if sales_amended_from is None:
				place_of_supply = seles_data.state
			elif sales_amended_from is not  None:
				sales_oder = sales_order_details(sales_amended_from)
				for order in sales_oder:
					place_of_supply = order.state
			creation = seles_data.creation
			creation_date = creation.date()
			creation_date = creation_date.strftime('%d-%m-%Y')
			item_code = seles_data.item_code
			net_amount = seles_data.net_amount
			additional_discount_percentage = seles_data.additional_discount_percentage
			sales_item = sales_item_details_order(invoice_id)
			tax_data = sales_tax_so(item_code,invoice_id)
			sales_invoice_tax_data = sales_account_tax(invoice_id)
			tax_rate_list = []
			if len(tax_data) != 0:
				for data in tax_data:
					tax_rate = data.tax_rate
					net_amount = data.net_amount
					key = invoice_id
					if key in invoice_map:
				    		item_entry = invoice_map[key]
						mapped_items_list = item_entry["mapped_items"]
						new_list = []
						for mapped_items in mapped_items_list:
					    		tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if tax_rate in data_rate:
						    	for items in mapped_items_list:
						   		if float(tax_rate) == float(items["tax_rate"]):
						    			qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (net_amount)
						else :
							new_list.append({
									"tax_rate": tax_rate,
									"net_amount" :net_amount,
									"place_of_supply": place_of_supply, 
									"payment_total_amount": payment_total_amount,
									"invoice_id":key,
									"advance_paid":advance_paid,
									"additional_discount_percentage":additional_discount_percentage,
									"grand_total":grand_total,
									"creation_date":creation_date,
									"sales_amended_from":sales_amended_from
									
									    })
							item_entry["mapped_items"] = mapped_items_list + new_list
					else :
						item_list = []
						item_list.append({
								"tax_rate": tax_rate,
								"net_amount" :net_amount,
								"place_of_supply": place_of_supply, 
								"payment_total_amount": payment_total_amount,
								"invoice_id":key,
								"advance_paid":advance_paid,
								"additional_discount_percentage":additional_discount_percentage,
								"grand_total":grand_total,
								"creation_date":creation_date,
								"sales_amended_from":sales_amended_from
							
							})
						invoice_map[key] = frappe._dict({
							    "mapped_items": item_list
							})
			else:
				sales_tax_rate = 0
				total_amount = 0.0
				if len(sales_invoice_tax_data) != 0:
					for invoice_tax_data in sales_invoice_tax_data:
						account_head = invoice_tax_data.account_head
						item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
						converted = ast.literal_eval(item_wise_tax_detail)
						if item_code in converted:
							details = converted[item_code]
							if "SGST" in account_head or "CGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
						
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
					if invoice_id in invoice_map:
						item_entry = invoice_map[invoice_id]
						mapped_items_list = item_entry["mapped_items"]
						for mapped_items in mapped_items_list:
							tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if sales_tax_rate in data_rate:
							for items in mapped_items_list:
								if float(sales_tax_rate) == float(items["tax_rate"]):
									qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (net_amount)
						else:
							mapped_items_list.append({
										"tax_rate": sales_tax_rate, 
								  		"net_amount": net_amount,
										"place_of_supply": place_of_supply, 
										"payment_total_amount": payment_total_amount,
										"invoice_id":invoice_id,
										"advance_paid":advance_paid,
										"additional_discount_percentage":additional_discount_percentage,
										"grand_total":grand_total,
										"creation_date":creation_date,
										"sales_amended_from":sales_amended_from
										})
							item_entry["mapped_items"] = mapped_items_list
					else:
						item_list = []
						item_list.append({
								"tax_rate": sales_tax_rate, 
								"net_amount": net_amount,
								"place_of_supply": place_of_supply, 
								"payment_total_amount": payment_total_amount,
								"invoice_id":invoice_id,
								"advance_paid":advance_paid,
								"additional_discount_percentage":additional_discount_percentage,
								"grand_total":grand_total,
								"creation_date":creation_date,
								"sales_amended_from":sales_amended_from
								})
						invoice_map[invoice_id] = frappe._dict({"mapped_items": item_list})	
	return invoice_map

def unique_order_invoice(sales):
	invoice_map = {}
	for seles_data in sales:
		sales_amended = seles_data.sales_amended
		payment_amended = seles_data.payment_amended
		order_total = seles_data.order_total
		invoice_total = seles_data.invoice_total
		if amended_from is None and payment_amended is None and order_total > invoice_total:
			invoice_id = seles_data.sales_invoice
			sales_order = seles_data.sales_order
			customer_address = seles_data.customer_address
			posting_date = seles_data.creation
			posting_date = posting_date.date()
			posting_date = posting_date.strftime('%d-%m-%Y')
			payment_id = seles_data.parent
			item_code = seles_data.item_code
			net_amount = sales_data.net_amount
			allocated_amount = seles_data.allocated_amount
			place_of_supply = seles_data.state
			gstin = seles_data.gstin
			account_head = ""
			tax_data = sales_tax(item_code,invoice_id)
			sales_invoice_tax_data = sales_account_tax(invoice_id)
			tax_rate_list = []
			if len(tax_data) != 0:
				for data in tax_data:
					tax_rate = data.tax_rate
					net_amount = data.net_amount
					key = sales_order
					if key in invoice_map:
				    		item_entry = invoice_map[key]
						mapped_items_list = item_entry["mapped_items"]
						new_list = []
						for mapped_items in mapped_items_list:
					    		tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if tax_rate in data_rate:
						    	for items in mapped_items_list:
						   		if float(tax_rate) == float(items["tax_rate"]):
						    			qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (net_amount)
						else :
							new_list.append({
									"tax_rate": tax_rate,
									"net_amount": net_amount,
									"sales_order": key,
									"customer_address": customer_address,
									"place_of_supply": place_of_supply,
									"payment_id": payment_id,
									"allocated_amount": allocated_amount,
									"posting_date": posting_date,
									"gstin": gstin
									
										    })
							item_entry["mapped_items"] = mapped_items_list + new_list
					else :
						item_list = []
						item_list.append({
									"tax_rate": tax_rate,
									"net_amount": net_amount,
									"sales_order": key,
									"customer_address": customer_address,
									"place_of_supply": place_of_supply,
									"payment_id": payment_id,
									"allocated_amount": allocated_amount,
									"posting_date": posting_date,
									"gstin": gstin
								})
						invoice_map[key] = frappe._dict({
							    "mapped_items": item_list
								})
			else:
				sales_tax_rate = 0
				total_amount = 0.0
				if len(sales_invoice_tax_data) != 0:
					for invoice_tax_data in sales_invoice_tax_data:
						account_head = invoice_tax_data.account_head
						item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
						converted = ast.literal_eval(item_wise_tax_detail)
						if item_code in converted:
							details = converted[item_code]
							if "SGST" in account_head or "CGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
					
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
					if sales_order in invoice_map:
						item_entry = invoice_map[sales_order]
				
						mapped_items_list = item_entry["mapped_items"]
						for mapped_items in mapped_items_list:
							tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if sales_tax_rate in data_rate:
							for items in mapped_items_list:
								if float(sales_tax_rate) == float(items["tax_rate"]):
									qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (item_net_amount)
						else:
							mapped_items_list.append({
										"tax_rate": sales_tax_rate,
										"net_amount": net_amount,
										"sales_order": sales_order,
										"customer_address": customer_address,
										"place_of_supply": place_of_supply,
										"payment_id": payment_id,
										"allocated_amount": allocated_amount,
										"posting_date": posting_date,
										"gstin": gstin
											})
							item_entry["mapped_items"] = mapped_items_list
					else:
						item_list = []
						item_list.append({
								"tax_rate": sales_tax_rate,
								"net_amount": net_amount,
								"sales_order": sales_order,
								"customer_address": customer_address,
								"place_of_supply": place_of_supply,
								"payment_id": payment_id,
								"allocated_amount": allocated_amount,
								"posting_date": posting_date,
								"gstin": gstin
								})
						invoice_map[sales_order] = frappe._dict({"mapped_items": item_list})	
	return invoice_map