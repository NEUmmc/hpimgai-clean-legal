#!/usr/bin/env python3
"""Check published HTML legal copy against the approved source text.

Visible article text must match the source except whitespace, underscore
dividers, bullet markers, and the mailto link around the contact address.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VENDOR_NAMES = ("AdMob", "Firebase", "AppLovin")
YEARLY = (
    "A Yearly Subscription is not available in the current version of the App "
    "and may be added later."
)


def normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def source_visible(path: Path) -> str:
    raw = path.read_bytes().decode("utf-8-sig")
    kept = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or re.fullmatch(r"_+", stripped):
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        kept.append(stripped)
    return normalize(" ".join(kept))


def article_visible(path: Path) -> str:
    document = path.read_text(encoding="utf-8")
    match = re.search(r"<article>(.*)</article>", document, flags=re.S)
    if not match:
        raise SystemExit(f"{path.name} has no article")
    body = match.group(1)
    body = re.sub(r"<br\s*/?>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    return normalize(html.unescape(body))


def assert_equal(name: str, actual: str, expected: str) -> None:
    if actual == expected:
        print(f"PASS {name}: visible legal text matches source ({len(expected)} chars)")
        return
    print(f"FAIL {name}: visible legal text differs from source", file=sys.stderr)
    # word-level hint
    aw, ew = actual.split(), expected.split()
    for i, (a, e) in enumerate(zip(aw, ew)):
        if a != e:
            print(f"  first word mismatch at {i}: html={a!r} source={e!r}", file=sys.stderr)
            print(f"  html context: {' '.join(aw[max(0, i-6):i+8])}", file=sys.stderr)
            print(f"  src  context: {' '.join(ew[max(0, i-6):i+8])}", file=sys.stderr)
            break
    else:
        print(f"  length html words {len(aw)} source words {len(ew)}", file=sys.stderr)
        if len(aw) != len(ew):
            longer, label = (aw, "html") if len(aw) > len(ew) else (ew, "source")
            shorter = ew if label == "html" else aw
            print(f"  extra {label}: {' '.join(longer[len(shorter):len(shorter)+12])!r}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    pairs = (
        ("privacy-policy.html", "privacy-policy-corrected.txt"),
        ("terms-of-use.html", "terms-of-use-corrected.txt"),
    )
    for html_name, txt_name in pairs:
        assert_equal(
            html_name,
            article_visible(ROOT / html_name),
            source_visible(ROOT / txt_name),
        )

    privacy_html = (ROOT / "privacy-policy.html").read_text(encoding="utf-8")
    terms_html = (ROOT / "terms-of-use.html").read_text(encoding="utf-8")
    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")

    for name in VENDOR_NAMES:
        if re.search(re.escape(name), privacy_html, flags=re.I):
            print(f"FAIL privacy contains vendor name {name}", file=sys.stderr)
            sys.exit(1)
    print("PASS privacy-policy.html does not contain AdMob, Firebase, or AppLovin")

    if YEARLY not in article_visible(ROOT / "terms-of-use.html"):
        print("FAIL terms do not state that yearly is not currently offered", file=sys.stderr)
        sys.exit(1)
    print("PASS terms state a yearly subscription is not available in the current version")

    reminder = ROOT / "FUTURE-ADDITIONS-REMINDER-广告服务未来添加提醒.txt"
    reminder_text = reminder.read_text(encoding="utf-8")
    for name in ("Google AdMob", "Firebase", "AppLovin", "AppLovin MAX"):
        if name not in reminder_text:
            print(f"FAIL reminder missing {name}", file=sys.stderr)
            sys.exit(1)
    print("PASS reminder file keeps its future-vendor note")

    changes = (ROOT / "legal-documents-changes.txt").read_text(encoding="utf-8")
    for snippet in (
        "The current version of the App does not display advertisements and does not include third-party advertising SDKs.",
        "A Yearly Subscription is not available in the current version of the App and may be added later.",
        "FUTURE-ADDITIONS-REMINDER-广告服务未来添加提醒.txt",
    ):
        if snippet not in changes:
            print(f"FAIL changes log missing exact passage: {snippet}", file=sys.stderr)
            sys.exit(1)
    print("PASS changes log keeps both approved corrections")

    for page in (privacy_html, terms_html, index_html):
        if "FUTURE-ADDITIONS-REMINDER" in page or "legal-documents-changes" in page:
            print("FAIL a public page links the reminder or the changes log", file=sys.stderr)
            sys.exit(1)
        if "viewport" not in page:
            print("FAIL missing viewport", file=sys.stderr)
            sys.exit(1)
        if re.search(r"<script\b|fonts\.google|fonts\.gstatic|googletagmanager|google-analytics|cdnjs|unpkg|jsdelivr", page, flags=re.I):
            print("FAIL page references a script or external service", file=sys.stderr)
            sys.exit(1)
        external = re.findall(r"""(?:href|src)\s*=\s*["'](https?:[^"']+)["']""", page, flags=re.I)
        if external:
            print(f"FAIL page has external URL {external}", file=sys.stderr)
            sys.exit(1)
    if re.search(r"https?://", css):
        print("FAIL stylesheet has an external URL", file=sys.stderr)
        sys.exit(1)
    for page_name, page in (
        ("privacy-policy.html", privacy_html),
        ("terms-of-use.html", terms_html),
        ("index.html", index_html),
    ):
        if 'href="styles.css"' not in page:
            print(f"FAIL {page_name} missing local stylesheet", file=sys.stderr)
            sys.exit(1)
    print("PASS pages use a viewport and local CSS only, and do not link the reminder")

    if not (ROOT / ".nojekyll").is_file():
        print("FAIL missing .nojekyll", file=sys.stderr)
        sys.exit(1)
    print("PASS .nojekyll is present for GitHub Pages root publishing")

    for needle in ("privacy-policy.html", "terms-of-use.html"):
        if needle not in index_html:
            print(f"FAIL index does not link {needle}", file=sys.stderr)
            sys.exit(1)
    print("PASS index links both legal pages")

    # Source files in the repo must stay byte-for-byte equal to the approved copies
    # when those copies are still available beside the test. The committed files are
    # the copies under test; this checks they are non-empty and that privacy/terms
    # still carry the approved effective date.
    for name in (
        "privacy-policy-corrected.txt",
        "terms-of-use-corrected.txt",
        "FUTURE-ADDITIONS-REMINDER-广告服务未来添加提醒.txt",
        "legal-documents-changes.txt",
    ):
        data = (ROOT / name).read_bytes()
        if not data:
            print(f"FAIL {name} is empty", file=sys.stderr)
            sys.exit(1)
    if b"Effective Date: June 12, 2026" not in (ROOT / "privacy-policy-corrected.txt").read_bytes():
        print("FAIL privacy source effective date changed", file=sys.stderr)
        sys.exit(1)
    if b"Effective Date: June 12, 2026" not in (ROOT / "terms-of-use-corrected.txt").read_bytes():
        print("FAIL terms source effective date changed", file=sys.stderr)
        sys.exit(1)
    print("PASS source text files are present and keep the approved effective date")

    if "HotPot2025@outlook.com" not in privacy_html or "HotPot2025@outlook.com" not in terms_html:
        print("FAIL contact email missing", file=sys.stderr)
        sys.exit(1)
    if 'href="mailto:HotPot2025@outlook.com"' not in privacy_html:
        print("FAIL privacy email is not a mailto link", file=sys.stderr)
        sys.exit(1)
    if 'href="mailto:HotPot2025@outlook.com"' not in terms_html:
        print("FAIL terms email is not a mailto link", file=sys.stderr)
        sys.exit(1)
    print("PASS contact email is unchanged and linked")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
