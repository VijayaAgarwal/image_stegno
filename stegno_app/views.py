from django.shortcuts import render,redirect
from django.http import HttpResponse
from .utils import encrypt_message, lsb_encode,lsb_decode,decrypt_message
from PIL import Image
import io
import secrets
import stepic
from PIL import Image #pillow
from django.conf import settings
import os
import mysql.connector as sql
import random
from django.core.mail import send_mail
from django.contrib import messages
from plyer import notification
import base64



name="" 
email=""
password=""

def howitworks(request):
    return render(request,"howitworks.html")

def encryption_AES(request):
    context = {}
    context['key']=""
    context['image']=""
    if request.method == 'POST':
        try:
            cover_file = request.FILES.get('cover')
            message_type = request.POST.get('message_type')

            if not cover_file:
                return HttpResponse("Cover image is required", status=400)

            cover_img = Image.open(cover_file).convert('RGB')

            if message_type == 'text':
                message = request.POST.get('message', '')
                if not message:
                    return HttpResponse("Text message is required", status=400)
                data = message.encode('utf-8')

            elif message_type == 'image':
                secret_file = request.FILES.get('secret')
                if not secret_file:
                    return HttpResponse("Secret image is required", status=400)
                data = secret_file.read()
            else:
                return HttpResponse("Invalid message type", status=400)

            key = secrets.token_hex(8)  # 16-character key (128-bit)
            encrypted = encrypt_message(data, key)
            stego_image = lsb_encode(cover_img, encrypted)

            buffer = io.BytesIO()
            stego_image.save(buffer, format='PNG')
            buffer.seek(0)

            # Prepare image for inline display/download
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            context['image'] = base64_image
            context['key'] = key
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return render(request,"encryption_AES.html",{'key':context['key'],'image': context['image'] })

def decryption_AES(request):
    context = {}
    context['result_text']=""
    context['result_image']=""
    if request.method == 'POST':
        try:
            stego_file = request.FILES.get('stego_image')
            key = request.POST.get('key')

            if not stego_file or not key:
                return HttpResponse("Stego image and key are required.", status=400)

            image = Image.open(stego_file).convert('RGB')
            extracted = lsb_decode(image, data_length=2048)

            try:
                decrypted = decrypt_message(extracted, key)
            except Exception:
                return HttpResponse("Failed to decrypt. Is the key correct?", status=400)

            if decrypted[:4] == b'\x89PNG':
                base64_img = base64.b64encode(decrypted).decode('utf-8')
                context['result_image'] = base64_img
            else:
                context['result_text'] = decrypted.decode('utf-8', errors='ignore')

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return render(request,"decryption_AES.html",{'result_text':context['result_text'],'result_image':context['result_image']})

def welcome(request):
    return render(request,"welcome.html")

def index_login(request):
    if request.method=="POST":
        m=sql.connect(host="localhost",user="root",passwd="mysql11",database="image")
        cursor=m.cursor()
        d=request.POST
        for key,value in d.items():
           if key=="email":
               email=value
           if key=="password":
               password=value
        c="select * from userdata where email='{}' and password='{}'".format(email,password)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
 
        if t==():
           return render(request,'error.html')
        else:
           return welcome(request)
    return render(request,'index.html')

def verify_otp(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        
        session_data = request.session.get('signup_data')
        

        if session_data and input_otp == session_data['otp']:
            # Create the user
            #user = User.objects.create_user(
            #    username=session_data['email'],
            #    email=session_data['email'],
            #    password=session_data['password'],
            #    name=session_data["name"]
            #)
            messages.success(request, 'Account created successfully!')
            m=sql.connect(host="localhost",user="root",passwd="mysql11",database="image")
            cursor=m.cursor()
            c="insert into userdata values('{}','{}','{}')".format(name,email,password)
            cursor.execute(c)
            m.commit()
            request.session.pop('email', None)
            request.session.pop('password', None)
            return redirect('index')  # or wherever
        else:
            messages.error(request, 'Invalid OTP')
    return render(request, 'verify_otp.html')

# Create your views here.3


def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(request):
    global name,email,password
    if request.method=="POST":
        email = request.POST["email"]
        name = request.POST["name"]
        password = request.POST["password"]
        otp = generate_otp()
        request.session['signup_data'] = {
            'name': name,
            'email': email,
            'password': password,
            'otp': str(otp)
        }  
            
        send_mail(
            'Your OTP Code for Verification at Image Steganogaphy !! ',
            f'Your OTP code is {otp}.',
            'vijayaagarwal11a@gmail.com',
            [email],
            fail_silently=False
        )
        request.session['otp'] = otp    
        return redirect('verify_otp')
                
    return render(request, "signup.html")


#def index(request):
  #  return render(request,'index.html') 

def hide_text_in_image(image,text):
    data=text.encode('utf-8')
    return stepic.encode(image,data)

def encryption_view(request):
    message = ""
    image_path = ""
    if request.method == "POST":
        text = request.POST['text']
        image_file = request.FILES['image']
        image = Image.open(image_file)

        new_image = hide_text_in_image(image, text)

        # Correct path
        save_path = os.path.join(settings.MEDIA_ROOT, 'encrypted_images')
        os.makedirs(save_path, exist_ok=True)  # Make sure the directory exists

        file_name = 'new_' + image_file.name
        full_path = os.path.join(save_path, file_name)
        new_image.save(full_path)

        # This path is for HTML
        image_path = settings.MEDIA_URL + 'encrypted_images/' + file_name
        message = "Text has been encrypted in the image."

    return render(request, 'encryption.html', { 'message': message, 'image_path': image_path })

def extract_text_from_image(image):
    data=stepic.decode(image)
    if isinstance(data,bytes):
        return data.decode('utf-8')
    return data
def decryption_view(request):
    text=""
    if request.method=="POST":
        image_file=request.FILES['image']
        image=Image.open(image_file)

        text=extract_text_from_image(image)
    return render(request,'decryption.html',{'text':text})

