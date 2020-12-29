from django.urls import path
from .controllers import tester

urlpatterns = [
    path('tester/channel/save/<str:channelId>/', tester.confirmSaveChannel, name='confirm-save-channel'),

    path('tester/update/feeds/', tester.updateRecentFeeds, name='update-recent-feeds'),
    path('tester/update/watchlist/', tester.updateWatchlist, name='update-watchlist'),
]