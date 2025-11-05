import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

import AdminChildren from './children/admin.js'
import PetugasChildren from './children/petugas.js'

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
