from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Wallet(models.Model):
    """
    Manages user balances, escrow deposits, and M-Pesa ledger allocations.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    escrowed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                          validators=[MinValueValidator(0.00)])
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet — Balance: {self.balance} KSh"


class Chama(models.Model):
    """
    A 4-player persistent or session-based squad competing against other rooms.
    """
    name = models.CharField(max_length=100, unique=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_chamas")
    members = models.ManyToManyField(User, related_name="chamas")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chama: {self.name} ({self.members.count()}/4 members)"


class TriviaRoom(models.Model):
    """
    Represents an orchestrated multi-player instance (Solo or Chama format).
    """
    ROOM_FORMAT_CHOICES = [
        ('SOLO', 'Solo Individual Room'),
        ('CHAMA', 'Chama Squad Room'),
    ]

    ROOM_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled / Accepting Stakes'),
        ('ACTIVE', 'Live In-Progress'),
        ('COMPLETED', 'Completed & Settled'),
        ('CANCELLED', 'Cancelled & Refunded'),
    ]

    room_code = models.CharField(max_length=12, unique=True, db_index=True)
    format_type = models.CharField(max_length=10, choices=ROOM_FORMAT_CHOICES, default='SOLO')
    status = models.CharField(max_length=15, choices=ROOM_STATUS_CHOICES, default='SCHEDULED')
    stake_amount = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    total_pot = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Active state flags managed by the game clock loop
    current_question_index = models.PositiveIntegerField(default=0)
    question_expires_at = models.DateTimeField(null=True, blank=True)

    scheduled_start = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_code} [{self.format_type}] — {self.status}"


class RoomParticipation(models.Model):
    """
    Through-table tracking active competitors, their running scores, and state.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_participations")
    room = models.ForeignKey(TriviaRoom, on_delete=models.CASCADE, related_name="participants")
    chama = models.ForeignKey(Chama, on_delete=models.SET_NULL, null=True, blank=True, related_name="room_entries")
    running_score = models.IntegerField(default=0)
    is_disqualified = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')


class Question(models.Model):
    """
    Bank of verified multi-choice trivia items.
    """
    text = models.TextField()
    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    correct_choice = models.CharField(max_length=1, choices=[('A', 'Choice A'), ('B', 'Choice B'), ('C', 'Choice C')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.text[:50]}..."


class PlayerResponse(models.Model):
    """
    Tracks precise speed/accuracy parameters for score decay evaluations.
    """
    participant = models.ForeignKey(RoomParticipation, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    response_time_ms = models.PositiveIntegerField(help_text="Time taken in milliseconds to determine score decay")
    is_correct = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant', 'question')


class SpectatorStream(models.Model):
    """
    Tracks transient passive connections monitoring a public room.
    """
    room = models.ForeignKey(TriviaRoom, on_delete=models.CASCADE, related_name="spectators")
    session_key = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)


class SpectatorChatMessage(models.Model):
    """
    Stores non-player public chat interactions tied to the lower presentation grid.
    """
    room = models.ForeignKey(TriviaRoom, on_delete=models.CASCADE, related_name="chat_messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spectator_chats")
    message = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"@{self.user.username} in Room {self.room.room_code}: {self.message[:20]}"