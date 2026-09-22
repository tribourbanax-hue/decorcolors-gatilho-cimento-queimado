import os
from ffbin import run, probe_duration

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(AQUI, "..", "source", "broll.mp4")
A = os.path.join(AQUI, "assets")
SFX = os.path.join(AQUI, "sfx")
BUILD = os.path.join(AQUI, "_build")
OUT = os.path.join(AQUI, "out")
os.makedirs(BUILD, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
FPS = 30

HOOK_DUR = 2.2
CLIP_DUR = 3.0
CTA_DUR = 4.5

# (start, end) trimmed from the 101s source broll
CLIPS = [
    (9.0, 9.0 + CLIP_DUR),
    (16.0, 16.0 + CLIP_DUR),
    (44.0, 44.0 + CLIP_DUR),
    (77.0, 77.0 + CLIP_DUR),
]
CAPTIONS = ["cap1.png", "cap2.png", "cap3.png", "cap4.png"]

TOTAL = HOOK_DUR + CLIP_DUR * len(CLIPS) + CTA_DUR
print("total duration ~%.2fs" % TOTAL)


def build_video():
    inputs = [
        "-loop", "1", "-t", str(HOOK_DUR), "-i", os.path.join(A, "hook_composite.png"),  # 0
        "-i", SRC,  # 1
        "-loop", "1", "-t", str(CLIP_DUR), "-i", os.path.join(A, CAPTIONS[0]),  # 2
        "-loop", "1", "-t", str(CLIP_DUR), "-i", os.path.join(A, CAPTIONS[1]),  # 3
        "-loop", "1", "-t", str(CLIP_DUR), "-i", os.path.join(A, CAPTIONS[2]),  # 4
        "-loop", "1", "-t", str(CLIP_DUR), "-i", os.path.join(A, CAPTIONS[3]),  # 5
        "-loop", "1", "-t", str(CTA_DUR), "-i", os.path.join(A, "cta_card.png"),  # 6
        "-loop", "1", "-t", str(TOTAL), "-i", os.path.join(A, "tag_cupom.png"),  # 7
    ]

    filt = []
    filt.append(f"[0:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p[hook]")

    b_labels = []
    for i, (s, e) in enumerate(CLIPS):
        dur = e - s
        base = f"b{i}base"
        cap_in = 2 + i
        out = f"b{i}"
        filt.append(
            f"[1:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,scale={W}:{H},setsar=1,fps={FPS},format=yuv420p[{base}]"
        )
        filt.append(f"[{cap_in}:v]format=rgba[{out}cap]")
        filt.append(f"[{base}][{out}cap]overlay=0:0:shortest=1,trim=duration={dur},format=yuv420p[{out}]")
        b_labels.append(out)

    filt.append(f"[6:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p[cta]")

    concat_in = "[hook]" + "".join(f"[{b}]" for b in b_labels) + "[cta]"
    n = 2 + len(b_labels)
    filt.append(f"{concat_in}concat=n={n}:v=1:a=0[concatv]")

    tag_in = 7
    filt.append(f"[{tag_in}:v]format=rgba[tagv]")
    filt.append("[concatv][tagv]overlay=0:0:shortest=1,format=yuv420p[outv]")

    filter_complex = ";".join(filt)

    out_path = os.path.join(BUILD, "base_video.mp4")
    args = inputs + [
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-r", str(FPS),
        out_path,
    ]
    run(args)
    print("wrote", out_path)
    return out_path


def build_audio():
    # cue times inside the final timeline (seconds)
    t_click = 0.05
    t_whoosh1 = HOOK_DUR - 0.1
    cut_times = [HOOK_DUR + CLIP_DUR * (i + 1) for i in range(len(CLIPS) - 1)]  # cuts between broll clips
    t_whoosh2 = HOOK_DUR + CLIP_DUR * len(CLIPS) - 0.1  # leading into CTA
    t_beep = HOOK_DUR + CLIP_DUR * len(CLIPS) + 0.15

    cues = [
        (os.path.join(SFX, "click.wav"), t_click),
        (os.path.join(SFX, "whoosh.wav"), t_whoosh1),
    ]
    for t in cut_times:
        cues.append((os.path.join(SFX, "hit.wav"), t - 0.05))
    cues.append((os.path.join(SFX, "whoosh.wav"), t_whoosh2))
    cues.append((os.path.join(SFX, "beep.wav"), t_beep))

    inputs = []
    for path, _ in cues:
        inputs += ["-i", path]

    filt = []
    labels = []
    for i, (_, t) in enumerate(cues):
        ms = int(t * 1000)
        filt.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
        labels.append(f"[a{i}]")
    filt.append("".join(labels) + f"amix=inputs={len(cues)}:duration=longest:dropout_transition=0[amixed]")
    filt.append(f"[amixed]apad=whole_dur={TOTAL}[aout]")

    out_path = os.path.join(BUILD, "audio.m4a")
    args = inputs + [
        "-filter_complex", ";".join(filt),
        "-map", "[aout]",
        "-t", str(TOTAL),
        "-c:a", "aac", "-b:a", "128k",
        out_path,
    ]
    run(args)
    print("wrote", out_path)
    return out_path


def mux(video_path, audio_path):
    vdur = probe_duration(video_path)
    final = os.path.join(OUT, "gatilho-cimento-queimado.mp4")
    run([
        "-i", video_path, "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(vdur),
        final,
    ])
    preview = os.path.join(OUT, "gatilho-cimento-queimado-preview.mp4")
    run([
        "-i", final,
        "-c:v", "libx264", "-crf", "30", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "96k",
        preview,
    ])
    print("wrote", final)
    print("wrote", preview)


if __name__ == "__main__":
    v = build_video()
    a = build_audio()
    mux(v, a)
