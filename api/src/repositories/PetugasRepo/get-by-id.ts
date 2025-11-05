import * as utils from "@/utils";
export async function getById(id: number) {
   return await utils.dbClient.petugas.findFirstOrThrow({
      where: {
         id: id,
      },
   });
}
