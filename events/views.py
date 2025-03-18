from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Session, Speaker
from .forms import EventForm, SessionForm, SpeakerForm
from django.db.models import Prefetch
from django.contrib import messages
from collections import defaultdict

def event_list(request):
    events = Event.objects.all()
    form = EventForm()

    if request.method == "POST":
        event_id = request.POST.get("event_id")  # Get event ID from form
        if event_id:
            event = get_object_or_404(Event, pk=event_id)  # Fetch event
            form = EventForm(request.POST, instance=event)  # Populate form with event data
        else:
            form = EventForm(request.POST)  # Create a new event

        if form.is_valid():
            form.save()
            return redirect("event_list")  # Refresh page

    return render(request, "events/event_list.html", {"events": events, "form": form})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})

def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

def session_list(request):
    sessions = Session.objects.select_related('event').order_by('event__date', 'start_time')
    print(sessions)
    return render(request, "events/session_list.html", {"sessions": sessions})


def session_create(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.event = event
            session.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = SessionForm()
    return render(request, 'events/session_form.html', {'form': form, 'event': event})

def session_update(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect('session_list')
    else:
        form = SessionForm(instance=session)
    return render(request, 'events/session_form.html', {'form': form})


def session_delete(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        session.delete()
        return redirect('event_detail', event_id=session.event.id)
    return render(request, 'events/session_confirm_delete.html', {'session': session})


def speaker_list(request):
    speakers = Speaker.objects.all()
    return render(request, 'events/speaker_list.html', {'speakers': speakers})

# Speaker Detail View

def speaker_detail(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    return render(request, 'events/speaker_detail.html', {'speaker': speaker})

# Create Speaker

def speaker_create(request):
    if request.method == 'POST':
        form = SpeakerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('speaker_list')
    else:
        form = SpeakerForm()
    return render(request, 'events/speaker_form.html', {'form': form})

# Edit Speaker

def speaker_edit(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    if request.method == 'POST':
        form = SpeakerForm(request.POST, instance=speaker)
        if form.is_valid():
            form.save()
            return redirect('speaker_detail', pk=speaker.pk)
    else:
        form = SpeakerForm(instance=speaker)
    return render(request, 'events/speaker_form.html', {'form': form})

# Delete Speaker

def speaker_delete(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    if request.method == 'POST':
        speaker.delete()
        return redirect('speaker_list')
    return render(request, 'events/speaker_confirm_delete.html', {'speaker': speaker})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Session, Speaker

def assign_speaker(request, session_id):
    session = get_object_or_404(Session, pk=session_id)

    if request.method == 'POST':
        speaker_id = request.POST.get('speaker_id')
        if speaker_id:
            speaker = get_object_or_404(Speaker, pk=speaker_id)

            # Check if speaker is already assigned to another overlapping session
            overlapping_sessions = Session.objects.filter(
                speaker=speaker,
                start_time__lt=session.end_time,
                end_time__gt=session.start_time
            ).exclude(id=session.id)

            if overlapping_sessions.exists():
                messages.error(request, f"{speaker.name} is already assigned to another session during this time slot.")
            else:
                session.speaker = speaker
                session.save()
                messages.success(request, f"Speaker '{speaker.name}' assigned successfully!")
        else:
            session.speaker = None  # Optional: handle unassigning
            session.save()
            messages.success(request, "Speaker unassigned successfully!")

    return redirect('optimized_schedule')  # Redirect to your optimized schedule page



def optimized_schedule_view(request):
    events = Event.objects.prefetch_related(
        Prefetch('sessions', queryset=Session.objects.select_related('speaker').order_by('start_time'))
    ).order_by('date')

    speakers = Speaker.objects.all()

    # General session time conflicts (regardless of speaker)
    conflict_sessions = []

    # Speaker-specific conflict detection
    speaker_conflicts = defaultdict(list)

    for event in events:
        event_conflicts = []
        sessions = list(event.sessions.all())

        for i in range(len(sessions)):
            for j in range(i + 1, len(sessions)):
                # General session time conflict check
                if (sessions[i].start_time < sessions[j].end_time and
                        sessions[j].start_time < sessions[i].end_time):
                    event_conflicts.append((sessions[i], sessions[j]))

                # Speaker double booking check
                if (sessions[i].speaker and sessions[i].speaker == sessions[j].speaker and
                        sessions[i].start_time < sessions[j].end_time and
                        sessions[j].start_time < sessions[i].end_time):
                    speaker_conflicts[sessions[i].speaker].append((sessions[i], sessions[j]))

        if event_conflicts:
            conflict_sessions.append((event, event_conflicts))

    # Flash a warning if conflicts exist
    if conflict_sessions or speaker_conflicts:
        messages.warning(request, "Conflicts detected in the schedule. Please review overlapping sessions or speaker assignments.")

    return render(request, 'events/optimized_schedule.html', {
        'events': events,
        'conflicts': conflict_sessions,
        'speakers': speakers,
        'speaker_conflicts': speaker_conflicts,
    })
