# Spatializer

## Introduction

This is an experiment to change apparent source location based on pitch (lower pitches to the left, higher to the right) using tiny delays to manipulate [Sound Localization](https://en.wikipedia.org/wiki/Sound_localization). The name comes from 'equalizer' which changes volume based on pitch. 

![Sample output](http://sam.casavant.org/assets/spatializer/sa.mp3?raw=true "Spatialized output from the Spirited Away soundtrack")

## Installation

```
pip install scipy pydub
git clone https://github.com/SamCasavant/Spatializer.git
cd Spatializer
python spatializer.py file.mp3
```