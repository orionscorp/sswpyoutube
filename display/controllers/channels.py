from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages

from datetime import datetime, timedelta

from youtubeapi.models.channel import Channel
from youtubeapi.models.video import Video
from youtubeapi.controllers.helper import isChannelExist, saveNewChannel

from display.forms.find_channel_form import findChannelForm

def channelsIndex(request):

    if request.method == 'POST':
        form = findChannelForm(request.POST)
        if form.is_valid():
            channelId = form.cleaned_data['channelId']
            # check if channel exists in db, otherwise fetch with youtube xml feed
            try:
                selectedChannel = Channel.objects.get(pk=channelId)
                # print("channel found in db")
                # display in another page
                return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))
            except:
                # print("channel not found in db")
                # check if its a valid youtube channel, and asks if user want to save it and crawl it
                return HttpResponseRedirect(reverse('confirm-save-channel', args=[channelId]))

    else:
        form = findChannelForm()
    
    channels = Channel.objects.all()

    data = {
        'form':form,
        'channels':channels,
    }

    return render(request, 'channel/index.html', context=data)

def channelDetail(request, channelId):
    try:
        selectedChannel = Channel.objects.get(pk=channelId)
    except:
        # the user isn't supposed to write the url manually
        messages.info(request, 'Channel associated with the ID not found on our database.')
        # don't forget to implement the message in the template
        return HttpResponseRedirect(reverse('channel-index'))

    upcomingVideos = Video.objects.filter(channelId=selectedChannel, liveBroadcastContent='upcoming')
    liveVideos = Video.objects.filter(channelId=selectedChannel, liveBroadcastContent='live')

    # still sceptical about this one, if its gte, does it also include 
    # every video in the future? of course i filtered with liveBroadcastContent='none'.
    # but still unsure nonetheless
    how_many_hours = 6
    recentlyEndedStreams = Video.objects.filter(channelId=selectedChannel, liveBroadcastContent='none', publishedAt__gte=datetime.now()-timedelta(hours=how_many_hours))

    data = {
        'selectedChannel':selectedChannel,
        'upcomingVideos':upcomingVideos,
        'liveVideos':liveVideos,
        'recentlyEndedStreams':recentlyEndedStreams,
    }

    return render(request, 'channel/detail.html', context=data)

def confirmSaveChannel(request, channelId):
    if request.method == 'POST':
        numOfVids = saveNewChannel(channelId)
        if numOfVids:
            return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))
        else:
            return HttpResponseRedirect(reverse('channel-index'))

    else:
        channelTuple = isChannelExist(channelId)
        if channelTuple:
            data = {
                'fetchedChannel':channelTuple,
            }
            return render(request, 'channel/confirm_save_channel.html', context=data)
        else:
            print("Channel not found")
            return HttpResponseRedirect(reverse('channel-index'))