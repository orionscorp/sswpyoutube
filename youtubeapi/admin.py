from django.contrib import admin

from youtubeapi.models import channel, video

# Register your models here.
admin.site.register(channel.Channel)
admin.site.register(video.Video)