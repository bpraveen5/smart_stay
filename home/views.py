from pyexpat.errors import messages
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.shortcuts import render
from accounts.models import Hotel, HotelUser, HotelBooking
# Create your views here.

def index(request):
    hotels = Hotel.objects.all()
    if request.GET.get('search'):
        hotels = hotels.filter(hotel_name__icontains=request.GET.get('search'))
    return render(request, 'index.html', context={'hotels': hotels[:50]})

from datetime import datetime
def hotel_details(request, slug):
    hotel = Hotel.objects.get(hotel_slug=slug)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        days_count = (end_date - start_date).days
        
        if days_count <= 0:
            messages.warning(request, "Invalid Booking Date.")
            return HttpResponseRedirect(request.path_info)
        HotelBooking.objects.create(
            hotel = hotel,
            booking_user = HotelUser.objects.get(id = request.user.id),
            booking_start_date = start_date,
            booking_end_date = end_date,
            price = hotel.hotel_offer_price * days_count
        )
        messages.success(request, "Hotel Booked Successfully.")
        return HttpResponseRedirect(request.path_info)

        # Handle booking logic here
        pass
    return render(request, 'hotel_detail.html', context={'hotel': hotel})

