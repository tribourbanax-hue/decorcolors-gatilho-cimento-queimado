# Resolve o ffmpeg embutido (vem com o pacote imageio-ffmpeg do Python).
# Nao precisa instalar ffmpeg no sistema.
import os
import subprocess

def ffmpeg_exe():
    env = os.environ.get("FFMPEG_BINARY")
    if env and os.path.isfile(env):
        return env
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    for c in (r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Windows\System32\ffmpeg.exe"):
        if os.path.isfile(c):
            return c
    raise RuntimeError("ffmpeg nao encontrado. `pip install imageio-ffmpeg`.")

FFMPEG = ffmpeg_exe()

def run(args, **kw):
    """Roda ffmpeg com a lista de argumentos (sem o 'ffmpeg' na frente)."""
    cmd = [FFMPEG, "-hide_banner", "-y"] + list(args)
    kw.setdefault("check", True)
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    p = subprocess.run(cmd, **kw)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg falhou:\n" + (p.stderr or "")[-4000:])
    return p

def probe_duration(path):
    """Duracao em segundos lendo o stderr do ffmpeg (nao precisa de ffprobe)."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", path],
                       capture_output=True, text=True)
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr or "")
    if not m:
        return None
    h, mm, ss = m.groups()
    return int(h) * 3600 + int(mm) * 60 + float(ss)

if __name__ == "__main__":
    print("ffmpeg:", FFMPEG)
    print(run(["-version"], check=False).stdout.splitlines()[0])
