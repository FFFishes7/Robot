"""v13 panorama: v12 without the corner trees (Alan: delete rather than keep mediocre trees). The frame is carried
by the full-width hill band and the side cloud banks."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import KIT
sys.path.insert(0, KIT + 'v12')
import panorama12 as P12
from panorama12 import N, W, H
class Pano(P12.Pano):
    def foliage(self, img, P, t, off, f): return
