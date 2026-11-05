/**
 * HELIATECH DIGITAL TEMPLATES MARKETPLACE
 * Server-Side Role-Based Access Control (RBAC) & Ownership Guards
 */

import type { UserRole } from './types';

export interface AuthContext {
  userId: string;
  email: string;
  role: UserRole;
  sellerId?: string; // Set if user is an approved seller
}

export class PermissionError extends Error {
  status: number;
  constructor(message: string, status = 403) {
    super(message);
    this.name = 'PermissionError';
    this.status = status;
  }
}

/**
 * Validates that an authenticated session exists.
 */
export function requireAuth(ctx?: AuthContext | null): asserts ctx is AuthContext {
  if (!ctx || !ctx.userId) {
    throw new PermissionError("Authentification requise. Veuillez vous connecter.", 401);
  }
}

/**
 * Validates that the user has at least one of the specified roles.
 */
export function requireRole(ctx: AuthContext, allowedRoles: UserRole[]): void {
  requireAuth(ctx);
  if (!allowedRoles.includes(ctx.role)) {
    throw new PermissionError(`Accès refusé. Rôle insuffisant (${ctx.role}).`);
  }
}

/**
 * Validates that the user is an administrator or super-administrator.
 */
export function requireAdmin(ctx: AuthContext): void {
  requireRole(ctx, ['ADMIN', 'SUPER_ADMIN']);
}

/**
 * Validates that the user is an approved seller or administrator.
 */
export function requireSeller(ctx: AuthContext): void {
  requireRole(ctx, ['SELLER', 'ADMIN', 'SUPER_ADMIN']);
  if (ctx.role === 'SELLER' && !ctx.sellerId) {
    throw new PermissionError("Profil vendeur introuvable ou non approuvé.");
  }
}

/**
 * Validates resource ownership for Sellers (can only view/edit their own products).
 */
export function assertProductOwnership(ctx: AuthContext, productSellerId: string): void {
  requireAuth(ctx);
  if (ctx.role === 'ADMIN' || ctx.role === 'SUPER_ADMIN') {
    return; // Admins have oversight access
  }
  if (ctx.role !== 'SELLER' || ctx.sellerId !== productSellerId) {
    throw new PermissionError("Interdit : Vous ne pouvez modifier que vos propres produits.");
  }
}

/**
 * Validates resource ownership for Buyers (can only download their own purchased products).
 */
export function assertPurchaseOwnership(ctx: AuthContext, purchaseUserId: string): void {
  requireAuth(ctx);
  if (ctx.userId !== purchaseUserId && ctx.role !== 'SUPER_ADMIN') {
    throw new PermissionError("Interdit : Vous ne pouvez accéder qu'aux fichiers de votre bibliothèque personnelle.");
  }
}
