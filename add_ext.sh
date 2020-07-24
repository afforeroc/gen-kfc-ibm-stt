#!/bin/bash
# Adding '.mp3' ext to audio files."""

echo "Adding '.mp3' ext to audio files...";
for audio_file in ./*-all;
do
    mv -- "$audio_file" "${audio_file%}.mp3";
    echo "${audio_file%}.mp3"
done;
