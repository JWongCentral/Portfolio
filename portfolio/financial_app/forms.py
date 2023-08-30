from django import forms



class Contact_EmailForm(forms.Form):
    contact_name = forms.CharField(label="Your name", max_length=100,
                                   widget=forms.TextInput(attrs={
                                           'id':'main_search',
                                           'class': 'main_search',
                                           'placeholder':'Search for symbol or companies',
                                           'required':False
                                        }))


