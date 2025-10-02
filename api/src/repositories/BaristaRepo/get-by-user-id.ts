import prismaClient from "@/app/database";
import type { BaristaProfile } from "@/types/BaristaTypes";

export async function getByUserId(userId: number): Promise<BaristaProfile> {
   return await prismaClient.barista
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
         err.meta.message = "Tidak menemukan user barista";
         throw err;
      });
}
