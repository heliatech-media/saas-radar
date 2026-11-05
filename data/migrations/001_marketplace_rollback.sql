-- ============================================================================
-- HELIATECH DIGITAL TEMPLATES MARKETPLACE — ROLLBACK SCRIPT FOR MIGRATION 001
-- Safe Reversible Teardown of Marketplace Tables
-- ============================================================================

DROP TRIGGER IF EXISTS trg_tickets_upd ON public.support_tickets;
DROP TRIGGER IF EXISTS trg_payouts_upd ON public.seller_payouts;
DROP TRIGGER IF EXISTS trg_bundles_upd ON public.product_bundles;
DROP TRIGGER IF EXISTS trg_orders_upd ON public.orders;
DROP TRIGGER IF EXISTS trg_products_upd ON public.marketplace_products;
DROP TRIGGER IF EXISTS trg_categories_upd ON public.marketplace_categories;
DROP TRIGGER IF EXISTS trg_seller_apps_upd ON public.seller_applications;
DROP TRIGGER IF EXISTS trg_seller_profiles_upd ON public.seller_profiles;
DROP FUNCTION IF EXISTS public.handle_updated_at();

DROP TABLE IF EXISTS public.admin_audit_logs CASCADE;
DROP TABLE IF EXISTS public.marketplace_notifications CASCADE;
DROP TABLE IF EXISTS public.seller_notifications CASCADE;
DROP TABLE IF EXISTS public.support_messages CASCADE;
DROP TABLE IF EXISTS public.support_tickets CASCADE;
DROP TABLE IF EXISTS public.seller_payouts CASCADE;
DROP TABLE IF EXISTS public.promotion_redemptions CASCADE;
DROP TABLE IF EXISTS public.seller_promotions CASCADE;
DROP TABLE IF EXISTS public.bundle_items CASCADE;
DROP TABLE IF EXISTS public.product_bundles CASCADE;
DROP TABLE IF EXISTS public.payment_events CASCADE;
DROP TABLE IF EXISTS public.payments CASCADE;
DROP TABLE IF EXISTS public.purchases CASCADE;
DROP TABLE IF EXISTS public.order_items CASCADE;
DROP TABLE IF EXISTS public.orders CASCADE;
DROP TABLE IF EXISTS public.product_reports CASCADE;
DROP TABLE IF EXISTS public.review_replies CASCADE;
DROP TABLE IF EXISTS public.reviews CASCADE;
DROP TABLE IF EXISTS public.product_favorites CASCADE;
DROP TABLE IF EXISTS public.product_licenses CASCADE;
DROP TABLE IF EXISTS public.product_tag_relations CASCADE;
DROP TABLE IF EXISTS public.product_tags CASCADE;
DROP TABLE IF EXISTS public.product_versions CASCADE;
DROP TABLE IF EXISTS public.product_files CASCADE;
DROP TABLE IF EXISTS public.product_media CASCADE;
DROP TABLE IF EXISTS public.marketplace_products CASCADE;
DROP TABLE IF EXISTS public.marketplace_categories CASCADE;
DROP TABLE IF EXISTS public.seller_applications CASCADE;
DROP TABLE IF EXISTS public.seller_profiles CASCADE;
