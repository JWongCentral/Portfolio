from django import forms


class Contact_EmailForm(forms.Form):
    contact_name = forms.CharField(label="Your name", max_length=100,
                                   widget=forms.TextInput(attrs={
                                           'id':'contact_name',
                                           'class': 'contact_input name',
                                           'placeholder':'Your Name...',
                                           'required':True
                                        }))
    contact_email = forms.CharField(label="Your Email", max_length=100,
                                    widget=forms.TextInput(attrs={
                                           'id':'contact_email',
                                           'class': 'contact_input email',
                                           'placeholder':'Your Email...',
                                           'required':True
                                        }))
                                    
    contact_subject = forms.CharField(label="Subject", max_length=100,
                                      widget=forms.TextInput(attrs={
                                           'id':'contact_subject',
                                           'class': 'contact_input subject',
                                           'placeholder':'Subject...',
                                           'required':True
                                        }))
    contact_message = forms.CharField(label = "Message", max_length=500,
                                      widget=forms.Textarea(attrs={
                                           'id':'contact_message',
                                           'class': 'contact_input content',
                                           'placeholder':'Body of Email here...',
                                           'required':True
                                        }))


    