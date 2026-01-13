from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django_filters.views import FilterView
from .forms import StockForm
from num2words import num2words

from .models import Stock


from .filters import StockFilter


# =====================================================
# HELPER FUNCTION: AMOUNT IN WORDS
# =====================================================

def amount_in_words(amount):
    return num2words(amount, to='currency', lang='en')


# =====================================================
# STOCK MANAGEMENT VIEWS
# =====================================================

class StockListView(FilterView):
    filterset_class = StockFilter
    queryset = Stock.objects.filter(is_deleted=False)
    template_name = "inventory.html"
    paginate_by = 10


class StockCreateView(SuccessMessageMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = "edit_stock.html"
    success_url = "/inventory"
    success_message = "Stock has been created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Stock"
        context["savebtn"] = "Add to Inventory"
        return context


class StockUpdateView(SuccessMessageMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "edit_stock.html"
    success_url = "/inventory"
    success_message = "Stock has been updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Stock"
        context["savebtn"] = "Update Stock"
        context["delbtn"] = "Delete Stock"
        return context


class StockDeleteView(View):
    template_name = "delete_stock.html"

    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {"object": stock})

    def post(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        stock.is_deleted = True
        stock.save()
        messages.success(request, "Stock has been deleted successfully")
        return redirect("inventory")


# =====================================================
# SALES & INVOICE CREATION (WITH AMOUNT IN WORDS)
# =====================================================

class SaleCreateView(View):
    template_name = "sales/new_sale.html"

    def get(self, request):
        form = SaleForm()
        formset = SaleItemFormset()
        stocks = Stock.objects.filter(is_deleted=False)

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "stocks": stocks
        })

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)

        if form.is_valid() and formset.is_valid():
            bill = form.save()
            subtotal = 0

            for f in formset:
                item = f.save(commit=False)
                item.billno = bill
                item.totalprice = item.quantity * item.perprice
                subtotal += item.totalprice

                stock = get_object_or_404(Stock, name=item.stock.name)
                stock.quantity -= item.quantity
                stock.save()

                item.save()

            # Calculations
            vat = round(subtotal * 0.15, 2)
            withholding = round(subtotal * 0.03, 2)
            total = round(subtotal + vat - withholding, 2)

            # Save invoice summary
            SaleBillDetails.objects.create(
                billno=bill,
                subtotal=subtotal,
                vat=vat,
                withholding=withholding,
                total=total,
                total_words=amount_in_words(total)
            )

            messages.success(request, "Sales invoice created successfully")
            return redirect("transactions:sale-bill", billno=bill.billno)
            

        return render(request, self.template_name, {
            "form": form,
            "formset": formset
        })
