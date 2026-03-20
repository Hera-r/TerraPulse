from django.db import models


class EcoCompany(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=20, unique=True)
    sector = models.CharField(max_length=50)  # EV, Solar, Wind, etc.
    emoji = models.CharField(max_length=4, default='🌱')

    def __str__(self):
        return f"{self.name} ({self.ticker})"


class TradingSignal(models.Model):
    SIGNAL_CHOICES = [('BUY', 'Achat'), ('SELL', 'Vente'), ('HOLD', 'Attente')]
    company = models.ForeignKey(EcoCompany, on_delete=models.CASCADE)
    signal_type = models.CharField(max_length=10, choices=SIGNAL_CHOICES)
    confidence = models.IntegerField(default=70)
    reasoning = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.signal_type} {self.company.ticker} — {self.confidence}%"

    class Meta:
        ordering = ['-timestamp']
