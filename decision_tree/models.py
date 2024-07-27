from django.db import models

class PotType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class FlopTexture(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class BetSize(models.Model):
    pot_type = models.ForeignKey(PotType, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    flop_texture = models.ForeignKey(FlopTexture, on_delete=models.CASCADE)
    size = models.CharField(max_length=50)

    class Meta:
        unique_together = ('pot_type', 'position', 'player', 'flop_texture')

    def __str__(self):
        return f"{self.pot_type} - {self.position} - {self.player} - {self.flop_texture}: {self.size}"

class BetFrequency(models.Model):
    pot_type = models.ForeignKey(PotType, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    flop_texture = models.ForeignKey(FlopTexture, on_delete=models.CASCADE)
    hand = models.CharField(max_length=10)
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1_frequencies')
    player1_frequency = models.IntegerField()
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2_frequencies')
    player2_frequency = models.IntegerField()

    class Meta:
        unique_together = ('pot_type', 'position', 'flop_texture', 'hand')

    def __str__(self):
        return f"{self.pot_type} - {self.position} - {self.flop_texture} - {self.hand}"