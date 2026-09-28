"""Native page-turn frames for the calendar (world canvas 448x288): the 12 page lifts from the bottom, swings up past
horizontal and over the top of the header. Used in BOTH the wide (composited in assembly) and the calendar inset."""
import numpy as np
from PIL import Image
K = "/workspace/robot2d/kit/"
bg = np.array(Image.open(K + "v09/albedo09.png").convert("RGBA"))
c12 = Image.fromarray(bg.copy()); c12.alpha_composite(Image.open(K + "v07/cal_1207.png").convert("RGBA")); c12 = np.array(c12)
X0, X1 = 246, 256                       # page columns (inside the 245..256 outline)
P1, P2, P3, OL = (0xf4, 0xe6, 0xc8, 255), (0xd8, 0xc4, 0xa0, 255), (0xa8, 0x8a, 0x68, 255), (0x4e, 0x24, 0x18, 255)
def blank(): return np.zeros_like(bg)
f = {}
a = blank(); a[82:86, X0:X1] = c12[82:86, X0:X1]; a[86, X0:X1] = P1; a[87, X0:X1] = P2; a[88, X0:X1] = P3; a[89, X0:X1] = OL; a[86:89, X0 - 1] = OL; a[86:89, X1] = OL; f[1] = a
a = blank(); a[79, X0:X1] = OL; a[80, X0:X1] = P1; a[81, X0:X1] = P2; a[80:82, X0 - 1] = OL; a[80:82, X1] = OL; f[2] = a
a = blank(); a[70, X0:X1] = OL; a[71:78, X0 - 1] = OL; a[71:78, X1] = OL; a[71:78, X0:X1] = P2; a[71:78, X1 - 1] = P3; a[77, X0:X1] = P3; a[71, X0:X1 - 1] = P1; f[3] = a
a = blank(); a[74, X0 + 2:X1 - 2] = OL; a[75:77, X0 + 2:X1 - 2] = P2; a[76, X0 + 2:X1 - 2] = P3; a[75:77, X0 + 1] = OL; a[75:77, X1 - 2] = OL; f[4] = a
for k, a in f.items(): Image.fromarray(a).save(K + f"v10/calfx/calfx{k}.png")
