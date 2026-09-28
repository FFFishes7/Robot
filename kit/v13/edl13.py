"""v10 cut: the wide plays continuously (insets are overlays, no cut-aways) -> interior sunset shot -> wide -> ending
panorama -> credits. Output frame o == wide frame F for F < PANO_F."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import KIT
HOLD = 60                                 # v13: hold the still window close-up 2.5 s longer after the peek
R9 = KIT + "robot09/frames/"
M = json.load(open(R9 + "marks10.json")); mk = M["marks"]; N = M["N"]; PAN = M["panels"]
SUN0 = PAN["sunset"][0]; SUN1 = SUN0 + 74 + HOLD; PANO_F = SUN1 + 40; PANO_N = 168; CRED_N = 168
def ow(F): return F                      # wide frame -> output frame (valid for F < PANO_F)
def total(): return PANO_F + PANO_N + CRED_N
def segments():
    return [("wide", 0, SUN0), ("sunset", SUN0, SUN1), ("wide", SUN1, PANO_F), ("pano", PANO_F, PANO_N), ("cred", 0, CRED_N)]
