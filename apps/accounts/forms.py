from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur, Role

_fc = lambda ph='': forms.TextInput(attrs={'class':'form-control','placeholder':ph})
_fe = lambda ph='': forms.EmailInput(attrs={'class':'form-control','placeholder':ph})
_fp = lambda: forms.PasswordInput(attrs={'class':'form-control'})
_fs = lambda: forms.Select(attrs={'class':'form-select'})
_fck= lambda: forms.CheckboxInput(attrs={'class':'form-check-input'})

class ConnexionForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control form-control-lg','placeholder':'email@mintransport.ne','autofocus':True}))
    mot_de_passe = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-lg','placeholder':'••••••••','id':'pwd-input'}))
    se_souvenir = forms.BooleanField(required=False, widget=_fck())

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self._user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        email = cd.get('email')
        mdp = cd.get('mot_de_passe')
        if email and mdp:
            self._user = authenticate(self.request, username=email, password=mdp)
            if not self._user:
                raise forms.ValidationError("E-mail ou mot de passe incorrect.")
            if not self._user.is_active:
                raise forms.ValidationError("Ce compte est désactivé. Contactez l'administrateur.")
        return cd

    def get_utilisateur(self): return self._user

class CreationUtilisateurForm(forms.ModelForm):
    mdp1 = forms.CharField(label="Mot de passe", widget=_fp(), validators=[validate_password])
    mdp2 = forms.CharField(label="Confirmation", widget=_fp())

    class Meta:
        model = Utilisateur
        fields = ['email','nom','prenom','role','service','telephone','notifier_par_email']
        widgets = {'email':_fe(),'nom':_fc(),'prenom':_fc(),'role':_fs(),'service':_fs(),'telephone':_fc('+227 90 00 00 00'),'notifier_par_email':_fck()}

    def clean_mdp2(self):
        if self.cleaned_data.get('mdp1') != self.cleaned_data.get('mdp2'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return self.cleaned_data.get('mdp2')

    def clean(self):
        cd = super().clean()
        if cd.get('role') not in ['DIRECTEUR','ADMIN'] and not cd.get('service'):
            self.add_error('service', "Un service est requis pour ce rôle.")
        return cd

    def save(self, commit=True):
        u = super().save(commit=False)
        u.set_password(self.cleaned_data['mdp1'])
        if commit: u.save()
        return u

class EditionUtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['email','nom','prenom','role','service','telephone','is_active','notifier_par_email']
        widgets = {'email':_fe(),'nom':_fc(),'prenom':_fc(),'role':_fs(),'service':_fs(),'telephone':_fc(),'is_active':_fck(),'notifier_par_email':_fck()}

class EditionProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['nom','prenom','telephone','avatar','notifier_par_email']
        widgets = {'nom':_fc(),'prenom':_fc(),'telephone':_fc(),'avatar':forms.FileInput(attrs={'class':'form-control'}),'notifier_par_email':_fck()}

class ChangeMDPForm(forms.Form):
    ancien = forms.CharField(label="Mot de passe actuel", widget=_fp())
    mdp1 = forms.CharField(label="Nouveau mot de passe", widget=_fp(), validators=[validate_password])
    mdp2 = forms.CharField(label="Confirmation", widget=_fp())
    def __init__(self, utilisateur, *args, **kwargs):
        self.utilisateur = utilisateur
        super().__init__(*args, **kwargs)
    def clean_ancien(self):
        if not self.utilisateur.check_password(self.cleaned_data.get('ancien')):
            raise forms.ValidationError("Mot de passe actuel incorrect.")
        return self.cleaned_data.get('ancien')
    def clean(self):
        cd = super().clean()
        if cd.get('mdp1') != cd.get('mdp2'):
            raise forms.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return cd
    def sauvegarder(self):
        self.utilisateur.set_password(self.cleaned_data['mdp1'])
        self.utilisateur.save(update_fields=['password'])

class DemandeReinitForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control form-control-lg','placeholder':'votre.email@mintransport.ne'}))
    def get_utilisateur(self):
        try: return Utilisateur.objects.get(email=self.cleaned_data['email'], is_active=True)
        except Utilisateur.DoesNotExist: return None

class NouveauMDPForm(forms.Form):
    mdp1 = forms.CharField(label="Nouveau mot de passe", widget=_fp(), validators=[validate_password])
    mdp2 = forms.CharField(label="Confirmation", widget=_fp())
    def clean(self):
        cd = super().clean()
        if cd.get('mdp1') != cd.get('mdp2'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cd
