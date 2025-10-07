import { path_route } from "@/components/dashboard/staf/config/data-env.ts";

const routes = [
   {
      path: "",
      name: `${path_route}-main`,
      component: () => import("@/views/dashboard/staf/surat-masuk.vue"),
   },
   {
      path: "surat-masuk",
      name: `${path_route}-surat-masuk`,
      component: () => import("@/views/dashboard/staf/surat-masuk.vue"),
   },
   {
      path: "surat-keluar",
      name: `${path_route}-surat-keluar`,
      component: () => import("@/views/dashboard/staf/surat-keluar.vue"),
   },
   {
      path: "surat-disposisi",
      name: `${path_route}-surat-disposisi`,
      component: () => import("@/views/dashboard/staf/surat-disposisi.vue"),
   },
   {
      path: "belum-disposisi",
      name: `${path_route}-belum-disposisi`,
      component: () => import("@/views/dashboard/staf/belum-disposisi.vue"),
   },
   

   // not-found
   {
      path: `/${path_route}/:pathMatch(.*)*`,
      name: "Not-Found-Staf",
      component: () => import("@/widgets/others/404Layout.vue"),
   },
];

export default routes;
