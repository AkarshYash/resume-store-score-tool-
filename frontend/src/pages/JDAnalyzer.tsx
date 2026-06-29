import axios from 'axios'
import { AlertCircle, BarChart2, Briefcase, CheckCircle2, PieChart as PieIcon, TrendingUp } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

interface JDTrend {
  technology: string
  count: number
  category: string
}

interface AnalyzeResponse {
  id: number
  job_title: string
  role_type: string
  technologies_found: string[]
  technology_categories: Record<string, string[]>
  years_experience: number | null
  message: string
}

const CATEGORY_COLORS = ['#2563EB', '#16A34A', '#9333EA', '#EA580C', '#DB2777', '#0891B2']

export default function JDAnalyzer() {
  const [jobTitle, setJobTitle] = useState('')
  const [rawText, setRawText] = useState('')
  const [days, setDays] = useState(7)
  const [analyzing, setAnalyzing] = useState(false)
  const [trends, setTrends] = useState<JDTrend[]>([])
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTrends(days)
  }, [days])

  const fetchTrends = async (trendDays: number) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/jd/trends?days=${trendDays}`)
      setTrends(response.data)
    } catch (err) {
      console.error('Failed to fetch JD trends:', err)
    }
  }

  const categoryData = useMemo(() => {
    const map = new Map<string, number>()
    trends.forEach((trend) => map.set(trend.category, (map.get(trend.category) || 0) + trend.count))
    return Array.from(map.entries()).map(([name, value]) => ({ name, value }))
  }, [trends])

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!rawText.trim()) return

    setAnalyzing(true)
    setError(null)
    setAnalysisResult(null)

    try {
      const response = await axios.post('http://localhost:8000/api/v1/jd/analyze', {
        job_title: jobTitle || undefined,
        raw_text: rawText
      })
      setAnalysisResult(response.data)
      setRawText('')
      fetchTrends(days)
    } catch (err) {
      console.error('Error analyzing JD:', err)
      setError('Failed to analyze the job description. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
          <Briefcase className="h-8 w-8 mr-3 text-blue-600" />
          JD Analytics & Trends
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Paste JDs, identify the role, and track the most requested tech stacks.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 h-fit">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-4">
            <BarChart2 className="h-6 w-6 mr-2 text-indigo-500" />
            Analyze Job Description
          </h2>

          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Job Title
              </label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Optional, auto-detected from JD if blank"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Job Description Text
              </label>
              <textarea
                required
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Paste the full JD here..."
                rows={10}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={analyzing || !rawText.trim()}
              className="w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center font-medium"
            >
              {analyzing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                'Analyze Tech Stack'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start text-red-700 dark:text-red-400">
              <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {analysisResult && (
            <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
              <div className="flex items-center text-green-700 dark:text-green-400 mb-3">
                <CheckCircle2 className="h-5 w-5 mr-2" />
                <h3 className="font-semibold">{analysisResult.message}</h3>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm mb-4">
                <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-800">
                  <span className="text-gray-500 dark:text-gray-400">Role</span>
                  <p className="font-semibold text-gray-900 dark:text-white">{analysisResult.role_type}</p>
                </div>
                <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-800">
                  <span className="text-gray-500 dark:text-gray-400">Experience</span>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {analysisResult.years_experience ? `${analysisResult.years_experience}+ years` : 'Not specified'}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysisResult.technologies_found.length > 0 ? (
                  analysisResult.technologies_found.map((tech) => (
                    <span key={tech} className="px-2.5 py-1 bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700 text-green-800 dark:text-green-300 text-xs font-medium rounded-full shadow-sm">
                      {tech}
                    </span>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 italic">No standard tech stack keywords found.</p>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between gap-4 mb-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-green-500" />
                Top Technologies
              </h2>
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm text-gray-900 dark:text-white"
              >
                <option value={7}>This week</option>
                <option value={30}>30 days</option>
                <option value={90}>90 days</option>
              </select>
            </div>

            <div className="h-[360px]">
              {trends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trends} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#94A3B8" opacity={0.35} />
                    <XAxis type="number" hide />
                    <YAxis dataKey="technology" type="category" axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} width={110} />
                    <Tooltip cursor={{ fill: 'rgba(37, 99, 235, 0.08)' }} />
                    <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} barSize={22} name="JD mentions" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-400">
                  <BarChart2 className="h-14 w-14 mb-3 opacity-50" />
                  <p>No JD trend data for this period.</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6">
              <PieIcon className="h-6 w-6 mr-2 text-cyan-500" />
              Stack Category Mix
            </h2>
            <div className="h-[280px]">
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={categoryData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={95} paddingAngle={2}>
                      {categoryData.map((entry, index) => (
                        <Cell key={entry.name} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-400">
                  <PieIcon className="h-14 w-14 mb-3 opacity-50" />
                  <p>Analyze JDs to build the category chart.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
