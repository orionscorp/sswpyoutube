from django.urls import path
from .controllers import livestreams, channels

urlpatterns = [
    path('', livestreams.index, name='index'),

    path('channel/all/', channels.channelsIndex, name='channel-index'),
    path('channel/<str:channelId>/', channels.channelDetail, name='channel-detail'),
    path('channel/save/<str:channelId>/', channels.confirmSaveChannel, name='confirm-save-channel'),
]