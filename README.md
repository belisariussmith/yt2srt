# yt2srt
Converts YouTube transcripts to SRT (SubRip) file format

   If you go to a youtube video page and click on '..more', at the bottom of
the video information, you will see a button for "Show Transcript". These
are usually auto-generated transcripts.

   You can select all the text from these transcripts and save them. However
they do not have an index, nor do they provide a duration for how long the
text should stay up.

   This program determines how long text should stay up based on the number
of characters and number of words being displayed, as well as when the next
subtitle text is being displayed (so that the times do not overlap).

   With this information, the program is able to easily generate the index
numbers and the two timestamps that an SRT file needs.
