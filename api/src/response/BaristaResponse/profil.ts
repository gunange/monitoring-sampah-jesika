import type { BaristaProfile } from "@/types/BaristaTypes";

export function profil(db: BaristaProfile) {
   if (!db) return {};

   // hapus properti yang tidak diinginkan
   const { id, userId, User, ...rest } = db;

   // hapus properti yang tidak diinginkan dari User
   const {
      id: usersId,
      role_id,
      password,
      remember_token,
      created_at: userCreated,
      updated_at: userUpdated,
      Role,
      ...userRest
   } = User ?? {};

   return {
      ...rest,

      User: {
         ...userRest,
         role_label: Role?.label,
         role: Role?.role,
      },
   };
}
