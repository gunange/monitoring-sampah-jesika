import * as utils from "@/utils";

export class OrderCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.order.findMany({
            include: {
               Meja: true,
               Pembayaran: true,
               Items: {
                  include: {
                     MenuItem: true,
                  },
               },
            },
         }),
      });
   }

   static async destroy(c: utils.Context): Promise<any> {
      const db = await utils.dbClient.order.delete({
         where: {
            id: Number(c.req.param("id")),
            
         },
      });

      if (db) {
         await utils.dbClient.meja.update({
            where: {
               nomor: db.mejaId,
            },
            data: {
               status: "TERSEDIA",
            },
         });
      }
      return c.json({
         data: db,
         message: "Data berhasil dihapus",
      });
   }
}
