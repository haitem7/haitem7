#!/usr/bin/env python3
"""
Build the TLEMCENYA Shopify theme from the same sources as the static site.

    python3 build_shopify.py

Reads content/{fr,en,ar}.json, content/wilayas.json and the compiled
assets/css/site.css, and writes into shopify/theme/:

    assets/theme.css         site.css with font URLs flattened for the Shopify
                             CDN, followed by shopify/src/shopify.css
    assets/*.woff2, *.jpg…   the self-hosted fonts and the photographs
    locales/*.json           every storefront string, in three languages

then zips the theme to shopify/tlemcenya-theme.zip, ready for
Online Store > Themes > Add theme > Upload zip file.

The Liquid, the JSON templates, the settings and theme.js are hand-written
and live in shopify/theme/ directly: this script never touches them.

Copy lives in content/*.json, as it does for the static site. Edit it there
and rebuild; do not edit shopify/theme/locales/ by hand, the next build
overwrites it.
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import shutil
import zipfile

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "shopify" / "src"
THEME = ROOT / "shopify" / "theme"
ZIP = ROOT / "shopify" / "tlemcenya-theme.zip"
CSV = ROOT / "shopify" / "products.csv"
LOCALES = {"fr": "fr.default.json", "en": "en.json", "ar": "ar.json"}

# Theme assets copied as-is. harvest-placeholder.* is deliberately absent:
# it is not the client's photograph and must never reach a live store.
IMAGES = [
    "img/bottles-1l.jpg",
    "img/mill-extraction.jpg",
    "img/mark.jpg",
    "img/favicon.svg",
    "video/hero-poster.jpg",
]

# Arabic is an RTL paragraph and digits are bidi-weak: without an isolate
# "18 – 22 %" renders as "22 % – 18". Same rule as num() in build.py.
RANGE = re.compile(r"\d[\d., ]*\s[–—-]\s\d[\d.,]*\s?[%٪]?")


def iso(s: str, lang: str) -> str:
    if lang != "ar":
        return s
    return RANGE.sub(lambda m: "⁦" + m.group(0) + "⁩", s)


# ------------------------------------------------------------ UI strings
# Strings the static site never needed: a product page, a collection, the
# customer account, search. Written here in all three languages because
# content/*.json has no home for them.
UI = {
    "fr": {
        "general": {
            "home": "Accueil",
            "back_home": "Retour à la boutique",
            "search": "Rechercher",
            "search_placeholder": "Rechercher un format…",
            "search_results": "Résultats pour « {{ terms }} »",
            "search_none": "Aucun résultat pour « {{ terms }} ».",
            "previous": "Précédent",
            "next": "Suivant",
            "page_of": "Page {{ current }} sur {{ total }}",
            "not_found_title": "Page introuvable",
            "not_found_body": "Cette adresse ne mène nulle part. L'huile, elle, est toujours à la boutique.",
            "language": "Langue",
            "account": "Mon compte",
            "cart_link": "Panier",
            "cart_count": "{{ count }} article(s) dans le panier",
            "password_title": "Ouverture prochaine",
            "password_enter": "Accès boutique",
            "password_label": "Mot de passe",
            "password_submit": "Entrer",
            "newsletter_label": "Votre e-mail",
            "newsletter_submit": "Me prévenir",
            "newsletter_done": "Merci, nous vous écrirons à l'ouverture.",
            "policies": "Informations légales",
            "read_more": "Lire la suite",
            "blog_empty": "Aucun article pour le moment.",
        },
        "products": {
            "quantity": "Quantité",
            "add": "Ajouter au panier",
            "sold_out": "Indisponible",
            "price_pending": "Prix à définir",
            "unavailable": "Cette combinaison n'est pas disponible.",
            "option": "Format",
            "tax_note": "Toutes taxes comprises, hors livraison.",
            "cod": "Paiement en espèces à la livraison.",
            "delivery_link": "Livraison dans les 58 wilayas",
            "more": "Les autres formats",
            "empty_collection": "Aucun produit dans cette collection pour le moment.",
            "sort": "Trier",
        },
        "cart_page": {
            "title": "Votre panier",
            "product": "Produit",
            "price": "Prix",
            "total": "Total",
            "note": "Remarque pour la livraison",
            "note_hint": "Facultatif : un repère, un horaire qui vous arrange.",
            "update": "Mettre à jour",
            "continue": "Continuer mes achats",
            "error": "La quantité demandée n'est pas disponible.",
        },
        "customer": {
            "login": "Connexion",
            "register": "Créer un compte",
            "email": "E-mail",
            "password": "Mot de passe",
            "first_name": "Prénom",
            "last_name": "Nom",
            "sign_in": "Se connecter",
            "create": "Créer le compte",
            "forgot": "Mot de passe oublié ?",
            "recover_title": "Réinitialiser le mot de passe",
            "recover_body": "Nous vous envoyons un lien par e-mail.",
            "recover_submit": "Envoyer",
            "recover_done": "Un e-mail vient de vous être envoyé.",
            "cancel": "Annuler",
            "no_account": "Pas encore de compte ?",
            "guest": "Continuer sans compte",
            "account": "Mon compte",
            "logout": "Se déconnecter",
            "orders": "Mes commandes",
            "no_orders": "Vous n'avez pas encore passé de commande.",
            "order": "Commande",
            "date": "Date",
            "payment": "Paiement",
            "fulfillment": "Expédition",
            "total": "Total",
            "addresses": "Mes adresses",
            "view_addresses": "Voir les adresses ({{ count }})",
            "add_address": "Ajouter une adresse",
            "edit": "Modifier",
            "delete": "Supprimer",
            "delete_confirm": "Supprimer cette adresse ?",
            "default": "Adresse par défaut",
            "set_default": "Utiliser par défaut",
            "save": "Enregistrer",
            "company": "Société",
            "address1": "Adresse",
            "address2": "Complément d'adresse",
            "city": "Commune",
            "province": "Wilaya",
            "country": "Pays",
            "zip": "Code postal",
            "phone": "Téléphone",
            "activate": "Activer le compte",
            "activate_body": "Choisissez un mot de passe pour activer votre compte.",
            "password_confirm": "Confirmer le mot de passe",
            "decline": "Refuser l'invitation",
            "reset": "Nouveau mot de passe",
            "reset_body": "Choisissez un nouveau mot de passe.",
            "back_account": "Retour au compte",
            "subtotal": "Sous-total",
            "shipping": "Livraison",
            "tax": "Taxes",
            "cancelled": "Commande annulée le {{ date }}",
            "billing": "Adresse de facturation",
            "shipping_address": "Adresse de livraison",
            "sku": "Réf.",
            "qty": "Qté",
        },
        "gift_card": {
            "title": "Votre carte-cadeau",
            "code": "Code",
            "expired": "Cette carte-cadeau a expiré.",
            "disabled": "Cette carte-cadeau est désactivée.",
            "shop": "Aller à la boutique",
            "print": "Imprimer",
        },
    },
    "en": {
        "general": {
            "home": "Home",
            "back_home": "Back to the shop",
            "search": "Search",
            "search_placeholder": "Search for a size…",
            "search_results": "Results for “{{ terms }}”",
            "search_none": "Nothing found for “{{ terms }}”.",
            "previous": "Previous",
            "next": "Next",
            "page_of": "Page {{ current }} of {{ total }}",
            "not_found_title": "Page not found",
            "not_found_body": "This address leads nowhere. The oil is still in the shop.",
            "language": "Language",
            "account": "My account",
            "cart_link": "Basket",
            "cart_count": "{{ count }} item(s) in the basket",
            "password_title": "Opening soon",
            "password_enter": "Store access",
            "password_label": "Password",
            "password_submit": "Enter",
            "newsletter_label": "Your email",
            "newsletter_submit": "Let me know",
            "newsletter_done": "Thank you, we will write when we open.",
            "policies": "Legal information",
            "read_more": "Read more",
            "blog_empty": "No articles yet.",
        },
        "products": {
            "quantity": "Quantity",
            "add": "Add to basket",
            "sold_out": "Unavailable",
            "price_pending": "Price to be set",
            "unavailable": "This combination is not available.",
            "option": "Size",
            "tax_note": "All taxes included, delivery extra.",
            "cod": "Cash on delivery.",
            "delivery_link": "Delivery to all 58 wilayas",
            "more": "The other sizes",
            "empty_collection": "No products in this collection yet.",
            "sort": "Sort",
        },
        "cart_page": {
            "title": "Your basket",
            "product": "Product",
            "price": "Price",
            "total": "Total",
            "note": "Delivery note",
            "note_hint": "Optional: a landmark, a time that suits you.",
            "update": "Update",
            "continue": "Continue shopping",
            "error": "The quantity requested is not available.",
        },
        "customer": {
            "login": "Sign in",
            "register": "Create an account",
            "email": "Email",
            "password": "Password",
            "first_name": "First name",
            "last_name": "Last name",
            "sign_in": "Sign in",
            "create": "Create account",
            "forgot": "Forgot your password?",
            "recover_title": "Reset your password",
            "recover_body": "We will email you a link.",
            "recover_submit": "Send",
            "recover_done": "We have sent you an email.",
            "cancel": "Cancel",
            "no_account": "No account yet?",
            "guest": "Continue as guest",
            "account": "My account",
            "logout": "Sign out",
            "orders": "My orders",
            "no_orders": "You have not placed an order yet.",
            "order": "Order",
            "date": "Date",
            "payment": "Payment",
            "fulfillment": "Shipping",
            "total": "Total",
            "addresses": "My addresses",
            "view_addresses": "View addresses ({{ count }})",
            "add_address": "Add an address",
            "edit": "Edit",
            "delete": "Delete",
            "delete_confirm": "Delete this address?",
            "default": "Default address",
            "set_default": "Set as default",
            "save": "Save",
            "company": "Company",
            "address1": "Address",
            "address2": "Address line 2",
            "city": "Town",
            "province": "Wilaya",
            "country": "Country",
            "zip": "Postcode",
            "phone": "Phone",
            "activate": "Activate your account",
            "activate_body": "Choose a password to activate your account.",
            "password_confirm": "Confirm password",
            "decline": "Decline invitation",
            "reset": "New password",
            "reset_body": "Choose a new password.",
            "back_account": "Back to account",
            "subtotal": "Subtotal",
            "shipping": "Delivery",
            "tax": "Tax",
            "cancelled": "Order cancelled on {{ date }}",
            "billing": "Billing address",
            "shipping_address": "Delivery address",
            "sku": "SKU",
            "qty": "Qty",
        },
        "gift_card": {
            "title": "Your gift card",
            "code": "Code",
            "expired": "This gift card has expired.",
            "disabled": "This gift card is disabled.",
            "shop": "Go to the shop",
            "print": "Print",
        },
    },
    "ar": {
        "general": {
            "home": "الرئيسية",
            "back_home": "العودة إلى المتجر",
            "search": "بحث",
            "search_placeholder": "ابحث عن عبوة…",
            "search_results": "نتائج البحث عن «{{ terms }}»",
            "search_none": "لا توجد نتائج لـ «{{ terms }}».",
            "previous": "السابق",
            "next": "التالي",
            "page_of": "الصفحة {{ current }} من {{ total }}",
            "not_found_title": "الصفحة غير موجودة",
            "not_found_body": "هذا العنوان لا يؤدي إلى أي صفحة. الزيت ما زال في المتجر.",
            "language": "اللغة",
            "account": "حسابي",
            "cart_link": "السلة",
            "cart_count": "{{ count }} منتج في السلة",
            "password_title": "الافتتاح قريبًا",
            "password_enter": "دخول المتجر",
            "password_label": "كلمة المرور",
            "password_submit": "دخول",
            "newsletter_label": "بريدك الإلكتروني",
            "newsletter_submit": "أعلمني",
            "newsletter_done": "شكرًا، سنراسلك عند الافتتاح.",
            "policies": "معلومات قانونية",
            "read_more": "اقرأ المزيد",
            "blog_empty": "لا توجد مقالات حاليًا.",
        },
        "products": {
            "quantity": "الكمية",
            "add": "أضف إلى السلة",
            "sold_out": "غير متوفر",
            "price_pending": "السعر لم يُحدَّد بعد",
            "unavailable": "هذا الاختيار غير متوفر.",
            "option": "العبوة",
            "tax_note": "شامل جميع الرسوم، دون التوصيل.",
            "cod": "الدفع نقدًا عند الاستلام.",
            "delivery_link": "التوصيل إلى 58 ولاية",
            "more": "العبوات الأخرى",
            "empty_collection": "لا توجد منتجات في هذه المجموعة حاليًا.",
            "sort": "ترتيب",
        },
        "cart_page": {
            "title": "سلتك",
            "product": "المنتج",
            "price": "السعر",
            "total": "الإجمالي",
            "note": "ملاحظة للتوصيل",
            "note_hint": "اختياري: علامة مميزة، أو وقت يناسبك.",
            "update": "تحديث",
            "continue": "متابعة التسوق",
            "error": "الكمية المطلوبة غير متوفرة.",
        },
        "customer": {
            "login": "تسجيل الدخول",
            "register": "إنشاء حساب",
            "email": "البريد الإلكتروني",
            "password": "كلمة المرور",
            "first_name": "الاسم",
            "last_name": "اللقب",
            "sign_in": "دخول",
            "create": "إنشاء الحساب",
            "forgot": "نسيت كلمة المرور؟",
            "recover_title": "إعادة تعيين كلمة المرور",
            "recover_body": "سنرسل لك رابطًا عبر البريد الإلكتروني.",
            "recover_submit": "إرسال",
            "recover_done": "أرسلنا إليك رسالة بالبريد الإلكتروني.",
            "cancel": "إلغاء",
            "no_account": "ليس لديك حساب؟",
            "guest": "المتابعة دون حساب",
            "account": "حسابي",
            "logout": "تسجيل الخروج",
            "orders": "طلباتي",
            "no_orders": "لم تقدّم أي طلب بعد.",
            "order": "الطلب",
            "date": "التاريخ",
            "payment": "الدفع",
            "fulfillment": "الشحن",
            "total": "الإجمالي",
            "addresses": "عناويني",
            "view_addresses": "عرض العناوين ({{ count }})",
            "add_address": "إضافة عنوان",
            "edit": "تعديل",
            "delete": "حذف",
            "delete_confirm": "حذف هذا العنوان؟",
            "default": "العنوان الافتراضي",
            "set_default": "اجعله الافتراضي",
            "save": "حفظ",
            "company": "الشركة",
            "address1": "العنوان",
            "address2": "تكملة العنوان",
            "city": "البلدية",
            "province": "الولاية",
            "country": "البلد",
            "zip": "الرمز البريدي",
            "phone": "الهاتف",
            "activate": "تفعيل الحساب",
            "activate_body": "اختر كلمة مرور لتفعيل حسابك.",
            "password_confirm": "تأكيد كلمة المرور",
            "decline": "رفض الدعوة",
            "reset": "كلمة مرور جديدة",
            "reset_body": "اختر كلمة مرور جديدة.",
            "back_account": "العودة إلى الحساب",
            "subtotal": "المجموع الفرعي",
            "shipping": "التوصيل",
            "tax": "الرسوم",
            "cancelled": "أُلغي الطلب في {{ date }}",
            "billing": "عنوان الفوترة",
            "shipping_address": "عنوان التوصيل",
            "sku": "المرجع",
            "qty": "الكمية",
        },
        "gift_card": {
            "title": "بطاقة الهدية",
            "code": "الرمز",
            "expired": "انتهت صلاحية بطاقة الهدية هذه.",
            "disabled": "بطاقة الهدية هذه معطّلة.",
            "shop": "الذهاب إلى المتجر",
            "print": "طباعة",
        },
    },
}


# ------------------------------------------------------------ content

def numbered(items: list[dict], prefix: str, lang: str, keys=("label", "value")) -> dict:
    out = {}
    for n, it in enumerate(items, 1):
        for k in keys:
            out[f"{prefix}_{n}_{k}"] = iso(str(it[k]), lang)
    return out


def content_strings(c: dict, wilayas: list[dict]) -> dict:
    """content/<lang>.json, flattened into the keys the Liquid reads."""
    lang = c["lang"]
    s = c["shop"]
    h, k, d, cart = s["hero"], s["catalog"], s["delivery"], s["cart"]
    g, p, L, f = c["gallery"], c["process"], c["location"], c["footer"]

    zones = {}
    for z in d["zones"]:
        zones[f"zone_{z['id']}_name"] = z["name"]
        zones[f"zone_{z['id']}_wilayas"] = ", ".join(
            w[lang] for w in wilayas if w["zone"] == z["id"])

    steps = {}
    for n, st in enumerate(p["steps"], 1):
        steps[f"step_{n}_title"] = st["title"]
        steps[f"step_{n}_body"] = iso(st["body"], lang)
        steps[f"step_{n}_tag"] = iso(st["tag"], lang)

    mill = next((sh for sh in g["shots"] if "mill-extraction" in sh["file"]), g["shots"][0])

    return {
        "brand": c.get("brand") or "TLEMCENYA",
        "skip": c["skip"],
        "nav_label": s["nav_label"],
        "nav_open": c["nav_menu_open"],
        "nav_close": c["nav_menu_close"],
        "nav_cta": s["nav_cta"],
        "nav_shop": s["nav"][0]["label"],
        "nav_delivery": s["nav"][1]["label"],
        "nav_mill": s["nav"][2]["label"],
        "nav_find": s["nav"][3]["label"],
        "cross": s["cross"]["label"],
        "meta_description": s["meta"]["description"],
        "hero": {
            "line_1": h["title_lines"][0],
            "line_2": h["title_lines"][1],
            "lede": h["lede"],
            "cta_primary": h["cta_primary"],
            "cta_secondary": h["cta_secondary"],
            **numbered(h["data"], "data", lang),
        },
        "catalog": {
            "title": k["title"],
            "lede": k["lede"],
            "price_pending": k["price_pending"],
            "add": k["add"],
            "added": k["added"],
            "sold_out": k["sold_out"],
            "note": k["note"],
        },
        "cart": {key: cart[key] for key in (
            "title", "open", "close", "empty", "empty_cta", "qty", "inc", "dec",
            "remove", "removed", "subtotal", "shipping", "total",
            "shipping_pending", "checkout", "added_live")},
        "delivery": {
            "title": d["title"],
            "lede": d["lede"],
            "zones_title": d["zones_title"],
            "zone_label": d["zone_label"],
            "price_label": d["price_label"],
            "wilayas_label": d["wilayas_label"],
            "pending": d["pending"],
            "pickup_title": d["pickup_title"],
            "pickup_body": d["pickup_body"],
            "note": d["note"],
            **zones,
            **numbered(d["facts"], "fact", lang),
        },
        "gallery": {
            "title": g["title"],
            "body_1": g["body"][0],
            "body_2": g["body"][1] if len(g["body"]) > 1 else "",
            "shot_alt": mill["alt"],
            "shot_caption": mill["caption"],
        },
        "process": {
            "title": p["title"],
            "lede": p["lede"],
            "mark_alt": p["mark"]["alt"],
            **steps,
        },
        "location": {
            "title": L["title"],
            "lede": L["lede"],
            "address_label": L["address_label"],
            "gps_label": L["gps_label"],
            "gps_pending": L["gps_pending"],
            "maps": L["maps"],
            "waze": L["waze"],
            "note": L["note"],
            **numbered(L["facts"], "fact", lang),
        },
        "footer": {
            "address_label": f["address_label"],
            "address_1": f["address"][0],
            "address_2": f["address"][1],
            "address_3": f["address"][2],
            "phone_label": f["phone_label"],
            "email_label": f["email_label"],
            "hours_label": f["hours_label"],
            "hours": iso(f["hours"], lang),
            "lang_label": f["lang_label"],
            "legal": f["legal"],
            "whatsapp": f["whatsapp"],
        },
    }


# ------------------------------------------------------------ steps

def build_css() -> None:
    css = (ROOT / "assets" / "css" / "site.css").read_text("utf-8")
    # Shopify serves every theme asset from one flat folder, so the fonts
    # sit beside theme.css rather than in ../fonts/.
    css = css.replace("url(../fonts/", "url(")
    extra = (SRC / "shopify.css").read_text("utf-8")
    out = ("/* Generated by build_shopify.py from assets/css/site.css and "
           "shopify/src/shopify.css — do not edit. */\n" + css + "\n" + extra)
    (THEME / "assets" / "theme.css").write_text(out, "utf-8")


def copy_assets() -> None:
    dst = THEME / "assets"
    for font in sorted((ROOT / "assets" / "fonts").glob("*.woff2")):
        shutil.copy2(font, dst / font.name)
    for rel in IMAGES:
        src = ROOT / "assets" / rel
        shutil.copy2(src, dst / src.name)


def build_locales() -> None:
    wilayas = json.loads((ROOT / "content" / "wilayas.json").read_text("utf-8"))
    for lang, name in LOCALES.items():
        c = json.loads((ROOT / "content" / f"{lang}.json").read_text("utf-8"))
        data = dict(UI[lang])
        data["content"] = content_strings(c, wilayas)
        (THEME / "locales" / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")


def check_locales() -> None:
    """Three languages, one set of keys. A key missing from en or ar shows
    the storefront visitor a "translation missing" string."""
    def keys(d: dict, pre: str = "") -> set[str]:
        out = set()
        for k, v in d.items():
            out |= keys(v, pre + k + ".") if isinstance(v, dict) else {pre + k}
        return out

    base = keys(json.loads((THEME / "locales" / LOCALES["fr"]).read_text("utf-8")))
    for lang, name in LOCALES.items():
        other = keys(json.loads((THEME / "locales" / name).read_text("utf-8")))
        if other != base:
            raise SystemExit(f"locales/{name}: keys differ from fr: "
                             f"{sorted(base ^ other)[:10]}")

    # Every t-key the Liquid asks for must exist.
    used = set()
    for f in THEME.rglob("*.liquid"):
        used |= set(re.findall(r"'([a-z_]+(?:\.[a-z0-9_]+)+)'\s*\|\s*t\b", f.read_text("utf-8")))
    missing = sorted(k for k in used if k not in base and not k.startswith("shopify."))
    if missing:
        raise SystemExit("Liquid uses locale keys that do not exist: " + ", ".join(missing))


def build_products_csv() -> None:
    """The five formats as a Shopify product import, from shop.catalog.

    Every product is imported as a DRAFT. content/fr.json holds no price
    yet, and an invented price is a commercial commitment: the price goes
    in at 0, the theme shows "Prix à définir" and refuses the basket, and
    nothing is on sale until someone sets a real figure and activates it.
    Weights are left empty for the same reason — fill them in before any
    weight-based delivery rate.
    """
    c = json.loads((ROOT / "content" / "fr.json").read_text("utf-8"))
    k = c["shop"]["catalog"]
    head = ["Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
            "Option1 Name", "Option1 Value", "Variant SKU", "Variant Grams",
            "Variant Inventory Tracker", "Variant Inventory Policy",
            "Variant Fulfillment Service", "Variant Price", "Variant Requires Shipping",
            "Variant Taxable", "Image Src", "Image Alt Text", "Status"]
    with CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(head)
        for it in k["items"]:
            price = str(it.get("price", "")).strip().replace("\u202f", "").replace(" ", "").replace(",", ".")
            w.writerow([
                "huile-olive-" + it["sku"].replace("tly-", ""),
                f"Huile d'olive vierge extra — {it['size']}",
                f"<p>{it['body']}</p>",
                "TLEMCENYA",
                it["material"],
                "huile d'olive, sigoise, tlemcen",
                "TRUE",
                "Title", "Default Title",
                it["sku"].upper(),
                "",
                "", "deny", "manual",
                price or "0",
                "TRUE", "TRUE",
                "", "",
                "draft",
            ])


def build_zip() -> None:
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(THEME.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(THEME).as_posix())


def main() -> None:
    for d in ("assets", "locales"):
        (THEME / d).mkdir(parents=True, exist_ok=True)
    build_css()
    copy_assets()
    build_locales()
    check_locales()
    build_products_csv()
    build_zip()
    n = sum(1 for f in THEME.rglob("*") if f.is_file())
    print(f"shopify/theme: {n} files -> {ZIP.relative_to(ROOT)} "
          f"({ZIP.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
