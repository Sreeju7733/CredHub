import os
import requests
import yaml
from slugify import slugify

# Configuration
CREDLY_USER_ID = os.getenv('CREDLY_USER_ID')
BADGES_DIR = '_badges'
DATA_FILE = '_data/badges.yml'

def fetch_credly_badges():
    """Fetch badges from Credly API"""
    url = f'https://www.credly.com/users/{CREDLY_USER_ID}/badges.json'
    response = requests.get(url)
    return response.json().get('data', []) if response.status_code == 200 else []

def transform_badge(credly_badge):
    """Transform Credly data to our schema"""
    template = credly_badge.get('badge_template', {})
    issuer = template.get('issuer', {})
    return {
        'title': template.get('name', ''),
        'image': template.get('image_url', ''),
        'issued': credly_badge.get('issued_at', '')[:10],  # Get YYYY-MM-DD
        'verify_url': credly_badge.get('public_url', ''),
        'issuer': issuer.get('name', ''),
        'description': template.get('description', ''),
        'tags': [skill['name'] for skill in template.get('skills', [])]
    }

def write_badge_file(badge_data):
    """Write individual badge markdown file"""
    slug = slugify(badge_data['title'])
    filename = f"{BADGES_DIR}/{slug}.md"

    frontmatter = {
        'layout': 'badge',
        'title': badge_data['title'],
        'image': badge_data['image'],
        'issued': badge_data['issued'],
        'verify_url': badge_data['verify_url'],
        'issuer': badge_data['issuer'],
        'description': badge_data['description'],
        'tags': badge_data['tags']
    }

    content = f"""---
{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip()}
---

## About this badge

{badge_data['description']}

## Skills Demonstrated

{', '.join(badge_data['tags'])}

[Verify this credential]({badge_data['verify_url']}){{: .btn .btn-primary}}
"""

    with open(filename, 'w') as f:
        f.write(content)

    return slug

def update_badges_data(badges, slugs):
    """Update the _data/badges.yml file"""
    data = []
    for i, badge in enumerate(badges):
        data.append({
            'title': badge['title'],
            'image': badge['image'],
            'issued': badge['issued'],
            'url': f"/badges/{slugs[i]}/",  # Jekyll will output to /badges/slug/
            'tags': badge['tags']
        })

    with open(DATA_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def main():
    # Create badges directory if not exists
    os.makedirs(BADGES_DIR, exist_ok=True)

    # Fetch badges from Credly
    credly_badges = fetch_credly_badges()
    transformed_badges = [transform_badge(b) for b in credly_badges]

    # Write each badge to a markdown file and collect slugs
    slugs = []
    for badge in transformed_badges:
        slug = write_badge_file(badge)
        slugs.append(slug)

    # Update the _data/badges.yml file
    update_badges_data(transformed_badges, slugs)
    print(f"Successfully updated {len(transformed_badges)} badges")

if __name__ == '__main__':
    main()
