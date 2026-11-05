with open('site/src/pages/templates/[slug].astro', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    // Free Download / Add to Library Handler
    document.getElementById('free-download-btn')?.addEventListener('click', () => {
      alert("🎁 [Template Gratuit Ajouté !] : Ce blueprint a été ajouté avec succès à votre bibliothèque. Vous pouvez télécharger le package immédiatement depuis votre Espace Client.");
      window.location.href = '/dashboard/';
    });

    // Buy Button: Validates and Redirects
    document.getElementById('checkout-btn')?.addEventListener('click', () => {
      alert("⚡ [Licence Commerciale Activée] : Votre commande a été traitée en mode staging sécurisé. Le blueprint et votre clé de licence sont prêts dans votre Espace Client.");
      window.location.href = '/dashboard/';
    });"""

replacement = """    // Helper to store in buyer's personal library
    function addBlueprintToLibrary(title, slug, price, ecosystem) {
      let session = null;
      try {
        session = JSON.parse(localStorage.getItem('_ht_user_session'));
      } catch(e) {}

      const email = session?.email || 'guest';
      const libKey = '_ht_buyer_library_' + email;
      let lib = [];
      try {
        lib = JSON.parse(localStorage.getItem(libKey) || '[]');
      } catch(e) {}

      if (!lib.some(item => item.slug === slug)) {
        lib.unshift({
          title: title,
          slug: slug,
          price: price,
          ecosystem: ecosystem,
          version: '1.0.0',
          licenseKey: 'HLT-LIC-' + Math.random().toString(36).slice(2, 8).toUpperCase() + '-PRO-2026',
          purchaseDate: new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }),
          downloads: 1
        });
        localStorage.setItem(libKey, JSON.stringify(lib));
      }
    }

    // Free Download / Add to Library Handler
    document.getElementById('free-download-btn')?.addEventListener('click', () => {
      addBlueprintToLibrary(
        `{template.title}`,
        `{template.slug}`,
        0,
        `{template.ecosystem}`
      );
      alert("🎁 [Template Gratuit Ajouté !] : Ce blueprint a été ajouté avec succès à votre bibliothèque personnelle. Vous pouvez télécharger le package immédiatement depuis votre Espace Client.");
      window.location.href = '/dashboard/';
    });

    // Buy Button: Validates and Redirects
    document.getElementById('checkout-btn')?.addEventListener('click', () => {
      addBlueprintToLibrary(
        `{template.title}`,
        `{template.slug}`,
        Number(`{template.price_usd || 49}`),
        `{template.ecosystem}`
      );
      alert("⚡ [Licence Commerciale Activée] : Votre commande a été traitée en mode staging sécurisé. Le blueprint et votre clé de licence sont prêts dans votre Espace Client.");
      window.location.href = '/dashboard/';
    });"""

content_norm = content.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

assert target_norm in content_norm, "Target not found in templates/[slug].astro"
content_norm = content_norm.replace(target_norm, replacement_norm)

with open('site/src/pages/templates/[slug].astro', 'w', encoding='utf-8') as f:
    f.write(content_norm.replace('\n', '\r\n'))

print("[OK] templates/[slug].astro updated with addBlueprintToLibrary.")
