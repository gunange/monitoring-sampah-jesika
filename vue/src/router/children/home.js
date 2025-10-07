const path = 'home'

const routes = [
  {
    path: '',
    name: `${path}-main`,
    component: () => import('@/views/home/home-view.vue'),
  },
  {
    path: 'home',
    name: `${path}-main-home`,
    component: () => import('@/views/home/home-view.vue'),
  },
  

  // not-found
  {
    path: '/home/:pathMatch(.*)*',
    name: 'Not-Found-Home',
    component: () => import('@/widgets/others/404Layout.vue'),
  },
]

export default routes
