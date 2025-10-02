import type { User, Role } from "@prisma/client";

export function auth(db?: User & { Role: Role }): any | null {
   if (!db) return null;

   // Exclude unwanted fields from User
   const { id, created_at, updated_at, password, role_id, ...cleanUser } = db;

   // Exclude unwanted fields from Role
   const { id: roleId, created_at: roleCreated, ...cleanRole } = db.Role;

   return {
      ...cleanUser,
      Role: cleanRole,
   };
}
