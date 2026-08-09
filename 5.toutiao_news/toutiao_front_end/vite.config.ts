import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

/**
 * 读取本地 mock JSON 文件并返回
 * @param relativePath - 相对项目根的路径，如 '/src/mock/test.json'
 * @returns 解析后的 JSON 对象；文件不存在返回 null
 */
const loadMock = (relativePath: string) => {
  const absolute = resolve(__dirname, relativePath.replace(/^\//, ''))
  if (!fs.existsSync(absolute)) return null
  const raw = fs.readFileSync(absolute, 'utf-8')
  return JSON.parse(raw)
}

/**
 * Vite 插件：将 /api/history/* 与 /api/favorite/* 等请求转发到本地 mock JSON
 */
const mockApiPlugin = () => ({
  name: 'mock-api',
  configureServer(server: any) {
    server.middlewares.use('/api', (req: any, res: any, next: any) => {
      const url = req.url || ''
      // GET /api/history/list → src/mock/test.json
      if (req.method === 'GET' && url.startsWith('/history/list')) {
        const data = loadMock('src/mock/test.json')
        if (data) {
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(data))
          return
        }
      }
      next()
    })
  }
})

export default defineConfig({
  plugins: [vue(), mockApiPlugin()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler' // 使用新的 Sass 编译器 API
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:10001',
        changeOrigin: true
      }
    }
  }
})
