from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from .models import Room, Booking, CustomUser, Tenant, Landlord
from .forms import RoomForm, BookingForm, LandlordApplicationForm, TenantProfileForm
from dateutil.relativedelta import relativedelta
from myapp.allauth_forms import CustomSignupForm
import qrcode
from io import BytesIO
import base64
import logging
import libscrc

# ตั้งค่า logging
logger = logging.getLogger(__name__)

# --- EMVCo Tag Constants ---
TAG_PAYLOAD_FORMAT_INDICATOR = "00"
TAG_POINT_OF_INITIATION_METHOD = "01"
TAG_MERCHANT_ACCOUNT_INFORMATION = "29"
SUB_TAG_AID_PROMPTPAY = "00"
SUB_TAG_MOBILE_NUMBER_PROMPTPAY = "01"
TAG_TRANSACTION_CURRENCY = "53"
TAG_TRANSACTION_AMOUNT = "54"
TAG_COUNTRY_CODE = "58"
TAG_CRC = "63"

# --- Standard Values ---
VALUE_PAYLOAD_FORMAT_INDICATOR = "01"
VALUE_POINT_OF_INITIATION_MULTIPLE = "11"
VALUE_POINT_OF_INITIATION_ONETIME = "12"
VALUE_PROMPTPAY_AID = "A000000677010111"
VALUE_COUNTRY_CODE_TH = "TH"
VALUE_CURRENCY_THB = "764"
LEN_CRC_VALUE_HEX = "04"

class QRError(Exception):
    pass

class InvalidInputError(QRError):
    pass

def _format_tlv(tag: str, value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"TLV value for tag {tag} must be a string, got {type(value)}.")
    length_str = f"{len(value):02d}"
    return f"{tag}{length_str}{value}"

def calculate_crc(code_string: str) -> str:
    try:
        encoded_string = str.encode(code_string, 'ascii')
    except UnicodeEncodeError:
        raise InvalidInputError("Payload contains non-ASCII characters, which is not supported for CRC calculation.")
    crc_val = libscrc.ccitt_false(encoded_string)
    crc_hex_str = hex(crc_val)[2:].upper()
    return crc_hex_str.rjust(4, '0')

def generate_promptpay_qr_payload(mobile: str = None, amount: float = None, one_time: bool = False) -> str:
    if not mobile:
        raise InvalidInputError("Mobile number must be provided.")
    if mobile and not (len(mobile) == 10 and mobile.isdigit()):
        raise InvalidInputError("Mobile number must be a 10-digit string (e.g., '0812345678').")

    payload_elements = []

    # Tag 00: Payload Format Indicator
    payload_elements.append(_format_tlv(TAG_PAYLOAD_FORMAT_INDICATOR, VALUE_PAYLOAD_FORMAT_INDICATOR))

    # Tag 01: Point of Initiation Method
    initiation_method_value = VALUE_POINT_OF_INITIATION_ONETIME if one_time else VALUE_POINT_OF_INITIATION_MULTIPLE
    payload_elements.append(_format_tlv(TAG_POINT_OF_INITIATION_METHOD, initiation_method_value))

    # Tag 29: Merchant Account Information
    merchant_account_sub_elements = []
    merchant_account_sub_elements.append(_format_tlv(SUB_TAG_AID_PROMPTPAY, VALUE_PROMPTPAY_AID))
    formatted_mobile_value = f"00{VALUE_COUNTRY_CODE_TH}{mobile[1:]}"
    merchant_account_sub_elements.append(_format_tlv(SUB_TAG_MOBILE_NUMBER_PROMPTPAY, formatted_mobile_value))
    payload_elements.append(_format_tlv(TAG_MERCHANT_ACCOUNT_INFORMATION, "".join(merchant_account_sub_elements)))

    # Tag 53: Transaction Currency (THB)
    payload_elements.append(_format_tlv(TAG_TRANSACTION_CURRENCY, VALUE_CURRENCY_THB))

    # Tag 54: Transaction Amount (Optional)
    if amount is not None:
        amount_str = f"{float(amount):.2f}"
        payload_elements.append(_format_tlv(TAG_TRANSACTION_AMOUNT, amount_str))

    # Tag 58: Country Code (TH)
    payload_elements.append(_format_tlv(TAG_COUNTRY_CODE, VALUE_COUNTRY_CODE_TH))

    # CRC Calculation
    data_for_crc = "".join(payload_elements)
    string_to_calculate_crc_on = data_for_crc + TAG_CRC + LEN_CRC_VALUE_HEX
    crc_hex_value = calculate_crc(string_to_calculate_crc_on)
    final_payload = string_to_calculate_crc_on + crc_hex_value
    return final_payload.upper()

def display_promptpay_qr(mobile: str = None, amount: float = None, one_time: bool = False, box_size: int = 12, border: int = 6):
    try:
        payload = generate_promptpay_qr_payload(mobile=mobile, amount=amount, one_time=one_time)
        logger.debug(f"Generated Payload: {payload}")

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG", quality=100)
        qr_image = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        return qr_image
    except QRError as e:
        logger.error(f"Error generating QR code: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

def home(request):
    max_price = request.GET.get('max_price')
    min_price = request.GET.get('min_price')
    dorm_name = request.GET.get('dorm_name')
    description = request.GET.get('description')

    queryset = Room.objects.filter(available=True)
    if max_price:
        try:
            max_price = float(max_price)
            queryset = queryset.filter(price__lte=max_price)
        except ValueError:
            pass
    if min_price:
        try:
            min_price = float(min_price)
            queryset = queryset.filter(price__gte=min_price)
        except ValueError:
            pass
    if dorm_name:
        queryset = queryset.filter(dorm_name__icontains=dorm_name)
    if description:
        queryset = queryset.filter(description__icontains=description)

    rooms_per_page = 10
    page = request.GET.get('page', '1')
    paginator = Paginator(queryset, rooms_per_page)
    try:
        rooms = paginator.page(page)
    except:
        rooms = paginator.page(1)

    return render(request, 'home.html', {'rooms': rooms})

@login_required
def apply_landlord(request):
    if request.method == 'POST':
        user = request.user
        
        if user.role == 'landlord':
            messages.error(request, 'You are already a landlord.')
            return redirect('profile')
        
        form = LandlordApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                Tenant.objects.filter(user=user).delete()
                user.role = 'landlord'
                user.phone = form.cleaned_data['phone_number']
                user.save()
                
                landlord, created = Landlord.objects.get_or_create(user=user)
                landlord.phone_number = form.cleaned_data['phone_number']
                landlord.dorm_name = form.cleaned_data['dorm_name']
                landlord.bank_name = form.cleaned_data['bank_name']
                landlord.bank_account_number = form.cleaned_data['bank_account_number']
                landlord.account_holder_name = form.cleaned_data['account_holder_name']
                landlord.save()
                
                landlord_group, _ = Group.objects.get_or_create(name='Landlord')
                user.groups.clear()
                user.groups.add(landlord_group)
                
                messages.success(request, 'Your application has been submitted and you are now a Landlord.')
                return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LandlordApplicationForm()
    
    return render(request, 'apply_landlord.html', {'form': form})

class RoomDetailView(DetailView):
    model = Room
    template_name = 'room_detail.html'
    context_object_name = 'room'

class RoomSearchView(ListView):
    model = Room
    template_name = 'room_search.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = Room.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(room_name__icontains=query) |
                Q(location__icontains=query) |
                Q(description__icontains=query)
            )
        if self.request.GET.get('table'):
            queryset = queryset.filter(table_count__gt=0)
        if self.request.GET.get('bed'):
            queryset = queryset.filter(bed_count__gt=0)
        if self.request.GET.get('chair'):
            queryset = queryset.filter(chair_count__gt=0)
        return queryset

def all_rooms(request):
    rooms = Room.objects.filter(available=True)
    paginator = Paginator(rooms, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_rooms.html', {'page_obj': page_obj})

def booking_complete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_complete.html', {'booking': booking})

@login_required
def room_create(request):
    if request.user.role != 'landlord':
        messages.error(request, "Only landlords can create rooms.")
        return redirect('home')
    
    try:
        landlord_profile = request.user.landlord_profile
    except Landlord.DoesNotExist:
        messages.error(request, "Landlord profile not found. Please apply as a landlord first.")
        return redirect('apply_landlord')

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            room = form.save(commit=False)
            room.landlord = landlord_profile
            if Room.objects.filter(landlord=landlord_profile, dorm_name=room.dorm_name, room_name=room.room_name).exists():
                form.add_error('room_name', "A room with this name already exists in this dorm.")
                return render(request, 'room_create.html', {'form': form})
            room.save()
            messages.success(request, "Room created successfully.")
            return redirect('profile')
    else:
        form = RoomForm(user=request.user)
    return render(request, 'room_create.html', {'form': form})

def booking_create(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if not room.available:
        messages.error(request, "This room is not available for booking.")
        return redirect('room_detail', pk=room_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            if request.user.is_authenticated and request.user.role == 'tenant':
                try:
                    booking.tenant = request.user.tenant
                    booking.email = request.user.email
                    booking.phone = request.user.phone or form.cleaned_data['phone']
                    booking.full_name = request.user.username
                except Tenant.DoesNotExist:
                    messages.error(request, "Tenant profile not found. Please complete your profile.")
                    return render(request, 'room_detail.html', {'room': room, 'form': form})
            else:
                booking.full_name = form.cleaned_data['full_name']
                booking.phone = form.cleaned_data['phone']
                booking.email = form.cleaned_data.get('email', '')

            booking.check_in = form.cleaned_data['check_in']
            try:
                booking.clean()
                booking.save()
                
                if room.landlord and room.landlord.user.email:
                    subject = f"New Booking for {room.dorm_name} - {room.room_name}"
                    message = (
                        f"Dear {room.landlord.user.username},\n\n"
                        f"A new booking has been made for your room: {room.dorm_name} - {room.room_name}.\n"
                        f"Tenant: {booking.full_name or booking.tenant.user.username}\n"
                        f"Check-in: {booking.check_in}\n"
                        f"Check-out: {booking.check_out}\n"
                        f"Status: {booking.status.title()}\n\n"
                        f"Please review and confirm the booking in your profile."
                    )
                    try:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [room.landlord.user.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send booking email to {room.landlord.user.email}: {str(e)}")
                
                messages.success(request, "Booking created successfully!")
                return redirect('booking_complete', booking_id=booking.id)
            except ValidationError as e:
                form.add_error(None, e)
        return render(request, 'room_detail.html', {'room': room, 'form': form})
    else:
        form = BookingForm(initial={'check_in': date.today()})
    return render(request, 'room_detail.html', {'room': room, 'form': form})

@login_required
def booking_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, status='pending')
    if booking.tenant and booking.tenant.user != request.user:
        messages.error(request, "You are not authorized to view this booking.")
        return redirect('profile')

    mobile = booking.room.landlord.bank_account_number
    if not mobile or not mobile.isdigit() or len(mobile) != 10:
        mobile = booking.room.landlord.phone_number
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            logger.error(f"Invalid mobile number: {mobile}")
            messages.error(request, "Invalid mobile number for PromptPay QR Code.")
            return render(request, 'payment.html', {'booking': booking})

    amount = float(booking.room.price)
    qr_image = None
    try:
        qr_image = display_promptpay_qr(mobile=mobile, amount=amount, one_time=True)
        logger.info("QR Code generated successfully with PromptPay payload.")
    except Exception as e:
        logger.error(f"Error generating QR Code: {e}")
        messages.error(request, f"Error generating QR Code: {e}")

    return render(request, 'payment.html', {'booking': booking, 'qr_image': qr_image})

@login_required
def booking_payment_confirm(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tenant__user=request.user)
    if booking.status != 'pending':
        messages.error(request, "This booking cannot be confirmed as it is not in pending status.")
        return redirect('profile')
    if request.method == 'POST':
        with transaction.atomic():
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, "Payment confirmed! Your booking is now confirmed.")
        return redirect('profile')
    return redirect('booking_payment', booking_id=booking_id)

@login_required
def profile_view(request):
    user = request.user
    context = {'user': user, 'bookings': [], 'rooms': []}

    try:
        if user.role == 'tenant':
            tenant, created = Tenant.objects.get_or_create(user=user, defaults={'budget': 0})
            context['bookings'] = Booking.objects.filter(tenant=tenant).select_related('room').prefetch_related('room__landlord')
            context['tenant_form'] = TenantProfileForm(instance=tenant, user=user)
        elif user.role == 'landlord':
            landlord_profile = user.landlord_profile
            context['bookings'] = Booking.objects.filter(room__landlord=landlord_profile).select_related('room').prefetch_related('tenant__user')
            context['rooms'] = Room.objects.filter(landlord=landlord_profile)
    except (Tenant.DoesNotExist, Landlord.DoesNotExist):
        messages.error(request, "Profile not found. Please complete your profile setup.")
    
    return render(request, 'profile.html', context)

@login_required
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user.role != 'landlord' or booking.room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to confirm this booking.")
        return redirect('profile')
    booking.status = 'confirmed'
    booking.save()
    messages.success(request, "Booking confirmed successfully.")
    return redirect('profile')

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user.role == 'landlord' and booking.room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('profile')
    if request.user.role == 'tenant' and booking.tenant != request.user.tenant:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('profile')
    booking.status = 'canceled'
    booking.save()
    messages.success(request, "Booking canceled successfully.")
    return redirect('profile')

@login_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user.role != 'landlord' or room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to edit this room.")
        return redirect('profile')
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully.")
            return redirect('profile')
    else:
        form = RoomForm(instance=room, user=request.user)
    return render(request, 'room_edit.html', {'form': form, 'room': room})

@login_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user.role != 'landlord' or room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to delete this room.")
        return redirect('profile')
    room.delete()
    messages.success(request, "Room deleted successfully.")
    return redirect('profile')

@login_required
def profile_edit(request):
    if request.user.role != 'tenant':
        messages.error(request, "Only tenants can edit tenant profiles.")
        return redirect('profile')
    
    try:
        tenant = request.user.tenant
    except Tenant.DoesNotExist:
        tenant = Tenant.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = TenantProfileForm(request.POST, instance=tenant, user=request.user)
        if form.is_valid():
            request.user.email = request.POST.get('email', request.user.email)
            request.user.phone = request.POST.get('phone', request.user.phone)
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TenantProfileForm(instance=tenant, user=request.user)
    
    return render(request, 'profile.html', {'form': form})

@login_required
def landlord_profile_edit(request):
    if request.user.role != 'landlord':
        messages.error(request, "Only landlords can edit landlord profiles.")
        return redirect('profile')
    
    try:
        landlord = request.user.landlord_profile
    except Landlord.DoesNotExist:
        messages.error(request, "Landlord profile not found.")
        return redirect('profile')
    
    if request.method == 'POST':
        form = LandlordApplicationForm(request.POST, instance=landlord)
        if form.is_valid():
            request.user.email = request.POST.get('email', request.user.email)
            request.user.phone = request.POST.get('phone_number', request.user.phone)
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LandlordApplicationForm(instance=landlord)
    
    return render(request, 'profile.html', {'form': form})