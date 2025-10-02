import { UsersRepo } from "@/repositories";
import * as utils from "@/utils";
import { BaristaValidate } from "@/validators/BaristaValidate";
import { UserValidate } from "@/validators/UserValidate";

const role_id = 2;
const includeData = {
   User: {
      select: {
         username: true,
      },
   },
};

export class BaristaCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.barista.findMany({
            orderBy: {
               id: "desc",
            },
            include: {
               User: {
                  select: {
                     username: true,
                  },
               },
            },
         }),
      });
   }
   static async store(c: utils.Context): Promise<any> {
      const data = await BaristaValidate.upsert(c);
      const dataUser = await UserValidate.registrasiUsernameOnly(c);

      const username = dataUser.username;
      const user = await UsersRepo.create({
         username: username,
         password: username,
         role_id: role_id,
      });

      data.userId = user.id;
      return c.json({
         data: await utils.dbClient.barista.create({
            data: data,
            include : includeData
         }),

         message: "Data berhasil ditambahkan",
      });
   }
   static async update(c: utils.Context): Promise<any> {
      const data = await BaristaValidate.upsert(c);
      return c.json({
         data: await utils.dbClient.barista.update({
            where: {
               id: Number(c.req.param("id")),
            },
            data,
            include : includeData
         }),
         message: "Data berhasil diperbahrui",
      });
   }
   static async resetPassword(c: utils.Context): Promise<any> {
      const barista = await utils.dbClient.barista.findFirstOrThrow({
         where: {
            id: Number(c.req.param("id")),
         },
         include: includeData,
      });

      const { data, message } = await UsersRepo.resetPassword(
         c,
         barista.userId
      );

      return c.json({
         data: data,
         message: message,
      });
   }

   static async destroy(c: utils.Context): Promise<any> {
      const data = await utils.dbClient.barista.findFirstOrThrow({
         where: {
            id: Number(c.req.param("id")),
         },
         include: includeData,
      });
      await UsersRepo.destroy({
         id: data.userId,
         role_id: role_id,
      });
      return c.json({
         data: data,
         message: "Data berhasil dihapus",
      });
   }
}
