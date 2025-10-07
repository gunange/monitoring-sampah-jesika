import { path_route } from "@/components/dashboard/camat/config/data-env.ts";

const routes = [
   {
      path: "",
      name: `${path_route}-main`,
      component: () => import("@/views/dashboard/camat/disposisi-surat.vue"),
   },

   {
      path: "disposisi",
      name: `${path_route}-disposisi`,
      component: () => import("@/views/dashboard/camat/disposisi-surat.vue"),
   },
   {
      path: "surat-masuk",
      name: `${path_route}-surat-masuk`,
      component: () => import("@/views/dashboard/camat/surat-masuk.vue"),
   },
   {
      path: "surat-keluar",
      name: `${path_route}-surat-keluar`,
      component: () => import("@/views/dashboard/camat/surat-keluar.vue"),
   },
   {
      path: "riwayat-disposisi",
      name: `${path_route}-riwayat-disposisi`,
      component: () => import("@/views/dashboard/camat/riwayat-disposisi.vue"),
   },
   

   // not-found
   {
      path: `/${path_route}/:pathMatch(.*)*`,
      name: "Not-Found-Camat",
      component: () => import("@/widgets/others/404Layout.vue"),
   },
];

export default routes;
