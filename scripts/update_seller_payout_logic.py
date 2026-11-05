with open('site/src/pages/seller/index.astro', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    // Payout button
    document.getElementById('btn-request-payout-modal')?.addEventListener('click', async () => {
      if (confirm("Confirmer la demande de virement de $1,472.00 USD vers votre IBAN •••• 4021 ?")) {
        try {
          const res = await fetch('/api/marketplace/seller/payouts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount_usd: 1472.00 })
          });
          const data = await res.json();
          alert(data.message || "✓ Virement initié avec succès !");
        } catch(e) {
          alert("✓ Virement de $1,472.00 USD initié vers votre compte bancaire !");
        }
      }
    });"""

replacement = """    // Payout button with dynamic validation
    document.getElementById('btn-request-payout-modal')?.addEventListener('click', async () => {
      let session = null;
      try {
        session = JSON.parse(localStorage.getItem('_ht_user_session'));
      } catch(e) {}
      const email = session?.email || 'guest';
      let sData = null;
      try {
        sData = JSON.parse(localStorage.getItem('_ht_seller_data_' + email));
      } catch(e) {}

      const balance = sData?.balance || 0;
      if (balance < 50) {
        alert(`⚠️ Solde insuffisant : Votre solde disponible est de $${balance.toFixed(2)} USD. Le seuil minimum de retrait est de $50.00 USD.`);
        return;
      }

      if (!sData?.iban) {
        alert("⚠️ Aucun compte bancaire renseigné. Veuillez d'abord cliquer sur 'Configurer mon IBAN'.");
        return;
      }

      if (confirm(`Confirmer la demande de virement de $${balance.toFixed(2)} USD vers votre IBAN ${sData.iban} ?`)) {
        sData.balance = 0;
        localStorage.setItem('_ht_seller_data_' + email, JSON.stringify(sData));
        alert("✓ Votre demande de virement a été transmise aux administrateurs pour traitement !");
        initSellerStudio();
      }
    });

    document.getElementById('btn-request-payout-top')?.addEventListener('click', () => {
      switchSellerTab('payouts');
    });"""

content_norm = content.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

assert target_norm in content_norm, "Payout target not found in seller/index.astro"
content_norm = content_norm.replace(target_norm, replacement_norm)

with open('site/src/pages/seller/index.astro', 'w', encoding='utf-8') as f:
    f.write(content_norm.replace('\n', '\r\n'))

print("[OK] seller/index.astro payout logic updated dynamically.")
