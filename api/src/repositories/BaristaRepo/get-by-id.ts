import * as utils from "@/utils";
export async function getById(id: number) {
   return await utils.dbClient.barista.findFirstOrThrow({
      where: {
         id: id,
      },
   });
}
