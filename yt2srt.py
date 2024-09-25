#!/usr/bin/python3
##############################################################################
# yt2srt - converts youtube transcripts to SRT (SubRip) file format
##############################################################################
# version : 1.0
# license : MIT
# last ed : Tue Sep 24 20:19:58
##############################################################################
#    If you go to a youtube video page and click on '..more', at the bottom of
# the video information, you will see a button for "Show Transcript". These
# are usually auto-generated transcripts.
#
#    You can select all the text from these transcripts and save them. However
# they do not have an index, nor do they provide a duration for how long the
# text should stay up.
#
#    This program determines how long text should stay up based on the number
# of characters and number of words being displayed, as well as when the next
# subtitle text is being displayed (so that the times do not overlap).
#
#    With this information, the program is able to easily generate the index
# numbers and the two timestamps that an SRT file needs.
# 
##############################################################################
import sys
##############################################################################
##########################       DEFINES       ###############################
##############################################################################
# Note: if subs appear to be lasting too long on the screen you can adjust
#       the OFFSET to be lower. OFFSET should be between 000 and 999.
##############################################################################
OFFSET = '999'

##############################################################################
##########################      FUNCTIONS      ###############################
##############################################################################
def IsYTtimestamp(timestamp):
    if len(timestamp) == 0:
        return False
    # does it have a number at the start [0] and at the end?
    if not timestamp[0].isdigit():
        return False
    if not timestamp[len(timestamp)-1].isdigit():
        return False
    # does it contain a semi-colon ':'
    if ':' not in timestamp:
        return False
    # Its probably a valid timestamp 
    return True

def timestamp2seconds(timestamp):
    hours   = 0
    minutes = 0
    seconds = 0
    times = timestamp.split(':')
    if len(times) == 3:
        hours   = int(times[0])
        minutes = int(times[1])
        seconds = int(times[2])
    if len(times) == 2:
        minutes = int(times[0])
        seconds = int(times[1])
    if hours:
        seconds = seconds + (hours   * 60 * 60)
    if minutes:
        seconds = seconds + (minutes * 60)
    return seconds

def seconds2timestamp(seconds):
    timestampSeconds = 0
    timestampMinutes = 0
    timestampHours   = 0

    # seconds
    timestampSeconds = seconds % 60

    # update time
    seconds = seconds - (timestampSeconds)

    # hours
    if (seconds > 3600):
        timestampHours = int(seconds / 3600)

    # update time
    seconds = seconds - (timestampHours * 3600)

    # minutes
    timestampMinutes = int(seconds / 60)

    timestamp = str(timestampHours).zfill(2)
    timestamp = timestamp + ':'
    timestamp = timestamp + str(timestampMinutes).zfill(2)
    timestamp = timestamp + ':'
    timestamp = timestamp + str(timestampSeconds).zfill(2)

    return timestamp

def ScrubLines(lines):
    newLines   = []
    oddness    = True
    lineNumber = 0
    for line in lines:
        lineNumber = lineNumber+1
        line = line.rstrip()
        if (oddness):
            # check if this line contains a number as first character
            # if it doesn't, then skip this line
            if IsYTtimestamp(line) == False:
                #print('Found an invalid timestamp at line #' + str(lineNumber))
                continue
            newLines.append(line)
        else:
            newLines.append(line)
        oddness = not oddness
    return newLines

def lines2subs(lines):
    subtitles  = []
    lineNumber = 0
    index      = 0
    subSeconds = 0
    for line in lines:
        subtitle = {}
        lineNumber = lineNumber + 1
        if (lineNumber % 2):
            subSeconds = timestamp2seconds(line)
        else:
            subtitle['seconds'] = subSeconds
            subtitle['text']    = line
            subtitles.append(subtitle)
            subSeconds = 0 # reset should be un-necessary, but may be useful
    return subtitles

def TimeDifference(time1, time2):
    if (time2 <= time1):
        return 0
    duration = (time2 - time1)
    return duration

def SubTime(text):
    numCharacters = len(text)
    numWords      = len(text.split())

    if (numCharacters < 8):
        return 1

    characterTime = round(numCharacters/15)
    wordTime      = round(numWords/3)

    subTime = round((characterTime + wordTime) / 2)

    return subTime

def DurationDifferential(sub1, sub2 = None):
    maxDuration = 0

    if sub2 is not None:
        maxDuration = TimeDifference(sub1['seconds'], sub2['seconds'])

        if (maxDuration <= 1):
            return 0

    duration = SubTime(sub1['text'])

    # max check should be all done outside of this function since this 
    # function is only supposed to give us the differential.

    if maxDuration:
        if maxDuration < duration:
            duration = maxDuration

    # we always have to have the duration 1 seconds less than the intended
    duration = duration - 1

    if duration < 0:
        duration = 0

    return duration

def TimestampDuration(time1, time2):
    duration = ''
    duration = duration + seconds2timestamp(time1)
    duration = duration + ',000'
    duration = duration + ' --> '
    duration = duration + seconds2timestamp(time2)
    duration = duration + ',' + OFFSET

    return duration
    
def subs2lines(subtitles):
    lines = []
    numSubs = len(subtitles)
    for i in range(numSubs):
        index      = i+1
        startTime  = subtitles[i]['seconds']
        endTime    = 0
        if index >= numSubs:
            endTime = startTime + DurationDifferential(subtitles[i])
        else:
            endTime = startTime + DurationDifferential(subtitles[i], subtitles[i+1])
        timestamp  = TimestampDuration(startTime, endTime)
        text       = subtitles[i]['text']
        lines.append(str(index)+ '\n')
        lines.append(timestamp + '\n')
        lines.append(text      + '\n')
        lines.append('\n')
    return lines

def ReadYTFile(fileName):
    try:
        with open(fileName, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print('File not found.')
        exit();
    except:
        print('Unable to read file.')
        exit();

    return lines
##############################################################################
##########################         MAIN        ###############################
##############################################################################
def main():
    if (len(sys.argv) != 2):
        print('Usage: yt2srt <file.yt>');
        exit();

    #
    # Read the file
    #
    subfile  = sys.argv[1]

    if (subfile[-3:] != ".yt"):
        fileName = str(subfile) + ".yt"
    else:
        fileName = str(subfile)

    lines = ReadYTFile(fileName)

    #
    # Convert lines to subtitles (after cleaning/scrubbing them)
    #

    lines     = ScrubLines(lines)
    subtitles = lines2subs(lines)

    #
    # Debug/Verbose information
    #

    #print(str(len(lines)) + ' lines read.')
    #print('Subtitle count: ' + str(int(len(subtitles))))

    #
    # Process the subtitles
    #

    output = subs2lines(subtitles)

    try:
        #
        # Set output filename
        #
        if (subfile[-3:] != ".yt"):
            outFilename = str(subfile)
        else:
            outFilename = str(subfile[:-3])
        outFilename = outFilename + '.srt'

        #
        # Write to file
        #
        file2 = open(outFilename, "w")
        file2.writelines(output)
        file2.close()
    except:
        print('Failed to output to file.')
        exit()

##############################################################################
##############################################################################
##############################################################################
if __name__ == "__main__":
    main()
