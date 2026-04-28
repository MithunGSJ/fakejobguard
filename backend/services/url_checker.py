# backend/services/url_checker.py
import requests
import whois
from datetime import datetime, timezone
import os

GOOGLE_SAFE_BROWSING_KEY = os.getenv('GOOGLE_SAFE_BROWSING_KEY', '')


def check_url_safety(url: str) -> dict:
    """
    Checks a URL for safety using 3 methods:
    1. Google Safe Browsing API (phishing/malware detection)
    2. WHOIS domain age check (new domains are suspicious)
    3. Redirect chain analysis (too many redirects = suspicious)

    Returns a dict with:
    - is_safe: bool
    - risk_score: int (0-100)
    - flags: list of strings explaining what was found
    """
    flags = []
    risk = 0

    # 1. Check with Google Safe Browsing API
    if GOOGLE_SAFE_BROWSING_KEY:
        try:
            api_url = (
                f'https://safebrowsing.googleapis.com/v4/threatMatches:find'
                f'?key={GOOGLE_SAFE_BROWSING_KEY}'
            )
            payload = {
                'client': {
                    'clientId': 'fake-job-detector',
                    'clientVersion': '1.0'
                },
                'threatInfo': {
                    'threatTypes': [
                        'MALWARE',
                        'SOCIAL_ENGINEERING',
                        'UNWANTED_SOFTWARE'
                    ],
                    'platformTypes': ['ANY_PLATFORM'],
                    'threatEntryTypes': ['URL'],
                    'threatEntries': [{'url': url}]
                }
            }
            resp = requests.post(api_url, json=payload, timeout=5)
            data = resp.json()
            if data.get('matches'):
                flags.append(
                    'URL flagged by Google Safe Browsing as phishing/malware'
                )
                risk += 60
        except Exception as e:
            flags.append(
                f'Could not verify URL with Safe Browsing: {str(e)}'
            )

    # 1.5. Heuristic: suspicious TLDs and URL patterns (runs before WHOIS)
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url if url.startswith('http') else f'http://{url}')
        domain = parsed.netloc.lower().replace('www.', '')
        url_lower = url.lower()

        # Suspicious TLDs commonly used in scam sites
        suspicious_tlds = ['.xyz', '.top', '.click', '.win', '.loan', '.bid',
                           '.work', '.download', '.racing', '.science', '.faith']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            flags.append(f'Suspicious TLD detected in domain: {domain}')
            risk += 30

        # Scam keywords in the URL itself
        scam_url_keywords = ['free-job', 'earn-money', 'work-from-home', 'daily-earn',
                             'guaranteed', 'no-experience', 'job-offer', 'cash-daily']
        found_kws = [kw for kw in scam_url_keywords if kw in url_lower]
        if found_kws:
            flags.append(f'Scam keywords found in URL: {", ".join(found_kws)}')
            risk += 25

        # HTTP (no SSL) is a warning sign for job sites
        if parsed.scheme == 'http':
            flags.append('URL uses plain HTTP (not HTTPS) — insecure')
            risk += 10
    except Exception:
        pass

    # 2. Check domain age using WHOIS
    try:
        from urllib.parse import urlparse as _up
        domain = _up(url).netloc.replace('www.', '')
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            if creation_date.tzinfo is None:
                creation_date = creation_date.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_days = (now - creation_date).days
            if age_days < 30:
                flags.append(
                    f'Domain created only {age_days} days ago — very new, suspicious'
                )
                risk += 40
            elif age_days < 90:
                flags.append(
                    f'Domain is relatively new ({age_days} days old)'
                )
                risk += 20
    except Exception:
        flags.append('Could not determine domain age')
        risk += 10

    # 3. Check for redirect chains
    try:
        resp = requests.get(url, allow_redirects=True, timeout=5)
        if len(resp.history) > 3:
            flags.append(
                f'URL has {len(resp.history)} redirects — suspicious'
            )
            risk += 20
        # Check if final URL domain differs from original
        from urllib.parse import urlparse
        orig_domain = urlparse(url).netloc
        final_domain = urlparse(resp.url).netloc
        if orig_domain != final_domain:
            flags.append(
                f'URL redirects to different domain: {final_domain}'
            )
            risk += 25
    except Exception:
        flags.append('Could not follow URL redirects')
        risk += 5

    risk = min(risk, 100)  # cap at 100
    return {
        'is_safe': risk < 40,
        'risk_score': risk,
        'flags': flags
    }
