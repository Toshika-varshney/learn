from django.urls import path
from .views import *

urlpatterns = [
    # path('signup/', signup, name='signup'),
    path('verify/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('forgot/', forgot_password, name='forgot'),
    # path('verify/', reset_verify, name='verify'),
    path('set-password/', set_new_password, name='set_password'),
    path('home',home_view,name='home'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password, name='change_password'),
]