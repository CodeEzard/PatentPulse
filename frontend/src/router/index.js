import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Explorer from '../views/Explorer.vue'

const routes = [
  { path: '/', name: 'dashboard', component: Dashboard },
  { path: '/explore', name: 'explorer', component: Explorer },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
