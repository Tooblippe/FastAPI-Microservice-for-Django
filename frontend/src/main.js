import Vue from "vue";
import "./plugins/axios";
import App from "./App.vue";
import store from "./store";
import vuetify from "./plugins/vuetify";

Vue.config.productionTip = false;

console.log(process.env);

// eslint-disable-next-line no-undef
axios.defaults.baseURL = process.env.VUE_APP_BASEURL;

new Vue({
  store,
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
