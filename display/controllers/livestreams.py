from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages

from datetime import datetime, timedelta

from youtubeapi.models.video import Video

def index(request):
    upcomingVideos = Video.objects.filter(liveBroadcastContent='upcoming')
    liveVideos = Video.objects.filter(liveBroadcastContent='live')

    # still sceptical about this one, if its gte, does it also include 
    # every video in the future? of course i filtered with liveBroadcastContent='none'.
    # but still unsure nonetheless
    how_many_hours = 6
    recentlyEndedStreams = Video.objects.filter(liveBroadcastContent='none', publishedAt__gte=datetime.now()-timedelta(hours=how_many_hours))

    data = {
        'upcomingVideos':upcomingVideos,
        'liveVideos':liveVideos,
        'recentlyEndedStreams':recentlyEndedStreams,
    }

    return render(request, 'stream/index.html', context=data)