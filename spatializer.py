import sys
import math
import time
from pydub import AudioSegment
import pydub.scipy_effects

def getDelay(ear_separation, angle, freq): #distances in centimeters
	angle = math.radians(angle)
	source_distance = 50
	return((9/34)*(angle+math.sin(angle)))
	#-------------------------------------------------------
	#if freq <= 4000:
	#	return (300*(ear_separation/2)*math.sin(angle))/34.3
	#else:
	#	return (200*(ear_separation/2)*math.sin(angle))/34.3
	#--------------------------------------------------------
    #angle = math.radians(angle)
	#a = source_distance ** 2.0
	#b = ear_separation ** 2 / 4
	#c = source_distance * ear_separation * math.cos(angle)
	#d = source_distance * ear_separation * math.cos(math.pi-angle)
	#distance = math.sqrt(a+b-d)-math.sqrt(a+b-c)
	#delay = distance / 34.3 #time in ms
	return delay

def getGain(angle, freq):
	angle = math.radians(angle)
	l_perc = ((1+math.cos(angle+math.pi/2))*freq + 2*34/9)/(freq + 2*34/9) - 1
	r_perc = ((1+math.cos(angle-math.pi/2))*freq + 2*34/9)/(freq + 2*34/9) - 1
	return (l_perc, r_perc)

if len(sys.argv) < 2:
    print("Usage: %s <filename> [order=5] [resolution=3] [lower=9] [upper=97]" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]

song = AudioSegment.from_file(filename, format=filename[-3:])
mono = song.set_channels(1)

freqs = [
 16.3516, 17.3239, 18.3540, 19.4454, 20.6017, 21.8268, 23.1247, 24.4997, 25.9565, 27.5000, 29.1352, 30.8677,
 32.7032, 34.6478, 36.7081, 38.8909, 41.2034, 43.6535, 46.2493, 48.9994, 51.9131, 55.0000, 58.2705, 61.7354,
 65.4064, 69.2957, 73.4162, 77.7817, 82.4069, 87.3071, 92.4986, 97.9989, 103.826, 110.000, 116.541, 123.471,
 130.813, 138.591, 146.832, 155.563, 164.814, 174.614, 184.997, 195.998, 207.652, 220.000, 233.082, 246.942,
 261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.995, 391.995, 415.305, 440.000, 466.164, 493.883,
 523.251, 554.365, 587.330, 622.254, 659.255, 698.456, 739.989, 783.991, 830.609, 880.000, 932.328, 987.767,
 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1975.53,
 2093.00, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3279.31, 3951.07,
 4186.01, 4434.92, 4698.64, 4978.03, 5274.04, 5587.65]

def genDelayGain(mono, angle, order, low_freq=0, high_freq=math.inf):
	if low_freq == 0:
		if high_freq == math.inf:
			filtered = mono
		else:
			filtered = mono.low_pass_filter(high_freq, order=order)
	elif high_freq == math.inf:
		filtered = mono.high_pass_filter(low_freq, order=order)
	else:
		filtered = mono.band_pass_filter(low_freq, high_freq, order=order)
	left = right = filtered
	delay = getDelay(21.5, angle,1)
	l_gain, r_gain = getGain(angle, 1)
	spacer = AudioSegment.silent(math.fabs(delay))
	if delay<0:
		left = spacer + (left + l_gain)
		right = (right + r_gain) + spacer
	elif delay>0:
		right = spacer + (right + r_gain)
		left = (left+l_gain) + spacer
	return(left, right)

def spatialize(mono, span=(50, 70), resolution = 3, order = 8):
	outsong = AudioSegment.silent(len(mono)+500)
	l = (span[1]-span[0])
	scalar = 180/(l-1)
	start = int(span[0]/resolution)
	end = int(span[1]/resolution)
	cur_freq = 0
	for n in range(start, end):
		n_res = resolution*n
		pivot = (freqs[n_res]+freqs[n_res+1])/2
		print("Splitting at", pivot)
		angle = -1* ((n-start)*scalar*resolution - 90)
		left, right = genDelayGain(mono, angle, order, cur_freq, pivot)
		cur_freq = pivot
		outsong = outsong.overlay(AudioSegment.from_mono_audiosegments(left, right))
	left, right = genDelayGain(mono, angle, order, cur_freq)
	outsong = outsong.overlay(AudioSegment.from_mono_audiosegments(left, right))
	return outsong

def octavate(mono, resolution = 1, order = 8000):
	outsong = AudioSegment.silent(len(mono)+500)
	used_freqs = []
	for n in range(0, 12):
			for index, freq in enumerate(freqs[1:-1][n::12]):
				print(round(100*(n+index/9)/12, 3), "%")
				angle = (n * 180/12) - 90
				low_freq = (freqs[index*12+n-1]+freqs[index*12+n])/2
				high_freq = (freqs[index*12]+freqs[index*12+n+1])/2
				used_freqs.append((low_freq, high_freq))
				left, right = genDelayGain(mono, angle, order, low_freq, high_freq)
				outsong=outsong.overlay(AudioSegment.from_mono_audiosegments(left, right))
	#left, right = genDelayGain(mono, -90, order, 0, (freqs[0]+freqs[1])/2)
	outsong = outsong.overlay(mono.low_pass_filter((freqs[0]+freqs[1])/2))
	#left, right = genDelayGain(mono, 90, order, ()
	outsong = outsong.overlay(mono.high_pass_filter((freqs[-2]+freqs[-3])/2))
	#outsong = outsong.overlay(AudioSegment.from_mono_audiosegments(left, right))
	print("100.0 %")
	print(sorted(used_freqs))
	return outsong

#outsong = outsong.overlay(mono.high_pass_filter(pivot, order=order))


outsong = octavate(mono[:5000])

outsong.export("out_%s" % filename, format=filename[-3:])
print("\a")