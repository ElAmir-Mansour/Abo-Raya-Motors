from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Listing, Make, Model, CarTrim, User

class ListingForm(forms.ModelForm):
    """Form for creating/editing car listings with cascading dropdowns"""
    
    # Custom fields for cascading selection
    make = forms.ModelChoiceField(
        queryset=Make.objects.all(),
        empty_label=_("Select Make"),
        label=_("Make")
    )
    model = forms.ModelChoiceField(
        queryset=Model.objects.none(),
        empty_label=_("Select Model"),
        label=_("Model")
    )
    
    class Meta:
        model = Listing
        fields = [
            'make', 'model', 'trim',
            'price', 'odometer', 'color', 'description', 'location',
            'image_main', 'image_2', 'image_3', 'image_4', 'image_5'
        ]
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500000'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50000'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g. White')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'trim': forms.Select(attrs={'class': 'form-select', 'id': 'id_trim'}),
            'image_main': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_2': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_3': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_4': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_5': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to custom fields
        self.fields['make'].widget.attrs.update({'class': 'form-select', 'id': 'id_make'})
        self.fields['model'].widget.attrs.update({'class': 'form-select', 'id': 'id_model'})
        
        # If editing an existing listing, populate the dropdowns
        if self.instance.pk:
            self.fields['make'].initial = self.instance.trim.model.make
            self.fields['model'].queryset = Model.objects.filter(make=self.instance.trim.model.make)
            self.fields['model'].initial = self.instance.trim.model
            self.fields['trim'].queryset = CarTrim.objects.filter(model=self.instance.trim.model)
    
    def clean(self):
        cleaned_data = super().clean()
        make = cleaned_data.get('make')
        model = cleaned_data.get('model')
        trim = cleaned_data.get('trim')
        
        # Validation: Ensure trim belongs to the selected model
        if trim and model and trim.model != model:
            raise forms.ValidationError(_("Selected trim does not match the selected model."))
        
        # Validation: Ensure model belongs to the selected make
        if model and make and model.make != make:
            raise forms.ValidationError(_("Selected model does not match the selected make."))
        
        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    """Custom registration form with phone number and dealer option"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+20XXXXXXXXXX'})
    )
    is_dealer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_dealer'})
    )
    commercial_registry = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    tax_card = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'is_dealer', 'commercial_registry', 'tax_card']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        is_dealer = cleaned_data.get('is_dealer')
        commercial_registry = cleaned_data.get('commercial_registry')
        tax_card = cleaned_data.get('tax_card')

        if is_dealer:
            if not commercial_registry:
                self.add_error('commercial_registry', _("Commercial Registry is required for dealers."))
            if not tax_card:
                self.add_error('tax_card', _("Tax Card is required for dealers."))
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.is_dealer = self.cleaned_data.get('is_dealer', False)
        
        if user.is_dealer:
            user.commercial_registry = self.cleaned_data.get('commercial_registry')
            user.tax_card = self.cleaned_data.get('tax_card')
            
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Form for users to update their profile"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+20XXXXXXXXXX'})
    )
    commercial_registry = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    tax_card = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'commercial_registry', 'tax_card']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If user is not a dealer, hide dealer fields
        if not self.instance.is_dealer:
            self.fields.pop('commercial_registry')
            self.fields.pop('tax_card')

