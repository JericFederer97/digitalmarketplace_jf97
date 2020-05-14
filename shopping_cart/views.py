from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from books.models import Book
from .models import Order, OrderItem, Payment

import string
import random


# Stripe settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))


def add_to_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item, created = OrderItem.objects.get_or_create(book=book)
    order, created = Order.objects.get_or_create(user=request.user)
    order.items.add(order_item)
    order.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_from_cart(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    order_item = get_object_or_404(OrderItem, book=book)
    order = get_object_or_404(Order, user=request.user)
    order.items.remove(order_item)
    order.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def order_view(request):
    order = get_object_or_404(Order, user=request.user)
    context = {
        'order': order,
    }
    return render(request, "order_summary.html", context)


def checkout(request):
    order = get_object_or_404(Order, user=request.user)
    if request.method == "POST":
        # Complete the order (ref code and set ordered to true)
        order.ref_code = create_ref_code()

        # Create a Stripe charge
        token = request.POST.get('stripeToken')
        charge = stripe.Charge.create(
            amount=int(order.get_total()) * 100,  # cents
            currency="jpy",
            source=request.POST.get('stripeToken'),
            description=f"Charge for {request.user.username}",
        )

        print(charge)

        # # Create our payment object and link to the order
        # payment = Payment()
        # payment.order = order
        # payment.stipe_charge_id = charge.id
        # payment.total_amount = charge.amount
        # payment.save()

        # # Add the book to the users book list
        # books = [item.book for item in order.items.all()]
        # for book in books:
        #     request.user.userlibrary.books.add(book)

        # order.is_ordered = True
        # order.save()

        # # Redirect to user's profile
        return redirect('/account/profile/')

    context = {
        'order': order,
    }

    return render(request, "checkout.html", context)
