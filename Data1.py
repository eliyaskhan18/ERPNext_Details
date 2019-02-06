# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
import datetime
from datetime import date, timedelta
from collections import defaultdict
import operator
import frappe
import json
import time
import math
import ast

def execute(filters=None):
	global data
	columns = []
	data = []
	columns = get_columns()

	data.append(["", "", ""])
	invoice_list_for_day = get_day_wise_invoices()
	data.append(["Day", "", ""])
	if invoice_list_for_day is not None:
		invoice_type = "Day"
		get_invoice_amount(invoice_list_for_day,invoice_type)
	
	data.append(["", "", ""])
	data.append(["Month To Date", "", ""])

	invoice_list_for_month = get_month_wise_invoices()
	if invoice_list_for_month is not None:
		invoice_type = "Month"
		get_invoice_amount(invoice_list_for_month,invoice_type)
	
	data.append(["", "", ""])
	data.append(["Year To Date", "", ""])

	invoice_list_for_fin_year = get_year_wise_invoices()
	if invoice_list_for_fin_year is not None:
		invoice_type = "Year"
		get_invoice_amount(invoice_list_for_fin_year,invoice_type)
	print "Data-----",data
	return columns, data

def get_columns():
	"""return columns"""
	columns = [
	_(" ")+"::100",
	_("Day")+"::100",
	_("Month to Date")+"::150",
	_("Year to Date")+"::150"
	 ]
	return columns

def get_invoice_amount(invoice_list,invoice_type):
	customer_type = ""
	total_invoice_amount_of_Cash = 0
	total_invoice_amount_of_NEFT =0
	total_invoice_amount_of_company = 0
	total_invoice_amount_of_Credit = 0
	total_invoice_amount_of_Credit_card =0
	total_invoice_amount_of_Cheque =0
	total_invoice_amount_of_Bank_Draft =0
	total_invoice_amount_of_individual = 0
	total_invoice_amount_of_ind_Cash =0
	total_invoice_amount_of_ind_NEFT_ = 0
	total_invoice_amount_of_ind_Credit =0
	total_invoice_amount_of_ind_Credit_card = 0
	total_invoice_amount_of_ind_Cheque = 0
	total_invoice_amount_of_ind_Bank_Draft =0
	current_date = getdate(datetime.datetime.now())
	c_date = frappe.utils.formatdate(current_date, "dd-MM-yyyy")
	now = datetime.datetime.now()
	current_year = now.year
	monthinteger = now.month
	name = ""
	mode_of_payment = ""
	Amount = 0
	current_month = datetime.date(1900, monthinteger, 1).strftime('%B')
	for invoice_data in invoice_list:
		name = invoice_data['name']
		#print "name----------",name
		
		#print "mode_of_payment----------",mode_of_payment
		#print "Amount----------",Amount
		customer_type = invoice_data['customer_type']
		#amount = invoice_data['net_total']
		status = invoice_data['status']
		if customer_type == "Company":
			sales_invoice_payment = frappe.get_list("Sales Invoice Payment",{"parent" : name},["mode_of_payment","amount"])
			#print "sales_invoice_payment----------",sales_invoice_payment
			for payment_type in sales_invoice_payment:
				mode_of_payment = payment_type["mode_of_payment"]
				#print "mode_of_payment------------",mode_of_payment
				if mode_of_payment == "Cash":
					Amount = payment_type["amount"]
					total_invoice_amount_of_Cash= total_invoice_amount_of_Cash + payment_type["amount"]
				if mode_of_payment == "NEFT/RTGS":
					Amount = payment_type["amount"]
					total_invoice_amount_of_NEFT= total_invoice_amount_of_NEFT + payment_type["amount"]
				elif mode_of_payment == "CREDIT":
					Amount = payment_type["amount"]
					total_invoice_amount_of_Credit= total_invoice_amount_of_Credit + payment_type["amount"]
				elif mode_of_payment == "Credit Card":
					Amount = payment_type["amount"]
					total_invoice_amount_of_Credit_card= total_invoice_amount_of_Credit_card + payment_type["amount"]
				elif mode_of_payment == "Cheque":
					Amount = payment_type["amount"]
					total_invoice_amount_of_Cheque= total_invoice_amount_of_Cheque + payment_type["amount"]
				elif mode_of_payment == "Bank Draft":
					Amount = payment_type["amount"]
					total_invoice_amount_of_Bank_Draft = total_invoice_amount_of_Bank_Draft+ payment_type["amount"]
			#print "total_invoice_amount_of_Cash--------",total_invoice_amount_of_Cash
			#print "total_invoice_amount_of_NEFT--------",total_invoice_amount_of_NEFT
			#print "total_invoice_amount_of_Credit--------",total_invoice_amount_of_Credit
			#print "total_invoice_amount_of_Credit_card-----------",total_invoice_amount_of_Credit_card
			#print "total_invoice_amount_of_Cheque-----------",total_invoice_amount_of_Cheque
			#print "total_invoice_amount_of_Bank_Draft-----------",total_invoice_amount_of_Bank_Draft
		day_amount = 0
		month_amount = 0
		year_amount = 0
		payment = ""
		if invoice_type == "Day":
			#data.append([str(c_date), total_invoice_amount_of_individual, total_invoice_amount_of_company, total])
			if mode_of_payment == "Cash":
				payment = mode_of_payment
				day_amoubt = 
			if mode_of_payment == "NEFT/RTGS":
				Amount = payment_type["amount"]
				total_invoice_amount_of_ind_NEFT_= total_invoice_amount_of_ind_NEFT_ + payment_type["amount"]
			elif mode_of_payment == "CREDIT":
				Amount = payment_type["amount"]
				total_invoice_amount_of_ind_Credit= total_invoice_amount_of_ind_Credit + payment_type["amount"]
			elif mode_of_payment == "Credit Card":
				Amount = payment_type["amount"]
				total_invoice_amount_of_ind_Credit_card=total_invoice_amount_of_ind_Credit_card+ payment_type["amount"]
			elif mode_of_payment == "Cheque":
				Amount = payment_type["amount"]
				total_invoice_amount_of_ind_Cheque= total_invoice_amount_of_ind_Cheque + payment_type["amount"]
			elif mode_of_payment == "Bank Draft":
				Amount = payment_type["amount"]
				total_invoice_amount_of_ind_Bank_Draft = total_invoice_amount_of_ind_Bank_Draft+ payment_type["amount"]
		elif invoice_type == "Month":
			data.append([ (str(current_month) + ", " + str(current_year)), total_invoice_amount_of_individual, 				       total_invoice_amount_of_company, total])
		elif invoice_type == "Year":
			data.append([ ("FY" + str(current_year) + "-"+ str(current_year + 1)), total_invoice_amount_of_individual, 					total_invoice_amount_of_company, total])
	for invoice_data in invoice_list:
		name = invoice_data['name']
		#print "name----------",name
		
		#print "mode_of_payment----------",mode_of_payment
		#print "Amount----------",Amount
		customer_type = invoice_data['customer_type']
		#amount = invoice_data['net_total']
		status = invoice_data['status']
		elif customer_type == "Individual":
			sales_invoice_payment = frappe.get_list("Sales Invoice Payment",{"parent" : name},["mode_of_payment","amount"])
			#print "sales_invoice_payment----------",sales_invoice_payment
			for payment_type in sales_invoice_payment:
				mode_of_payment = payment_type["mode_of_payment"]
				if mode_of_payment == "Cash":
					print "mode_of_payment------------",mode_of_payment
					print "name---------",name
					Amount = payment_type["amount"]
					total_invoice_amount_of_ind_Cash= total_invoice_amount_of_ind_Cash + payment_type["amount"]
				if mode_of_payment == "NEFT/RTGS":
					Amount = payment_type["amount"]
					total_invoice_amount_of_ind_NEFT_= total_invoice_amount_of_ind_NEFT_ + payment_type["amount"]
				elif mode_of_payment == "CREDIT":
					Amount = payment_type["amount"]
					total_invoice_amount_of_ind_Credit= total_invoice_amount_of_ind_Credit + payment_type["amount"]
				elif mode_of_payment == "Credit Card":
					Amount = payment_type["amount"]
					total_invoice_amount_of_ind_Credit_card=total_invoice_amount_of_ind_Credit_card+ payment_type["amount"]
				elif mode_of_payment == "Cheque":
					Amount = payment_type["amount"]
					total_invoice_amount_of_ind_Cheque= total_invoice_amount_of_ind_Cheque + payment_type["amount"]
				elif mode_of_payment == "Bank Draft":
					Amount = payment_type["amount"]
					total_invoice_amount_of_ind_Bank_Draft = total_invoice_amount_of_ind_Bank_Draft+ payment_type["amount"]
			print "total_invoice_amount_of_ind_Cash--------",total_invoice_amount_of_ind_Cash
			#print "total_invoice_amount_of_ind_NEFT_--------",total_invoice_amount_of_ind_NEFT_
			#print "total_invoice_amount_of_ind_Credit--------",total_invoice_amount_of_ind_Credit
			#print "total_invoice_amount_of_ind_Credit_card-----------",total_invoice_amount_of_ind_Credit_card
			#print "total_invoice_amount_of_ind_Cheque-----------",total_invoice_amount_of_ind_Cheque
			#print "total_invoice_amount_of_ind_Bank_Draft-----------",total_invoice_amount_of_ind_Bank_Draft
			
	total = total_invoice_amount_of_company + total_invoice_amount_of_individual
	day_amount = 0
	month_amount = 0
	year_amount = 0
	payment = ""
	if invoice_type == "Day":
		#data.append([str(c_date), total_invoice_amount_of_individual, total_invoice_amount_of_company, total])
		if mode_of_payment == "Cash":
			payment = mode_of_payment
			day_amoubt = 
		if mode_of_payment == "NEFT/RTGS":
			Amount = payment_type["amount"]
			total_invoice_amount_of_ind_NEFT_= total_invoice_amount_of_ind_NEFT_ + payment_type["amount"]
		elif mode_of_payment == "CREDIT":
			Amount = payment_type["amount"]
			total_invoice_amount_of_ind_Credit= total_invoice_amount_of_ind_Credit + payment_type["amount"]
		elif mode_of_payment == "Credit Card":
			Amount = payment_type["amount"]
			total_invoice_amount_of_ind_Credit_card=total_invoice_amount_of_ind_Credit_card+ payment_type["amount"]
		elif mode_of_payment == "Cheque":
			Amount = payment_type["amount"]
			total_invoice_amount_of_ind_Cheque= total_invoice_amount_of_ind_Cheque + payment_type["amount"]
		elif mode_of_payment == "Bank Draft":
			Amount = payment_type["amount"]
			total_invoice_amount_of_ind_Bank_Draft = total_invoice_amount_of_ind_Bank_Draft+ payment_type["amount"]
	elif invoice_type == "Month":
		data.append([ (str(current_month) + ", " + str(current_year)), total_invoice_amount_of_individual, 				       total_invoice_amount_of_company, total])
	elif invoice_type == "Year":
		data.append([ ("FY" + str(current_year) + "-"+ str(current_year + 1)), total_invoice_amount_of_individual, 					total_invoice_amount_of_company, total])

def get_day_wise_invoices():
	current_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_type, name, net_total, status from `tabSales Invoice` where posting_date = %s and 
					docstatus=1""", (current_date), as_dict=1)
	
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_month_wise_invoices():
	d = date.today()
	from_date = get_first_day(d)
	to_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_type, name, net_total, status from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1""", (from_date, to_date), as_dict=1)
	#print "invoice_details------------",invoice_details
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_year_wise_invoices():
	now = datetime.datetime.now()
	current_year = now.year
	from_date = str(current_year) + "-04-01"
	to_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_type, name, net_total, status from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1""", (from_date, to_date), as_dict=1)
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)


