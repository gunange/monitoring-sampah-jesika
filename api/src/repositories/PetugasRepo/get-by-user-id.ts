import prismaClient from "@/app/database";
import type { PetugasProfile } from "@/types/PetugasTypes";

export async function getByUserId(userId: number): Promise<PetugasProfile> {
   return await prismaClient.petugas
      .findFirstOrThrow({
         where: {
            userId: userId,
         },
         include: {
            User: {
               include: {
                  Role: true,
               },
            },
         },
      })
      .catch((err) => {
         err.meta.message = "Tidak menemukan user petugas";
         throw err;
      });
}
