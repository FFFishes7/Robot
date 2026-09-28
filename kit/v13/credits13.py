"""v13 credits: v10 credits with a cleaned head icon (the crop of the 'attention' drawing caught the broom
handle at its lower-right; those pixels are removed and the lower-right outline mirrored from the left side)."""
import sys, numpy as np
sys.path.insert(0, '/workspace/robot2d/kit/v10')
import credits10 as C
from PIL import Image
_orig = C.head_icon
def head_icon():
    a = np.array(_orig())                         # 23 x 19 (x 281..303, y 74..92 of the world)
    H, W = a.shape[:2]
    E = a[16, 1].copy(); I = a[17, 3].copy()      # outline + shade colours from the clean left side
    a[16, 19] = I; a[16, 20] = I; a[16, 21] = E; a[16, 22] = 0
    a[17, 19] = I; a[17, 20] = E; a[17, 21] = 0; a[17, 22] = 0
    a[18, 19] = E; a[18, 20] = 0; a[18, 21] = 0; a[18, 22] = 0
    return Image.fromarray(a)
C.head_icon = head_icon; C._cache.clear()
frame = C.frame
