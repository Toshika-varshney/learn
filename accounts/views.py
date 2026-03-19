from django.shortcuts import render,redirect
from .models import EmailOTP,CustomUser
from .utils import send_otp_email,generate_otp
from django.utils.timezone import now
from django.contrib.auth import authenticate,login,logout
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def signup(request):
    email_value = ""
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        confirm=request.POST['confirm']

        
            

        try:
            validate_email(email)
            email_value = email
        except ValidationError:
            return render(request, 'accounts/signup.html', {
            'error': 'Type correct email address',
            'email_value':""
            })
        if not password or password.strip() == "":
            return render(request, 'accounts/signup.html', {
            'error': 'Enter password',
            'email_value': email_value
    })

        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {
            'error': 'Try again with another email',
             'email_value' : ""
        })
        
        
        if password!= confirm:
            return render(request,'accounts/signup.html',{'error':'Password do not match','email_value':email_value})

        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, 'accounts/signup.html', {
            'error': e.messages[0],
            'email_value':email_value
            })


          
        
        
        
        otp=generate_otp()
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email,otp=otp)
        send_otp_email(email,otp)

        request.session['signup_email']=email
        request.session['signup_password']=password
        request.session['otp_purpose'] = 'signup'

        return redirect('verify_otp')
    return render(request,'accounts/signup.html')

def otp_failed_redirect(purpose):
    if purpose == 'signup':
        return redirect('signup')
    return redirect('forgot_password')


def verify_otp(request):
    purpose = request.session.get('otp_purpose')

    if purpose == 'signup':
        email = request.session.get('signup_email')
    elif purpose == 'reset':
        email = request.session.get('reset_email')
    if not email:
        return fail_redirect()

    otp_obj = EmailOTP.objects.filter(email=email).last()

    def fail_redirect():
        return redirect('signup' if purpose == 'signup' else 'set_password')

    if not otp_obj:
        return fail_redirect()

    if request.method == 'POST':
        if otp_obj.attempts > 2:
            otp_obj.delete()
            return fail_redirect()

        entered_otp = request.POST.get('otp')

        if entered_otp == otp_obj.otp:
            

            if purpose == 'signup':
                user = CustomUser.objects.create_user(
                    email=email,
                    password=request.session['signup_password']
                )
                user.is_verified = True
                user.save()

                del request.session['signup_email']
                del request.session['signup_password']
                del request.session['otp_purpose']
                messages.success(request, 'Signup successful. Please login.')
                return redirect('login')
                

            if purpose == 'reset':
                del request.session['otp_purpose']
                return redirect('set_password')


        otp_obj.attempts += 1
        otp_obj.save()

        return render(request, 'accounts/verify.html', {
            'error': 'Invalid OTP'
        })

    return render(request, 'accounts/verify.html')

           

def login_view(request):
    email_value = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            email_value = email
        except CustomUser.DoesNotExist:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid credentials',
                'email_value': "" 
            })
        if password=="":
            return render(request,'accounts/login.html', {
                'error': 'Enter password',
                'email_value': email_value
            })
        
        if user.is_blocked:
            return render(request, 'accounts/login.html', {
                'error': 'Your account is permanently blocked',
                'email_value': email_value
            })

        
        if user.block_until and user.block_until > now():
            seconds = int((user.block_until - now()).total_seconds())
            return render(request, 'accounts/login.html', {
                'error': f'Too many attempts. Try again in {seconds} seconds',
                'email_value': email_value
            })
       
        
        if user.block_until and user.block_until <= now():
           user.block_until = None
           user.save()


        
        if not user.check_password(password):
            user.login_attempts += 1

            if user.login_attempts == 4:
                user.block_until = now() + timedelta(minutes=1)
                user.save()
                return render(request, 'accounts/login.html', {
                    'error': 'Too many attempts. Blocked for 1 minute',
                    'email_value': email_value
                })

            elif user.login_attempts == 5:
                user.block_until = now() + timedelta(minutes=2)
                user.save()
                return render(request, 'accounts/login.html', {
                    'error': 'Too many attempts. Blocked for 2 minutes',
                    'email_value': email_value
                })

            elif user.login_attempts >= 6:
                user.is_blocked = True
                user.save()
                return render(request, 'accounts/login.html', {
                    'error': 'Your account is permanently blocked',
                    'email_value': email_value
                })

            user.save()
            return render(request, 'accounts/login.html', {
                'error': 'Enter correct password',
                'email_value': email_value
                
            })

        
        user.login_attempts = 0
        user.block_until = None
        user.save()

        login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html')

           
       
    
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'accounts/signup.html', {
            'error': 'Type correct email address'
            })

        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return render(
                request,
                'accounts/forgot.html',
                {'error': 'Please enter valid email'}
            )
        

        otp = generate_otp()
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp=otp)
        send_otp_email(email, otp)

        request.session['reset_email'] = email
        request.session.modified = True
        print("SESSION KEY:", request.session.session_key)
        request.session['otp_purpose'] = 'reset'

        return redirect('verify_otp')

    return render(request, 'accounts/forgot.html')




def set_new_password(request):
    email = request.session.get('reset_email')
    print("RESET EMAIL:", email)


    if not email:
        return redirect('forgot')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm=request.POST.get('confirm')

        if password!=confirm:
            return render(request,'accounts/set_password.html',{'error':'password do not match'})
        user = CustomUser.objects.get(email=email)
        try:
            validate_password(password, user)
        except ValidationError as e:
            return render(request, 'accounts/set_password.html', {
            'error': e.messages[0]
            })

        
        user.set_password(password)
        user.save()

        del request.session['reset_email']
        return redirect('login')

    return render(request, 'accounts/set_password.html')
@login_required(login_url='/login/')
def home_view(request):
    return render (request,'accounts/home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        
        if not user.check_password(old_password):
            return render(request, 'accounts/change_password.html', {
                'error': 'Old password is incorrect'
            })

        
        if new_password != confirm_password:
            return render(request, 'accounts/change_password.html', {
                'error': 'New passwords do not match'
            })

        
        if old_password == new_password:
            return render(request, 'accounts/change_password.html', {
                'error': 'New password must be different from old password'
            })

       
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return render(request, 'accounts/change_password.html', {
                'errors': e.messages
            })

        user.set_password(new_password)
        user.save()

        
        logout(request)
        messages.success(request, 'Password Change Successful. Please login.')
        return redirect('login')

    return render(request, 'accounts/change_password.html')