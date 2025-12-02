/**
 * Database type definitions for Supabase.
 *
 * This is a placeholder that should be replaced with generated types
 * from your Supabase project using:
 * npx supabase gen types typescript --project-id <project-id> > types.ts
 *
 * For now, we use a minimal type definition.
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: Record<string, never>; // Placeholder - tables are managed by FastAPI backend
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
  };
}
