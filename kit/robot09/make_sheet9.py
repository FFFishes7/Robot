from PIL import Image, ImageDraw, ImageFont
import os, json
D = os.path.dirname(os.path.abspath(__file__)); F = D + '/frames/'; CL8 = D + '/../closeups08/'; V = D + '/../v07/'; CL = D + '/../closeups07/'
rows = [("Turnaround: 8 facings", ["turn_front", "turn_qr", "turn_r", "turn_br", "turn_back", "turn_bl", "turn_l", "turn_ql"]),
("Expressions (screen eyes)", ["expr_open", "expr_blink", "expr_wide", "expr_soft", "expr_happy", "expr_squint", "expr_dim", "expr_off", "expr_lookL", "expr_lookU"]),
("Cue > mechanical start: standby, boot flicker, SNAP to attention, robotic look + pivot, grab", ["standby", "boot_a", "boot_b", "snap_up", "attention", "att_left", "att_nod", "att_qr", "grab", "grab3"]),
("Sweep cycle (8 drawings) + finish (device shows a check)", ["sweep1", "sweep2", "sweep3", "sweep4", "sweep5", "sweep6", "sweep7", "sweep8", "done_look", "done_nod"]),
("Dusk: stop, notice, look up, then LONGING: turn to the window, head up, lean in, broom sags", ["stop", "notice", "antic", "look2", "look4", "long_r", "long0", "long2", "long3", "long5"]),
("Hesitation: startle, eye darts, antenna twitch, look window/alarm, step toward alarm and back, sigh, decide", ["tb_qr", "startle2", "hz_al_tw", "hz_fr_l", "hz_win_b", "hz_step1", "hz_step2_doubt", "hz_back1", "hz_sigh", "hz_dec_nod"]),
("Reach: anticipation, arc in-betweens, overshoot, hover, contact, press, follow-through", ["reach_antic1", "reach_antic", "reach_arc0", "reach_arc1", "reach_arc2", "reach_arc3", "reach_over", "contact", "press", "rel2"]),
("Lean action (v09): tip against the sill face, bristles on the floor, contact shadows; wobble, let go, pat; walk away", ["lean1", "lean2", "lean3", "lean_wob", "lean_let", "lean_pat", "lean_look", "walk10", "walk14", "walk24"]),
("Climb onto the new cushioned bench (v09: 16 drawings): hands, crouch, push, knee, pull, kneel, rise", ["cl_hands", "cl_crouch2", "cl_jump", "cl_knee", "cl_knee2", "cl_pull", "cl_pull2", "cl_kneel_a", "cl_kneel", "cl_rise"]),
("Stand, glance back at the broom, sit down, land, settle", ["cl_stand", "cl_glance2", "cl_sitdown", "cl_sit_a", "land", "land2"]),
("On the bench + night sleep mode (screen glow)", ["sit", "sit_idle1", "sit_lookup", "sit_lean", "sit_breath", "sleep"])]
DJ = json.load(open(F + 'drawings.json'))
S = 5; CW = 44; cell = CW * S; LAB = 24; HDR = 30; cols = 10
Fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); Fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
TH = 432; Wd = max(cols * (cell + 4) + 4, 3 * 772 + 4)
Hh = sum(HDR + LAB + cell + 10 for _ in rows) + HDR + 2 * (TH + LAB + 6)
sheet = Image.new('RGB', (Wd, Hh + 10), (30, 22, 28)); d = ImageDraw.Draw(sheet)
bg = Image.open(D + '/../v09/albedo09.png').convert('RGBA')
for e in ('emit_win07.png', 'emit_lamps07.png', 'cal_1307.png'): bg.alpha_composite(Image.open(V + e).convert('RGBA'))
y = 6
for title, names in rows:
    d.text((8, y + 4), title, font=Fb, fill=(245, 232, 210)); y += HDR
    for i, n in enumerate(names):
        wx = DJ[n]['cx'] + 56; wy = DJ[n]['by'] + 26
        if n.startswith(('reach', 'hover', 'contact', 'press', 'rel')): wx -= 6
        box = (wx - 22, wy - 40, wx + 22, wy + 4)
        im = bg.copy()
        al = 'alarm_off07.png' if n.startswith(('press', 'rel')) else ('alarm_task07.png' if n.startswith(('boot', 'snap', 'att')) else ('alarm_ring07.png' if n.startswith(('startle', 'hz', 'tb_', 'shuf', 'reach', 'hover', 'contact')) else 'alarm_idle07.png'))
        im.alpha_composite(Image.open(V + al).convert('RGBA'))
        if n.startswith('press') or n == 'contact': im.alpha_composite(Image.open(V + 'alarm_btn07.png').convert('RGBA'))
        im = im.crop(box)
        sh = Image.open(F + n + '_s.png').crop(box); a = sh.getchannel('A').point(lambda v: int(v * 0.42)); s2 = Image.new('RGBA', sh.size, (20, 8, 16, 0)); s2.putalpha(a); im.alpha_composite(s2)
        im.alpha_composite(Image.open(F + n + '_a.png').crop(box)); im.alpha_composite(Image.open(F + n + '_e.png').crop(box))
        x = 4 + i * (cell + 4)
        d.text((x + 4, y + 2), n, font=Fs, fill=(210, 196, 180))
        sheet.paste(im.resize((cell, cell), Image.NEAREST), (x, y + LAB))
    y += LAB + cell + 10
d.text((8, y + 4), "Close-up inserts (drawn natively at 384x216): the cue, the time pass, his face, his own arm pressing the button", font=Fb, fill=(245, 232, 210)); y += HDR
thumbs = [("device: task cue flashes, he boots", CL8 + "task/f026.png"), ("device: he snaps to attention", CL8 + "task/f060.png"), ("calendar: night, page 12 lifts and tears away", CL8 + "cal/f028.png"),
          ("face: soft, lit by the sunset", CL + "face/f044.png"), ("press: his salmon arm + mitten winds up", CL8 + "press/f018.png"), ("press: button in, green check", CL8 + "press/f040.png")]
for k, (lab, p) in enumerate(thumbs):
    x = 4 + (k % 3) * 772; yy = y + (k // 3) * (TH + LAB + 6)
    d.text((x + 4, yy + 2), lab, font=Fs, fill=(210, 196, 180)); sheet.paste(Image.open(p).convert('RGB').resize((768, 432), Image.NEAREST), (x, yy + LAB))
out = D + '/../../robot_sheet_09.png'; sheet.save(out); print(sheet.size)
