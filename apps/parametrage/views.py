from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from core.permissions import AdminMixin
from .models import Priorite, StatutCourrier, TypeCourrier

_fc=lambda: forms.TextInput(attrs={'class':'form-control'})
_fa=lambda: forms.Textarea(attrs={'class':'form-control','rows':2})
_fs=lambda: forms.Select(attrs={'class':'form-select'})
_fck=lambda: forms.CheckboxInput(attrs={'class':'form-check-input'})
_fn=lambda: forms.NumberInput(attrs={'class':'form-control'})

class TypeCourrierForm(forms.ModelForm):
    class Meta:
        model=TypeCourrier; fields=['libelle','code','description','ordre','actif']
        widgets={'libelle':_fc(),'code':_fc(),'description':_fa(),'ordre':_fn(),'actif':_fck()}

class StatutForm(forms.ModelForm):
    class Meta:
        model=StatutCourrier; fields=['code','libelle','couleur','est_final','ordre']
        widgets={'code':_fc(),'libelle':_fc(),'couleur':_fs(),'est_final':_fck(),'ordre':_fn()}

class PrioriteForm(forms.ModelForm):
    class Meta:
        model=Priorite; fields=['code','libelle','delai_jours','couleur','ordre']
        widgets={'code':_fc(),'libelle':_fc(),'delai_jours':_fn(),'couleur':_fs(),'ordre':_fn()}

class IndexView(AdminMixin, ListView):
    template_name = 'parametrage/index.html'
    def get_queryset(self): return TypeCourrier.objects.all()
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['types'] = TypeCourrier.objects.all().order_by('ordre')
        ctx['statuts'] = StatutCourrier.objects.all().order_by('ordre')
        ctx['priorites'] = Priorite.objects.all().order_by('ordre')
        return ctx

class TypeCreateView(AdminMixin, CreateView):
    model=TypeCourrier; form_class=TypeCourrierForm; template_name='parametrage/form.html'
    success_url=reverse_lazy('parametrage:index')
    def form_valid(self,f): messages.success(self.request,"Type créé."); return super().form_valid(f)
    def get_context_data(self,**kw): return {**super().get_context_data(**kw),'titre':"Nouveau type de courrier",'retour_url':self.success_url}

class TypeUpdateView(AdminMixin, UpdateView):
    model=TypeCourrier; form_class=TypeCourrierForm; template_name='parametrage/form.html'
    success_url=reverse_lazy('parametrage:index')
    def form_valid(self,f): messages.success(self.request,"Type mis à jour."); return super().form_valid(f)
    def get_context_data(self,**kw): return {**super().get_context_data(**kw),'titre':f"Modifier – {self.object.libelle}",'retour_url':self.success_url}

class StatutCreateView(AdminMixin, CreateView):
    model=StatutCourrier; form_class=StatutForm; template_name='parametrage/form.html'
    success_url=reverse_lazy('parametrage:index')
    def form_valid(self,f): messages.success(self.request,"Statut créé."); return super().form_valid(f)
    def get_context_data(self,**kw): return {**super().get_context_data(**kw),'titre':"Nouveau statut",'retour_url':self.success_url}

class StatutUpdateView(AdminMixin, UpdateView):
    model=StatutCourrier; form_class=StatutForm; template_name='parametrage/form.html'
    success_url=reverse_lazy('parametrage:index')
    def form_valid(self,f): messages.success(self.request,"Statut mis à jour."); return super().form_valid(f)
    def get_context_data(self,**kw): return {**super().get_context_data(**kw),'titre':f"Modifier statut – {self.object.code}",'retour_url':self.success_url}

class PrioriteCreateView(AdminMixin, CreateView):
    model=Priorite; form_class=PrioriteForm; template_name='parametrage/form.html'
    success_url=reverse_lazy('parametrage:index')
    def form_valid(self,f): messages.success(self.request,"Priorité créée."); return super().form_valid(f)
    def get_context_data(self,**kw): return {**super().get_context_data(**kw),'titre':"Nouvelle priorité",'retour_url':self.success_url}

class PrioriteUpdateView(AdminMixin, UpdateView):
    model=Priorite; form_class=PrioriteForm; template_name='parametrage/form.html'
    success_url=reverse_lazy('parametrage:index')
    def form_valid(self,f): messages.success(self.request,"Priorité mise à jour."); return super().form_valid(f)
    def get_context_data(self,**kw): return {**super().get_context_data(**kw),'titre':f"Modifier – {self.object.libelle}",'retour_url':self.success_url}
