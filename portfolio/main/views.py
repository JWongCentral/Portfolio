from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import Contact_EmailForm
import sys,os

#to enable contact messages being sent
EMAIL_ENABLED = False

#to mark if it is ready for next AI_Solver entry
#will act as a simple mutex lock
ready = True
payload = {}


#Basic views to render template sub function calls to organize each web component
def index(request):
    return render(request,"home.html")
def resume(request):
    return render(request,"resume.html")
def expertise(request):
    return render(request,"expertise.html")
def projects(request):
    return render(request,"projects.html")


def contact(request):
    
    #only one button to send data
    if request.method == "POST":
        
        form = Contact_EmailForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data["contact_name"]
            email = form.cleaned_data["contact_email"]
            subject = form.cleaned_data["contact_subject"]
            message = name + " would like to contact you\n"+"My email is "+email+"\n"+form.cleaned_data["contact_message"]
            if(EMAIL_ENABLED):
                email = send_mail(
                    subject,    #subject line
                    message,    #message content
                    settings.EMAIL_HOST_USER,   #sender email, this should be the email bot set up in configs
                    ["jackbwong1998@gmail.com"],#the email receiving the message
                    fail_silently=False,
                )
            
            return render(request, "contact.html", {"form": Contact_EmailForm(), "success":True, "error":False})
        
        #error
        else:
            return render(request, "contact.html", {"form": form, "success":False, "error":True})
    else:
        form = Contact_EmailForm()

    return render(request, "contact.html", {"form":Contact_EmailForm()})



#contains live version of minesweeper
def minesweeper(request):

    return render(request,"minesweeper.html")

def minesweeper_get(request):
    global payload
    global ready
    if(len(payload) == 0):
        return HttpResponse("Get request FAILED")
    else:
        ready = True
        return JsonResponse(payload)

def minesweeper_post(request):
    global payload 
    global ready
    print(ready)
    if(ready == False):
        return HttpResponse("Post request Failed")
    else:
        ready = False
    if(compile(request.POST['gamestate'])):
        payload = loadFile("main\scripts\output.txt")
        print("Finished Loading")
        return HttpResponse("Post request received successfully")
    else:
        ready = True
        return HttpResponse("Post request Failed")

#this code will compile the C++ script with the parameter in question
def compile(gameState):

    cpp_file = 'main\scripts\minesweeperSolver.cpp'
    exe_file = 'main\scripts\\run'
    print("Compiling C++ script")
    if(os.system('g++ -o ' + exe_file + ' ' + cpp_file) == 0):
        if(os.system(exe_file + ' 20 ' + gameState) == 0):
            print("Success")
            return True
        else:
            print("Failed Running")
            return False
    else:
        print("Failed Compiling")
        return False

#this code will gather the input from the file and read it into python
def loadFile(file):
    try:
        f = open(file, 'r')
        entries = 0
        ret = {}

        #reading file data
        for line in f:
            temp = line.strip('\n').split('|')
            col = temp[0]
            row = temp[1]
            probability = temp[2]
            action = temp[3]
            ret[entries] = {
                'row':row,
                'col':col,
                'probability':probability,
                'action':action,
            }
            entries+=1

        ret['entries']=entries
        f.close()
    except:
        print("Error")
    
    return ret





def main(request):
    #only one button to send data
    if request.method == "POST":
        
        form = Contact_EmailForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data["contact_name"]
            email = form.cleaned_data["contact_email"]
            subject = form.cleaned_data["contact_subject"]
            message = name + " would like to contact you\n"+"My email is "+email+"\n"+form.cleaned_data["contact_message"]
            if(EMAIL_ENABLED):
                email = send_mail(
                    subject,    #subject line
                    message,    #message content
                    settings.EMAIL_HOST_USER,   #sender email, this should be the email bot set up in configs
                    ["jackbwong1998@gmail.com"],#the email receiving the message
                    fail_silently=False,
                )
            
            return render(request, "main.html", {"form": Contact_EmailForm(), "success":True, "error":False})
        
        #error
        else:
            return render(request, "main.html", {"form": form, "success":False, "error":True})
    else:
        form = Contact_EmailForm()

    return render(request, "main.html", {"form":Contact_EmailForm()})

