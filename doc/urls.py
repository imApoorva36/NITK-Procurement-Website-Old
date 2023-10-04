from django.urls import path
from . import views

urlpatterns=[
    path("",views.index, name="index"),
    path("home/",views.home, name="home"),
    path("login/", views.login_post, name="login"),
    path("logout/",views.logout_post,name="logout"),
    path("register/",views.register,name="register"),
    path("pdfgen/",views.pdfgen,name="pdfgen"),
    path("doc2/",views.doc2,name="doc2"),
    path("doc2pdfgen/",views.doc2pdfgen,name="doc2pdf"),
    path("doc3/",views.doc3,name="doc3"),
    path("doc3pdfgen/",views.doc3pdfgen,name="doc3pdf"),
    path("doc4q/",views.doc4q,name="doc4q"),
    path("doc4qpdfgen/",views.doc4qpdfgen,name="doc4qpdf"),
    path("doc4t1/",views.doc4t1,name="doc4t1"),
    path("doc4t1pdfgen/",views.doc4t1pdfgen,name="doc4t1pdf"),
    path("doc4t2/",views.doc4t2,name="doc4t2"),
    path("doc4t2pdfgen/",views.doc4t2pdfgen,name="doc4t2pdf"),
    path("doc5/",views.doc5,name="doc5"),
    path("doc5pdfgen/",views.doc5pdfgen,name="doc5pdf"),
    path("doc6/",views.doc6,name="doc6"),
    path("doc6pdfgen/",views.doc6pdfgen,name="doc6pdf"),
    path("doc78/",views.doc78,name="doc78"),
    path("doc78pdfgen/",views.doc78pdfgen,name="doc78pdf"),
    path("doc9/",views.doc9,name="doc9"),
    path("doc9pdfgen/",views.doc9pdfgen,name="doc9pdf"),
]