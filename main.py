import argparse
import datetime
import os
import re
import sys
from io import FileIO as file

# Flow of the Below Code
# main --> parse_input_arguments --> subtitles_setter --> offset_time  --> rzeropad


# Input the srt file and offset timing from user
def parse_input_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('offset', type=float)
    parser.add_argument('srt_file', type=file)

    return parser.parse_args()


# Use to add extra 0's to millisecond in case len of milli secs is less than 3
def rzeropad(ms):
    ms = str(int(ms))
    while len(ms) < 3:
        ms += "0"
    return ms


# This function modifies the actual time in srt by the given input offset
def offset_time(offset, time_string):
    ts = time_string.replace(',', ':').split(':')
    # replacing the last , with : and splitting by :
    ts = [int(x) for x in ts]
    # string to int
    ts = datetime.datetime(2020, 1, 1, ts[0], ts[1], ts[2], ts[3] * 1000)
    # millisecond -> microsecond

    delta = datetime.timedelta(seconds=offset)
    ts += delta  # Time adjustments are done

    if ts.year != 2020 or ts.month != 1 or ts.day != 1:
        sys.exit("ERROR: invalid offset resulting timestamp overflow")

    return "%s,%s" % (ts.strftime("%H:%M:%S"), rzeropad(ts.microsecond / 1000))
    # microsecond -> millisecond


def subtitles_setter(options):
    if '.srt' not in options.srt_file.name:
        # Checking the Extension of File
        sys.exit("ERROR: invalid srt file")
    # Adding the -sync to the original filename
    out_filename = os.path.splitext(options.srt_file.name)[0] + '-sync.srt'
    with open(out_filename, 'w', encoding='utf-8') as out:
        # Opening the new File in Write Mode
        with open(options.srt_file.name, 'r', encoding='utf-8') as srt:
            # Opening the Main Srt File in Read Mode
            for line in srt.readlines():
                # Extracting the Timer lines using regex: 00:03:36,055
                match = re.search(r'^(\d+:\d+:\d+,\d+)\s+--\>\s+(\d+:\d+:\d+,\d+)', line)
                if match:
                    out.write("%s --> %s\n" % (
                        offset_time(options.offset, match.group(1)),
                        # Modifying the Start time
                        offset_time(options.offset, match.group(2))
                        # Modifying the End time
                    ))
                else:
                    out.write(line)


if __name__ == "__main__":
    subtitles_setter(parse_input_arguments())

# expected input
# python main.py -0.5 C:\Users\deepatat\Downloads\Avengers_.Endgame.2019.720p.BluRay.x264.[YTS.MX]-English.srt
