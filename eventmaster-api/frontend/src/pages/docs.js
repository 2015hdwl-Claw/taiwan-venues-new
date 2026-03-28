import Link from 'next/link'
import { useState } from 'react'

export default function DocsPage() {
  const [apiKey, setApiKey] = useState('')
  const [showKey, setShowKey] = useState(false)

  const toggleKey = () => setShowKey(!showKey)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-blue-900">
            EventMaster API
          </Link>
          <Link
            href="/register"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            註冊 API Key
          </Link>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              API 文檔
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              完整的 API 參考文檔與使用範例
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 inline-block">
              <code className="text-sm">
                Base URL: <span className="font-semibold">http://localhost:8000</span>
              </code>
            </div>
          </div>

          {/* Quick Start */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-blue-600">🚀</span>
              快速開始
            </h2>

            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4">1. 註冊 API Key</h3>
              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg mb-4">
                <pre className="text-sm">
{`curl -X POST "http://localhost:8000/api/v1/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Your Name",
    "email": "you@example.com",
    "use_case": "Building an AI venue finder"
  }'`}
                </pre>
              </div>
              <p className="text-sm text-gray-600">
                回應會包含您的 API Key，請妥善保管。
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">2. 使用 API Key</h3>
              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg mb-4">
                <pre className="text-sm">
{`curl "http://localhost:8000/api/v1/venues" \\
  -H "X-API-Key: em_your_api_key_here"`}
                </pre>
              </div>
            </div>
          </section>

          {/* Endpoints */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-green-600">📡</span>
              API 端點
            </h2>

            {/* GET /api/v1/venues */}
            <EndpointDoc
              method="GET"
              path="/api/v1/venues"
              title="取得場地列表"
              description="取得所有場地或根據條件篩選"
              params={[
                { name: 'city', type: 'string', description: '城市（如：台北）' },
                { name: 'capacity_min', type: 'integer', description: '最小容量' },
                { name: 'page', type: 'integer', description: '頁碼（預設1）' },
                { name: 'limit', type: 'integer', description: '每頁數量（預設20）' }
              ]}
              example={`curl "http://localhost:8000/api/v1/venues?city=台北&capacity_min=300"`}
            />

            {/* GET /api/v1/venues/{id} */}
            <EndpointDoc
              method="GET"
              path="/api/v1/venues/{id}"
              title="取得場地詳情"
              description="取得單一場地的完整資訊，包括會議室"
              params={[
                { name: 'id', type: 'integer', description: '場地ID', required: true }
              ]}
              example={`curl "http://localhost:8000/api/v1/venues/1086"`}
            />

            {/* GET /api/v1/venues/{id}/availability */}
            <EndpointDoc
              method="GET"
              path="/api/v1/venues/{id}/availability"
              title="查詢可用性"
              description="查詢指定日期範圍內的場地可用性"
              params={[
                { name: 'id', type: 'integer', description: '場地ID', required: true },
                { name: 'start_date', type: 'string', description: '開始日期（YYYY-MM-DD）', required: true },
                { name: 'end_date', type: 'string', description: '結束日期（YYYY-MM-DD）' }
              ]}
              example={`curl "http://localhost:8000/api/v1/venues/1086/availability?start_date=2026-05-01&end_date=2026-05-07"`}
            />

            {/* POST /api/v1/venues/search */}
            <EndpointDoc
              method="POST"
              path="/api/v1/venues/search"
              title="智能搜尋"
              description="根據自然語言查詢和需求找到最合適的場地"
              body={{
                query: "我要辦一個500人的發布會",
                requirements: {
                  style: "presentation",
                  audience_size: 500,
                  city: "台北",
                  budget_max: 50000
                }
              }}
              example={`curl -X POST "http://localhost:8000/api/v1/venues/search" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: em_your_api_key" \\
  -d '{
    "query": "500人發布會，台北",
    "requirements": {
      "audience_size": 500,
      "city": "台北",
      "budget_max": 50000
    }
  }'`}
            />
          </section>

          {/* Authentication */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-red-600">🔒</span>
              認證
            </h2>

            <div className="bg-white rounded-xl shadow-md p-6">
              <p className="text-gray-700 mb-4">
                大部分 API 端點需要認證。請在請求中加入 API Key：
              </p>

              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg">
                <pre className="text-sm">
{`# Header 格式
X-API-Key: em_your_api_key_here

# curl 範例
curl "http://localhost:8000/api/v1/venues/1086" \\
  -H "X-API-Key: em_your_api_key_here"`}
                </pre>
              </div>

              <p className="text-sm text-gray-600 mt-4">
                註冊 API Key 是免費的，每月 1000 次調用額度。
              </p>
            </div>
          </section>

          {/* Response Format */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-purple-600">📦</span>
              回應格式
            </h2>

            <div className="bg-white rounded-xl shadow-md p-6">
              <p className="text-gray-700 mb-4">
                所有 API 回應都遵循統一格式：
              </p>

              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg">
                <pre className="text-sm">
{`{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-04-01T10:00:00Z"
  }

// 錯誤回應
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  }
}`}
                </pre>
              </div>
            </div>
          </section>

          {/* Error Codes */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-yellow-600">⚠️</span>
              錯誤代碼
            </h2>

            <div className="grid md:grid-cols-2 gap-4">
              <ErrorCodeCard code="400" message="Bad Request" description="請求參數錯誤" />
              <ErrorCodeCard code="401" message="Unauthorized" description="API Key 無效或缺失" />
              <ErrorCodeCard code="404" message="Not Found" description="資源不存在" />
              <ErrorCodeCard code="429" message="Rate Limit" description="超過速率限制" />
              <ErrorCodeCard code="500" message="Server Error" description="伺服器內部錯誤" />
            </div>
          </section>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2026 EventMaster API. All rights reserved.
          </p>
          <div className="mt-4 flex justify-center gap-6 text-sm">
            <Link href="/terms" className="text-gray-400 hover:text-white">
              服務條款
            </Link>
            <Link href="/privacy" className="text-gray-400 hover:text-white">
              隱私政策
            </Link>
            <Link href="/" className="text-gray-400 hover:text-white">
              返回首頁
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

function EndpointDoc({ method, path, title, description, params = [], example = '' }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 mb-6 border-l-4 border-blue-500">
      <div className="flex items-start gap-3 mb-4">
        <span className="px-3 py-1 bg-blue-600 text-white rounded font-mono text-sm font-semibold">
          {method}
        </span>
        <code className="text-lg text-gray-900 font-mono">{path}</code>
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>

      {params.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">參數：</h4>
          <div className="space-y-1">
            {params.map((param, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                <code className="px-2 py-1 bg-gray-100 rounded">{param.name}</code>
                <span className="text-gray-600">{param.type}</span>
                <span className="text-gray-500">{param.description}</span>
                {param.required && <span className="text-red-500">*</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {example && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">範例：</h4>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg">
            <pre className="text-xs overflow-x-auto">{example}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

function ErrorCodeCard({ code, message, description }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
      <div className="text-2xl font-mono text-gray-900 mb-2">{code}</div>
      <div className="font-semibold text-gray-800 mb-1">{message}</div>
      <div className="text-sm text-gray-600">{description}</div>
    </div>
  )
}
