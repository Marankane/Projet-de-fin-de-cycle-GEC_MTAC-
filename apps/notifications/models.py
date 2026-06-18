from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    TYPES = [
        ('COURRIER_ASSIGNE', 'Courrier assigné'),
        ('COURRIER_ECHU', 'Courrier échu'),
        ('COURRIER_RETOURNE', 'Courrier retourné'),
        ('RAPPEL', 'Rappel'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.URLField(blank=True)
    courrier = models.ForeignKey('courriers.Courrier', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    lue = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']

    def __str__(self):
        return f"{self.utilisateur} - {self.titre}"

    @property
    def priority_order(self):
        # Define priority order: urgent first, then by type, then by date
        type_priority = {
            'COURRIER_ECHU': 1,
            'COURRIER_ASSIGNE': 2,
            'COURRIER_RETOURNE': 3,
            'RAPPEL': 4,
        }
        base_priority = type_priority.get(self.type, 5)
        
        # For COURRIER_ASSIGNE, check if the courrier is urgent
        if self.type == 'COURRIER_ASSIGNE' and hasattr(self, '_courrier'):
            courrier = self._courrier
            if courrier.priorite.code in ['URG', 'TRES_URG']:
                return 0  # Urgent always first
        
        return base_priority