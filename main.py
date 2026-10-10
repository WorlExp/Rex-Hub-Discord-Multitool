#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════╗
║   NEXUS DISCORD MULTITOOL v1.0       ║
║   150 Özellik | Modüller Otomatik    ║
╚══════════════════════════════════════╝
"""

import os, sys, subprocess, time, random, string, json, base64, threading, re, datetime

# ---------- OTOMATİK MODÜL KURULUMU ----------
def kur(paket):
    print(f"[*] '{paket}' paketi kuruluyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", paket, "-q"])

try:
    import requests
except ImportError:
    kur("requests"); import requests

try:
    from colorama import Fore, Style, init
    from colorama import init
except ImportError:
    kur("colorama")
    from colorama import Fore, Style, init

init(autoreset=True)

API = "https://discord.com/api/v9"
CDN = "https://cdn.discordapp.com"
KAYITLI_TOKEN = None

# ---------- YARDIMCI FONKSİYONLAR ----------
def logo():
    print(Fore.MAGENTA + """
╔════════════════════════════════════════╗
║    NEXUS DISCORD MULTITOOL  v1.0       ║
║    150 Özellik | Python Edition        ║
╚════════════════════════════════════════╝""" + Style.RESET_ALL)

def basari(m): print(Fore.GREEN + "[+] " + str(m))
def hata(m):   print(Fore.RED + "[-] " + str(m))
def bilgi(m):  print(Fore.YELLOW + "[*] " + str(m))

def sor(m, t=str):
    try:
        v = input(Fore.CYAN + "[?] " + m + ": " + Style.RESET_ALL)
        return t(v)
    except ValueError:
        hata("Geçersiz giriş!")
        return sor(m, t)

def hdr(tok, tur="application/json"):
    return {
        "Authorization": tok,
        "Content-Type": tur,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*"
    }

def token_al():
    global KAYITLI_TOKEN
    if KAYITLI_TOKEN:
        bilgi(f"Kayıtlı token kullanılıyor: {KAYITLI_TOKEN[:20]}...")
        if input("[?] Farklı token gir? (e/h): ").lower().strip() == "e":
            return sor("Token")
        return KAYITLI_TOKEN
    return sor("Token (boşsa kayıtlı kaydetmek için Araçlar > Token Yöneticisi)")

def token_gecerli(r, tok):
    resp = r.get(f"{API}/users/@me", headers=hdr(tok))
    return resp.status_code == 200

def guvenli(fn):
    def sarmal():
        try:
            r = requests.Session()
            fn(r)
        except KeyboardInterrupt:
            hata("İşlem durduruldu.")
        except requests.exceptions.RequestException as e:
            hata(f"Bağlantı hatası: {e}")
        except Exception as e:
            hata(f"Hata: {e}")
    return sarmal

# ---------- ÇEKİRDEK FONKSİYONLAR ----------
def _sel_guild(r, tok):
    g = r.get(f"{API}/users/@me/guilds", headers=hdr(tok)).json()
    for i, x in enumerate(g):
        print(f"  [{i}] {x['name']} ({x['id']})")
    return g[sor("Sunucu numarası", int)]["id"]

def _sel_channel(r, tok, gid):
    c = r.get(f"{API}/guilds/{gid}/channels", headers=hdr(tok)).json()
    ch = [x for x in c if x["type"] == 0]
    for i, x in enumerate(ch):
        print(f"  [{i}] #{x['name']} ({x['id']})")
    return ch[sor("Kanal numarası", int)]["id"]

def _send_msg(r, tok, kanal, icerik):
    return r.post(f"{API}/channels/{kanal}/messages", headers=hdr(tok), json={"content": icerik})

def _spam(r, kanal, mesaj, adet, hiz=0.4, tok=None):
    basari(f"Başlandı. Hedef: {kanal} | Adet: {adet}")
    for i in range(adet):
        rr = r.post(kanal, json={"content": mesaj},
                    headers={"Content-Type": "application/json"})
        if rr.status_code in (200, 204):
            print(Fore.GREEN + f"  [{i+1}/{adet}] gönderildi")
        else:
            print(Fore.RED + f"  [{i+1}/{adet}] hata ({rr.status_code})")
        time.sleep(hiz)

def _webhook_spam(url, mesaj, adet, hiz=0.3, hizli=False):
    def govde():
        return mesaj
    if hizli:
        ths = [threading.Thread(target=_spam, args=(requests.Session(), url, mesaj, adet//5 + 1, hiz)) for _ in range(5)]
        [t.start() for t in ths]; [t.join() for t in ths]
    else:
        _spam(requests.Session(), url, mesaj, adet, hiz)

# ==========================================================================
# A) TOKEN ARAÇLARI (20)
# ==========================================================================
def t_kontrol(r):
    t = sor("Token")
    rr = r.get(f"{API}/users/@me", headers=hdr(t))
    if rr.status_code == 200:
        d = rr.json(); basari(f"Token Geçerli! Kullanıcı: {d['username']}")
    elif rr.status_code == 401: hata("Token geçersiz!")
    else: hata(f"Bilinmeyen hata: {rr.status_code}")

def t_bilgi(r):
    t = token_al(); d = r.get(f"{API}/users/@me", headers=hdr(t)).json()
    email = d.get("email", "yok")
    print(f"""  Kullanıcı: {d['username']}#{d.get('discriminator','0')}
  ID: {d['id']}
  E-posta: {email}
  Telefon: {d.get('phone','yok')}
  2FA: {d.get('mfa_enabled')}
  Premium: {d.get('premium_type',0)}
  Bayraklar: {d.get('flags',0)}""")

def t_sunucular(r):
    t = token_al()
    g = r.get(f"{API}/users/@me/guilds", headers=hdr(t)).json()
    for x in g: print(f"  • {x['name']} | ID: {x['id']} | Sahip: {'Evet' if x.get('owner') else 'Hayır'}")
    basari(f"Toplam {len(g)} sunucu.")

def t_dms(r):
    t = token_al()
    c = r.get(f"{API}/users/@me/channels", headers=hdr(t)).json()
    for x in c:
        if x["type"] == 1: print(f"  • DM: {x['recipients'][0]['username']} ({x['id']})")
        else: print(f"  • Grup: {x.get('name','İsimsiz')} ({x['id']})")

def t_dostlar(r):
    t = token_al()
    f = r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json()
    for x in f: print(f"  • {x['user']['username']} ({x['user']['id']}) | Tip: {x['type']}")

def t_istekler(r):
    t = token_al()
    f = r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json()
    bekleyen = [x for x in f if x["type"] == 3]
    if not bekleyen: bilgi("Bekleyen istek yok.")
    for x in bekleyen: print(f"  • {x['user']['username']} ({x['user']['id']})")

def t_game(r):
    t = token_al(); isim = sor("Oynuyor adı")
    rr = r.patch(f"{API}/users/@me/settings", headers=hdr(t),
                 json={"activity": {"name": isim, "type": 0}})
    basari("Ayarlandı!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_custom(r):
    t = token_al(); isim = sor("Özel durum metni")
    rr = r.patch(f"{API}/users/@me/settings", headers=hdr(t),
                 json={"custom_status": {"text": isim}})
    basari("Ayarlandı!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_username(r):
    t = token_al(); u = sor("Yeni kullanıcı adı"); p = sor("Şifre (boş olabilir)")
    body = {"username": u}
    if p: body["password"] = p
    rr = r.patch(f"{API}/users/@me", headers=hdr(t), json=body)
    basari("Değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_avatar(r):
    t = token_al(); yol = sor("Resim dosya yolu")
    with open(yol, "rb") as f: dat = base64.b64encode(f.read()).decode()
    rr = r.patch(f"{API}/users/@me", headers=hdr(t),
                 json={"avatar": f"data:image/png;base64,{dat}"})
    basari("Avatar değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_bio(r):
    t = token_al(); b = sor("Yeni bio")
    rr = r.patch(f"{API}/users/@me/profile", headers=hdr(t), json={"bio": b})
    basari("Bio değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_tema(r, tema):
    t = token_al()
    rr = r.patch(f"{API}/users/@me/settings", headers=hdr(t), json={"theme": tema})
    basari(f"Tema: {tema}" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_locale(r, loc):
    t = token_al()
    rr = r.patch(f"{API}/users/@me/settings", headers=hdr(t), json={"locale": loc})
    basari(f"Dil: {loc}" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_status(r):
    t = token_al()
    print("  [1] Çevrimiçi [2] Boşta [3] Rahatsız Etmeyin")
    m = {"1":"online","2":"idle","3":"dnd"}[str(sor("Seçim", int))]
    rr = r.patch(f"{API}/users/@me/settings", headers=hdr(t), json={"status": m})
    basari("Durum değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def t_tokenid(r):
    t = token_al()
    try:
        cid = base64.b64decode(t.split(".")[0] + "==").decode()
        basari(f"Kullanıcı ID: {cid}")
    except Exception: hata("Token formatı okunamadı (yeni format olabilir).")

def t_dump(r):
    t = token_al()
    u = r.get(f"{API}/users/@me", headers=hdr(t)).json()
    g = r.get(f"{API}/users/@me/guilds", headers=hdr(t)).json()
    f = r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json()
    with open("token_yedek.json", "w", encoding="utf-8") as fh:
        json.dump({"user": u, "guilds": g,
                   "friends": [x["user"] for x in f if x["type"] == 1]}, fh, indent=2)
    basari("token_yedek.json dosyasına kaydedildi!")

def t_profil(r):
    t = token_al()
    d = r.get(f"{API}/users/@me", headers=hdr(t)).json()
    print(f"  Kullanıcı: {d['username']}\n  ID: {d['id']}\n  Avatar: {CDN}/avatars/{d['id']}/{d.get('avatar')}.png")

def t_istatistik(r):
    t = token_al()
    g = r.get(f"{API}/users/@me/guilds", headers=hdr(t)).json()
    c = r.get(f"{API}/users/@me/channels", headers=hdr(t)).json()
    f = r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json()
    print(f"  Sunucu: {len(g)} | DM: {len(c)} | Dost: {len([x for x in f if x['type']==1])}")

# ==========================================================================
# B) SPAM ARAÇLARI (25)
# ==========================================================================
def m_spam_sabit(r, adet):
    t = token_al(); k = sor("Kanal ID"); m = sor("Mesaj")
    _send_spam_core(r, t, k, m, adet)

def _send_spam_core(r, t, kanal, mesaj, adet, hiz=0.4):
    for i in range(adet):
        rr = r.post(f"{API}/channels/{kanal}/messages", headers=hdr(t), json={"content": mesaj})
        print(f"  [{i+1}/{adet}] {'OK' if rr.status_code==200 else 'Hata '+str(rr.status_code)}")
        time.sleep(hiz)

def m_spam_soru(r):
    t = token_al(); k = sor("Kanal ID"); m = sor("Mesaj"); a = sor("Adet", int)
    _send_spam_core(r, t, k, m, a)

def m_spam_rastgele(r):
    t = token_al(); k = sor("Kanal ID"); a = sor("Adet", int)
    havuz = ["selam", "naber", "https://discord.gg", "xd", "lo", "basarili", "?", "!", "nexus", "+++"]
    for i in range(a):
        _send_msg(r, t, k, random.choice(havuz)); time.sleep(0.4); print(f"  [{i+1}/{a}] gönderildi")

def m_spam_hizli(r):
    t = token_al(); k = sor("Kanal ID"); m = sor("Mesaj"); a = sor("Adet", int)
    def th():
        for _ in range(a // 5):
            _send_msg(requests.Session(), t, k, m); time.sleep(0.3)
    ts = [threading.Thread(target=th) for _ in range(5)]
    [x.start() for x in ts]; [x.join() for x in ts]

def m_everyone(r):
    t = token_al(); k = sor("Kanal ID"); m = sor("Mesaj") + " @everyone"; a = sor("Adet", int)
    _send_spam_core(r, t, k, m, a)

def m_react(r, adet_anlasilir=None):
    t = token_al(); k = sor("Kanal ID"); mid = sor("Mesaj ID")
    e = sor("Emoji (örn: 😀 veya isim:id)")
    for i in range(adet_anlasilir or sor("Adet", int)):
        rr = r.put(f"{API}/channels/{k}/messages/{mid}/reactions/{e}/@me", headers=hdr(t))
        print(f"  [{i+1}] {'OK' if rr.status_code==204 else 'Hata'}"); time.sleep(0.5)

def m_typing(r):
    t = token_al(); k = sor("Kanal ID")
    bilgi("Durdurmak için Ctrl+C")
    try:
        while True:
            r.post(f"{API}/channels/{k}/typing", headers=hdr(t)); time.sleep(8)
    except KeyboardInterrupt: pass

def m_edit_spam(r):
    t = token_al(); k = sor("Kanal ID"); mid = sor("Mesaj ID"); m = sor("Yeni içerik"); a = sor("Adet", int)
    for i in range(a):
        r.patch(f"{API}/channels/{k}/messages/{mid}", headers=hdr(t), json={"content": f"{m} {i}"}); time.sleep(0.5)
    basari("Bitti!")

def f_spam(r, a=None):
    t = token_al(); u = sor("Kullanıcı adı"); adet = a or sor("Adet", int)
    kod = 0
    for i in range(adet):
        rr = r.post(f"{API}/users/@me/relationships", headers=hdr(t), json={"username": u})
        if rr.status_code == 204: kod += 1
        print(f"  [{i+1}/{adet}] {'OK' if rr.status_code==204 else 'Hata '+str(rr.status_code)}"); time.sleep(0.5)
    basari(f"{kod} istek gönderildi.")

def f_spam_variants(r, n):
    f_spam(r, n)

def dm_spam(r):
    t = token_al(); k = sor("DM Kanal ID"); m = sor("Mesaj"); a = sor("Adet", int)
    _send_spam_core(r, t, k, m, a)

def toplu_dm(r):
    t = token_al(); m = sor("Mesaj"); a = sor("Her DM'ye adet", int)
    ch = r.get(f"{API}/users/@me/channels", headers=hdr(t)).json()
    for x in ch:
        for _ in range(a):
            _send_msg(r, t, x["id"], m); time.sleep(0.5)
        print(f"  OK -> {x['id']}")

def tum_sunuculara_spam(r):
    t = token_al(); m = sor("Mesaj")
    g = r.get(f"{API}/users/@me/guilds", headers=hdr(t)).json()
    for x in g:
        c = [c for c in r.get(f"{API}/guilds/{x['id']}/channels", headers=hdr(t)).json() if c["type"] == 0]
        if c: _send_msg(r, t, c[0]["id"], m); time.sleep(1)
    basari("Bitti!")

def spam_gecikmeli(r):
    t = token_al(); k = sor("Kanal ID"); m = sor("Mesaj"); a = sor("Adet", int); hz = sor("Gecikme (saniye, örn 0.5)", float)
    _send_spam_core(r, t, k, m, a, hz)

def spam_sonsuz(r):
    t = token_al(); k = sor("Kanal ID"); m = sor("Mesaj")
    bilgi("Durdurmak için Ctrl+C. İyi spamler!")
    try:
        while True:
            _send_msg(r, t, k, m); time.sleep(0.4)
    except KeyboardInterrupt: basari("Durduruldu.")

# ==========================================================================
# C) SUNUCU ARAÇLARI (35)
# ==========================================================================
def sunucudan_cik(r):
    t = token_al(); g = _sel_guild(r, t)
    rr = r.delete(f"{API}/users/@me/guilds/{g}", headers=hdr(t))
    basari("Çıkıldı!" if rr.status_code == 204 else f"Hata: {rr.status_code}")

def tum_sunuculardan_cik(r):
    t = token_al()
    for x in r.get(f"{API}/users/@me/guilds", headers=hdr(t)).json():
        rr = r.delete(f"{API}/users/@me/guilds/{x['id']}", headers=hdr(t))
        print(f"  {'Çıkıldı' if rr.status_code==204 else 'Hata'} -> {x['name']}")

def sunucu_bilgi(r):
    t = token_al(); g = _sel_guild(r, t)
    d = r.get(f"{API}/guilds/{g}?with_counts=true", headers=hdr(t)).json()
    print(f"  Ad: {d.get('name')}\n  ID: {d.get('id')}\n  Sahip: {d.get('owner_id')}\n  Üye: {d.get('approximate_member_count')}\n  Boost: {d.get('premium_subscription_count',0)}")

def sunucu_ikon(r):
    t = token_al(); g = _sel_guild(r, t)
    d = r.get(f"{API}/guilds/{g}", headers=hdr(t)).json()
    if d.get("icon"): basari(f"{CDN}/icons/{g}/{d['icon']}.png?size=1024")
    else: hata("İkon yok.")

def sunucu_banner(r):
    t = token_al(); g = _sel_guild(r, t)
    d = r.get(f"{API}/guilds/{g}", headers=hdr(t)).json()
    if d.get("banner"): basari(f"{CDN}/banners/{g}/{d['banner']}.png?size=1024")
    else: hata("Banner yok.")

def kanal_olustur(r, adet=None):
    t = token_al(); g = _sel_guild(r, t); isim = sor("Kanal adı")
    for i in range(adet or sor("Adet", int)):
        r.post(f"{API}/guilds/{g}/channels", headers=hdr(t), json={"name": f"{isim}-{i}", "type": 0})
        print(f"  [{i+1}] oluştu"); time.sleep(0.3)

def tum_kanallari_sil(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/channels", headers=hdr(t)).json():
        r.delete(f"{API}/channels/{x['id']}", headers=hdr(t)); print(f"  Silindi -> {x['name']}"); time.sleep(0.2)

def rol_olustur(r, adet=None):
    t = token_al(); g = _sel_guild(r, t); isim = sor("Rol adı")
    for i in range(adet or sor("Adet", int)):
        r.post(f"{API}/guilds/{g}/roles", headers=hdr(t), json={"name": f"{isim}-{i}"}); print(f"  [{i+1}] ok"); time.sleep(0.3)

def tum_rolleri_sil(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/roles", headers=hdr(t)).json():
        if not x.get("managed"):
            r.delete(f"{API}/guilds/{g}/roles/{x['id']}", headers=hdr(t)); print(f"  Silindi -> {x['name']}"); time.sleep(0.2)

def emoji_listele(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/emojis", headers=hdr(t)).json():
        print(f"  :{x['name']}: ({x['id']})")

def emoji_sil(r):
    t = token_al(); g = _sel_guild(r, t)
    emoji_listele(r); eid = sor("Emoji ID")
    rr = r.delete(f"{API}/guilds/{g}/emojis/{eid}", headers=hdr(t))
    basari("Silindi!" if rr.status_code == 204 else f"Hata: {rr.status_code}")

def tum_emojileri_sil(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/emojis", headers=hdr(t)).json():
        r.delete(f"{API}/guilds/{g}/emojis/{x['id']}", headers=hdr(t)); print(f"  Silindi -> :{x['name']}:"); time.sleep(0.2)

def sunucu_adi_degistir(r):
    t = token_al(); g = _sel_guild(r, t); isim = sor("Yeni sunucu adı")
    rr = r.patch(f"{API}/guilds/{g}", headers=hdr(t), json={"name": isim})
    basari("Değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def sunucu_ikonu_degistir(r):
    t = token_al(); g = _sel_guild(r, t); yol = sor("Resim dosya yolu")
    dat = base64.b64encode(open(yol, "rb").read()).decode()
    rr = r.patch(f"{API}/guilds/{g}", headers=hdr(t), json={"icon": f"data:image/png;base64,{dat}"})
    basari("Değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def webhook_olustur(r):
    t = token_al(); g = _sel_guild(r, t); k = _sel_channel(r, t, g)
    rr = r.post(f"{API}/channels/{k}/webhooks", headers=hdr(t), json={"name": "nexus"})
    if rr.status_code == 200: basari(f"URL: https://discord.com/api/webhooks/{rr.json()['id']}/{rr.json()['token']}")
    else: hata(f"Hata: {rr.status_code}")

def uye_listesi(r):
    t = token_al(); g = _sel_guild(r, t)
    m = r.get(f"{API}/guilds/{g}/members?limit=1000", headers=hdr(t)).json()
    for x in m[:100]: print(f"  • {x['user']['username']} ({x['user']['id']})")
    basari(f"Toplam {len(m)} (ilk 100 gösterildi)")

def kanal_listesi(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/channels", headers=hdr(t)).json(): print(f"  • {x['name']} ({x['id']}) type:{x['type']}")

def rol_listesi(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/roles", headers=hdr(t)).json(): print(f"  • {x['name']} ({x['id']})")

def uye_bilgisi(r):
    t = token_al(); g = _sel_guild(r, t); uid = sor("Kullanıcı ID")
    m = r.get(f"{API}/guilds/{g}/members/{uid}", headers=hdr(t)).json()
    print(f"  Kullanıcı: {m['user']['username']}\n  Takma ad: {m.get('nick','yok')}\n  Roller: {m.get('roles',[])}")

def uye_banla(r):
    t = token_al(); g = _sel_guild(r, t); uid = sor("Kullanıcı ID")
    rr = r.put(f"{API}/guilds/{g}/bans/{uid}", headers=hdr(t), json={})
    basari("Banlandı!" if rr.status_code in (200, 204) else f"Hata: {rr.status_code} (2FA kodu gerekebilir)")

def toplu_ban(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/members?limit=1000", headers=hdr(t)).json():
        rr = r.put(f"{API}/guilds/{g}/bans/{x['user']['id']}", headers=hdr(t), json={})
        print(f"  {'Ban' if rr.status_code in (200,204) else 'Hata'} -> {x['user']['username']}"); time.sleep(0.3)

def ban_listesi(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/bans", headers=hdr(t)).json(): print(f"  • {x['user']['username']} ({x['user']['id']})")

def ban_kaldir(r):
    t = token_al(); g = _sel_guild(r, t); uid = sor("Kullanıcı ID")
    rr = r.delete(f"{API}/guilds/{g}/bans/{uid}", headers=hdr(t))
    basari("Kaldırıldı!" if rr.status_code == 204 else f"Hata: {rr.status_code}")

def davet_olustur(r):
    t = token_al(); g = _sel_guild(r, t); k = _sel_channel(r, t, g)
    rr = r.post(f"{API}/channels/{k}/invites", headers=hdr(t), json={"max_age": 86400})
    if rr.status_code == 200: basari(f"discord.gg/{rr.json()['code']}")
    else: hata(f"Hata: {rr.status_code}")

def davet_listesi(r):
    t = token_al(); g = _sel_guild(r, t)
    for x in r.get(f"{API}/guilds/{g}/invites", headers=hdr(t)).json(): print(f"  • discord.gg/{x['code']} ({x.get('uses',0)} kullanım)")

def sunucu_sahibi(r):
    t = token_al(); g = _sel_guild(r, t)
    d = r.get(f"{API}/guilds/{g}", headers=hdr(t)).json()
    u = r.get(f"{API}/users/{d['owner_id']}", headers=hdr(t)).json()
    print(f"  Sahip: {u['username']} ({u['id']})")

def kanal_ismi_degistir(r):
    t = token_al(); g = _sel_guild(r, t); k = _sel_channel(r, t, g); isim = sor("Yeni isim")
    rr = r.patch(f"{API}/channels/{k}", headers=hdr(t), json={"name": isim})
    basari("Değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def takma_ad_degistir(r):
    t = token_al(); g = _sel_guild(r, t); n = sor("Yeni takma ad (boş=sıfırla)")
    rr = r.patch(f"{API}/guilds/{g}/members/@me/nick", headers=hdr(t), json={"nick": n})
    basari("OK!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def sunucu_sustur(r):
    t = token_al(); g = _sel_guild(r, t)
    rr = r.patch(f"{API}/users/@me/guilds/{g}/settings", headers=hdr(t), json={"muted": True})
    basari("Susturuldu!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

# ==========================================================================
# D) WEBHOOK ARAÇLARI (20)
# ==========================================================================
def _wh_spam(a=None, gorsel=None, tts=False, everyone=False, embed=False):
    url = sor("Webhook URL")
    m = sor("Mesaj (boşsa rastgele)")
    adet = a or sor("Adet", int)
    def git():
        if embed:
            body = {"embeds": [{"title": m, "description": random.choice(["nexus","was here","hi"]), "color": random.randint(0, 16777215)}]}
        elif gorsel:
            body = {"embeds": [{"image": {"url": f"https://picsum.photos/400?{random.randint(1,9999)}"}}]}
        elif tts: body = {"content": m, "tts": True}
        elif everyone: body = {"content": m + " @everyone"}
        else: body = {"content": random.choice([m, m, m, m+" xD", "!!"]) if m else "nexus"}
        requests.post(url, json=body)
    for i in range(adet):
        git(); print(f"  [{i+1}/{adet}] gönderildi"); time.sleep(0.3)

def wh_bilgi():
    url = sor("Webhook URL")
    d = requests.get(url).json()
    print(f"  Ad: {d.get('name')}\n  ID: {d.get('id')}\n  Kanal: {d.get('channel_id')}\n  Sahip: {d.get('user',{}).get('username')}")

def wh_sil():
    url = sor("Webhook URL")
    rr = requests.delete(url)
    basari("Silindi!" if rr.status_code == 204 else f"Hata: {rr.status_code}")

def wh_isim():
    url = sor("Webhook URL"); isim = sor("Yeni isim")
    rr = requests.patch(url, json={"name": isim})
    basari("OK!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def wh_avatar():
    url = sor("Webhook URL"); yol = sor("Resim dosya yolu")
    dat = base64.b64encode(open(yol, "rb").read()).decode()
    rr = requests.patch(url, json={"avatar": f"data:image/png;base64,{dat}"})
    basari("OK!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def wh_coklu():
    urls = sor("Webhook URL'leri (virgülle)").split(",")
    m = sor("Mesaj"); a = sor("Her birine adet", int)
    for u in [x.strip() for x in urls]:
        for _ in range(a): requests.post(u, json={"content": m}); time.sleep(0.3)
        print(f"  OK -> {u[:50]}...")

def wh_yedekle():
    url = sor("Webhook URL")
    with open("webhook_yedek.json", "w") as f: json.dump(requests.get(url).json(), f, indent=2)
    basari("webhook_yedek.json kaydedildi!")

# ==========================================================================
# E) HESAP & DOSTLUK (25)
# ==========================================================================
def tum_istekleri_isle(r, kabul=True):
    t = token_al()
    for x in r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json():
        if x["type"] == 3:
            tip = "accept" if kabul else "ignore"
            rr = r.put(f"{API}/users/@me/relationships/{x['id']}", headers=hdr(t), json={"type": tip})
            print(f"  {'OK' if rr.status_code in (204,200) else 'Hata'} -> {x['user']['username']}")

def tum_dostlari_sil(r):
    t = token_al()
    for x in r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json():
        if x["type"] == 1:
            rr = r.delete(f"{API}/users/@me/relationships/{x['id']}", headers=hdr(t))
            print(f"  {'Silindi' if rr.status_code==204 else 'Hata'} -> {x['user']['username']}"); time.sleep(0.2)

def engelle(r, engelle=True):
    t = token_al()
    gid = _sel_guild(r, t) if False else None
    uid = sor("Kullanıcı ID")
    if engelle:
        rr = r.put(f"{API}/users/@me/relationships/{uid}", headers=hdr(t), json={"type": 2})
    else:
        rr = r.delete(f"{API}/users/@me/relationships/{uid}", headers=hdr(t))
    basari("OK!" if rr.status_code in (204, 200) else f"Hata: {rr.status_code}")

def usernfo(r):
    t = token_al(); uid = sor("Kullanıcı ID")
    d = r.get(f"{API}/users/{uid}", headers=hdr(t)).json()
    print(f"  Kullanıcı: {d['username']}\n  ID: {d['id']}\n  Avatar: {CDN}/avatars/{d['id']}/{d.get('avatar')}.png")

def avatar_cek(r):
    t = token_al(); uid = sor("Kullanıcı ID")
    d = r.get(f"{API}/users/{uid}", headers=hdr(t)).json()
    if d.get("avatar"): basari(f"{CDN}/avatars/{uid}/{d['avatar']}.png?size=1024")
    else: hata("Avatar yok.")

def banner_cek(r):
    t = token_al(); uid = sor("Kullanıcı ID")
    d = r.get(f"{API}/users/{uid}", headers=hdr(t)).json()
    if d.get("banner"): basari(f"{CDN}/banners/{uid}/{d['banner']}.png?size=1024")
    else: hata("Banner yok.")

def kullanciya_dm(r):
    t = token_al(); uid = sor("Kullanıcı ID"); m = sor("Mesaj")
    ch = r.post(f"{API}/users/@me/channels", headers=hdr(t), json={"recipient_id": uid}).json()
    _send_msg(r, t, ch["id"], m); basari("Gönderildi!")

def dm_sessize_al(r):
    t = token_al(); k = sor("DM Kanal ID"); m = sor("1=sessiz 0=açık", int)
    rr = r.patch(f"{API}/users/@me/guilds/@me/settings", headers=hdr(t), json={"muted": bool(m)}) if False else None
    rr = r.patch(f"{API}/channels/{k}/recipients/@me/settings", headers=hdr(t), json={"muted": bool(m)})
    basari("OK!" if rr.status_code != 404 else "Bu IDM için sessize alma API üzerinden sınırlı olabilir.")

def baglantilar(r):
    t = token_al()
    for x in r.get(f"{API}/users/@me/connections", headers=hdr(t)).json():
        print(f"  • {x.get('type')}: {x.get('name')}")

def hesap_not(r):
    t = token_al(); uid = sor("Kullanıcı ID"); n = sor("Not")
    rr = r.put(f"{API}/users/@me/notes/{uid}", headers=hdr(t), json={"note": n})
    basari("Not eklendi!" if rr.status_code == 204 else f"Hata: {rr.status_code}")

def dost_yedekle(r):
    t = token_al()
    f = [{"id": x["user"]["id"], "username": x["user"]["username"]}
         for x in r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json() if x["type"] == 1]
    json.dump(f, open("dostlar.json", "w"), indent=2); basari(f"{len(f)} dost kaydedildi!")

def dost_geri_yukle(r):
    t = token_al()
    f = json.load(open("dostlar.json"))
    for x in f:
        rr = r.post(f"{API}/users/@me/relationships", headers=hdr(t), json={"username": x["username"]})
        print(f"  {'OK' if rr.status_code==204 else 'Hata'} -> {x['username']}"); time.sleep(0.5)

def sifre_degistir(r):
    t = token_al(); eski = sor("Mevcut şifre"); yeni = sor("Yeni şifre")
    rr = r.patch(f"{API}/users/@me", headers=hdr(t), json={"password": eski, "new_password": yeni})
    basari("Değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def id_tarih(r):
    uid = sor("Kullanıcı ID")
    ts = ((int(uid) >> 22) + 1420070400000) / 1000
    basari(f"Hesap oluşturma: {datetime.datetime.utcfromtimestamp(ts)}")

def gonderilen_istekler_iptal(r):
    t = token_al()
    for x in r.get(f"{API}/users/@me/relationships", headers=hdr(t)).json():
        if x["type"] == 4:
            r.delete(f"{API}/users/@me/relationships/{x['id']}", headers=hdr(t))
            print(f"  İptal -> {x['user']['username']}"); time.sleep(0.3)

# ==========================================================================
# F) ARAÇLAR / UTILITY (25)
# ==========================================================================
def nitro_uret(n=None):
    kodlar = [''.join(random.choices(string.ascii_letters + string.digits, k=16)) for _ in range(n or sor("Adet", int))]
    open("nitro_kodlar.txt", "w").write("\n".join(kodlar))
    basari(f"{len(kodlar)} kod nitro_kodlar.txt dosyasına kaydedildi!")

def nitro_kontrol_tek(r=None):
    kod = sor("Nitro kodu")
    rr = requests.get(f"{API}/entitlements/gift-codes/{kod}")
    if rr.status_code == 200: basari(f"GEÇERLİ! -> discord.gift/{kod}")
    else: hata(f"Geçersiz ({rr.status_code})")

def nitro_toplu(r):
    try:
        kodlar = open("nitro_kodlar.txt").read().split()
    except FileNotFoundError:
        nitro_uret(1000); kodlar = open("nitro_kodlar.txt").read().split()
    for i, k in enumerate(kodlar):
        if requests.get(f"{API}/entitlements/gift-codes/{k}").status_code == 200:
            basari(f"BULUNDU: discord.gift/{k}")
        else: print(f"  [{i+1}] geçersiz")
        time.sleep(1)

def proxy_cek():
    rr = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000")
    open("proxies.txt", "w").write(rr.text)
    basari(f"{len(rr.text.splitlines())} proxy proxies.txt dosyasına kaydedildi!")

def proxy_test():
    ok = 0
    for p in open("proxies.txt").read().splitlines():
        try:
            requests.get("https://discord.com", proxies={"http": p, "https": p}, timeout=5)
            ok += 1; print(f"  OK -> {p}")
        except Exception: pass
    basari(f"{ok} proxy çalışıyor.")

def token_dosya_kontrol(r):
    yol = sor("Tokens dosyası (her satıra bir token)")
    for t in open(yol).read().splitlines():
        if t.strip():
            rr = r.get(f"{API}/users/@me", headers=hdr(t.strip()))
            print(f"  {'GEÇERLİ' if rr.status_code==200 else f'Geçersiz ({rr.status_code})'} -> {t.strip()[:25]}...")

def hypesquad(r, ev=None):
    t = token_al()
    if ev:
        rr = r.post(f"{API}/hypesquad/online", headers=hdr(t), json={"house_id": ev})
    else:
        rr = r.delete(f"{API}/hypesquad/online", headers=hdr(t))
    basari("OK!" if rr.status_code in (200, 204) else f"Hata: {rr.status_code}")

def ip_sorgula():
    ip = sor("IP adresi (boş = senin IP)")
    d = requests.get(f"http://ip-api.com/json/{ip}").json()
    print(f"  IP: {d.get('query')} | Şehir: {d.get('city')} | Ülke: {d.get('country')} | ISS: {d.get('isp')}")

def kullanici_adi_uret():
    for _ in range(10): print("  • " + random.choice(["nexus","hyper","dark","toxic","kaos","cyber","xx"]) + str(random.randint(100, 9999)))

def sifre_uret():
    print("  • " + ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=16)))

def rastgele_avatar(r):
    t = token_al()
    yaratici = random.choice(["adventurer", "bottts", "identicon", "avataaars"])
    dat = requests.get(f"https://api.dicebear.com/7.x/{yaratici}/png?seed={random.randint(1,99999)}").content
    b64 = base64.b64encode(dat).decode()
    rr = r.patch(f"{API}/users/@me", headers=hdr(t), json={"avatar": f"data:image/png;base64,{b64}"})
    basari("Avatar değişti!" if rr.status_code == 200 else f"Hata: {rr.status_code}")

def davet_bilgi():
    kod = sor("Davet kodu")
    d = requests.get(f"{API}/invites/{kod}").json()
    g = d.get("guild", {})
    print(f"  Sunucu: {g.get('name')} | Üye: ~{d.get('approximate_member_count')}")

def b64encode_arac():
    print("  " + base64.b64encode(sor("Metin").encode()).decode())

def b64decode_arac():
    print("  " + base64.b64decode(sor("Base64") + "==").decode(errors="ignore"))

def timestamp():
    ts = sor("Unix timestamp")
    print("  " + str(datetime.datetime.utcfromtimestamp(float(ts))))

def api_ping():
    rr = requests.get(f"{API}/gateway")
    print(f"  Discord API: {'ÇEVRİMİÇİ' if rr.status_code == 200 else 'SORUNLU'}")

def mesajlari_sil(r):
    t = token_al(); k = sor("Kanal ID"); ben = r.get(f"{API}/users/@me", headers=hdr(t)).json()["id"]
    a = sor("Kaç mesaj tara (max 100)", int)
    ms = r.get(f"{API}/channels/{k}/messages?limit={min(a,100)}", headers=hdr(t)).json()
    for m in [x for x in ms if x["author"]["id"] == ben]:
        r.delete(f"{API}/channels/{k}/messages/{m['id']}", headers=hdr(t)); print("  Silindi"); time.sleep(1)

def token_regex():
    t = sor("Token")
    print("  Format: " + ("GEÇERLİ görünüyor" if re.match(r"^[\w-]{20,}\.[\w-]{5,}\.[\w-]{20,}$", t) else "ŞÜPHELİ"))

def dil_temizle():
    for f in ["nitro_kodlar.txt", "proxies.txt", "webhook_yedek.json", "token_yedek.json", "dostlar.json"]:
        if os.path.exists(f): os.remove(f); print(f"  Silindi -> {f}")

def token_yonetici():
    global KAYITLI_TOKEN
    print("  [1] Kayıtlı token göster\n  [2] Token kaydet\n  [3] Kayıtlı tokenı sil")
    sec = sor("Seçim", int)
    if sec == 1: print("  " + (KAYITLI_TOKEN or "Kayıtlı yok"))
    elif sec == 2: KAYITLI_TOKEN = sor("Token"); basari("Kaydedildi (bellekte).")
    elif sec == 3: KAYITLI_TOKEN = None; basari("Silindi.")

# ==========================================================================
# KOMUT KAYDI (TOPLAM: 150 ÖZELLİK)
# ==========================================================================
KOMUTLAR = []
def ekle(kat, isim, fn):
    KOMUTLAR.append((kat, isim, guvenli(fn)))

# --- A) TOKEN ARAÇLARI (20) ---
for k, n, f in [
    ("TOKEN", "Token Kontrol", t_kontrol), ("TOKEN", "Token Bilgileri", t_bilgi),
    ("TOKEN", "Sunucuları Listele", t_sunucular), ("TOKEN", "DM Listesi", t_dms),
    ("TOKEN", "Dostları Listele", t_dostlar), ("TOKEN", "Bekleyen İstekler", t_istekler),
    ("TOKEN", "Oynuyor Değiştir", t_game), ("TOKEN", "Özel Durum Değiştir", t_custom),
    ("TOKEN", "Kullanıcı Adı Değiştir", t_username), ("TOKEN", "Avatar Değiştir", t_avatar),
    ("TOKEN", "Bio Değiştir", t_bio), ("TOKEN", "Tema: Koyu", lambda: None),
    ("TOKEN", "Tema: Açık", lambda: None),
    ("TOKEN", "Hesap Dili: Türkçe", lambda: None), ("TOKEN", "Hesap Dili: İngilizce", lambda: None),
    ("TOKEN", "Hesap Durumu Değiştir", t_status), ("TOKEN", "Token'dan ID Bul", t_tokenid),
    ("TOKEN", "Token Yedeği Al", t_dump), ("TOKEN", "Profil Bilgisi", t_profil),
    ("TOKEN", "Token İstatistikleri", t_istatistik)]:
    ekle(k, n, f if callable(f) and f != (lambda: None) else f)
# tema/dil düzeltmeleri
KOMUTLAR[-9] = ("TOKEN", "Tema: Koyu", guvenli(lambda: t_tema(requests.Session(), "dark")))
KOMUTLAR[-8] = ("TOKEN", "Tema: Açık", guvenli(lambda: t_tema(requests.Session(), "light")))
KOMUTLAR[-7] = ("TOKEN", "Hesap Dili: Türkçe", guvenli(lambda: t_locale(requests.Session(), "tr")))
KOMUTLAR[-6] = ("TOKEN", "Hesap Dili: İngilizce", guvenli(lambda: t_locale(requests.Session(), "en-US")))

# --- B) SPAM ARAÇLARI (25) ---
ekle("SPAM", "Mesaj Spam (Adet Sor)", m_spam_soru)
for a in [5, 10, 25, 50, 100, 1000]:
    ekle("SPAM", f"MESAJ Spam ({a} adet)", lambda a=a: m_spam_sabit(requests.Session(), a))
ekle("SPAM", "Mesaj Spam: Rastgele", m_spam_rastgele)
ekle("SPAM", "Mesaj Spam: Hızlı (5 Thread)", m_spam_hizli)
ekle("SPAM", "Spam: Sonsuz (Ctrl+C ile durdur)", spam_sonsuz)
ekle("SPAM", "Spam: Özel Gecikme", spam_gecikmeli)
ekle("SPAM", "Herkese Bahsetme Spam", m_everyone)
ekle("SPAM", "Typing (Yazıyor) Spam", m_typing)
ekle("SPAM", "Mesaj Düzenleme Spam", m_edit_spam)
ekle("SPAM", "Reaksiyon Spam (Sürekli)", m_react)
for a in [10, 50]:
    ekle("SPAM", f"Reaksiyon Spam ({a}x)", lambda a=a: m_react(requests.Session(), a))
ekle("SPAM", "Dostluk İsteği Spam (Adet Sor)", f_spam)
for a in [5, 10, 50]:
    ekle("SPAM", f"Dostluk İsteği Spam ({a})", lambda a=a: f_spam(requests.Session(), a))
ekle("SPAM", "DM: Tek Kullanıcıya Spam", dm_spam)
ekle("SPAM", "DM: Toplu Mass DM", toplu_dm)
ekle("SPAM", "Tüm Sunucuların İlk Kanalına Mesaj", tum_sunuculara_spam)

# --- C) SUNUCU ARAÇLARI (35) ---
for n, f in [
    ("Sunucudan Çık", sunucudan_cik), ("Tüm Sunuculardan Çık", tum_sunuculardan_cik),
    ("Sunucu Bilgisi", sunucu_bilgi), ("Sunucu İkonu Çek", sunucu_ikon),
    ("Sunucu Banner Çek", sunucu_banner), ("Kanal Oluştur (Adet Sor)", lambda: kanal_olustur(requests.Session())),
    ("Tüm Kanalları Sil", tum_kanallari_sil), ("Rol Oluştur (Adet Sor)", lambda: rol_olustur(requests.Session())),
    ("Tüm Rolleri Sil", tum_rolleri_sil), ("Emoji Listesi", emoji_listele),
    ("Emoji Sil", emoji_sil), ("Tüm Emojileri Sil", tum_emojileri_sil),
    ("Sunucu Adı Değiştir", sunucu_adi_degistir), ("Sunucu İkonu Değiştir", sunucu_ikonu_degistir),
    ("Webhook Oluştur", webhook_olustur), ("Üye Listesi", uye_listesi),
    ("Kanal Listesi", kanal_listesi), ("Rol Listesi", rol_listesi),
    ("Üye Bilgisi", uye_bilgisi), ("Üye Banla", uye_banla),
    ("Toplu Ban (Nuke)", toplu_ban), ("Ban Listesi", ban_listesi),
    ("Ban Kaldır", ban_kaldir), ("Davet Oluştur", davet_olustur),
    ("Davet Listesi", davet_listesi), ("Sunucu Sahibi Bilgisi", sunucu_sahibi),
    ("Kanal İsmi Değiştir", kanal_ismi_degistir), ("Takma Ad Değiştir", takma_ad_degistir),
    ("Kendini Sunucuda Sustur", sunucu_sustur)]:
    ekle("SUNUCU", n, f)
for a in [5, 10, 25, 50]:
    ekle("SUNUCU", f"Kanal Spam ({a} adet)", lambda a=a: kanal_olustur(requests.Session(), a))
for a in [5, 10, 25]:
    ekle("SUNUCU", f"Rol Spam ({a} adet)", lambda a=a: rol_olustur(requests.Session(), a))

# --- D) WEBHOOK ARAÇLARI (20) ---
ekle("WEBHOOK", "Webhook Spam (Adet Sor)", lambda: _wh_spam())
for a in [5, 10, 25, 50, 100]:
    ekle("WEBHOOK", f"Webhook Spam ({a} adet)", lambda a=a: _wh_spam(a))
ekle("WEBHOOK", "Webhook Spam: Embed", lambda: _wh_spam(embed=True))
ekle("WEBHOOK", "Webhook Spam: TTS", lambda: _wh_spam(tts=True))
ekle("WEBHOOK", "Webhook Spam: @everyone", lambda: _wh_spam(everyone=True))
ekle("WEBHOOK", "Webhook Spam: Rastgele Görsel", lambda: _wh_spam(gorsel=True))
ekle("WEBHOOK", "Webhook Spam: Hızlı", lambda: _wh_spam(50, hiz=0.05))
ekle("WEBHOOK", "Webhook Bilgisi", wh_bilgi)
ekle("WEBHOOK", "Webhook Sil", wh_sil)
ekle("WEBHOOK", "Webhook İsim Değiştir", wh_isim)
ekle("WEBHOOK", "Webhook Avatar Değiştir", wh_avatar)
ekle("WEBHOOK", "Çoklu Webhook Spam (virgülle)", wh_coklu)
ekle("WEBHOOK", "Webhook'a Tek Mesaj", lambda: _wh_spam(1))
ekle("WEBHOOK", "Webhook Yedekle", wh_yedekle)
ekle("WEBHOOK", "Webhook Içerik Görüntüle", wh_bilgi)

# --- E) HESAP & DOSTLUK (25) ---
for n, f in [
    ("Dostluk İsteği Gönder", lambda: f_spam(requests.Session(), 1)),
    ("Tüm İstekleri Kabul Et", lambda: tum_istekleri_isle(requests.Session(), True)),
    ("Tüm İstekleri Reddet", lambda: tum_istekleri_isle(requests.Session(), False)),
    ("Gönderilen İstekleri İptal Et", gonderilen_istekler_iptal),
    ("Tüm Dostları Sil", tum_dostlari_sil),
    ("Kullanıcı Bilgisi (ID)", usernfo), ("Avatar Çek (ID)", avatar_cek),
    ("Banner Çek (ID)", banner_cek), ("Kullanıcıya DM At", kullanciya_dm),
    ("DM Sessize Al/Aç", dm_sessize_al),
    ("Hesap Bağlantıları", baglantilar), ("Kullanıcıya Not Ekle", hesap_not),
    ("Dostları Yedekle", dost_yedekle), ("Dostları Geri Yükle", dost_geri_yukle),
    ("Şifre Değiştir", sifre_degistir), ("ID'den Hesap Tarihi", id_tarih)]:
    ekle("HESAP", n, f)
ekle("HESAP", "Kullanıcıyı Engelle", lambda: engelle(requests.Session(), True))
ekle("HESAP", "Engeli Kaldır", lambda: engelle(requests.Session(), False))
ekle("HESAP", "Dostu Kaldır", lambda: engelle(requests.Session(), False))
ekle("HESAP", "Kullanıcı Profil URL", avatar_cek)
ekle("HESAP", "E-posta Görüntüle", lambda: t_bilgi(requests.Session()))
ekle("HESAP", "2FA Durumu Görüntüle", lambda: t_bilgi(requests.Session()))
ekle("HESAP", "Premium Bilgisi", lambda: t_bilgi(requests.Session()))
ekle("HESAP", "Dost Sayısı", lambda: t_istatistik(requests.Session()))

# --- F) ARAÇLAR (25) ---
ekle("ARAÇLAR", "Nitro Kod Üret", nitro_uret)
ekle("ARAÇLAR", "Nitro Kod Kontrol (Tek)", nitro_kontrol_tek)
ekle("ARAÇLAR", "Nitro Toplu Kontrol", nitro_toplu)
ekle("ARAÇLAR", "Proxy Çek", proxy_cek)
ekle("ARAÇLAR", "Proxy Test", proxy_test)
ekle("ARAÇLAR", "Token Dosyası Kontrol", token_dosya_kontrol)
ekle("ARAÇLAR", "HypeSquad: Bravery", lambda: hypesquad(requests.Session(), 1))
ekle("ARAÇLAR", "HypeSquad: Brilliance", lambda: hypesquad(requests.Session(), 2))
ekle("ARAÇLAR", "HypeSquad: Balance", lambda: hypesquad(requests.Session(), 3))
ekle("ARAÇLAR", "HypeSquad: Kaldır", lambda: hypesquad(requests.Session(), None))
ekle("ARAÇLAR", "IP Sorgula", ip_sorgula)
ekle("ARAÇLAR", "Kullanıcı Adı Üret", kullanici_adi_uret)
ekle("ARAÇLAR", "Şifre Üret", sifre_uret)
ekle("ARAÇLAR", "Rastgele Avatar Yükle", rastgele_avatar)
ekle("ARAÇLAR", "Davet Bilgisi", davet_bilgi)
ekle("ARAÇLAR", "Base64 Şifrele", b64encode_arac)
ekle("ARAÇLAR", "Base64 Çöz", b64decode_arac)
ekle("ARAÇLAR", "Timestamp Dönüştür", timestamp)
ekle("ARAÇLAR", "Discord API Ping", api_ping)
ekle("ARAÇLAR", "Kendi Mesajlarını Sil", mesajlari_sil)
ekle("ARAÇLAR", "Token Format Kontrol", token_regex)
ekle("ARAÇLAR", "Hızlı Token Yöneticisi", token_yonetici)
ekle("ARAÇLAR", "Dosyaları Temizle", dil_temizle)

# ==========================================================================
# MENÜ
# ==========================================================================
def main():
    logo()
    print(Fore.CYAN + f"Toplam {len(KOMUTLAR)} özellik yüklü.\n" + Style.RESET_ALL)
    kategoriler = []
    for k, _, _ in KOMUTLAR:
        if k not in kategoriler: kategoriler.append(k)
    while True:
        print(Fore.CYAN + "\n=== ANA MENÜ ===")
        for i, k in enumerate(kategoriler, 1):
            adet = len([x for x in KOMUTLAR if x[0] == k])
            print(f"  [{i}] {k} ({adet} özellik)")
        print("  [q] Çıkış")
        sec = input(Fore.CYAN + "[?] Seçim: " + Style.RESET_ALL).strip().lower()
        if sec == "q":
            print(Fore.MAGENTA + "Görüşürüz!"); break
        try:
            kat = kategoriler[int(sec) - 1]
        except (ValueError, IndexError):
            hata("Geçersiz seçim!"); continue
        i = 1
        print(f"\n--- {kat} ---")
        sayfa = {}
        for k, isim, fn in KOMUTLAR:
            if k == kat:
                print(f"  [{i}] {isim}")
                sayfa[str(i)] = fn
                i += 1
        c = input(Fore.CYAN + "[?] Özellik no (geri=g): " + Style.RESET_ALL).strip().lower()
        if c == "g": continue
        if c in sayfa:
            print()
            sayfa[c]()
        else:
            hata("Geçersiz seçim!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nÇıkıldı.")
