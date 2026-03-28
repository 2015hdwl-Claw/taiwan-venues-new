import Link from 'next/link'
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    use_case: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (data.success) {
        setSuccess(true)
      } else {
        setError(data.error?.message || '註冊失敗')
      }
    } catch (err) {
      setError('網路錯誤，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">✅</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              API Key 註冊成功！
            </h1>
            <p className="text-gray-600">
              您的 API Key 已生成
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-600 mb-2">API Key:</p>
            <code className="block bg-white p-3 rounded border border-gray-300 text-sm break-all">
              {data.data?.api_key || 'em_xxx...'}
            </code>
            <p className="text-xs text-gray-500 mt-2">
              ⚠️ 請妥善保管您的 API Key，不要分享給他人
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-600">✓</span>
              <span className="text-gray-600">免費額度：1000次/月</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-600">✓</span>
              <span className="text-gray-600">有效期：1年</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-600">✓</span>
              <span className="text-gray-600">權限：read:venues, read:availability</span>
            </div>
          </div>

          <div className="mt-8">
            <Link
              href="/docs"
              className="block w-full text-center px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            >
              查看文檔 →
            </Link>
          </div>

          <div className="mt-4 text-center">
            <button
              onClick={() => router.push('/')}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              返回首頁
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="container mx-auto max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            註冊 API Key
          </h1>
          <p className="text-gray-600">
            免費開始，1000次/月額度
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                姓名 / 團隊名稱
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="請輸入您的姓名"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                使用場景
              </label>
              <textarea
                required
                value={formData.use_case}
                onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
                placeholder="描述您的使用場景..."
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? '註冊中...' : '免費註冊'}
            </button>

            <div className="mt-4 text-center">
              <Link
                href="/"
                className="text-blue-600 hover:text-blue-700 text-sm"
              >
                返回首頁
              </Link>
            </div>
          </form>
        </div>

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            註冊即表示同意我們的
            <Link href="/terms" className="text-blue-600 hover:underline">服務條款</Link>
            和
            <Link href="/privacy" className="text-blue-600 hover:underline">隱私政策</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
