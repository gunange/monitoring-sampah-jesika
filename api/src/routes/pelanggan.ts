import { Hono } from "hono";
import { PelangganRoute } from "@/controllers/pelanggan";

export const pelanggan = new Hono();

pelanggan.use("/*", async (_, next) => {
   return next();
});

/* ---- order ---- */
pelanggan.get("/order/item/:orderId", PelangganRoute.OrderCtrl.orderItem);
pelanggan.get("/order/:mejaId", PelangganRoute.OrderCtrl.index);
pelanggan.post("/order", PelangganRoute.OrderCtrl.store);
pelanggan.patch("/order/:orderItemId", PelangganRoute.OrderCtrl.update);
pelanggan.delete("/order/:orderItemId", PelangganRoute.OrderCtrl.destroy);


/* ---- atribut ---- */
pelanggan.get("/atribut/meja", PelangganRoute.AtributCtrl.meja);
pelanggan.get("/atribut/kategori", PelangganRoute.AtributCtrl.kategori);
