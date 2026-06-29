import axios from 'axios'
import { Award, BarChart3, Cloud, Code, Database, TrendingUp } from 'lucide-react'
import { useEffect, useState } from 'react'

interface SkillDistribution {
  skill: string
  count: number
  percentage: number
}

interface TechnologyStats {
  category: string
  technologies: SkillDistribution[]
}

export default function Analytics() {
  const [techStats, setTechStats] = useState<TechnologyStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/analytics/technologies')
      setTechStats(response.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCategoryIcon = (category: string) => {
    if (category.includes('Cloud')) return <Cloud className="h-6 w-6" />
    if (category.includes('Programming')) return <Code className="h-6 w-6" />
    if (category.includes('Database')) return <Database className="h-6 w-6" />
    if (category.includes('DevOps')) return <Award className="h-6 w-6" />
    return <BarChart3 className="h-6 w-6" />
  }

  const getCategoryColor = (index: number) => {
    const colors = [
      { bg: 'from-blue-500 to-blue-600', light: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-600 dark:text-blue-400' },
      { bg: 'from-green-500 to-green-600', light: 'bg-green-50 dark:bg-green-900/20', text: 'text-green-600 dark:text-green-400' },
      { bg: 'from-purple-500 to-purple-600', light: 'bg-purple-50 dark:bg-purple-900/20', text: 'text-purple-600 dark:text-purple-400' },
      { bg: 'from-orange-500 to-orange-600', light: 'bg-orange-50 dark:bg-orange-900/20', text: 'text-orange-600 dark:text-orange-400' },
      { bg: 'from-pink-500 to-pink-600', light: 'bg-pink-50 dark:bg-pink-900/20', text: 'text-pink-600 dark:text-pink-400' },
      { bg: 'from-indigo-500 to-indigo-600', light: 'bg-indigo-50 dark:bg-indigo-900/20', text: 'text-indigo-600 dark:text-indigo-400' },
    ]
    return colors[index % colors.length]
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 via-teal-600 to-blue-600 rounded-2xl shadow-xl p-8">
        <div className="flex items-center space-x-3 mb-4">
          <TrendingUp className="h-8 w-8 text-white" />
          <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
        </div>
        <p className="text-green-100 text-lg">
          Insights into your candidate pool and technology distribution
        </p>
      </div>

      {/* Technology Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {techStats.map((category, index) => {
          const colors = getCategoryColor(index)
          return (
            <div
              key={category.category}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className={`${colors.light} p-3 rounded-xl`}>
                  <div className={colors.text}>
                    {getCategoryIcon(category.category)}
                  </div>
                </div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {category.category}
                </h2>
              </div>

              {category.technologies.length > 0 ? (
                <div className="space-y-4">
                  {category.technologies.map((tech, idx) => (
                    <div key={idx} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-gray-700 dark:text-gray-300">
                          {tech.skill}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-500 dark:text-gray-400">
                            {tech.count} resume{tech.count !== 1 ? 's' : ''}
                          </span>
                          <span className={`font-semibold ${colors.text}`}>
                            {tech.percentage.toFixed(0)}%
                          </span>
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                        <div
                          className={`bg-gradient-to-r ${colors.bg} h-2.5 rounded-full transition-all duration-500`}
                          style={{ width: `${tech.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400">No data available</p>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {techStats.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center border border-gray-200 dark:border-gray-700">
          <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No Analytics Data Yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Upload resumes to see technology distribution and skill analytics
          </p>
        </div>
      )}
    </div>
  )
}
