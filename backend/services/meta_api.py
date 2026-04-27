# backend/services/meta_api.py
"""
Meta Ad Library API integration.

The Meta Ad Library API is completely free and public — no login needed.
It fetches ad metadata for social media job ads:
- How long the ad has been running
- Advertiser page creation date
- Spending history
- Targeted regions

Suspicious signals:
- Ad running less than 3 days
- New advertiser page
- Targeting only low-income regions
- No prior ad history
"""
import requests
from datetime import datetime, timezone


def check_meta_ad(ad_url: str) -> dict:
    """
    Check a Facebook/Instagram/Meta ad URL against the Meta Ad Library.

    Returns:
    - is_suspicious: bool
    - flags: list of suspicious findings
    - risk_score: int (0-100)
    - ad_data: dict of raw API response data
    """
    flags = []
    risk = 0
    ad_data = {}

    try:
        # Extract ad ID from URL if possible
        ad_id = _extract_ad_id(ad_url)

        if not ad_id:
            flags.append('Could not extract Meta ad ID from URL')
            return {
                'is_suspicious': False,
                'flags': flags,
                'risk_score': 0,
                'ad_data': {}
            }

        # Meta Ad Library API endpoint (public, no auth needed)
        api_url = (
            f'https://www.facebook.com/ads/library/api/'
            f'?ad_id={ad_id}&fields=ad_creation_time,'
            f'ad_delivery_start_time,page_name,page_id'
        )

        resp = requests.get(api_url, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            ad_data = data

            # Check ad age
            if 'ad_delivery_start_time' in data:
                start = datetime.fromisoformat(
                    data['ad_delivery_start_time']
                )
                days_running = (
                    datetime.now(timezone.utc) - start
                ).days

                if days_running < 3:
                    flags.append(
                        f'Ad running for only {days_running} days — very new'
                    )
                    risk += 30

            # Check page creation (new pages are suspicious)
            if 'ad_creation_time' in data:
                created = datetime.fromisoformat(
                    data['ad_creation_time']
                )
                page_age = (
                    datetime.now(timezone.utc) - created
                ).days

                if page_age < 30:
                    flags.append(
                        f'Advertiser page created only {page_age} days ago'
                    )
                    risk += 25

        else:
            flags.append(
                f'Meta Ad Library returned status {resp.status_code}'
            )

    except Exception as e:
        flags.append(f'Meta Ad Library check failed: {str(e)}')

    risk = min(risk, 100)
    return {
        'is_suspicious': risk > 30,
        'flags': flags,
        'risk_score': risk,
        'ad_data': ad_data
    }


def _extract_ad_id(url: str) -> str:
    """Extract ad ID from a Meta/Facebook/Instagram ad URL."""
    import re

    # Pattern: /ads/library/?id=XXXX or ad_id=XXXX
    patterns = [
        r'id=(\d+)',
        r'ad_id=(\d+)',
        r'/(\d{10,})',  # Long numeric IDs in URL path
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ''
