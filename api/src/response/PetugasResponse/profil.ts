import type { PetugasProfile } from "@/types/PetugasTypes";

export function profil(db: PetugasProfile) {
   if (!db) return {};

   const { id, userId, User, ...rest } = db;

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
