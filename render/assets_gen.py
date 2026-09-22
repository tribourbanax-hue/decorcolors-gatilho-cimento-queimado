# Gera os PNGs (caixinha estilo sticker de pergunta, legendas, cartela final)
# usados no vídeo gatilho. Roda uma vez: python render/assets_gen.py
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "assets")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920

FONT_DIR = "C:/Windows/Fonts/"
def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

F_BOLD = "segoeuib.ttf"
F_BLACK = "arialbd.ttf"
F_REG = "segoeui.ttf"

GOLD = (194, 163, 107, 255)
GOLD_BRIGHT = (212, 184, 127, 255)
INK = (17, 17, 19, 255)
GRAPHITE = (23, 23, 26, 255)
OFFWHITE = (242, 238, 229, 255)
SILVER = (201, 199, 193, 255)


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def soft_shadow(size, box, radius, blur=28, opacity=110):
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(box, radius=radius, fill=(0, 0, 0, opacity))
    return shadow.filter(ImageFilter.GaussianBlur(blur))


def wrap_text(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card_caixinha(question, fname):
    """Sticker estilo caixinha de pergunta do Stories, flutuando no topo do quadro."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    card_w = W - 140
    pad_x, pad_y = 44, 34
    f_q = font(F_BOLD, 40)

    draw_tmp = ImageDraw.Draw(im)
    lines = wrap_text(draw_tmp, question, f_q, card_w - pad_x * 2)
    line_h = 50
    card_h = pad_y * 2 + line_h * len(lines) + 46  # +46 for the top label row

    card_x0 = (W - card_w) // 2
    card_y0 = 300
    card_x1 = card_x0 + card_w
    card_y1 = card_y0 + card_h

    shadow = soft_shadow((W, H), (card_x0, card_y0 + 10, card_x1, card_y1 + 10), radius=34, blur=30, opacity=120)
    im = Image.alpha_composite(im, shadow)
    draw = ImageDraw.Draw(im)

    rounded_rect(draw, (card_x0, card_y0, card_x1, card_y1), radius=34, fill=(255, 255, 255, 255))

    # top label row: small "?" bubble + "pergunta" tag, mimicking the sticker header
    tag_f = font(F_BOLD, 24)
    tag_y = card_y0 + pad_y - 6
    circ_d = 34
    draw.ellipse((card_x0 + pad_x, tag_y, card_x0 + pad_x + circ_d, tag_y + circ_d), fill=(30, 30, 34, 255))
    draw.text((card_x0 + pad_x + circ_d / 2, tag_y + circ_d / 2), "?", font=font(F_BLACK, 22),
               fill=(255, 255, 255, 255), anchor="mm")
    draw.text((card_x0 + pad_x + circ_d + 14, tag_y + circ_d / 2), "PERGUNTARAM PRA GENTE",
               font=tag_f, fill=(150, 150, 150, 255), anchor="lm")

    ty = tag_y + circ_d + 18
    f_q2 = font(F_BOLD, 40)
    for ln in lines:
        draw.text((card_x0 + pad_x, ty), ln, font=f_q2, fill=(20, 20, 22, 255))
        ty += line_h

    im.save(os.path.join(OUT, fname))
    print("saved", fname, "card box", (card_x0, card_y0, card_x1, card_y1))


def pill_caption(text, fname):
    """Legenda tipo tarja inferior, respeitando a zona segura (base >=350px)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(F_BOLD, 40)
    draw = ImageDraw.Draw(im)
    tw = draw.textlength(text, font=f)
    pad_x, pad_y = 38, 22
    box_w = tw + pad_x * 2
    box_h = 40 + pad_y * 2
    x0 = (W - box_w) / 2
    y1 = H - 420
    y0 = y1 - box_h

    shadow = soft_shadow((W, H), (x0, y0 + 8, x0 + box_w, y1 + 8), radius=box_h / 2, blur=22, opacity=130)
    im = Image.alpha_composite(im, shadow)
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (x0, y0, x0 + box_w, y1), radius=box_h / 2, fill=(17, 17, 19, 235))
    draw.rounded_rectangle((x0, y0, x0 + box_w, y1), radius=box_h / 2, outline=GOLD, width=2)
    draw.text((W / 2, (y0 + y1) / 2), text, font=f, fill=OFFWHITE, anchor="mm")

    im.save(os.path.join(OUT, fname))
    print("saved", fname)


def diamond(draw, cx, cy, r, color, width=3):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(pts, outline=color, width=width)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=color, width=max(1, width - 1))
    draw.line([(cx, cy - r), (cx - r * 0.5, cy)], fill=color, width=max(1, width - 1))
    draw.line([(cx, cy - r), (cx + r * 0.5, cy)], fill=color, width=max(1, width - 1))
    draw.line([(cx - r * 0.5, cy), (cx, cy + r)], fill=color, width=max(1, width - 1))
    draw.line([(cx + r * 0.5, cy), (cx, cy + r)], fill=color, width=max(1, width - 1))


def card_cta():
    im = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(im)

    # faint diamond watermark, low opacity, tucked behind the headline only
    wm_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wmd = ImageDraw.Draw(wm_layer)
    diamond(wmd, W // 2, 560, 280, (255, 255, 255, 16), width=2)
    im = Image.alpha_composite(im.convert("RGBA"), wm_layer).convert("RGB")
    draw = ImageDraw.Draw(im)

    diamond(draw, 120, 150, 26, GOLD_BRIGHT, width=4)

    f_eyebrow = font(F_BOLD, 26)
    draw.line((W / 2 - 150, 300, W / 2 - 120, 300), fill=GOLD, width=2)
    draw.text((W / 2 - 100, 300), "I N F O G R Á F I C O   G R Á T I S", font=f_eyebrow, fill=GOLD_BRIGHT, anchor="lm")

    f_h1 = font(F_BLACK, 62)
    h1_lines = [
        "Quer receber o guia",
        "de aplicação do",
    ]
    y = 430
    for ln in h1_lines:
        draw.text((W / 2, y), ln, font=f_h1, fill=OFFWHITE, anchor="mm")
        y += 78
    draw.text((W / 2, y + 10), "Cimento Queimado?", font=font(F_BLACK, 62), fill=GOLD_BRIGHT, anchor="mm")

    # CTA box
    box_y0, box_y1 = 900, 1130
    rounded_rect(draw, (100, box_y0, W - 100, box_y1), radius=28, fill=(38, 38, 43, 255))
    draw.rounded_rectangle((100, box_y0, W - 100, box_y1), radius=28, outline=GOLD, width=2)
    draw.text((W / 2, box_y0 + 68), "Comenta", font=font(F_BOLD, 44), fill=OFFWHITE, anchor="mm")
    draw.text((W / 2, box_y0 + 135), chr(8220) + "PASSO A PASSO" + chr(8221), font=font(F_BLACK, 54), fill=GOLD_BRIGHT, anchor="mm")
    draw.text((W / 2, box_y0 + 195), "que a gente manda grátis no seu direct", font=font(F_REG, 32), fill=SILVER, anchor="mm")

    draw.text((W / 2, 1500), "@decorcolors.sjcsaodimas", font=font(F_BOLD, 34), fill=OFFWHITE, anchor="mm")
    draw.text((W / 2, 1550), "São José dos Campos · SP", font=font(F_REG, 26), fill=(120, 120, 120), anchor="mm")

    im.save(os.path.join(OUT, "cta_card.png"))
    print("saved cta_card.png")


def tag_cupom(fname="tag_cupom.png"):
    """Tag dourada fixa (cupom de desconto), pra ficar visivel o video inteiro."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    f = font(F_BOLD, 30)
    text = "USE O CUPOM  PINTORESSJC10"
    pad_x, pad_y = 30, 16
    tw = draw.textlength(text, font=f)
    box_w = tw + pad_x * 2 + 46
    box_h = 30 + pad_y * 2
    x0 = (W - box_w) / 2
    y0 = 150
    y1 = y0 + box_h
    x1 = x0 + box_w

    shadow = soft_shadow((W, H), (x0, y0 + 6, x1, y1 + 6), radius=box_h / 2, blur=16, opacity=110)
    im = Image.alpha_composite(im, shadow)
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (x0, y0, x1, y1), radius=box_h / 2, fill=(17, 17, 19, 235))
    draw.rounded_rectangle((x0, y0, x1, y1), radius=box_h / 2, outline=GOLD, width=2)

    icx, icy = x0 + pad_x + 12, (y0 + y1) / 2
    draw.ellipse((icx - 12, icy - 16, icx + 12, icy + 16), outline=GOLD_BRIGHT, width=3)
    draw.line((icx - 12, icy - 4, icx + 12, icy - 4), fill=GOLD_BRIGHT, width=2)

    draw.text((x0 + pad_x + 46, (y0 + y1) / 2), text, font=f, fill=GOLD_BRIGHT, anchor="lm")

    im.save(os.path.join(OUT, fname))
    print("saved", fname, "box", (x0, y0, x1, y1))


if __name__ == "__main__":
    card_caixinha("Dá pra aplicar cimento queimado direto no azulejo do banheiro, sem quebrar nada?", "caixinha.png")
    pill_caption("Direto sobre o azulejo", "cap1.png")
    pill_caption("Sem quebra-quebra", "cap2.png")
    pill_caption("Acabamento liso e uniforme", "cap3.png")
    pill_caption("Pronto em poucas horas", "cap4.png")
    card_cta()
    tag_cupom()
