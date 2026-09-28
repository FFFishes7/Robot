from PIL import Image, ImageDraw, ImageFont
import os, json
D = os.path.dirname(os.path.abspath(__file__)); F = D + '/frames/'; V = D + '/../v07/'; CL = D + '/../closeups07/'
rows = [("Turnaround: 8 facings (turns pass through every in-between, no snaps)", ["turn_front", "turn_qr", "turn_r", "turn_br", "turn_back", "turn_bl", "turn_l", "turn_ql"]),
("Expressions (screen eyes)", ["expr_open", "expr_blink", "expr_wide", "expr_soft", "expr_happy", "expr_squint", "expr_dim", "expr_off", "expr_lookL", "expr_lookU"]),
("Start of day: standby, device lights, wake, turn, take the broom", ["standby", "wake1", "wake2", "wake3", "wake_look", "wake_nod", "toBroom_qr", "grab", "grab2"]),
("Sweep cycle (8 drawings, 3 frames each)", [f"sweep{i}" for i in range(1, 9)]),
("Dusk: stop, notice, anticipation, look up (broom drifts)", ["stop", "notice", "antic", "look1", "look2", "look3", "look4", "look4_blink"]),
("Alarm: startle, hesitate (alarm, window, alarm)", ["startle1", "startle2", "hes_alarm", "hes_front", "hes_window", "hes_window_b", "hes_alarm2", "hes_alarm2_nod"]),
("Press beat: shuffle over, wind-up, reach, hover, contact, press, release", ["shuf2", "shuf4", "reach_antic", "reach", "hover", "contact", "press", "press_hold", "release", "release2"]),
("Walk (profile, 8 phases at 1 drawing/frame) + corner in-between", ["walk08", "walk09", "walk10", "walk11", "walk12", "walk13", "walk14", "walk15", "corner_bl", "walk69"]),
("Epilogue: lean the broom, turn qr > front > ql > l, arrive, hop up", ["place1", "place2", "stand_qr", "stand_front", "stand_ql", "stand_l", "arrive_look", "hop_antic", "hop", "land"]),
("On the window seat (drawn over the glass, backlit rim)", ["sit", "sit_lookup", "sit_lean", "sit_breath"])]
DJ = json.load(open(F + 'drawings.json'))
S = 5; CW = 44; cell = CW * S; LAB = 24; HDR = 30; cols = 10
Fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); Fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
TH = 432; Wd = max(cols * (cell + 4) + 4, 3 * 772 + 4)
Hh = sum(HDR + LAB + cell + 10 for _ in rows) + HDR + 2 * (TH + LAB + 6)
sheet = Image.new('RGB', (Wd, Hh + 10), (30, 22, 28)); d = ImageDraw.Draw(sheet)
bg = Image.open(V + 'albedo07.png').convert('RGBA')
for e in ('emit_win07.png', 'emit_lamps07.png', 'cal_1307.png'): bg.alpha_composite(Image.open(V + e).convert('RGBA'))
y = 6
for title, names in rows:
    d.text((8, y + 4), title, font=Fb, fill=(245, 232, 210)); y += HDR
    for i, n in enumerate(names):
        wx = DJ[n]['cx'] + 56; wy = DJ[n]['by'] + 26
        if n.startswith('sit') or n == 'land': wx, wy = 164, 97
        if n in ('reach_antic', 'reach', 'hover', 'contact', 'press', 'press_hold', 'release', 'release2', 'shuf2', 'shuf4'): wx -= 6
        box = (wx - 22, wy - 40, wx + 22, wy + 4)
        im = bg.copy()
        al = 'alarm_off07.png' if n.startswith('press') or n.startswith('release') else ('alarm_task07.png' if n in ('wake_look', 'wake_nod') else ('alarm_ring07.png' if n.startswith(('startle', 'hes', 'shuf', 'reach', 'hover', 'contact')) else 'alarm_idle07.png'))
        im.alpha_composite(Image.open(V + al).convert('RGBA'))
        if n.startswith('press') or n == 'contact': im.alpha_composite(Image.open(V + 'alarm_btn07.png').convert('RGBA'))
        im = im.crop(box)
        sh = Image.open(F + n + '_s.png').crop(box); a = sh.getchannel('A').point(lambda v: int(v * 0.42)); s2 = Image.new('RGBA', sh.size, (20, 8, 16, 0)); s2.putalpha(a); im.alpha_composite(s2)
        im.alpha_composite(Image.open(F + n + '_a.png').crop(box)); im.alpha_composite(Image.open(F + n + '_e.png').crop(box))
        x = 4 + i * (cell + 4)
        d.text((x + 4, y + 2), n, font=Fs, fill=(210, 196, 180))
        sheet.paste(im.resize((cell, cell), Image.NEAREST), (x, y + LAB))
    y += LAB + cell + 10
d.text((8, y + 4), "Close-up inserts: drawn natively at 384x216 (same pixel size as the wide shot, not upscaled crops)", font=Fb, fill=(245, 232, 210)); y += HDR
thumbs = [("face f02: first glance up", CL + "face/f002.png"), ("face f14: awe (wide eyes)", CL + "face/f014.png"), ("face f44: soft, lit by the sunset", CL + "face/f044.png"),
          ("device f04: ringing, mitten hovers", CL + "device/f004.png"), ("device f23: contact + press", CL + "device/f023.png"), ("device f60: button in, alarm off", CL + "device/f060.png")]
for k, (lab, p) in enumerate(thumbs):
    x = 4 + (k % 3) * 772; yy = y + (k // 3) * (TH + LAB + 6)
    d.text((x + 4, yy + 2), lab, font=Fs, fill=(210, 196, 180)); sheet.paste(Image.open(p).convert('RGB').resize((768, 432), Image.NEAREST), (x, yy + LAB))
out = D + '/../../robot_sheet_07.png'; sheet.save(out); print(sheet.size)
