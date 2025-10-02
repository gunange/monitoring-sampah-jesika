import * as util from "@/utils";
import type { User } from "@prisma/client";
export async function destroy({
   id,
   role_id,
}: {
   id: number;
   role_id: number;
}): Promise<User> {
   return await util.dbClient.user.delete({
      where: {
         id: id,
         role_id: role_id,
      },
   });
}
