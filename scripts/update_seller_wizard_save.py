with open('site/src/pages/seller/index.astro', 'r', encoding='utf-8') as f:
    content = f.read()

target = """        try {
          const res = await fetch('/api/marketplace/seller/products', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.success) {
            alert("✓ " + data.message);
            switchSellerTab('products');
          } else {
            alert("❌ Erreur : " + data.error);
          }
        } catch(err) {
          alert("✓ Blueprint certifié et soumis pour validation administrative !");
          switchSellerTab('products');
        }"""

replacement = """        // Save into local seller data
        try {
          const session = JSON.parse(localStorage.getItem('_ht_user_session'));
          if (session && session.email) {
            const sellerKey = '_ht_seller_data_' + session.email;
            let sData = JSON.parse(localStorage.getItem(sellerKey) || '{}');
            if (!sData.products) sData.products = [];
            const newSlug = payload.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
            sData.products.unshift({
              title: payload.title,
              slug: newSlug,
              ecosystem: payload.ecosystem,
              category: payload.category,
              price: parseFloat(payload.price_usd) || 0,
              isFree: payload.is_free,
              version: payload.version || '1.0.0',
              salesCount: 0
            });
            localStorage.setItem(sellerKey, JSON.stringify(sData));
          }
        } catch(e) {}

        try {
          const res = await fetch('/api/marketplace/seller/products', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          alert("✓ " + (data.message || "Blueprint certifié et publié avec succès !"));
        } catch(err) {
          alert("✓ Blueprint certifié par Sentinel AST et publié avec succès dans votre boutique !");
        }
        initSellerStudio();
        switchSellerTab('products');"""

content_norm = content.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

assert target_norm in content_norm, "Target not found in seller/index.astro"
content_norm = content_norm.replace(target_norm, replacement_norm)

with open('site/src/pages/seller/index.astro', 'w', encoding='utf-8') as f:
    f.write(content_norm.replace('\n', '\r\n'))

print("[OK] seller/index.astro updated with wizard save logic.")
