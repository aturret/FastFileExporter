# FastYTDownloader
 
A Flask services wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp) and other Python packages cannot run in an asynchronous way, which is an optional extension for [FastFetchBot](https://github.com/aturret/FastFetchBot).

This is archived now since I have refactored FastFetchBot from HTTP over HTTP to a Celery worker to coordinate the synchronous functionalities.
