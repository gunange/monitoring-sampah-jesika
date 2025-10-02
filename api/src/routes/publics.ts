import { Hono } from "hono";
import { PublicsRoute } from "@/controllers/publics";

export const publics = new Hono();

publics.use("/*", async (_, next) => {
   return next();
});

/* ---- storage ---- */
publics.get("/storage/:uid", PublicsRoute.StorageController.index);
publics.get("/storage/:uid/clear-chache/:clear_chache_uid", PublicsRoute.StorageController.index);
publics.get("/storage/:uid/info", PublicsRoute.StorageController.info);

/* ---- atribut ---- */
publics.get("/atribut/meja", PublicsRoute.AtributCtrl.meja);
publics.get("/atribut/menu", PublicsRoute.AtributCtrl.menu);
publics.get("/atribut/kategori", PublicsRoute.AtributCtrl.kategori);
