from django.shortcuts import render, redirect
from .models import HotelImages, HotelUser, HotelVendor, Hotel, Amenities, HotelImages
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
import random
from django.contrib.auth.decorators import login_required
from .utils import generateSlug
from django.http import HttpResponseRedirect

#login page
def login_page(request):
    
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        hotel_user = HotelUser.objects.filter(
            email=email)
        
        if not hotel_user.exists():
            messages.warning(request, "No user with this email exists.")
            return redirect('/account/login/')
        
        if not hotel_user[0].is_verified:
            messages.warning(request, "Your email is not verified. Please verify your email before logging in.")
            return redirect('/account/login/')
        hotel_user = authenticate(username=hotel_user[0].username, password=password)
        
        if hotel_user:
            messages.success(request, "Login successful.")
            login(request, hotel_user)
            return redirect('/account/login/')
        messages.warning(request, "Invalid password.")
        return redirect('/account/login/')
            
    return render(request, 'login.html')

        
        #sent = sendEmailToken(email, hotel_user.email_token)

#signup page
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')  
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        
        hotel_user = HotelUser.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )
        
        if hotel_user.exists():
            messages.warning(request, "A user with this email or phone number already exists.")
            return redirect('/account/register/')
        
        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            email_token=generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        
        sent = sendEmailToken(email, hotel_user.email_token)
        
        if sent:
            messages.success(request, "An email has been sent to your email address.")
        else:
            messages.warning(request, "Verification email could not be sent. The verification link was printed to the server console for debugging.")
        return redirect('/account/login/')

    return render(request, 'register.html')

def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Your email has been verified.")
        return redirect('/account/login/')

    except Exception as e:
        return HttpResponse("Invalid token")
    
def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(email=email)
    if not hotel_user.exists():
        messages.warning(request, "No user with this email exists.")
        return redirect('/account/login/')
    otp = random.randint(1000, 9999)
    hotel_user.update(otp=otp)
    #hotel_user.save()
    sendOTPtoEmail(email, otp)
    
    return redirect(f'/account/verify-otp/{email}/')

def verify_otp(request, email):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email=email)
        
        if otp == hotel_user.otp:
            messages.success(request, "Login successful.")
            login(request, hotel_user)
            return redirect('/account/login/')
        messages.warning(request, "Invalid OTP.")
        return redirect(f'/account/verify-otp/{email}/')
    return render(request, 'verify_otp.html')

#Vendor login/registration pages
def login_vendor(request):
    
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        hotel_user = HotelVendor.objects.filter(
            email=email)
        
        if not hotel_user.exists():
            messages.warning(request, "No user with this email exists.")
            return redirect('/account/login-vendor/')
        
        if not hotel_user[0].is_verified:
            messages.warning(request, "Your email is not verified. Please verify your email before logging in.")
            return redirect('/account/login-vendor/')
        hotel_user = authenticate(username=hotel_user[0].username, password=password)
        
        if hotel_user:
            #messages.success(request, "Login successful.")
            login(request, hotel_user)
            return redirect('/account/dashboard/')
        messages.warning(request, "Invalid password.")
        return redirect('/account/login-vendor/')
            
    return render(request, 'vendor/login_vendor.html')

        
        #sent = sendEmailToken(email, hotel_user.email_token)

#signup page
def register_vendor(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name') 
        business_name = request.POST.get('business_name') 
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        
        hotel_user = HotelUser.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )
        
        if hotel_user.exists():
            messages.warning(request, "A user with this email or phone number already exists.")
            return redirect('/account/register-vendor/')
        
        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            business_name=business_name,
            email_token=generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        
        sent = sendEmailToken(email, hotel_user.email_token)
        
        if sent:
            messages.success(request, "An email has been sent to your email address.")
        else:
            messages.warning(request, "Verification email could not be sent. The verification link was printed to the server console for debugging.")
        return redirect('/account/register-vendor/')

    return render(request, 'vendor/register_vendor.html')


#Vendor Dashoboard
@login_required(login_url='login_vendor')
def dashboard(request):
    context = {'hotels': Hotel.objects.filter(hotel_owner=request.user)}
    return render(request, 'vendor/vendor_dashboard.html', context)

#Add Hotel
@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        amenities = request.POST.getlist('amenities')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)
        
        # print(
        #     f"""
        #     hotel_name,
        #     hotel_description,
        #     amenities,
        #     hotel_price,
        #     hotel_offer_price,
        #     hotel_location,
            
        #     """
        # )
        hotel_vendor = None
        try:
            hotel_vendor = request.user.hotelvendor
        except Exception:
            messages.error(request, "Only verified vendor accounts can add hotels.")
            return redirect('/account/login-vendor/')

        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )
        
        for ameneti in amenities:
            ameneti = Amenities.objects.get(id=ameneti)
            hotel_obj.amenities.add(ameneti)
            hotel_obj.save()
            
        messages.success(request, " Hotel created.")
        return redirect('/account/add-hotel/')

    amenities = Amenities.objects.all()
        
    return render(request, 'vendor/add_hotel.html', context={'amenities': amenities})


@login_required(login_url='login_vendor')
def upload_images(request , slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
            hotel=hotel_obj,
            image=image
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context={'images': hotel_obj.hotel_images.all()})

#delete images

@login_required(login_url='login_vendor')
def delete_image(request , id):
    print(id)
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('dashboard')

    #return render(request, 'vendor/upload_images.html', context={'images': hotel_obj.hotel_images.all()})
# edit hotel

@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized to edit this hotel.")
    if request.method == "POST":
       hotel_name = request.POST.get('hotel_name')
       hotel_description = request.POST.get('hotel_description')
       hotel_price = request.POST.get('hotel_price')
       hotel_offer_price = request.POST.get('hotel_offer_price')
       hotel_location = request.POST.get('hotel_location')
       hotel_obj.hotel_name = hotel_name
       hotel_obj.hotel_description = hotel_description
       hotel_obj.hotel_price = hotel_price
       hotel_obj.hotel_offer_price = hotel_offer_price
       hotel_obj.hotel_location = hotel_location
       hotel_obj.save()
       messages.success(request, "Hotel updated successfully.")
       return HttpResponseRedirect(request.path_info)
   
    amenities = Amenities.objects.all()
    return render(request, 'vendor/edit_hotel.html', context={'hotel': hotel_obj, 'amenities': amenities})

# logout

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/account/login-vendor/')