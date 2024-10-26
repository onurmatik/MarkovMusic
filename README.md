# Markov Music Generator

A Python program that generates music using Markov chains based on input MIDI files.

## Overview

The Markov Music Generator analyzes one or more MIDI files and uses a Markov chain to generate new music sequences. By modeling the probabilities of note transitions, the program creates music that reflects the patterns found in the input files.

## Features

- Markov Chain Implementation: Supports variable-order Markov chains, allowing for control over the complexity and resemblance to the input music.
- MIDI File Handling: Reads and writes standard MIDI files using the mido library.
- Command-Line Interface: Accepts MIDI files and Markov chain order as command-line arguments.
- Customizable Parameters: Allows adjustment of rounding properties to influence the diversity of generated music.

## Installation

### Prerequisites

	•	Python 3.6 or higher

### Required Libraries

	•	mido: For MIDI file handling.
	•	python-rtmidi: Optional, required if you plan to use real-time MIDI functionalities.

### Install Dependencies

pip install mido
pip install python-rtmidi  # Optional, for real-time MIDI support

## Usage

Command-Line Arguments

- MIDI_FILE: One or more MIDI files to use as input for generating music.
- -o, –order: (Optional) The order of the Markov chain (default is 3).
- -of, –output-file: (Optional) The output MIDI file name (default is output.mid).

## Running the Program

python markov_music.py [OPTIONS] MIDI_FILE [MIDI_FILE ...]

### Examples

- Using a single MIDI file with default order:


    python markov_music.py twinkle.mid


- Using multiple MIDI files:


    python markov_music.py song1.mid song2.mid song3.mid


- Specifying the Markov chain order:


    python markov_music.py --order 4 twinkle.mid



## Output

The generated MIDI file will be saved as output.mid in the current working directory.

## How It Works

1.	Reading MIDI Files: The program reads the input MIDI files and parses the note events, collecting information about pitches, velocities, durations, and timing.


2. Building the Markov Chain:

- Creates mappings of note sequences based on the specified order.
- Calculates the probabilities of transitioning from one note sequence to the next.

3. Generating New Music:

- Starts with a random note sequence from the mappings.
- Uses the Markov chain to probabilistically select subsequent notes.
- Continues until no further transitions are possible or a termination condition is met.

4. Writing the Output File:

- Compiles the generated note events into a MIDI file.
- Ensures correct timing and event ordering.

## Customization

### Adjusting Markov Chain Order

- Higher Order: The generated music will more closely resemble the input files, as it considers longer sequences of notes.
- Lower Order: Introduces more randomness, potentially creating more novel compositions.

### Modifying Rounding Parameters

The following attributes can be adjusted in the MarkovMusic class to influence the generated music:

- velocity_rounding: Controls the rounding of note velocities.
- duration_rounding: Controls the rounding of note durations.
- tempo_rounding: Controls the rounding of tempo changes.

These parameters affect how similar notes are grouped during the Markov chain construction.

## Dependencies

Ensure you have `mido` library installed:

    pip install mido



## Notes

- Input Files: The MIDI files provided should be valid and accessible. Use full paths if the files are not in the current directory.
- Error Handling: The program includes basic error handling to inform you of issues with file reading or writing.
- Ouput File: The output MIDI file output.mid will be overwritten each time the program runs. Rename or move the file after generation if you wish to keep it.

## Troubleshooting

- No Mappings Available: If the program outputs “No mappings available to generate music,” ensure that the input MIDI files contain note data and are correctly parsed.
- Empty Output: If no output is generated, check that the Markov chain order is appropriate for the length of the input sequences.
- Exceptions: If you encounter exceptions or errors, verify that all dependencies are installed and that your MIDI files are not corrupted.


## License

This project is released under the MIT License.


## Acknowledgments

- Original Java Implementation: This program is a Python adaptation of an [original Java implementation](https://github.com/aaronvanzyl/markov-music) for music generation using Markov chains by [@aaronvanzyl](https://github.com/aaronvanzyl/).
- mido Library: https://mido.readthedocs.io/en/latest/
