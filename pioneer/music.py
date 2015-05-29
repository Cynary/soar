import re
melody = "HauntHouse: d=4,o=5,b=108: 2a4, 2e, 2d#, 2b4, 2a4, 2c, 2d, 2a#4, 2e., e, 1f4, 1a4, 1d#, 2e., d, 2c., b4, 1a4, 1p, 2a4, 2e, 2d#, 2b4, 2a4, 2c, 2d, 2a#4, 2e., e, 1f4, 1a4, 1d#, 2e., d, 2c., b4, 1a4"

# Melody
def get_melody(rtttl_melody):
    rtttl_melody = rtttl_melody.replace(' ','')
    rtttl_pattern = "^[^:]*:d=(\d*),o=(\d*),b=(\d*):(.*)$"
    rtttl_match = re.search(rtttl_pattern,rtttl_melody)
    assert rtttl_match is not None, "Melody is not valid: %s" % melody
    d_duration,d_octave,bpm = (int(rtttl_match.group(i)) for i in (1,2,3))
    ms = 60000*4/bpm # 60,000 ms per minute, 4 beats per whole note

    notes = rtttl_match.group(4).split(",")
    note_pattern = "^(\d+)?([a-gA-GpP][#b]?)(\.)?(\d+)?$"
    answer = []
    for note in notes:
        note_match = re.search(note_pattern,note)
        assert note_match is not None, "Note is not valid: %s" % note
        gd,n,ge,go = (note_match.group(i) for i in (1,2,3,4))
        duration = int(gd) if gd is not None else d_duration
        octave = int(go) if go is not None else d_octave
        duration = ms/float(duration) if ge is None else 1.5*ms/float(duration)
        midi = 0 if n.lower() == 'p' else note_to_midi(n+str(octave))
        answer.extend([int(duration/20),midi])
    return answer

#Input is string in the form C#-4, Db-4, or F-3. If your implementation doesn't use the hyphen, 
#just replace the line :
#    letter = midstr.split('-')[0].upper()
#with:
#    letter = midstr[:-1]
def note_to_midi(note):
    notes = [
        ["C"],
        ["C#","Db"],
        ["D"],
        ["D#","Eb"],
        ["E"],
        ["F"],
        ["F#","Gb"],
        ["G"],
        ["G#","Ab"],
        ["A"],
        ["A#","Bb"],
        ["B"]
    ]
    answer = 0
    letter = note[:-1].upper()
    answer = [i for (i,n) in enumerate(notes) if letter in n][0]
    #Octave
    answer += (int(note[-1]))*12
    return answer
