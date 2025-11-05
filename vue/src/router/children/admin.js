import { path_route } from "@/components/dashboard/admin/config/data-env.ts";

const routes = [
   {
      path: "",
      name: `${path_route}-main`,
      component: () => import("@/views/dashboard/admin/petugas.vue"),
   },
   {
      path: "petugas",
      name: `${path_route}-petugas`,
      component: () => import("@/views/dashboard/admin/petugas.vue"),
   },
   {
      path: "staf",
      name: `${path_route}-staf`,
      component: () => import("@/views/dashboard/admin/staf.vue"),
   },
   

   // not-found
   {
      path: `/${path_route}/:pathMatch(.*)*`,
      name: "Not-Found-Admin",
      component: () => import("@/widgets/others/404Layout.vue"),
   },
];

export default routes;
