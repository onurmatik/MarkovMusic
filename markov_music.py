import random
import mido
import argparse


class Note:
    def __init__(
        self,
        key,
        start_velocity,
        end_velocity,
        note_duration,
        next_note_delay,
        tempo,
        instrument,
        timestamp,
    ):
        self.key = key
        self.start_velocity = start_velocity
        self.end_velocity = end_velocity
        self.note_duration = note_duration
        self.next_note_delay = next_note_delay
        self.tempo = tempo
        self.instrument = instrument
        self.timestamp = timestamp

    def __str__(self):
        return (
            f"k: {self.key} sv: {self.start_velocity} ev: {self.end_velocity} "
            f"nd: {self.note_duration} nnd: {self.next_note_delay}"
        )

    def __eq__(self, other):
        if isinstance(other, Note):
            return (
                self.key == other.key
                and self.start_velocity == other.start_velocity
                and self.end_velocity == other.end_velocity
                and self.note_duration == other.note_duration
                and self.next_note_delay == other.next_note_delay
                and self.tempo == other.tempo
                and self.instrument == other.instrument
            )
        return False

    def __hash__(self):
        hash_value = 5
        hash_value = 67 * hash_value + self.key
        hash_value = 67 * hash_value + self.start_velocity
        hash_value = 67 * hash_value + self.end_velocity
        hash_value = 67 * hash_value + self.note_duration
        hash_value = 67 * hash_value + self.next_note_delay
        hash_value = 67 * hash_value + self.tempo
        hash_value = 67 * hash_value + self.instrument
        return hash_value

    def rounded(self, velocity_rounding, duration_rounding, tempo_rounding):
        return Note(
            self.key,
            self.start_velocity - (self.start_velocity % velocity_rounding),
            self.end_velocity - (self.end_velocity % velocity_rounding),
            self.note_duration - (self.note_duration % duration_rounding),
            self.next_note_delay - (self.next_note_delay % duration_rounding),
            self.tempo - (self.tempo % tempo_rounding),
            self.instrument,
            self.timestamp,
        )


class MarkovMusic:
    def __init__(self, files, order=3, output_file='output.mid'):
        self.output = []
        self.option_map = {}
        self.count_map = {}
        self.resolution = 0
        self.files = files  # List of MIDI files to process
        self.order = order  # Markov chain order, default is 3
        self.output_file = output_file  # Output MIDI file name
        # Rounding properties of notes
        self.velocity_rounding = 40
        self.duration_rounding = 2000
        self.tempo_rounding = 1000000000
        self.target_channels = []
        self.default_tempo = 500001

    def run(self):
        self.output = []
        self.option_map = {}
        self.count_map = {}
        for file_name in self.files:
            print(f"Reading file: {file_name}")
            # Convert from a MIDI file to a list of parsed notes
            notes = self.read_input(file_name)
            # Add the notes to the probability map
            self.add_to_map(notes)
            print(f"{len(notes)} notes converted")
        print(f"\n{len(self.option_map)} mappings made (order {self.order})")
        print("Generating music")
        self.output = self.generate()
        print(f"{len(self.output)} notes generated")
        self.write_to_file()
        print("Output written to file")

    def read_input(self, file_name):
        merged_tracks = []
        try:
            mid = mido.MidiFile(file_name)
            self.resolution = mid.ticks_per_beat
            track_number = 0
            for track in mid.tracks:
                track_number += 1
                print(f"Track {track_number}: size = {len(track)}")
                ls = self.parse_track(track)
                merged_tracks.extend(ls)
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
        # Sort merged_tracks by timestamp
        merged_tracks.sort(key=lambda x: x.timestamp)
        for i in range(len(merged_tracks) - 1):
            a = merged_tracks[i]
            a.next_note_delay = merged_tracks[i + 1].timestamp - a.timestamp
        return merged_tracks

    def parse_track(self, track):
        notes = []
        open_notes = []
        tempo_changes = []
        tempo_values = []
        instrument_changes = []
        instrument_values = []

        current_tick = 0

        for msg in track:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity != 0:
                if not self.target_channels or msg.channel in self.target_channels:
                    data = [msg.note, msg.velocity, current_tick]
                    open_notes.append(data)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if not self.target_channels or msg.channel in self.target_channels:
                    for j, open_note in enumerate(open_notes):
                        if open_note[0] == msg.note:
                            n = Note(
                                key=open_note[0],
                                start_velocity=open_note[1],
                                end_velocity=msg.velocity,
                                note_duration=current_tick - open_note[2],
                                next_note_delay=open_note[2],
                                tempo=self.default_tempo,
                                instrument=0,
                                timestamp=open_note[2],
                            )
                            notes.append(n)
                            open_notes.pop(j)
                            break
            elif msg.type == "program_change":
                instrument_changes.append(current_tick)
                instrument_values.append(msg.program)
            elif msg.type == "set_tempo":
                tempo_changes.append(current_tick)
                tempo_values.append(msg.tempo)

        # Sort notes by timestamp
        notes.sort(key=lambda x: x.timestamp)

        # Assign tempo and instrument to each note
        current_tempo = self.default_tempo
        current_instrument = 0
        tempo_idx = 0
        instrument_idx = 0

        tempo_changes.append(float("inf"))  # Sentinel value
        instrument_changes.append(float("inf"))

        for n in notes:
            while (
                tempo_idx < len(tempo_changes)
                and n.timestamp >= tempo_changes[tempo_idx]
            ):
                current_tempo = tempo_values[tempo_idx]
                tempo_idx += 1
            n.tempo = current_tempo

            while (
                instrument_idx < len(instrument_changes)
                and n.timestamp >= instrument_changes[instrument_idx]
            ):
                current_instrument = instrument_values[instrument_idx]
                instrument_idx += 1
            n.instrument = current_instrument

        return notes

    def round_list(self, list_of_notes):
        return [
            note.rounded(
                self.velocity_rounding, self.duration_rounding, self.tempo_rounding
            )
            if note is not None
            else None
            for note in list_of_notes
        ]

    def add_to_map(self, notes):
        for i in range(len(notes)):
            # Add all subsequences up to the order as matches
            for j in range(i, max(i - self.order, -1), -1):
                # Use rounded notes for prediction
                n = tuple(self.round_list(notes[j : i + 1]))
                if i == len(notes) - 1:
                    s2 = None  # None indicates end of sequence
                else:
                    s2 = notes[i + 1]
                if n not in self.option_map:
                    self.option_map[n] = []
                    self.count_map[n] = []
                option_list = self.option_map[n]
                count_list = self.count_map[n]
                try:
                    pos = option_list.index(s2)
                    # Increase the counter
                    count_list[pos] += 1
                except ValueError:
                    # Add new entry
                    option_list.append(s2)
                    count_list.append(1)

    def generate(self):
        if not self.option_map:
            print("No mappings available to generate music.")
            return []
        current = []
        rand = random.choice(list(self.option_map.values()))
        current.append(random.choice(rand))
        while True:
            # Find the furthest back note to include in the subsequence for predicting
            lowest = max(0, len(current) - self.order)
            add = None
            # Try progressively smaller subsequences until a match is found
            for i in range(len(current) - lowest):
                use = tuple(self.round_list(current[lowest + i :]))
                if use in self.option_map:
                    add = self.pick(self.option_map[use], self.count_map[use])
                    break
            if add is None:
                break
            current.append(add)
        return current

    def pick(self, options, counts):
        total = sum(counts)
        rand = random.randint(1, total)
        for i, count in enumerate(counts):
            if rand <= count:
                return options[i]
            else:
                rand -= count
        return None

    def write_to_file(self):
        if not self.output:
            print("No output to write to file.")
            return

        # Create a new MIDI file
        mid = mido.MidiFile(ticks_per_beat=self.resolution)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        # Turn on General MIDI sound set (sysex event)
        sysex_msg = mido.Message("sysex", data=[0x7E, 0x7F, 0x09, 0x01])
        track.append(sysex_msg)

        # Set track name (meta event)
        track.append(mido.MetaMessage("track_name", name="midifile track"))

        # Set omni on (control change)
        track.append(mido.Message("control_change", control=0x7D, value=0x00))

        # Set poly on (control change)
        track.append(mido.Message("control_change", control=0x7F, value=0x00))

        # Set instrument to Piano (program change)
        track.append(mido.Message("program_change", program=0))

        events = []
        current_tick = 0
        current_tempo = None
        current_instrument = None

        for i in self.output:
            # Handle tempo changes
            if current_tempo != i.tempo:
                events.append(
                    (current_tick, mido.MetaMessage("set_tempo", tempo=i.tempo))
                )
                current_tempo = i.tempo

            # Handle instrument changes
            if current_instrument != i.instrument:
                events.append(
                    (
                        current_tick,
                        mido.Message("program_change", program=i.instrument),
                    )
                )
                current_instrument = i.instrument

            # Add note_on message at current_tick
            events.append(
                (
                    current_tick,
                    mido.Message("note_on", note=i.key, velocity=i.start_velocity),
                )
            )

            # Add note_off message at current_tick + i.note_duration
            events.append(
                (
                    current_tick + i.note_duration,
                    mido.Message("note_off", note=i.key, velocity=i.end_velocity),
                )
            )

            # Advance current_tick by i.next_note_delay
            current_tick += i.next_note_delay

        # Now sort events by time
        events.sort(key=lambda x: x[0])

        # Build track messages with correct delta times
        previous_time = 0
        for event_time, message in events:
            delta_time = event_time - previous_time
            message.time = int(delta_time)
            track.append(message)
            previous_time = event_time

        # Set end of track
        track.append(mido.MetaMessage("end_of_track", time=0))

        # Write the MIDI file
        mid.save(self.output_file)
        print(f"Generated music saved to {self.output_file}")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate music using Markov chains.")
    parser.add_argument(
        "files",
        metavar="MIDI_FILE",
        type=str,
        nargs="+",
        help="One or more MIDI files to use as input",
    )
    parser.add_argument(
        "-o",
        "--order",
        type=int,
        default=3,
        help="Order of the Markov chain (default: 3)",
    )
    parser.add_argument(
        "-of",
        "--output-file",
        type=str,
        default="output.mid",
        help="Output MIDI file name (default: output.mid)",
    )

    args = parser.parse_args()

    m = MarkovMusic(files=args.files, order=args.order, output_file=args.output_file)
    m.run()
