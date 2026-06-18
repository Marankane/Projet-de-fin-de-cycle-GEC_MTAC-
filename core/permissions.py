from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

try:
    from rest_framework.permissions import BasePermission
    class _R(BasePermission):
        roles = []
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated and request.user.role in self.roles)
    class EstAdmin(_R):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')
    class EstAgent(_R):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated and request.user.role in ['AGENT', 'ADMIN'])
    class PeutDispatchez(_R):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated and request.user.peut_dispatcher)
    class PeutValider(_R):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated and request.user.peut_valider)
    class PeutVoirConfidentiel(_R):
        def has_permission(self, request, view):
            u = request.user
            return bool(u and u.is_authenticated and (u.role == 'ADMIN' or (u.service and u.service.code in ['SGA', 'SG', 'MIN', 'CABINET'])))
    class PeutGererTransmission(_R):
        def has_permission(self, request, view):
            u = request.user
            return bool(u and u.is_authenticated and (u.role in ['AGENT', 'ADMIN'] or (u.service and u.service.code in ['SGA', 'SG', 'MIN', 'CABINET'])))
except ImportError:
    pass

class _M(LoginRequiredMixin, UserPassesTestMixin):
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

class AgentMixin(_M):
    def test_func(self): return self.request.user.role in ['AGENT', 'ADMIN']

class SecretaireMixin(_M):
    def test_func(self): return self.request.user.role in ['SECRETAIRE', 'ADMIN']

class ChefMixin(_M):
    def test_func(self): return self.request.user.role in ['CHEF_SERVICE', 'ADMIN']

class AdminMixin(_M):
    def test_func(self): return self.request.user.role == 'ADMIN'

class DispatchMixin(_M):
    def test_func(self): return self.request.user.peut_dispatcher

class ValidationMixin(_M):
    def test_func(self): return self.request.user.peut_valider

class ConfidentielMixin(_M):
    def test_func(self):
        u = self.request.user
        if u.role == 'ADMIN' or u.peut_voir_tout:
            return True
        if u.service and u.service.code in ['SGA', 'SG', 'MIN', 'CABINET']:
            return True
        return False

class TransmissionMixin(_M):
    def test_func(self):
        u = self.request.user
        if u.role in ['AGENT', 'ADMIN']:
            return True
        if u.service and u.service.code in ['SGA', 'SG', 'MIN', 'CABINET']:
            return True
        return False
