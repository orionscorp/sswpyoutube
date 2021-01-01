'''
This is the only modules that other apps should 
interact with
'''

from django.db.models import Q

from youtubeapi.models.channel import Channel
from youtubeapi.models.video import Video

from .youtube_xml import fetchXML, fetchChannelXML
from .youtube_api import fetchVideosAPI, fetchChannelAPI, fetchPlaylistItemsAPI
import youtubeapi.controllers.debug_helper as debug_helper

# Yield successive n-sized chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n]

'''
make an asynchronous http requests to all channels' rss, acquire the
respective xml file, parse them, and if there is any new video, use
youtube api to get its details and save it into db.

arguments: none
return value: number of new videos found (int)

should be running periodically in the background
'''
@debug_helper.st_time
def refreshFeeds():
    fetched = fetchXML()
    newlyCrawledVideoIdList = []
    for item in fetched:
        newlyCrawledVideoIdList.extend(item)
    
    # YouTube API videos.list() allows up to 50 videoIds per call.
    # since we crawl all channels periodically, it shouldn't exceeds 50.
    # but for testing purposes, we might crawl all channels that has never been 
    # crawled which potentially yields more than 50 uncrawled videos
    numOfVids = len(newlyCrawledVideoIdList)

    if numOfVids > 0:
        dividedChunks = list(divide_chunks(newlyCrawledVideoIdList, 50))
        for chunk in dividedChunks:
            videoIdString = ",".join(chunk)
            items = fetchVideosAPI(videoIdString)

            for item in items:
                currVideoId = item['id']
                currChannelId = item['snippet']['channelId']
                currTitle = item['snippet']['title']
                currThumbnail = item['snippet']['thumbnails']['medium']['url']
                currPublishedAt = item['snippet']['publishedAt']
                currLiveBroadcastContent = item['snippet']['liveBroadcastContent']
                try:
                    currScheduledStartTime = item['liveStreamingDetails']['scheduledStartTime']
                except:
                    currScheduledStartTime = None

                try:
                    currActualStartTime = item['liveStreamingDetails']['actualStartTime']
                except:
                    currActualStartTime = None

                try:
                    currActualEndTime = item['liveStreamingDetails']['actualEndTime']
                except:
                    currActualEndTime = None

                newVideo = Video(
                    videoId=currVideoId,
                    # channelId=currChannelId,
                    title=currTitle,
                    thumbnail=currThumbnail,
                    publishedAt=currPublishedAt,
                    liveBroadcastContent=currLiveBroadcastContent,
                    scheduledStartTime=currScheduledStartTime,
                    actualStartTime=currActualStartTime,
                    actualEndTime=currActualEndTime,
                )
                newVideo.channelId_id = currChannelId

                try:
                    newVideo.save()
                except Exception as e:
                    print(e)
                    return HttpResponseRedirect(reverse('channel-index'))
        return numOfVids
    else:
        return 0

'''
For every videos in the db that are set as upcoming or live, use 
youtube api to get its metadata again (to check if it's already live
or has recently ended) and save it in the db.

arguments: none
return value: number of videos refreshed (int)

should be running periodically in the background
'''
@debug_helper.st_time
def refreshWatchlist():
    watchlist = Video.objects.filter(Q(liveBroadcastContent='live') | Q(liveBroadcastContent='upcoming'))
    # in most cases, if you run this with enough interval, it shouldn't exceeds 50 videos. but just in case
    watchlistedVideoIdList = [video.videoId for video in watchlist]
    dividedChunks = list(divide_chunks(watchlistedVideoIdList, 50))

    for chunk in dividedChunks:
        videoIdString = ",".join(chunk)

        # what would happen if the video is unarchived or privated, who knows, too bad
        items = fetchVideosAPI(videoIdString)

        for item in items:
            currVideoId = item['id']
            currTitle = item['snippet']['title']
            currThumbnail = item['snippet']['thumbnails']['medium']['url']
            currPublishedAt = item['snippet']['publishedAt']
            currLiveBroadcastContent = item['snippet']['liveBroadcastContent']
            try:
                currScheduledStartTime = item['liveStreamingDetails']['scheduledStartTime']
            except:
                currScheduledStartTime = None

            try:
                currActualStartTime = item['liveStreamingDetails']['actualStartTime']
            except:
                currActualStartTime = None

            try:
                currActualEndTime = item['liveStreamingDetails']['actualEndTime']
            except:
                currActualEndTime = None

            currVideo = Video.objects.get(pk=currVideoId)
            currVideo.title = currTitle
            currVideo.thumbnail = currThumbnail
            currVideo.publishedAt = currPublishedAt
            currVideo.liveBroadcastContent = currLiveBroadcastContent
            currVideo.scheduledStartTime = currScheduledStartTime
            currVideo.actualStartTime = currActualStartTime
            currVideo.actualEndTime = currActualEndTime

            try:
                currVideo.save()
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('channel-index'))
    return len(watchlistedVideoIdList)

'''
check if the channel exist, this is so that we don't have to 
expend a youtube api call just to check if a channel exists,
instead, we use its xml feed
'''
def isChannelExist(channelId):
    channelTuple = fetchChannelXML(channelId)
    if channelTuple:
        return channelTuple
    else:
        return False

'''
assuming a channel associated with the channelId exists, save the 
channel into the db along with all of its uploaded videos. Make
a validation before calling this function to ensure that the channel
really exists (use isChannelExist), otherwise the youtube api call 
will return a json response without any entries.

arguments: channelId associated with the YouTube channel (str)
return value: number of videos uploaded to the channel

important note: should we let users add new channel or just live it
to admins to curate the selection?
'''
@debug_helper.st_time
def saveNewChannel(channelId):
    fetchedChannel = fetchChannelAPI(channelId)
    newChannel = Channel(channelId=fetchedChannel[0], name=fetchedChannel[1], icon=fetchedChannel[2], uploadPlaylist=fetchedChannel[3])
    try:
        # save the channel and all the uploaded videos into db
        newChannel.save()
        # playlistItems.list() doesn't give full info of a video, you need videos.list() for that
        newlyCrawledVideoIdList = []
        fetchedVideos = fetchPlaylistItemsAPI(newChannel.uploadPlaylist)
        numOfVids = len(fetchedVideos)

        if numOfVids > 0:
            for item in fetchedVideos:
                newlyCrawledVideoIdList.append(item['snippet']['resourceId']['videoId'])

            dividedChunks = list(divide_chunks(newlyCrawledVideoIdList, 50))
            for chunk in dividedChunks:
                videoIdString = ",".join(chunk)
                items = fetchVideosAPI(videoIdString)

                for item in items:
                    currVideoId = item['id']
                    currChannelId = item['snippet']['channelId']
                    currTitle = item['snippet']['title']
                    currThumbnail = item['snippet']['thumbnails']['medium']['url']
                    currPublishedAt = item['snippet']['publishedAt']
                    currLiveBroadcastContent = item['snippet']['liveBroadcastContent']
                    try:
                        currScheduledStartTime = item['liveStreamingDetails']['scheduledStartTime']
                    except:
                        currScheduledStartTime = None

                    try:
                        currActualStartTime = item['liveStreamingDetails']['actualStartTime']
                    except:
                        currActualStartTime = None

                    try:
                        currActualEndTime = item['liveStreamingDetails']['actualEndTime']
                    except:
                        currActualEndTime = None

                    newVideo = Video(
                        videoId=currVideoId,
                        channelId=newChannel,
                        title=currTitle,
                        thumbnail=currThumbnail,
                        publishedAt=currPublishedAt,
                        liveBroadcastContent=currLiveBroadcastContent,
                        scheduledStartTime=currScheduledStartTime,
                        actualStartTime=currActualStartTime,
                        actualEndTime=currActualEndTime,
                    )

                    newVideo.save()

            return numOfVids

    except Exception as e:
        print(e)
        # implement the error msg!!!! but i dont even know what kind of error this'll produce, if any.
        return 0