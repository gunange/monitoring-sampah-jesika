import * as utils from "@/utils";

export class ExampleCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: [],
      });
   }
   static async store(c: utils.Context): Promise<any> {
      return c.json({
         data: "OK",
         message : "Data berhasil ditambahkan"
      });
   }
   static async update(c: utils.Context): Promise<any> {
      return c.json({
         data: "OK",
         message : "Data berhasil diperbahrui"
      });
   }
   static async destroy(c: utils.Context): Promise<any> {
      return c.json({
         data: "OK",
         message : "Data berhasil dihapus"
      });
   }

}
