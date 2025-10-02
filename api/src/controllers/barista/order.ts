import { UserService } from "@/services/UserService";
import * as utils from "@/utils";
import { OrderValidate } from "@/validators/OrderValidate";
import { PembayaranValidate } from "@/validators/PembayaranValidate";

const include = {
   Meja: true,
   Pembayaran: true,
   Items: {
      include: {
         MenuItem: true,
      },
   },
};

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

   static async orderItem(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.orderItem.findMany({
            where: {
               orderId: Number(c.req.param("orderId")),
            },
            include: {
               MenuItem: true,
            },
         }),
      });
   }

   static async upStatus(c: utils.Context): Promise<any> {
      const data = await OrderValidate.upStatus(c);

      return c.json({
         data: await utils.dbClient.order.update({
            where: {
               id: Number(c.req.param("id")),
            },
            data,
            include,
         }),
         message: "Status Diubah",
      });
   }
   static async bayar(c: utils.Context): Promise<any> {
      const data = await PembayaranValidate.upsert(c);
      const user = UserService.barista.store.profil;

      data.orderId = Number(c.req.param("orderId"));

      const pay = await utils.dbClient.pembayaran.upsert({
         where: {
            orderId: Number(c.req.param("orderId")),
         },
         create: data,
         update: data,
      });

      const db = await utils.dbClient.order.update({
         where: {
            id: pay.orderId,
         },
         data: {
            status: "PAID",
            baristaId: user.id,
         },
         include,
      });

      await utils.dbClient.meja.update({
         where: {
            id: db.mejaId,
         },
         data: {
            status: "TERSEDIA",
         },
      });

      return c.json({
         data: db,
         message: "Pembayaran berhasil",
      });
   }

   static async destroy(c: utils.Context): Promise<any> {
      const db = await utils.dbClient.order.delete({
         where: {
            id: Number(c.req.param("id")),
            AND: {
               status: {
                  in: ["PENDING", "PREPARING"],
               },
            },
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
