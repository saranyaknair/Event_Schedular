from django import forms
from .models import Event, Session, Speaker

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location']

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title', 'start_time', 'end_time', 'speaker']

    def clean(self):
        cleaned_data = super().clean()
        speaker = cleaned_data.get('speaker')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        event = cleaned_data.get('event')

        if not speaker or not start_time or not end_time:
            return cleaned_data  # Skip validation if incomplete

        # Check if the speaker is already booked in another session overlapping with this one
        overlapping_sessions = Session.objects.filter(
            speaker=speaker,
            event__date=event.date,
        ).exclude(id=self.instance.id).filter(
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if overlapping_sessions.exists():
            raise forms.ValidationError(
                f"{speaker.name} is already assigned to another session during this time slot."
            )

        return cleaned_data
    
class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = ['name', 'bio']
