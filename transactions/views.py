from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from num2words import num2words
from django.http import HttpResponse
import csv

from .models import (
    Supplier, PurchaseBill, PurchaseItem, PurchaseBillDetails,
    SaleBill, SaleItem, SaleBillDetails
)
from inventory.models import Stock
from .forms import (
    SupplierForm, SelectSupplierForm,
    PurchaseItemFormset, PurchaseDetailsForm,
    SaleForm, SaleItemFormset, SaleDetailsForm
)

# ------------------- DASHBOARD -------------------
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
# transactions/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, View
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Supplier
from .forms import SupplierForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ------------------- SUPPLIER VIEWS -------------------

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Supplier

class SupplierListView(ListView):
    model = Supplier
    template_name = 'transactions/supplier_list.html'
    context_object_name = 'transactions:suppliers-list'

class SupplierCreateView(CreateView):
    model = Supplier
    fields = ['name', 'phone', 'email', 'address']
    template_name = 'transactions/supplier_form.html'
    success_url = reverse_lazy('transactions:suppliers-list')  # ✅

    def form_valid(self, form):
        messages.success(self.request, "Supplier created successfully!")
        return super().form_valid(form)

class SupplierUpdateView(UpdateView):
    model = Supplier
    fields = ['name', 'phone', 'email', 'address']
    template_name = 'transactions/supplier_form.html'
    success_url = reverse_lazy('transactions:suppliers-list')  # ✅

    def form_valid(self, form):
        messages.success(self.request, "Supplier updated successfully!")
        return super().form_valid(form)

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'transactions/supplier_confirm_delete.html'
    success_url = reverse_lazy('transactions:suppliers-list')  # ✅

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Supplier deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'transactions/supplier_detail.html'
    context_object_name = 'transactions:suppliers-list'

class SelectSupplierView(ListView):
    model = Supplier
    template_name = 'purchases/select_supplier.html'
    context_object_name = 'transactions:suppliers-list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        suppliers = context['transactions:suppliers-list']
        paginator = Paginator(suppliers, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            suppliers_page = paginator.page(page)
        except PageNotAnInteger:
            suppliers_page = paginator.page(1)
        except EmptyPage:
            suppliers_page = paginator.page(paginator.num_pages)

        context['transactions:suppliers-list'] = suppliers_page
        return context

# ------------------- PURCHASE VIEWS -------------------
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

class PurchaseCreateView(View):
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        formset = PurchaseItemFormset()
        return render(request, self.template_name, {'formset': formset, 'supplier': supplier})

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        formset = PurchaseItemFormset(request.POST)

        if formset.is_valid():
            bill = PurchaseBill.objects.create(supplier=supplier)
            PurchaseBillDetails.objects.create(billno=bill)

            for form in formset:
                item = form.save(commit=False)
                item.billno = bill
                item.totalprice = item.perprice * item.quantity

                stock = get_object_or_404(Stock, name=item.stock.name)
                stock.quantity += item.quantity
                stock.save()

                item.save()

            messages.success(request, "Purchased items registered successfully.")
            return redirect('transactions:purchase-bill', billno=bill.billno)

        return render(request, self.template_name, {'formset': formset, 'supplier': supplier})

class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "delete_purchase.html"
    success_url = reverse_lazy('purchases-list')

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        for item in PurchaseItem.objects.filter(billno=self.object.billno):
            stock = get_object_or_404(Stock, name=item.stock.name)
            if not stock.is_deleted:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill deleted successfully.")
        return super().delete(*args, **kwargs)

class PurchaseBillView(View):
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        bill = get_object_or_404(PurchaseBill, billno=billno)
        items = PurchaseItem.objects.filter(billno=billno)
        details = get_object_or_404(PurchaseBillDetails, billno=billno)
        subtotal = sum(item.totalprice for item in items)
        vat = subtotal * 0.15
        wh = subtotal * 0.03
        net_total = subtotal + vat - wh
        amount_in_words = num2words(round(net_total, 2), lang='en').title()

        context = {
            'bill': bill,
            'items': items,
            'billdetails': details,
            'bill_base': self.bill_base,
            'subtotal': subtotal,
            'vat': vat,
            'wh': wh,
            'net_total': net_total,
            'amount_in_words': amount_in_words
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            details = get_object_or_404(PurchaseBillDetails, billno=billno)
            for field, value in form.cleaned_data.items():
                setattr(details, field, value)
            details.save()
            messages.success(request, "Purchase bill updated.")
        return self.get(request, billno)

# ------------------- SALE VIEWS -------------------
from django.views.generic import DetailView
from num2words import num2words
from .models import SaleBill, SaleItem, SaleBillDetails

from django.views.generic import ListView
from num2words import num2words
from .models import SaleBill, SaleItem, SaleBillDetails

class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bills = context['bills']

        # Prepare a list of bills with totals and amounts in words
        bills_with_totals = []

        for bill in bills:
            items = SaleItem.objects.filter(billno=bill.billno)
            details = SaleBillDetails.objects.filter(billno=bill.billno).first()  # optional details

            subtotal = sum(item.totalprice for item in items)
            vat = subtotal * 0.15
            total_after_vat = subtotal + vat
            withhold = total_after_vat * 0.03
            net_total = total_after_vat - withhold

            # Convert net total to words
            try:
                amount_in_words = num2words(round(net_total, 2), to='currency', lang='en').title()
            except:
                amount_in_words = "N/A"

            bills_with_totals.append({
                'bill': bill,
                'items': items,
                'details': details,
                'subtotal': subtotal,
                'vat': vat,
                'withhold': withhold,
                'net_total': net_total,
                'amount_in_words': amount_in_words
            })

        context['bills_with_totals'] = bills_with_totals
        return context


class SaleBillView(DetailView):
    model = SaleBill
    template_name = 'sales/sale_bill.html'
    context_object_name = 'bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bill = self.object
        items = SaleItem.objects.filter(billno=bill.billno)  # fetch items
        details = SaleBillDetails.objects.get(billno=bill.billno)  # fetch details

        # Calculate totals
        subtotal = sum(item.totalprice for item in items)
        vat = subtotal * 0.15
        total_after_vat = subtotal + vat
        withhold = total_after_vat * 0.03
        net_payable = total_after_vat - withhold

        # Convert net amount to words safely
        amount_in_words = num2words(round(net_payable, 2), to='currency', lang='en').title()

        context.update({
            'items': items,
            'billdetails': details,
            'subtotal': subtotal,
            'vat': vat,
            'withhold': withhold,
            'net_total': net_payable,
            'amount_in_words': amount_in_words
        })
        return context



class SaleCreateView(View):
    template_name = 'sales/new_sale.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': SaleForm(),
            'formset': SaleItemFormset(),
            'stocks': Stock.objects.filter(is_deleted=False)
        })

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)
        if form.is_valid() and formset.is_valid():
            bill = form.save()
            SaleBillDetails.objects.create(billno=bill)

            for form in formset:
                item = form.save(commit=False)
                item.billno = bill
                item.totalprice = item.perprice * item.quantity
                stock = get_object_or_404(Stock, name=item.stock.name)
                stock.quantity -= item.quantity
                stock.save()
                item.save()

            messages.success(request, "Sale registered successfully.")
            return redirect('transactions:sale-bill', billno=bill.billno)

        return render(request, self.template_name, {'form': form, 'formset': formset})

class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = reverse_lazy('sales-list')

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        for item in SaleItem.objects.filter(billno=self.object.billno):
            stock = get_object_or_404(Stock, name=item.stock.name)
            if not stock.is_deleted:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill deleted successfully.")

        return super().delete(*args, **kwargs)

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'transactions/supplier_confirm_delete.html'
    success_url = reverse_lazy('transactions:suppliers')

class SaleBillView(View):
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        bill = get_object_or_404(SaleBill, billno=billno)
        items = SaleItem.objects.filter(billno=billno)
        details = get_object_or_404(SaleBillDetails, billno=billno)

        # Calculate totals
        subtotal = sum(item.totalprice for item in items)
        vat = subtotal * 0.15
        total_after_vat = subtotal + vat
        withhold = total_after_vat * 0.03
        net_payable = total_after_vat - withhold
        net_in_words = num2words(round(net_payable, 2), lang='en').title()

        context = {
            'bill': bill,
            'items': items,
            'billdetails': details,
            'bill_base': self.bill_base,
            'subtotal': subtotal,
            'vat': vat,
            'withhold': withhold,
            'net_total': net_payable,
            'amount_in_words': net_in_words
        }

        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            details = get_object_or_404(SaleBillDetails, billno=billno)
            for field, value in form.cleaned_data.items():
                setattr(details, field, value)
            details.save()
            messages.success(request, "Sale bill updated.")
        return self.get(request, billno)


class SaleUpdateView(UpdateView):
    model = SaleBill
    fields = ['name', 'phone', 'address', 'tin']  # adjust if needed
    template_name = 'sales/edit_sale.html'
    success_url = reverse_lazy('transactions:sales-list')
# ------------------- EXPORT FUNCTIONS -------------------
# transactions/views.py
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from django.shortcuts import get_object_or_404
from .models import SaleBill, SaleBillDetails


# -----------------------------
# Export to Excel
# -----------------------------
def export_sale_excel(request, billno):
    # Get the sale bill
    sale = get_object_or_404(SaleBill, billno=billno)
    sale_details = SaleBillDetails.objects.filter(billno=sale)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sale_{billno}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Stock', 'Quantity', 'Price', 'Subtotal'])

    total_price = 0
    for details in sale_details:
        subtotal = details.quantity * details.price
        total_price += subtotal
        writer.writerow([details.stock.name, details.quantity, details.price, subtotal])

    # Write total at the end
    writer.writerow([])
    writer.writerow(['', '', 'Total', total_price])

    return response


# -----------------------------
# Export to PDF
# -----------------------------
def export_sale_pdf(request, billno):
    sale = get_object_or_404(SaleBill, billno=billno)
    sale_details = SaleBillDetails.objects.filter(billno=sale)

    # Prepare data for the template
    total_price = sum(d.quantity * d.price for d in sale_details)
    context = {
        'sale': sale,
        'sale_details': sale_details,
        'total_price': total_price,
    }

    html_string = render_to_string('transactions/sale_pdf_template.html', context)
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sale_{billno}.pdf"'
    html.write_pdf(response)

    return response


# -----------------------------
# Export to Word
# -----------------------------
def export_sale_word(request, billno):
    sale = get_object_or_404(SaleBill, billno=billno)
    sale_details = SaleBillDetails.objects.filter(billno=sale)

    doc = Document()
    doc.add_heading(f'Sale Bill #{sale.billno}', level=1)
    doc.add_paragraph(f'Customer: {sale.name} | Phone: {sale.phone}')
    doc.add_paragraph(f'Date: {sale.time.date}')

    # Add table
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Stock'
    hdr_cells[1].text = 'Quantity'
    hdr_cells[2].text = 'Price'
    hdr_cells[3].text = 'Subtotal'

    total_price = 0
    for details in sale_details:
        subtotal = details.quantity * details.price
        total_price += subtotal
        row_cells = table.add_row().cells
        row_cells[0].text = details.stock.name
        row_cells[1].text = str(details.quantity)
        row_cells[2].text = str(details.price)
        row_cells[3].text = str(subtotal)

    # Add total at the end
    doc.add_paragraph('')
    doc.add_paragraph(f'Total: {total_price}')

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="sale_{billno}.docx"'
    doc.save(response)

    return response

