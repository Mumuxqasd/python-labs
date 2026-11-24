import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Nodes from "../views/Nodes.vue";
import NodeDetail from "../views/NodeDetail.vue";
import CheckDetail from "../views/CheckDetail.vue";
import History from "../views/History.vue";
import About from "../views/About.vue";
export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Dashboard },
    { path: "/nodes", component: Nodes },
    { path: "/nodes/:id", component: NodeDetail },
    { path: "/checks/:id", component: CheckDetail },
    { path: "/history", component: History },
    { path: "/about", component: About },
  ],
});
