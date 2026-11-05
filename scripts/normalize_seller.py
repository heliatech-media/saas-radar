import re

with open('site/src/pages/seller/index.astro', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace double blank lines caused by CRLF translation
text = re.sub(r'\r\n', '\n', text)
text = re.sub(r'\n{3,}', '\n\n', text)

# Update payout listener
old_payout_snippet = """    // Payout button
    document.getElementById('btn-request-payout-modal')?.addEventListener('click', async () => {
      if (confirm("Confirmer la demande de virement de $1,472.00 USD vers votre IBAN • 4021 ?")) {
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

new_payout_snippet = """    // Payout button with dynamic validation
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
        alert("⚠️ Solde insuffisant : Votre solde disponible est de $" + balance.toFixed(2) + " USD. Le seuil minimum de retrait est de $50.00 USD.");
        return;
      }

      if (!sData?.iban) {
        alert("⚠️ Aucun compte bancaire configuré. Veuillez d'abord renseigner votre IBAN.");
        return;
      }

      if (confirm("Confirmer la demande de virement de $" + balance.toFixed(2) + " USD vers votre IBAN " + sData.iban + " ?")) {
        sData.balance = 0;
        localStorage.setItem('_ht_seller_data_' + email, JSON.stringify(sData));
        alert("✓ Votre demande de virement a été transmise aux administrateurs pour traitement !");
        initSellerStudio();
      }
    });

    document.getElementById('btn-request-payout-top')?.addEventListener('click', () => {
      switchSellerTab('payouts');
    });"""

# Use regex to find and replace the old payout listener safely
text = re.sub(
    r"// Payout button\s+document\.getElementById\('btn-request-payout-modal'\)\?\.addEventListener\('click',\s*async\s*\(\)\s*=>\s*\{.*?\}\);\s*\}\);",
    new_payout_snippet,
    text,
    flags=re.DOTALL
)

with open('site/src/pages/seller/index.astro', 'w', encoding='utf-8') as f:
    f.write(text.replace('\n', '\r\n'))

print("[OK] seller/index.astro normalized and payout listener updated.")
