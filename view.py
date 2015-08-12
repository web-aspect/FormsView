# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.forms.formsets import all_valid
        
        
        
        
class FormsView(TemplateView):
    """
    Позволяет работать с набором форм.
    form_class_dict - словарь, в котором ключ-префикс, значение-форма или формсет.
    instance_dict - словарь instance для форм, в котором ключ-префикс, значение-instance.
    Если instance_dict не содержит instance для формы, то в качестве instance будет использован
    результат метода get_object.
    
    """
    
    form_class_dict = {}
    instance_dict = {}
    success_url = None

    def get_form_class_dict(self):
        return self.form_class_dict.copy()

    def get_form_class(self, key):
        return self.get_form_class_dict()[key]
        
    def get_instance_dict(self):
        return self.instance_dict.copy()
        
    def get_object(self):
        return None
        
    def get_instance(self, key):
        return self.get_instance_dict().get(key, self.get_object())

    def get_kwargs_form(self, key, **kwargs):
        kwargs.update({'instance':self.get_instance(key), 'prefix':key})
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, key, **kwargs):
        class_ = self.get_form_class(key)
        return class_(**self.get_kwargs_form(key, **kwargs))
        
    def get_success_url(self):
        return self.success_url

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(objects=self.get_instance_dict())
        for key in self.get_form_class_dict().keys():
            context[key] = self.get_form(key)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        forms = {}
        for key in self.get_form_class_dict().keys():
            forms[key] = self.get_form(key)
            
        if all_valid(forms.values()):
            return self.form_valid(forms)
        else:
            return self.form_invalid(forms)

    def form_valid(self, forms):
        for key, value in forms.items():
            value.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        context = self.get_context_data(objects=self.get_instance_dict())
        context.update(**forms)
        return self.render_to_response(context)
