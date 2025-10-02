import type { User, Role } from "@prisma/client";

type UserWithRole = User & { Role: Role };

type LoginResponse = {
   username: string;
   role: string;
   role_label: string;
   token: string;
};

export function login(db?: UserWithRole, token?: string): LoginResponse | null {
   if (!db || !token) return null;

   return {
      username: db.username,
      role: db.Role.role,
      role_label: db.Role.label,
      token,
   };
}
