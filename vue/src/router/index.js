import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

import HomeChildren from './children/home.js'
import AdminChildren from './children/admin.js'
import PetugasChildren from './children/petugas.js'
import CamatChildren from './children/camat.js'
import StafChildren from './children/staf.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/others/login.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/layouts/admin-layout.vue'),
      children: AdminChildren,
    },
    {
      path: '/petugas',
      name: 'petugas',
      component: () => import('@/layouts/petugas-layout.vue'),
      children: PetugasChildren,
    },
    {
      path: '/camat',
      name: 'camat',
      component: () => import('@/layouts/camat-layout.vue'),
      children: CamatChildren,
    },
    {
      path: '/staf',
      name: 'staf',
      component: () => import('@/layouts/staf-layout.vue'),
      children: StafChildren,
    },

    // not-found
    {
      path: '/:pathMatch(.*)*',
      name: 'Not Found Home',
      component: () => import('@/widgets/others/404Layout.vue'),
    },
  ],
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  next()
})

router.afterEach(() => {
  NProgress.done()
})
export default router
