import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <nav className="flex justify-between items-center mb-16">
          <div className="text-2xl font-bold text-blue-900">
            EventMaster API
          </div>
          <div className="flex gap-4">
            <Link
              href="/docs"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              API 文檔
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              註冊 API Key
            </Link>
          </div>
        </nav>

        {/* Hero */}
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI 時代的活動場地智能接口
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            讓您的 AI 應用能提供準確、即時的台灣場地建議
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/docs"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            >
              查看文檔
            </Link>
            <Link
              href="/register"
              className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg font-semibold hover:bg-blue-50"
            >
              立即開始
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-24 max-w-5xl mx-auto">
          <FeatureCard
            icon="🎯"
            title="AI-First 設計"
            description="專為 AI 模型優化的 API 格式，包含自然語言處理建議"
          />
          <FeatureCard
            icon="📊"
            title="即時可用性"
            description="即時的場地檔期與價格資訊，讓您的應用能提供準確建議"
          />
          <FeatureCard
            icon="🔑"
            title="隱藏知識圖譜"
            title="專業 know-how，AI 無法從網頁獲得"
          />
        </div>

        {/* API Endpoints */}
        <div className="mt-24 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            API 端點
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <EndpointCard
              method="GET"
              path="/api/v1/venues"
              description="取得場地列表，支援篩選、分頁"
            />
            <EndpointCard
              method="GET"
              path="/api/v1/venues/{id}"
              description="取得單一場地詳情與會議室"
            />
            <EndpointCard
              method="GET"
              path="/api/v1/venues/{id}/availability"
              description="查詢場地即時可用性"
            />
            <EndpointCard
              method="POST"
              path="/api/v1/auth/register"
              description="註冊 API Key"
            />
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center bg-blue-900 rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-white mb-4">
            準備好開始了嗎？
          </h2>
          <p className="text-blue-200 mb-8">
            註冊 API Key，立即開始整合
          </p>
          <Link
            href="/register"
            className="inline-block px-8 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
          >
            免費註冊 →
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-24">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2026 EventMaster. AI時代的活動場地智能接口
          </p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function EndpointCard({ method, path, description }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md border-2 border-gray-100 hover:border-blue-300 transition">
      <div className="flex items-center gap-2 mb-3">
        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded font-mono text-sm font-semibold">
          {method}
        </span>
        <code className="text-gray-700 text-sm">{path}</code>
      </div>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
