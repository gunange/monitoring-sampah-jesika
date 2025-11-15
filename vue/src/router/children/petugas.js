import { path_route } from "@/components/dashboard/petugas/config/data-env.ts";

const routes = [
   {
      path: "",
      name: `${path_route}-main`,
      component: () => import("@/views/dashboard/petugas/main-view.vue"),
   },
   {
      path: "home",
      name: `${path_route}-home`,
      component: () => import("@/views/dashboard/petugas/main-view.vue"),
   },
   {
      path: "dataset",
      name: `${path_route}-dataset`,
      component: () => import("@/views/dashboard/petugas/dataset.vue"),
   },
   {
      path: "save-logs",
      name: `${path_route}-save-logs`,
      component: () => import("@/views/dashboard/petugas/save-logs.vue"),
   },
   {
      path: "monitoring",
      name: `${path_route}-monitoring`,
      component: () => import("@/views/dashboard/petugas/monitorin.vue"),
   },
   

   // not-found
   {
      path: `/${path_route}/:pathMatch(.*)*`,
      name: "Not-Found-Petugas",
      component: () => import("@/widgets/others/404Layout.vue"),
   },
];

export default routes;
