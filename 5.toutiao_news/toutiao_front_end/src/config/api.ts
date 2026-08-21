// API基础URL配置
export const apiConfig =  {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}


// API Key: sk-ws-H.EYDYPEI.zCB1.MEQCIGiQl7mcVkTmyL-SJyp2KSOPwkM-aW7zFH6cfIJS9J7-AiAieR2rGYBvMoEAMcM1405UH31hWhZeNW8l1R9Bj9vugA

export const aiChatConfig = {
  // OpenAI API地址（使用 vite dev 代理 /qwen，避免浏览器 CORS；生产环境需在 Nginx 同款反代）
  apiEndpoint: '/compatible-mode/v1/chat/completions',

  // API Key (由开发人员指定)
  apiKey: 'sk-ws-H.EYDYPEI.zCB1.MEQCIGiQl7mcVkTmyL-SJyp2KSOPwkM-aW7zFH6cfIJS9J7-AiAieR2rGYBvMoEAMcM1405UH31hWhZeNW8l1R9Bj9vugA',

  // 使用的模型
  model: 'qwen3-max-2026-01-23'
}
