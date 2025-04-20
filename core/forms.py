from django import forms
from .models import Session, QRCode

class QRCodeGenerationForm(forms.Form):
    """
    Form for generating QR codes for attendance
    """
    session = forms.ModelChoiceField(
        queryset=Session.objects.filter(is_active=True),
        empty_label="Select a session",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    expiration_minutes = forms.IntegerField(
        min_value=5,
        max_value=120,
        initial=15,
        help_text="QR code expiration time in minutes",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter sessions by lecturer if user is provided
        if user and user.user_type == 'lecturer':
            self.fields['session'].queryset = Session.objects.filter(
                course__lecturer=user,
                is_active=True
            )

class SessionForm(forms.ModelForm):
    """
    Form for creating or updating a session
    """
    class Meta:
        model = Session
        fields = ['course', 'location', 'date', 'start_time', 'end_time', 'is_active']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
        
        # Filter courses by lecturer if user is provided
        if user and user.user_type == 'lecturer':
            self.fields['course'].queryset = user.courses.all()
