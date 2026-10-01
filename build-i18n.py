#!/usr/bin/env python3
"""Genera los árboles en/ y es/ a partir del FR.

El sitio Wix original tiene EN/ES con el MISMO contenido francés (solo cambian
las URLs), así que la copia es mecánica + traducción del chrome (nav, botones,
prev/next) + switcher de idioma. El cuerpo queda en francés como el original.

Uso: python3 build-i18n.py   (corre desde sitio-tournesols/)
Idempotente: no duplica el switcher; re-ejecutable tras editar el FR.

NO genera: blog.html ni blog/ de en/es (contenido distinto por idioma, a mano).
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
EQUIPO = ["mariano-real", "cristian-mendoza", "santiago-gilardi",
          "melisa-taborda", "corina-prado", "marine-machabert"]
FR_PAGES = (["index.html", "ecole.html", "mobile.html",
             "privacy-policy.html", "terms-and-conditions.html",
             "accessibility-statement.html"]
            + ["equipe/%s.html" % s for s in EQUIPO])
# Solo switcher en FR (el contenido EN/ES se escribe a mano por diferir).
SWITCH_ONLY = (["blog.html"]
               + ["blog/origine-douleurs-fascias.html",
                  "blog/douleur-corps-cerveau.html",
                  "blog/securite-douleur-tension.html"])

# Solo strings que CAMBIAN. El cuerpo queda en francés como el original.
UI = {
    "en": [
        (">Équipe<", ">Team<"),
        (">Avis<", ">Reviews<"),
        (">Accès<", ">Access<"),
        (">Prendre rendez-vous<", ">Book now<"),
        (">Nous contacter<", ">Contact us<"),
        (">Demander le programme<", ">Request the program<"),
        (">Réserver en ligne<", ">Book online<"),
        ("Suivante : ", "Next: "),
        ("Suivant : ", "Next: "),
        ("Suivant →", "Next →"),
        (">Précédent<", ">Previous<"),
        ("Tous les articles →", "All articles →"),
        ("← Tous les articles", "← All articles"),
    ],
    "es": [
        (">Services<", ">Servicios<"),
        (">Équipe<", ">Equipo<"),
        (">Avis<", ">Opiniones<"),
        (">Accès<", ">Acceso<"),
        (">Contact<", ">Contacto<"),
        (">Prendre rendez-vous<", ">Reservar<"),
        (">Nous contacter<", ">Contáctanos<"),
        (">Demander le programme<", ">Solicitar el programa<"),
        (">Réserver en ligne<", ">Reservar en línea<"),
        ("Suivante : ", "Siguiente: "),
        ("Suivant : ", "Siguiente: "),
        ("Suivant →", "Siguiente →"),
        (">Précédent<", ">Anterior<"),
        ("Tous les articles →", "Todos los artículos →"),
        ("← Tous les articles", "← Todos los artículos"),
    ],
}

LANG_OF = {"fr": "fr", "en": "en", "es": "es"}


def switcher(cur, targets):
    """targets: dict lang -> href relativo. El idioma actual va en <strong>."""
    parts = []
    for lang in ("fr", "en", "es"):
        if lang == cur:
            parts.append("<strong>%s</strong>" % lang.upper())
        else:
            parts.append('<a href="%s">%s</a>' % (targets[lang], lang.upper()))
    return '<nav class="lang">%s</nav>' % "".join(parts)


def inject_switcher(html, cur, targets):
    if 'class="lang"' in html:
        return html, False
    m = re.search(r'(<a class="brand"[^>]*>Les&nbsp;Tournesols</a>)', html)
    if not m:
        return html, False
    return html.replace(m.group(1), m.group(1) + "\n    " + switcher(cur, targets), 1), True


def build():
    stats = {"archivos": 0, "switcher_fr": 0}
    for frel in FR_PAGES:
        fpath = os.path.join(ROOT, frel)
        if not os.path.exists(fpath):
            print("FALTA FR:", frel)
            continue
        src = open(fpath, encoding="utf-8").read()
        fdir = os.path.dirname(frel) or "."

        # 1. Switcher en el FR original (hrefs relativos a su carpeta).
        tgt = {lang: os.path.relpath(os.path.join(lang, frel), fdir)
               for lang in ("en", "es")}
        src, touched = inject_switcher(src, "fr", {"fr": "#", **tgt})
        if touched:
            open(fpath, "w", encoding="utf-8").write(src)
            stats["switcher_fr"] += 1

        # 2. Copias EN/ES.
        for lang in ("en", "es"):
            out_rel = os.path.join(lang, frel)
            out_path = os.path.join(ROOT, out_rel)
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            t = src
            t = t.replace('lang="fr"', 'lang="%s"' % lang, 1)
            # En copias: reemplazar el switcher FR heredado por el propio.
            t = re.sub(r'\s*<nav class="lang">.*?</nav>', '', t, count=1)
            for old, new in UI[lang]:
                t = t.replace(old, new)
            odir = os.path.dirname(out_rel) or "."
            depth = out_rel.count("/")
            pre = "../" * depth
            # Recursos de raíz (styles.css, assets/): prefijo según profundidad.
            t = t.replace('"../assets/', '"@@ASSETS@')
            t = t.replace('"assets/', '"%sassets/' % pre)
            t = t.replace('"@@ASSETS@', '"%sassets/' % pre)
            t = t.replace('"../styles.css"', '"@@CSS@')
            t = t.replace('"styles.css"', '"%sstyles.css"' % pre)
            t = t.replace('"@@CSS@', '"%sstyles.css"' % pre)
            links = {
                "fr": os.path.relpath(frel, odir),
                "en": os.path.relpath(os.path.join("en", frel), odir),
                "es": os.path.relpath(os.path.join("es", frel), odir),
            }
            t, _ = inject_switcher(t, lang, links)
            open(out_path, "w", encoding="utf-8").write(t)
            stats["archivos"] += 1
    for frel in SWITCH_ONLY:
        fpath = os.path.join(ROOT, frel)
        if not os.path.exists(fpath):
            print("FALTA FR:", frel)
            continue
        src = open(fpath, encoding="utf-8").read()
        fdir = os.path.dirname(frel) or "."
        tgt = {lang: os.path.relpath(os.path.join(lang, frel), fdir)
               for lang in ("en", "es")}
        src, touched = inject_switcher(src, "fr", {"fr": "#", **tgt})
        if touched:
            open(fpath, "w", encoding="utf-8").write(src)
            stats["switcher_fr"] += 1
    print("generados: %(archivos)d | switcher agregado a FR: %(switcher_fr)d" % stats)


if __name__ == "__main__":
    build()
