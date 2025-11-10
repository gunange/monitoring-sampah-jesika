import * as utils from "@/utils";
import { Env } from "@/app/env";

export class MachineCtrl {
   static async index(c: utils.Context): Promise<any> {
      const data = await utils.requestApi.get(
         `http://${Env.ml_hostname}:${Env.ml_port}/machine-learning`,
         { name: "Machine Learning" }
      );
      return c.json(data);
   }
   static async start(c: utils.Context): Promise<any> {
      const data = await utils.requestApi.get(
         `http://${Env.ml_hostname}:${Env.ml_port}/machine-learning/start`,
         { name: "Machine Learning" }
      );
      return c.json(data);
   }
   static async stop(c: utils.Context): Promise<any> {
      const data = await utils.requestApi.get(
         `http://${Env.ml_hostname}:${Env.ml_port}/machine-learning/stop`,
         { name: "Machine Learning" }
      );
      return c.json(data);
   }
}
