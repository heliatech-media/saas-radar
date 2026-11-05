/**
 * HELIATECH SENTINEL ANTI-SCAM & WORKFLOW SECURITY ENGINE
 * Forensic Inspection for n8n, Make, Airtable and AI Workflow Files
 */

export interface AntiScamAuditResult {
  passed: boolean;
  score: number; // 0 to 100
  issues: string[];
  detectedSecrets: string[];
  nodesCount: number;
  ecosystem: 'n8n' | 'make' | 'airtable' | 'cursor' | 'generic';
}

const SECRET_PATTERNS = [
  { name: 'OpenAI API Key', regex: /sk-[a-zA-Z0-9]{32,64}/g },
  { name: 'Stripe Live Secret Key', regex: /sk_live_[0-9a-zA-Z]{24,34}/g },
  { name: 'Stripe Restricted Key', regex: /rk_live_[0-9a-zA-Z]{24,34}/g },
  { name: 'GitHub Personal Access Token', regex: /ghp_[0-9a-zA-Z]{36}/g },
  { name: 'Database Connection String', regex: /(postgres|mysql|mongodb\+srv):\/\/[^:\s]+:[^@\s]+@[^\s/]+/gi },
  { name: 'Bearer Token Header', regex: /Bearer\s+["']?[a-zA-Z0-9_\-\.]{20,}["']?/gi },
  { name: 'Private Key Block', regex: /-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----/g },
  { name: 'Slack Bot Token', regex: /xoxb-[0-9]{11,13}-[0-9]{11,13}-[a-zA-Z0-9]{24}/g },
  { name: 'Telegram Bot Token', regex: /[0-9]{8,10}:[a-zA-Z0-9_-]{35}/g }
];

const SUSPICIOUS_URL_PATTERNS = [
  /https?:\/\/(www\.)?(bit\.ly|tinyurl\.com|ngrok\.io|ngrok-free\.app|webhook\.site)\/[^\s"']+/gi,
  /https?:\/\/discord(app)?\.com\/api\/webhooks\/[^\s"']+/gi
];

const CODE_INJECTION_PATTERNS = [
  /\beval\s*\(/gi,
  /\bexec\s*\(/gi,
  /\bchild_process\b/gi,
  /\bFunction\s*\(\s*["']return\s+this/gi,
  /\bprocess\.env\b/gi
];

/**
 * Audits a workflow file payload (.json, .txt, .sql) before publication.
 */
export function auditWorkflowPayload(rawContent: string, fileName = 'workflow.json'): AntiScamAuditResult {
  const issues: string[] = [];
  const detectedSecrets: string[] = [];
  let score = 100;
  let nodesCount = 0;
  let ecosystem: AntiScamAuditResult['ecosystem'] = 'generic';

  // 1. Secret Leakage Detection
  for (const { name, regex } of SECRET_PATTERNS) {
    const matches = rawContent.match(regex);
    if (matches && matches.length > 0) {
      detectedSecrets.push(`${name} (${matches.length} occurrence(s))`);
      issues.push(`Secret critique détecté : ${name}. Les clés privées doivent être remplacées par des variables d'environnement.`);
      score -= 35;
    }
  }

  // 2. Phishing & Suspicious Webhook Detection
  for (const regex of SUSPICIOUS_URL_PATTERNS) {
    if (regex.test(rawContent)) {
      issues.push("Lien masqué suspect ou webhook externe non autorisé détecté (bit.ly, ngrok, discord).");
      score -= 25;
      break;
    }
  }

  // 3. Malicious Code Injection
  for (const regex of CODE_INJECTION_PATTERNS) {
    if (regex.test(rawContent)) {
      issues.push("Instruction de code dangereux ou injection potentielle détectée (eval/exec).");
      score -= 30;
      break;
    }
  }

  // 4. Structural AST Validation (for JSON files)
  if (fileName.endsWith('.json')) {
    try {
      const parsed = JSON.parse(rawContent);

      // n8n detection
      if (Array.isArray(parsed.nodes)) {
        ecosystem = 'n8n';
        nodesCount = parsed.nodes.length;
        if (nodesCount < 2) {
          issues.push("Structure n8n incomplète : un workflow doit comporter au moins 2 nœuds interconnectés.");
          score -= 20;
        }
        if (!parsed.connections || Object.keys(parsed.connections).length === 0) {
          issues.push("Nœuds orphelins : le workflow ne possède aucune connexion logique active.");
          score -= 15;
        }
      }
      // Make.com detection
      else if (Array.isArray(parsed.blueprint?.nodes) || Array.isArray(parsed.flow)) {
        ecosystem = 'make';
        const flow = parsed.blueprint?.nodes || parsed.flow;
        nodesCount = flow.length;
        if (nodesCount < 2) {
          issues.push("Structure Make.com incomplète : le blueprint doit comporter au moins 2 modules.");
          score -= 20;
        }
      }
      // Cursor AI Rules
      else if (Array.isArray(parsed.rules) || typeof parsed.cursorrules === 'string') {
        ecosystem = 'cursor';
        nodesCount = Array.isArray(parsed.rules) ? parsed.rules.length : 1;
      }
      // Airtable / Generic JSON
      else {
        ecosystem = 'airtable';
        nodesCount = Object.keys(parsed).length;
      }
    } catch (e: any) {
      issues.push(`Fichier JSON corrompu ou invalide : ${e.message}`);
      score = 0;
    }
  }

  const finalScore = Math.max(0, Math.min(100, score));
  const passed = finalScore >= 80 && detectedSecrets.length === 0;

  return {
    passed,
    score: finalScore,
    issues,
    detectedSecrets,
    nodesCount,
    ecosystem
  };
}

/**
 * Sanitizes a user-submitted filename to prevent directory traversal.
 */
export function sanitizeFileName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9._-]/g, '_')
    .replace(/_{2,}/g, '_')
    .slice(0, 100);
}
