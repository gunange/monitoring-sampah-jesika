import { path_route } from "@/components/dashboard/admin/config/data-env.ts";

const routes = [
   {
      path: "",
      name: `${path_route}-main`,
      component: () => import("@/views/dashboard/admin/camat.vue"),
   },
   {
      path: "camat",
      name: `${path_route}-camat`,
      component: () => import("@/views/dashboard/admin/camat.vue"),
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
