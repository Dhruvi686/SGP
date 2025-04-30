from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from .forms import CustomUserCreationForm, OTPVerificationForm
from .models import CustomUser
import random
import string
import logging

logger = logging.getLogger(__name__)

def send_otp(phone_number, otp):
    """
    Mock function to send OTP via SMS
    In a real application, you would integrate with an SMS service provider
    """
    # For development, we'll just print the OTP
    # In production, replace this with actual SMS sending code
    print(f"Sending OTP {otp} to {phone_number}")
    return True

def send_otp_email(email, otp):
    """
    Send OTP via email
    """
    try:
        subject = 'Your OTP for Sign Language Converter'
        context = {
            'otp': otp,
        }
        
        # Render email templates
        html_message = render_to_string('email_otp.html', context)
        plain_message = strip_tags(html_message)
        
        # Create email message
        email_message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        email_message.content_subtype = 'html'  # Set content type to HTML
        
        # Send email
        print(f"Attempting to send OTP {otp} to {email}")
        email_message.send(fail_silently=False)
        print(f"Successfully sent OTP to {email}")
        return True
        
    except Exception as e:
        print(f"Error sending email to {email}: {str(e)}")
        logger.error(f"Failed to send OTP email: {str(e)}")
        return False

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Generate OTP
                otp = ''.join(random.choices(string.digits, k=6))
                email = form.cleaned_data['email']
                
                # Try to send OTP before creating user
                if send_otp_email(email, otp):
                    # Create and save user
                    user = form.save(commit=False)
                    user.is_active = False
                    user.otp = otp
                    user.otp_created_at = timezone.now()
                    user.save()
                    return redirect('verify_otp', user_id=user.id)
                else:
                    return render(request, 'signup.html', {'form': form})
                    
            except Exception as e:
                print(f"Error during signup: {str(e)}")
                return render(request, 'signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def verify_otp_view(request, user_id):
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        if user.is_active:
            return redirect('home')
        
        if request.method == 'POST':
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                otp = form.cleaned_data['otp']
                
                # Check OTP expiration
                if user.otp_created_at and (timezone.now() - user.otp_created_at).total_seconds() > 600:
                    user.delete()
                    return redirect('signup')
                
                if user.verify_otp(otp):
                    user.is_active = True
                    user.save()
                    login(request, user)
                    return redirect('animation')
                else:
                    return render(request, 'verify_otp.html', {'form': form, 'user': user})
        else:
            form = OTPVerificationForm()
        
        return render(request, 'verify_otp.html', {'form': form, 'user': user})
        
    except Exception as e:
        print(f"Error in OTP verification: {str(e)}")
        return redirect('signup')
