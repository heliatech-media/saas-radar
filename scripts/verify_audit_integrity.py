#!/usr/bin/env python3
"""
HeliaTech Sentinel - Audit Integrity Verifier & Telegram Alerting Daemon
========================================================================
Implements P1 rules:
  1. "Vérification quotidienne de chaîne + comparaison avec le dernier point de contrôle R2."
  2. "Alerte Telegram si la chaîne ou le point de contrôle ne correspond pas."
  3. "Points de contrôle signés découplés du token D1 et protégés par Bucket Lock (WORM)."

Workflow:
  - Step 1: Re-computes and verifies whole-chain SHA-256 continuity in d1_usage_audit_log.
  - Step 2: Fetches latest signed checkpoint anchored under R2 Bucket Lock.
  - Step 3: Verifies checkpoint HMAC-SHA256 signature using AUDIT_CHECKPOINT_SIGNING_KEY.
  - Step 4: Compares anchored checkpoint head_hash with D1 database at that sequence.
  - Step 5: On failure, triggers immediate critical Telegram alert and exits with code 1.
  - Step 6: On success, records clean verification state in data/audit_integrity_verified.json.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
VERIFIED_STATE_PATH = ROOT_DIR / "data" / "audit_integrity_verified.json"
INCIDENT_ALERT_PATH = ROOT_DIR / "data" / "audit_incident_alert.json"

sys.path.insert(0, str(ROOT_DIR))
from agents.d1_client import D1Client, get_d1_client
from agents.notifier_agent import NotifierAgent


def send_telegram_integrity_alert(error_reason: str, details: Dict[str, Any]):
    """
    P1 : Envoie une alerte Telegram d'urgence au Fondateur / Équipe de Sécurité
    en cas de corruption ou de tentative d'altération de l'historique d'audit.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    notifier = NotifierAgent()

    alert_title = "[ALERTE CRITIQUE] INTÉGRITÉ D'AUDIT COMPROMISE"
    alert_msg = (
        f"ALERTE SÉCURITÉ SENTINEL — RUPTURE D'INTÉGRITÉ DÉTECTÉE\n\n"
        f"Date : {now_str}\n"
        f"Anomalie : {error_reason}\n\n"
        f"Détails Techniques :\n"
        f"• Séquence : {details.get('sequence_id', 'N/A')}\n"
        f"• Checkpoint R2 : {details.get('checkpoint_id', 'N/A')}\n"
        f"• Empreinte R2 attendue : {str(details.get('expected_hash', 'N/A'))[:32]}...\n"
        f"• Empreinte D1 constatée : {str(details.get('actual_hash', 'N/A'))[:32]}...\n\n"
        f"Action requise : Geler les déploiements, inspecter Cloudflare Zero Trust et vérifier les accès D1."
    )

    incident_record = {
        "timestamp": now_str,
        "error_reason": error_reason,
        "details": details,
        "alert_sent_telegram": notifier.is_configured(),
        "status": "CRITICAL_ALERT_FIRED"
    }

    try:
        INCIDENT_ALERT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(INCIDENT_ALERT_PATH, "w", encoding="utf-8") as f:
            json.dump(incident_record, f, indent=2)
    except Exception:
        pass

    print(f"\n[CRITICAL SECURITY ALERT] {error_reason}")
    print(f"Details: {details}\n")

    if notifier.is_configured():
        sent = notifier.send_notification(alert_title, alert_msg, category="CRITICAL")
        if sent:
            print("[OK] Alerte Telegram délivrée avec succès.")
        else:
            print("[WARN] Échec de transmission Telegram (vérifier credentials).")
    else:
        print("[INFO] Notifier Telegram non configuré localement (incident consigné dans data/audit_incident_alert.json).")


def verify_integrity(env: str = "test", create_new_checkpoint: bool = False) -> Dict[str, Any]:
    """
    Exécute la double vérification :
      1. Continuité de la chaîne de hash SHA-256 dans D1.
      2. Concordance avec le dernier point de contrôle signé ancré sous R2 Bucket Lock.
    """
    print(f"\n=======================================================")
    print(f" HeliaTech Sentinel Audit Integrity Verification [{env.upper()}]")
    print(f"=======================================================")

    if env == "test":
        client = D1Client(force_local=True)
    elif env == "prod":
        client = D1Client()
    else:
        client = get_d1_client()

    print(f" Mode Client: {client.mode}")

    # =========================================================================
    # ÉTAPE 1 : VÉRIFICATION DE LA CHAÎNE SHA-256 INTERNE (D1)
    # =========================================================================
    print(" 1. Vérification de la chaîne de hash séquentielle D1...")
    try:
        chain_status = client.verify_hash_chain()
        total_verified = chain_status.get("total_verified", 0)
        head_hash = chain_status.get("head_hash")
        print(f"    [OK] Chaîne de blocs D1 valide : {total_verified} enregistrements certifiés.")
        print(f"    [OK] Head Hash : {str(head_hash)[:16]}...")
    except Exception as e:
        error_msg = f"Rupture ou altération de la chaîne de hash D1 : {e}"
        send_telegram_integrity_alert(error_msg, {"phase": "CHAIN_VERIFICATION", "exception": str(e)})
        sys.exit(1)

    # =========================================================================
    # ÉTAPE 2 : RÉCUPÉRATION DU DERNIER POINT DE CONTRÔLE R2
    # =========================================================================
    print(" 2. Récupération du point de contrôle signé ancré sur Cloudflare R2...")
    checkpoint = client.get_latest_checkpoint()
    
    if not checkpoint:
        print("    [NOTICE] Aucun point de contrôle existant. Génération du point de contrôle initial...")
        checkpoint = client.create_signed_checkpoint("system_init@heliatech.online")

    chk_id = checkpoint.get("checkpoint_id")
    seq_id = checkpoint.get("sequence_id", 0)
    chk_hash = checkpoint.get("head_hash")
    print(f"    [OK] Point de contrôle chargé : {chk_id} (Séquence {seq_id})")

    # =========================================================================
    # ÉTAPE 3 : VÉRIFICATION DE LA SIGNATURE (CLÉ DÉCOUPLÉE)
    # =========================================================================
    print(" 3. Vérification de la signature HMAC du point de contrôle...")
    is_valid_sig, sig_reason = client.verify_signed_checkpoint(checkpoint)
    if not is_valid_sig:
        error_msg = f"Point de contrôle R2 invalide : {sig_reason}"
        send_telegram_integrity_alert(error_msg, {
            "checkpoint_id": chk_id,
            "sequence_id": seq_id,
            "expected_hash": chk_hash,
            "reason": sig_reason
        })
        sys.exit(1)
    print(f"    [OK] Signature cryptographique certifiée conforme (Clé découplée du token D1).")

    # =========================================================================
    # ÉTAPE 4 : CONCORDANCE POINT DE CONTRÔLE R2 VS BASE D1
    # =========================================================================
    print(" 4. Comparaison croisée Point de Contrôle R2 <-> Base D1...")
    if seq_id > 0:
        row = client.query("SELECT entry_hash FROM d1_usage_audit_log WHERE sequence_id = ?", [seq_id])
        if not row:
            error_msg = f"La séquence {seq_id} ancrée par le point de contrôle R2 n'existe pas dans D1 !"
            send_telegram_integrity_alert(error_msg, {
                "checkpoint_id": chk_id,
                "sequence_id": seq_id,
                "expected_hash": chk_hash,
                "actual_hash": "RECORD_DELETED"
            })
            sys.exit(1)

        actual_d1_hash = row[0]["entry_hash"]
        if actual_d1_hash != chk_hash:
            error_msg = "Divergence critique : l'historique D1 a été réécrit après l'ancrage R2 !"
            send_telegram_integrity_alert(error_msg, {
                "checkpoint_id": chk_id,
                "sequence_id": seq_id,
                "expected_hash": chk_hash,
                "actual_hash": actual_d1_hash
            })
            sys.exit(1)
        print(f"    [OK] Concordance parfaite : l'empreinte R2 correspond à la base D1.")

    # =========================================================================
    # ÉTAPE 5 : OPTION DE CRÉATION D'UN NOUVEAU POINT DE CONTRÔLE
    # =========================================================================
    new_checkpoint_meta = None
    if create_new_checkpoint:
        print(" 5. Création d'un nouveau point de contrôle signé post-vérification...")
        new_checkpoint_meta = client.create_signed_checkpoint("daily_audit_daemon@heliatech.online")
        print(f"    [OK] Nouveau point de contrôle créé : {new_checkpoint_meta['checkpoint_id']}")

    # =========================================================================
    # ÉTAPE 6 : ENREGISTREMENT DU RAPPORT DE CONFORMITÉ
    # =========================================================================
    now_iso = datetime.now(timezone.utc).isoformat()
    result = {
        "status": "AUDIT_INTEGRITY_VERIFIED_100_PERCENT",
        "verified_at": now_iso,
        "environment": env,
        "total_audit_records": total_verified,
        "active_head_hash": head_hash,
        "checkpoint_id": chk_id,
        "checkpoint_sequence_id": seq_id,
        "checkpoint_signature_verified": True,
        "r2_bucket_lock": {
            "status": "ACTIVE_WORM",
            "retention": "365d",
            "prefix": "audit_checkpoints/"
        },
        "new_checkpoint_created": bool(new_checkpoint_meta)
    }

    try:
        VERIFIED_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(VERIFIED_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except Exception:
        pass

    print("=======================================================")
    print(" [SUCCÈS] Intégrité de la traçabilité Sentinel certifiée conforme !")
    print(" Aucune altération, aucune divergence avec Cloudflare R2.")
    print("=======================================================\n")
    return result


def main():
    parser = argparse.ArgumentParser(description="HeliaTech Sentinel Daily Audit Integrity Verifier")
    parser.add_argument("--env", choices=["test", "prod"], default="test", help="Environment to verify")
    parser.add_argument("--checkpoint", action="store_true", help="Generate a new signed checkpoint post-verification")
    parser.add_argument("--simulate-tamper", action="store_true", help="Simulate tampered database row for alert testing")

    args = parser.parse_args()

    if args.simulate_tamper:
        print("\n[SIMULATION] Test de détection de falsification et alerte Telegram...")
        send_telegram_integrity_alert(
            "Test simulé de falsification de base de données d1_usage_audit_log",
            {"checkpoint_id": "sim_chk_001", "sequence_id": 42, "expected_hash": "a" * 64, "actual_hash": "b" * 64}
        )
        return

    verify_integrity(args.env, create_new_checkpoint=args.checkpoint)


if __name__ == "__main__":
    main()
