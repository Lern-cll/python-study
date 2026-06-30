import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/styles/main.scss'

// 创建 Vue 应用实例
const app = createApp(App)
// 创建 Pinia 实例（全局状态管理）
const pinia = createPinia()

// 注册所有 Element Plus 图标为全局组件，模板中可直接以 <User /> 这种 PascalCase 形式使用
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 依次挂载：Pinia → 路由 → Element Plus
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 挂载到 #app 节点
app.mount('#app')