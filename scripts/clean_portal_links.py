import os

files_to_update = [
    ('site/src/layouts/Layout.astro', [
        ('href="/portal"', 'href="/dashboard/"'),
        ('href="/portal/"', 'href="/dashboard/"'),
    ]),
    ('site/src/pages/creator/[slug].astro', [
        ('(/portal/)', '(/dashboard/)'),
        ("window.location.href = '/portal/';", "window.location.href = '/dashboard/';"),
    ]),
    ('site/src/pages/dashboard/index.astro', [
        ('href="/portal/"', 'href="/seller/"'),
        ('Hub Portal', 'Studio Vendeur'),
    ]),
    ('site/src/pages/sell/index.astro', [
        ('href="/portal/"', 'href="/seller/"'),
        ('Mon Espace Client (/portal)', 'Mon Studio Vendeur (/seller)'),
    ]),
    ('site/src/pages/templates/[slug].astro', [
        ("window.location.href = '/portal/';", "window.location.href = '/dashboard/';"),
    ]),
    ('site/src/pages/templates/index.astro', [
        ('href="/portal/"', 'href="/dashboard/"'),
        ('Mon Espace (/portal)', 'Mon Dashboard (/dashboard)'),
        ('Espace Client (/portal)', 'Mon Dashboard (/dashboard)'),
    ]),
]

for file_path, replacements in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        original = content
        for target, repl in replacements:
            content = content.replace(target, repl)
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'[UPDATED] {file_path}')
        else:
            print(f'[NO CHANGE] {file_path}')
