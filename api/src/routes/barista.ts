import { Hono } from "hono";
import * as Middleware from "@/middleware";
import { BaristaRoute } from "@/controllers/barista";
import { UserService } from "@/services/UserService";
import { BaristaResponse } from "@/response/BaristaResponse";

export const barista = new Hono();

const userServiceStore = UserService.barista.store;

barista.use("/*", async (c, next) => {
   return userServiceStore.run(() =>
      Middleware.AuthBearer(
         c,
         async () => {
            await userServiceStore.setup(c);
            return next();
         },
         2
      )
   );
});

barista.get("", (c) =>
   c.json({
      data: BaristaResponse.profil(userServiceStore.profil),
   })
);

/* ---- meja ---- */
barista.get("/meja", BaristaRoute.MejaCtrl.index);
barista.post("/meja", BaristaRoute.MejaCtrl.upsert);
barista.delete("/meja/:id", BaristaRoute.MejaCtrl.destroy);

/* ---- order ---- */
barista.get("/order", BaristaRoute.OrderCtrl.index);
barista.get("/order/:orderId", BaristaRoute.OrderCtrl.orderItem);
barista.patch("/order/status/:id", BaristaRoute.OrderCtrl.upStatus);
barista.patch("/order/bayar/:orderId", BaristaRoute.OrderCtrl.bayar);
barista.delete("/order/:id", BaristaRoute.OrderCtrl.destroy);
