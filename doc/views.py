from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from io import BytesIO
from reportlab.pdfgen import canvas
from docx import Document
from docx.shared import Inches
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import UserData
from django.core.files.uploadedfile import InMemoryUploadedFile
import base64
import os
import tempfile
from django.template import Context
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter


def index(request) :
    if not request.user.is_authenticated : 
        return render(request, "doc/index.html")
    else :
        return HttpResponseRedirect(reverse(home))
    

def home(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/home.html', {'user_data': user_data})

def login_post(request) :
    if not request.user.is_authenticated:
        if request.method == "POST" :
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None :
                login(request, user)
                return HttpResponseRedirect(reverse(index))
            else :
                return render(request, "doc/index.html", {
                    "message" : "Invalid username and/or password."
                })
            
        else :
            return render(request, "doc/index.html")
    else :
        return HttpResponseRedirect(reverse(home))

def logout_post(request) :
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse(index))
    
def register(request) :
    if not request.user.is_authenticated:
        if request.method == "POST" :
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]

            if password != confirm_password :
                return render(request, "doc/register.html", {
                    "message" : "Password does not match"
                })
            
            try : 
                user = User.objects.create_user(username, email, password)
                user.save()

            except IntegrityError:
                return render(request, "doc/register.html", {
                    "message" : "A user with that username already exist"
                })
            
            login(request, user)
            return HttpResponseRedirect(reverse(index))

        else:
            return render(request, "doc/register.html")
    else:
        return HttpResponseRedirect(reverse(index))
    
def pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            refno =request.POST['refno']
            date = request.POST['date']
            dept=request.POST['dept']
            debit_head=request.POST['debit_head']
            item_name=request.POST['item_name']
            type=request.POST['type']
            quantity=request.POST['quantity']
            estcost=request.POST['estcost']
            approvedby=request.POST['approvedby']
            file_type=request.POST['file_type']
            if 'expert1Name' in request.POST and request.POST['expert1Name']:
                    expert1Name = request.POST['expert1Name']
            else:
                    expert1Name = None   
            if 'expert2Name' in request.POST and request.POST['expert2Name']:
                    expert2Name = request.POST['expert2Name']
            else:
                    expert2Name = None        
            try:
                new_userdata = UserData(
                    user=request.user,
                    refno = refno,  
                    date=date,
                    dept=dept,
                    debit_head=debit_head,
                    item_name=item_name,
                    type=type,
                    quantity=quantity,
                    estcost=estcost,
                    expert1Name=expert1Name,
                    expert2Name=expert2Name,
                    approvedby=approvedby
                )
                if 'facsign' in request.FILES:
                    new_userdata.facsign = request.FILES.get['facsign']
                if 'hodsign' in request.FILES:
                    new_userdata.hodsign = request.FILES.get['hodsign']
                if 'deansign' in request.FILES:
                    new_userdata.deansign = request.FILES.get['deansign']
                new_userdata.save()
            except IntegrityError:
                get_userdata = UserData.objects.get(
                    user=request.user
                )
                get_userdata.refno = refno  
                get_userdata.date=date
                get_userdata.dept=dept
                get_userdata.debit_head=debit_head
                get_userdata.item_name=item_name
                get_userdata.type=type
                get_userdata.quantity=quantity
                get_userdata.estcost=estcost
                get_userdata.expert1Name=expert1Name
                get_userdata.expert2Name=expert2Name
                get_userdata.approvedby=approvedby
                get_userdata.facsign = request.FILES.get('facsign', '../media/users/img.jpg')
                get_userdata.hodsign = request.FILES.get('hodsign', '../media/users/img.jpg')
                get_userdata.deansign = request.FILES.get('deansign', '../media/users/img.jpg')
                get_userdata.save()
                new_userdata=get_userdata
            new_userdata = UserData.objects.get(user = request.user)
            template = get_template('doc/pdf.html')
            context = {
                'refno': new_userdata.refno,
                'date':new_userdata.date,
                'dept':new_userdata.dept,
                'debit_head':new_userdata.debit_head,
                'item_name':new_userdata.item_name,
                'type':new_userdata.type,
                'quantity':new_userdata.quantity,
                'estcost':new_userdata.estcost,
                'expert1Name':new_userdata.expert1Name,
                'expert2Name':new_userdata.expert2Name,
                'hodsign':new_userdata.hodsign,
                'facsign':new_userdata.facsign,
                'deansign':new_userdata.deansign,
                'approvedby':new_userdata.approvedby,
                'file_type':file_type
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response

def doc2(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc2.html', {'user_data': user_data})

def doc2pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            refno2 =request.POST['refno2']
            date2 = request.POST['date2']
            venue=request.POST['venue']
            if 'expert1Name' in request.POST and request.POST['expert1Name']:
                    expert1Name = request.POST['expert1Name']
            else:
                    expert1Name = None   
            if 'expert2Name' in request.POST and request.POST['expert2Name']:
                    expert2Name = request.POST['expert2Name']
            else:
                    expert2Name = None     
            doc2_user_data = UserData.objects.get(user=request.user)   
            doc2_user_data.refno2 = refno2  
            doc2_user_data.date2=date2
            doc2_user_data.venue=venue
            doc2_user_data.expert1Name=expert1Name
            doc2_user_data.expert2Name=expert2Name
            doc2_user_data.save()
            context = {
                'debit_head':doc2_user_data.debit_head,
                'item_name':doc2_user_data.item_name,
                'quantity':doc2_user_data.quantity,
                'estcost':doc2_user_data.estcost,
                'hodsign':doc2_user_data.hodsign,
                'facsign':doc2_user_data.facsign,
                'deansign':doc2_user_data.deansign,
                'approvedby':doc2_user_data.approvedby,
                'refno':doc2_user_data.refno,
                'refno2': doc2_user_data.refno2,
                'date':doc2_user_data.date,
                'date2':doc2_user_data.date2,
                'dept':doc2_user_data.dept,
                'venue':doc2_user_data.venue,
                'type':doc2_user_data.type,
                'expert1Name':doc2_user_data.expert1Name,
                'expert2Name':doc2_user_data.expert2Name,
            }
            template = get_template('doc/doc2pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc2.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')
def doc3(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc3.html', {'user_data': user_data})

def doc3pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            warranty =request.POST['warranty']
            suppliers =request.POST['suppliers']
            listnadd =request.POST['listnadd']
            doc3_user_data = UserData.objects.get(user=request.user)   
            doc3_user_data.warranty=warranty
            doc3_user_data.suppliers=suppliers
            doc3_user_data.listnadd=listnadd 
            if 'addsheet' in request.FILES:
                addsheet = request.FILES.get('addsheet')
                doc3_user_data.addsheet = addsheet
                doc3_user_data.save()
            doc3_user_data.save()
            context = {
                'debit_head':doc3_user_data.debit_head,
                'item_name':doc3_user_data.item_name,
                'quantity':doc3_user_data.quantity,
                'estcost':doc3_user_data.estcost,
                'hodsign':doc3_user_data.hodsign,
                'facsign':doc3_user_data.facsign,
                'deansign':doc3_user_data.deansign,
                'approvedby':doc3_user_data.approvedby,
                'refno':doc3_user_data.refno,
                'refno2': doc3_user_data.refno2,
                'date':doc3_user_data.date,
                'date2':doc3_user_data.date2,
                'dept':doc3_user_data.dept,
                'venue':doc3_user_data.venue,
                'type':doc3_user_data.type,
                'expert1Name':doc3_user_data.expert1Name,
                'expert2Name':doc3_user_data.expert2Name,
                'warranty':doc3_user_data.warranty,
                'suppliers':doc3_user_data.suppliers,
                'listnadd':doc3_user_data.listnadd,
                'addsheet':doc3_user_data.addsheet
            }
            template = get_template('doc/doc3pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc3.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')

def doc4q(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc4q.html', {'user_data': user_data})

def doc4qpdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            notino =request.POST['notino']
            date4q =request.POST['date4q']
            name_goods =request.POST['name_goods']
            estamt =request.POST['estamt']
            timesupply =request.POST['timesupply']
            datebid =request.POST['datebid']
            addbid =request.POST['addbid']
            item_proc =request.POST['item_proc']
            spec =request.POST['spec']
            quantity_doc4q =request.POST['quantity_doc4q']
            warranty_doc4q =request.POST['warranty_doc4q']
            del_sched =request.POST['del_sched']
            details =request.POST['details']
            curr =request.POST['curr']
            name_add_firm=request.POST['name_add_firm']
            name_add_auth=request.POST['name_add_auth']
            name_des_bid=request.POST['name_des_bid']
            tax_dut =request.POST['tax_dut']
            other_charges =request.POST['other_charges']
            bus_add =request.POST['bus_add']

            doc4q_user_data = UserData.objects.get(user=request.user)   
            doc4q_user_data.notino=notino
            doc4q_user_data.date4q=date4q
            doc4q_user_data.name_goods=name_goods 
            doc4q_user_data.estamt=estamt
            doc4q_user_data.timesupply=timesupply
            doc4q_user_data.datebid=datebid
            doc4q_user_data.addbid=addbid
            doc4q_user_data.item_proc=item_proc
            doc4q_user_data.spec=spec
            doc4q_user_data.quantity_doc4q=quantity_doc4q
            doc4q_user_data.warranty_doc4q=warranty_doc4q
            doc4q_user_data.del_sched=del_sched
            doc4q_user_data.details=details
            doc4q_user_data.curr=curr
            doc4q_user_data.name_add_firm=name_add_firm
            doc4q_user_data.name_add_auth=name_add_auth
            doc4q_user_data.name_des_bid=name_des_bid
            doc4q_user_data.tax_dut=tax_dut
            doc4q_user_data.other_charges=other_charges
            doc4q_user_data.bus_add=bus_add
            doc4q_user_data.save()
            context = {
                'debit_head':doc4q_user_data.debit_head,
                'item_name':doc4q_user_data.item_name,
                'quantity':doc4q_user_data.quantity,
                'estcost':doc4q_user_data.estcost,
                'hodsign':doc4q_user_data.hodsign,
                'facsign':doc4q_user_data.facsign,
                'deansign':doc4q_user_data.deansign,
                'approvedby':doc4q_user_data.approvedby,
                'refno':doc4q_user_data.refno,
                'refno2': doc4q_user_data.refno2,
                'date':doc4q_user_data.date,
                'date2':doc4q_user_data.date2,
                'dept':doc4q_user_data.dept,
                'venue':doc4q_user_data.venue,
                'type':doc4q_user_data.type,
                'expert1Name':doc4q_user_data.expert1Name,
                'expert2Name':doc4q_user_data.expert2Name,
                'warranty':doc4q_user_data.warranty,
                'suppliers':doc4q_user_data.suppliers,
                'listnadd':doc4q_user_data.listnadd,
                'addsheet':doc4q_user_data.addsheet,
                'notino':doc4q_user_data.notino,
                'date4q':doc4q_user_data.date4q,
                'name_goods':doc4q_user_data.name_goods,
                'estamt':doc4q_user_data.estamt,
                'timesupply':doc4q_user_data.timesupply,
                'datebid':doc4q_user_data.datebid,
                'addbid':doc4q_user_data.addbid,
                'item_proc':doc4q_user_data.item_proc,
                'spec':doc4q_user_data.spec,
                'quantity_doc4q':doc4q_user_data.quantity_doc4q,
                'warranty_doc4q':doc4q_user_data.warranty_doc4q,
                'del_sched':doc4q_user_data.del_sched,
                'details':doc4q_user_data.details,
                'curr':doc4q_user_data.curr,
                'name_add_firm':doc4q_user_data.name_add_firm,
                'name_add_auth':doc4q_user_data.name_add_auth,
                'name_des_bid':doc4q_user_data.name_des_bid,
                'tax_dut':doc4q_user_data.tax_dut,
                'other_charges':doc4q_user_data.other_charges,
                'bus_add':doc4q_user_data.bus_add,
            }
            template = get_template('doc/doc4qpdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc4Q.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
        
def doc4t1(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc4t1.html', {'user_data': user_data})

def doc4t1pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            warranty =request.POST['warranty']
            suppliers =request.POST['suppliers']
            listnadd =request.POST['listnadd']
            doc3_user_data = UserData.objects.get(user=request.user)   
            doc3_user_data.warranty=warranty
            doc3_user_data.suppliers=suppliers
            doc3_user_data.listnadd=listnadd 
            if 'addsheet' in request.FILES:
                addsheet = request.FILES.get('addsheet')
                doc3_user_data.addsheet = addsheet
                doc3_user_data.save()
            doc3_user_data.save()
            context = {
                'debit_head':doc3_user_data.debit_head,
                'item_name':doc3_user_data.item_name,
                'quantity':doc3_user_data.quantity,
                'estcost':doc3_user_data.estcost,
                'hodsign':doc3_user_data.hodsign,
                'facsign':doc3_user_data.facsign,
                'deansign':doc3_user_data.deansign,
                'approvedby':doc3_user_data.approvedby,
                'refno':doc3_user_data.refno,
                'refno2': doc3_user_data.refno2,
                'date':doc3_user_data.date,
                'date2':doc3_user_data.date2,
                'dept':doc3_user_data.dept,
                'venue':doc3_user_data.venue,
                'type':doc3_user_data.type,
                'expert1Name':doc3_user_data.expert1Name,
                'expert2Name':doc3_user_data.expert2Name,
                'warranty':doc3_user_data.warranty,
                'suppliers':doc3_user_data.suppliers,
                'listnadd':doc3_user_data.listnadd,
                'addsheet':doc3_user_data.addsheet
            }
            template = get_template('doc/doc3pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc3.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')
    
def doc4t2(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc4t2.html', {'user_data': user_data})

def doc4t2pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            warranty =request.POST['warranty']
            suppliers =request.POST['suppliers']
            listnadd =request.POST['listnadd']
            doc3_user_data = UserData.objects.get(user=request.user)   
            doc3_user_data.warranty=warranty
            doc3_user_data.suppliers=suppliers
            doc3_user_data.listnadd=listnadd 
            if 'addsheet' in request.FILES:
                addsheet = request.FILES.get('addsheet')
                doc3_user_data.addsheet = addsheet
                doc3_user_data.save()
            doc3_user_data.save()
            context = {
                'debit_head':doc3_user_data.debit_head,
                'item_name':doc3_user_data.item_name,
                'quantity':doc3_user_data.quantity,
                'estcost':doc3_user_data.estcost,
                'hodsign':doc3_user_data.hodsign,
                'facsign':doc3_user_data.facsign,
                'deansign':doc3_user_data.deansign,
                'approvedby':doc3_user_data.approvedby,
                'refno':doc3_user_data.refno,
                'refno2': doc3_user_data.refno2,
                'date':doc3_user_data.date,
                'date2':doc3_user_data.date2,
                'dept':doc3_user_data.dept,
                'venue':doc3_user_data.venue,
                'type':doc3_user_data.type,
                'expert1Name':doc3_user_data.expert1Name,
                'expert2Name':doc3_user_data.expert2Name,
                'warranty':doc3_user_data.warranty,
                'suppliers':doc3_user_data.suppliers,
                'listnadd':doc3_user_data.listnadd,
                'addsheet':doc3_user_data.addsheet
            }
            template = get_template('doc/doc3pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc3.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')

def doc5(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc5.html', {'user_data': user_data})

def doc5pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            refno5 =request.POST['refno5']
            date5 =request.POST['date5']
            doc5_user_data = UserData.objects.get(user=request.user)   
            doc5_user_data.refno5=refno5
            doc5_user_data.date5=date5
            doc5_user_data.save()
            context = {
                'debit_head':doc5_user_data.debit_head,
                'item_name':doc5_user_data.item_name,
                'quantity':doc5_user_data.quantity,
                'estcost':doc5_user_data.estcost,
                'hodsign':doc5_user_data.hodsign,
                'facsign':doc5_user_data.facsign,
                'deansign':doc5_user_data.deansign,
                'approvedby':doc5_user_data.approvedby,
                'refno':doc5_user_data.refno,
                'refno2': doc5_user_data.refno2,
                'refno5': doc5_user_data.refno5,
                'date':doc5_user_data.date,
                'date2':doc5_user_data.date2,
                'date5':doc5_user_data.date5,
                'dept':doc5_user_data.dept,
                'venue':doc5_user_data.venue,
                'type':doc5_user_data.type,
                'expert1Name':doc5_user_data.expert1Name,
                'expert2Name':doc5_user_data.expert2Name,
                'warranty':doc5_user_data.warranty,
                'suppliers':doc5_user_data.suppliers,
                'listnadd':doc5_user_data.listnadd,
                'addsheet':doc5_user_data.addsheet
            }
            template = get_template('doc/doc5pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc5.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')

def doc6(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc6.html', {'user_data': user_data})

def doc6pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            refno6=request.POST['refno6']
            date6=request.POST['date6']
            bidno=request.POST['bidno']
            bidrepno=request.POST['bidrepno']
            bidaccno=request.POST['bidaccno']
            bidaccnames=request.POST['bidaccnames']
            bidrejno=request.POST['bidrejno']
            bidrejnames=request.POST['bidrejnames']
            datefinbid=request.POST['datefinbid']
            doc6_user_data = UserData.objects.get(user=request.user)   
            doc6_user_data.refno6=refno6
            doc6_user_data.date6=date6
            doc6_user_data.bidno=bidno 
            doc6_user_data.bidrepno=bidrepno
            doc6_user_data.bidaccno=bidaccno
            doc6_user_data.bidaccnames=bidaccnames
            doc6_user_data.bidrejno=bidrejno
            doc6_user_data.bidrejnames=bidrejnames
            doc6_user_data.datefinbid=datefinbid
            # if 'addsheet' in request.FILES:
            #     addsheet = request.FILES.get('addsheet')
            #     doc3_user_data.addsheet = addsheet
            #     doc3_user_data.save()
            doc6_user_data.save()
            context = {
                'debit_head':doc6_user_data.debit_head,
                'item_name':doc6_user_data.item_name,
                'quantity':doc6_user_data.quantity,
                'estcost':doc6_user_data.estcost,
                'hodsign':doc6_user_data.hodsign,
                'facsign':doc6_user_data.facsign,
                'deansign':doc6_user_data.deansign,
                'approvedby':doc6_user_data.approvedby,
                'refno':doc6_user_data.refno,
                'refno2': doc6_user_data.refno2,
                'date':doc6_user_data.date,
                'date2':doc6_user_data.date2,
                'dept':doc6_user_data.dept,
                'venue':doc6_user_data.venue,
                'type':doc6_user_data.type,
                'expert1Name':doc6_user_data.expert1Name,
                'expert2Name':doc6_user_data.expert2Name,
                'warranty':doc6_user_data.warranty,
                'suppliers':doc6_user_data.suppliers,
                'listnadd':doc6_user_data.listnadd,
                'addsheet':doc6_user_data.addsheet,
                'refno6':doc6_user_data.refno6,
                'date6':doc6_user_data.date6,
                'bidno':doc6_user_data.bidno,
                'bidrepno':doc6_user_data.bidrepno,
                'bidaccno':doc6_user_data.bidaccno,
                'bidaccnames':doc6_user_data.bidaccnames,
                'bidrejnames':doc6_user_data.bidrejnames,
                'bidrejno':doc6_user_data.bidrejno,
                'datefinbid':doc6_user_data.datefinbid
            }
            template = get_template('doc/doc6pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc6.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')

def doc78(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc78.html', {'user_data': user_data})

def doc78pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            refno7=request.POST['refno6']
            date7=request.POST['date6']
            bidno=request.POST['bidno']
            bidrepno=request.POST['bidrepno']
            bidaccno=request.POST['bidaccno']
            bidaccnames=request.POST['bidaccnames']
            bidrejno=request.POST['bidrejno']
            bidrejnames=request.POST['bidrejnames']
            datefinbid=request.POST['datefinbid']
            doc6_user_data = UserData.objects.get(user=request.user)   
            doc6_user_data.refno7=refno7
            doc6_user_data.date7=date7
            doc6_user_data.bidno=bidno 
            doc6_user_data.bidrepno=bidrepno
            doc6_user_data.bidaccno=bidaccno
            doc6_user_data.bidaccnames=bidaccnames
            doc6_user_data.bidrejno=bidrejno
            doc6_user_data.bidrejnames=bidrejnames
            doc6_user_data.datefinbid=datefinbid
            # if 'addsheet' in request.FILES:
            #     addsheet = request.FILES.get('addsheet')
            #     doc3_user_data.addsheet = addsheet
            #     doc3_user_data.save()
            doc6_user_data.save()
            context = {
                'debit_head':doc6_user_data.debit_head,
                'item_name':doc6_user_data.item_name,
                'quantity':doc6_user_data.quantity,
                'estcost':doc6_user_data.estcost,
                'hodsign':doc6_user_data.hodsign,
                'facsign':doc6_user_data.facsign,
                'deansign':doc6_user_data.deansign,
                'approvedby':doc6_user_data.approvedby,
                'refno':doc6_user_data.refno,
                'refno2': doc6_user_data.refno2,
                'date':doc6_user_data.date,
                'date2':doc6_user_data.date2,
                'dept':doc6_user_data.dept,
                'venue':doc6_user_data.venue,
                'type':doc6_user_data.type,
                'expert1Name':doc6_user_data.expert1Name,
                'expert2Name':doc6_user_data.expert2Name,
                'warranty':doc6_user_data.warranty,
                'suppliers':doc6_user_data.suppliers,
                'listnadd':doc6_user_data.listnadd,
                'addsheet':doc6_user_data.addsheet,
                'refno6':doc6_user_data.refno6,
                'date6':doc6_user_data.date6,
                'bidno':doc6_user_data.bidno,
                'bidrepno':doc6_user_data.bidrepno,
                'bidaccno':doc6_user_data.bidaccno,
                'bidaccnames':doc6_user_data.bidaccnames,
                'bidrejnames':doc6_user_data.bidrejnames,
                'bidrejno':doc6_user_data.bidrejno,
                'datefinbid':doc6_user_data.datefinbid
            }
            template = get_template('doc/doc6pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc6.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')

def doc9(request):
    if request.user.is_authenticated :
        user_data = UserData.objects.filter(user=request.user)
    else:
        user_data = None
    return render(request, 'doc/doc9.html', {'user_data': user_data})

def doc9pdfgen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            refno9=request.POST['refno6']
            date9=request.POST['date6']
            bidno=request.POST['bidno']
            bidrepno=request.POST['bidrepno']
            bidaccno=request.POST['bidaccno']
            bidaccnames=request.POST['bidaccnames']
            bidrejno=request.POST['bidrejno']
            bidrejnames=request.POST['bidrejnames']
            datefinbid=request.POST['datefinbid']
            doc6_user_data = UserData.objects.get(user=request.user)   
            doc6_user_data.refno9=refno9
            doc6_user_data.date6=date9
            doc6_user_data.bidno9=bidno 
            doc6_user_data.bidrepno=bidrepno
            doc6_user_data.bidaccno=bidaccno
            doc6_user_data.bidaccnames=bidaccnames
            doc6_user_data.bidrejno=bidrejno
            doc6_user_data.bidrejnames=bidrejnames
            doc6_user_data.datefinbid=datefinbid
            # if 'addsheet' in request.FILES:
            #     addsheet = request.FILES.get('addsheet')
            #     doc3_user_data.addsheet = addsheet
            #     doc3_user_data.save()
            doc6_user_data.save()
            context = {
                'debit_head':doc6_user_data.debit_head,
                'item_name':doc6_user_data.item_name,
                'quantity':doc6_user_data.quantity,
                'estcost':doc6_user_data.estcost,
                'hodsign':doc6_user_data.hodsign,
                'facsign':doc6_user_data.facsign,
                'deansign':doc6_user_data.deansign,
                'approvedby':doc6_user_data.approvedby,
                'refno':doc6_user_data.refno,
                'refno2': doc6_user_data.refno2,
                'date':doc6_user_data.date,
                'date2':doc6_user_data.date2,
                'dept':doc6_user_data.dept,
                'venue':doc6_user_data.venue,
                'type':doc6_user_data.type,
                'expert1Name':doc6_user_data.expert1Name,
                'expert2Name':doc6_user_data.expert2Name,
                'warranty':doc6_user_data.warranty,
                'suppliers':doc6_user_data.suppliers,
                'listnadd':doc6_user_data.listnadd,
                'addsheet':doc6_user_data.addsheet,
                'refno6':doc6_user_data.refno6,
                'date6':doc6_user_data.date6,
                'bidno':doc6_user_data.bidno,
                'bidrepno':doc6_user_data.bidrepno,
                'bidaccno':doc6_user_data.bidaccno,
                'bidaccnames':doc6_user_data.bidaccnames,
                'bidrejnames':doc6_user_data.bidrejnames,
                'bidrejno':doc6_user_data.bidrejno,
                'datefinbid':doc6_user_data.datefinbid
            }
            template = get_template('doc/doc6pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="my_document_doc6.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
            #return render(request, 'doc/doc2.html')
    
    