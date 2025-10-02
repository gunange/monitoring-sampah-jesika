import * as utils from "@/utils";
import { OrderItemValidate } from "@/validators/OrderItemValidate";
import { WsService } from "@/services/WsService";
import { wsResponse } from "@/response/WsSocketResponse";

const include = {
   Meja: true,
   Items: {
      include: {
         MenuItem: true,
      },
   },
};

export class OrderCtrl {
   static async index(c: utils.Context): Promise<any> {
      let db = await utils.dbClient.order.findFirst({
         where: {
            mejaId: Number(c.req.param("mejaId")),
            status: {
               in: ["PENDING", "PREPARING"],
            },
         },
         include: {
            Meja: true,
            Items: {
               include: {
                  MenuItem: true,
               },
            },
         },
      });

      if (!db) {
         db = await utils.dbClient.order.create({
            data: {
               mejaId: Number(c.req.param("mejaId")),
            },
            include,
         });
      }
      await utils.dbClient.meja.update({
         where: {
            id: Number(c.req.param("mejaId")),
         },
         data: {
            status: "DIPESAN",
         },
      });
      return c.json({
         data: db,
      });
   }
   static async orderItem(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.orderItem.findMany({
            where: {
               orderId: Number(c.req.param("orderId")),
            },
            include: {
               MenuItem: true,
               Order: {
                  include: {
                     Meja: true,
                  },
               },
            },
         }),
      });
   }

   static async store(c: utils.Context): Promise<any> {
      const data = await OrderItemValidate.store(c);

      const db = await utils.dbClient.orderItem.create({
         data,
         include: {
            MenuItem: true,
            Order: {
               include: {
                  Meja: true,
               },
            },
         },
      });

      for (const client of WsService.getClientsByRole([2])) {
         await client.send(
            wsResponse.add({
               data: db,
               message: `Pesanan dengan meja ${db.Order.Meja.nomor} membuat pesanan baru`,
               path: "order",
            })
         );
         
      }

      return c.json({
         data: db,
         message: "Data berhasil ditambahkan",
      });
   }

   static async update(c: utils.Context): Promise<any> {
      const data = await OrderItemValidate.update(c);
      const db = await utils.dbClient.orderItem.update({
         where: {
            id: Number(c.req.param("orderItemId")),
         },
         data,
         include: {
            MenuItem: true,
            Order: {
               include: {
                  Meja: true,
               },
            },
         },
      });

      for (const client of WsService.getClientsByRole([2])) {
         await client.send(
            wsResponse.modified({
               data: db,
               message: `Pesanan dengan meja ${db.Order.Meja.nomor} memperbahrui pesanannya`,
               path: "order",
            })
         );
      }

      return c.json({
         data: db,
         message: "Data berhasil diperbahrui",
      });
   }

   static async destroy(c: utils.Context): Promise<any> {
      const db = await utils.dbClient.orderItem.findFirstOrThrow({
         where: {
            id: Number(c.req.param("orderItemId")),
         },
         include: {
            MenuItem: true,
            Order: {
               include: {
                  Meja: true,
               },
            },
         },
      });

      if (db.Order.status !== "PENDING") {
         throw new utils.HTTPException(403, {
            message:
               "Pesanan sedang diproses atau sudah selesai, anda tidak dapat menghapusnya",
         });
      }

      const dbDrop = await utils.dbClient.orderItem.delete({
         where: {
            id: db.id,
         },
      });

      for (const client of WsService.getClientsByRole([2])) {
         await client.send(
            wsResponse.delete({
               data: dbDrop,
               message: `Pesanan dengan meja ${db.Order.Meja.nomor} menghapus pesannya`,
               path: "order",
            })
         );
      }

      return c.json({
         data: dbDrop,
         message: "Data berhasil dihapus",
      });
   }
}
