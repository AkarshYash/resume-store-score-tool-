import axios from 'axios'
import { AlertCircle, CheckCircle, Download, ExternalLink, Search, Sparkles, TrendingUp, Upload, XCircle } from 'lucide-react'
import { useState } from 'react'

interface MatchResult {
  resume_id: number
  candidate_name: string
  resume_name: string
  file_name: string
  overall_match_score: number
  technical_match_score: number | null
  experience_match_score: number | null
  cloud_match_score: number | null
  programming_match_score: number | null
  matched_skills: string[]
  missing_skills: string[]
  additional_skills: string[]
  match_explanation: string
  improvement_suggestions: string[]
  rank: number
}

export default function Matching() {
  const [jobDescription, setJobDescription] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobFile, setJobFile] = useState<File | null>(null)
  const [inputMode, setInputMode] = useState<'text' | 'file' | 'title'>('text')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<MatchResult[]>([])
  const [showResults, setShowResults] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleMatch = async () => {
    if (inputMode === 'text' && !jobDescription.trim()) {
      setError('Please enter a job description')
      return
    }
    if (inputMode === 'title' && !jobTitle.trim()) {
      setError('Please enter a job title')
      return
    }
    if (inputMode === 'file' && !jobFile) {
      setError('Please select a JD file')
      return
    }

    setLoading(true)
    setError(null)

    try {
      let response
      if (inputMode === 'file' && jobFile) {
        const formData = new FormData()
        formData.append('file', jobFile)
        formData.append('top_n', '10')
        response = await axios.post('http://localhost:8000/api/v1/matching/match-upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
        const payload = inputMode === 'title'
          ? { job_title_only: jobTitle, top_n: 10 }
          : { job_description_text: jobDescription, top_n: 10 }
        response = await axios.post('http://localhost:8000/api/v1/matching/match', payload)
      }

      setResults(response.data.results)
      setShowResults(true)
    } catch (error: any) {
      console.error('Error matching resumes:', error)
      setError(error.response?.data?.detail || 'Failed to match resumes. Make sure the backend is running and resumes are uploaded.')
    } finally {
      setLoading(false)
    }
  }

  const getRankLabel = (rank: number) => {
    if (rank === 1) return 'Top'
    if (rank === 2) return '2nd'
    if (rank === 3) return '3rd'
    return `#${rank}`
  }

  const scoreValue = (score: number | null | undefined) => score ?? 0

  const getScoreColor = (score: number | null | undefined) => {
    const value = scoreValue(score)
    if (value >= 80) return 'text-green-600 dark:text-green-400'
    if (value >= 60) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100 dark:bg-green-900/30'
    if (score >= 60) return 'bg-yellow-100 dark:bg-yellow-900/30'
    return 'bg-red-100 dark:bg-red-900/30'
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 rounded-2xl shadow-xl p-8">
        <div className="flex items-center space-x-3 mb-4">
          <Sparkles className="h-8 w-8 text-yellow-300" />
          <h1 className="text-3xl font-bold text-white">AI Resume Matching</h1>
        </div>
        <p className="text-purple-100 text-lg">
          Paste or upload a JD and find the best resume across every candidate.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
          {[
            { key: 'text', label: 'Paste JD' },
            { key: 'title', label: 'Job Title' },
            { key: 'file', label: 'Upload JD' },
          ].map((mode) => (
            <button
              key={mode.key}
              onClick={() => setInputMode(mode.key as 'text' | 'file' | 'title')}
              className={`py-3 px-4 rounded-lg font-medium transition-colors ${
                inputMode === mode.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {mode.label}
            </button>
          ))}
        </div>

        {inputMode === 'text' && (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Job Description
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={12}
              placeholder="Paste the full job description here..."
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
            />
          </div>
        )}

        {inputMode === 'title' && (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Job Title
            </label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="Python Developer, Cloud Engineer, Data Engineer"
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        )}

        {inputMode === 'file' && (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Upload Job Description
            </label>
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={(event) => setJobFile(event.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {jobFile && (
                <p className="text-sm text-gray-700 dark:text-gray-300 mt-3">
                  Selected: {jobFile.name}
                </p>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded">
            <p className="text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}

        <button
          onClick={handleMatch}
          disabled={loading}
          className="mt-6 w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Analyzing Resumes...</span>
            </>
          ) : (
            <>
              <Search className="h-5 w-5" />
              <span>Find Best Matches</span>
            </>
          )}
        </button>
      </div>

      {showResults && results.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
              <TrendingUp className="h-7 w-7 mr-2 text-green-600" />
              Match Results ({results.length})
            </h2>
          </div>

          {results.map((result) => (
            <div
              key={result.resume_id}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all"
            >
              <div className="flex items-start justify-between mb-4 gap-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-sm font-semibold px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full">
                      {getRankLabel(result.rank)}
                    </span>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        {result.resume_name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {result.candidate_name} - {result.file_name}
                      </p>
                    </div>
                  </div>
                </div>
                <div className={`text-center px-4 py-2 rounded-xl ${getScoreBg(result.overall_match_score)}`}>
                  <div className={`text-3xl font-bold ${getScoreColor(result.overall_match_score)}`}>
                    {result.overall_match_score.toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Overall Match</div>
                </div>
              </div>

              {result.rank === 1 && (
                <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <p className="text-sm font-semibold text-green-800 dark:text-green-300">
                    Recommended Resume: {result.file_name}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                {[
                  ['Technical', result.technical_match_score],
                  ['Experience', result.experience_match_score],
                  ['Cloud', result.cloud_match_score],
                  ['Programming', result.programming_match_score],
                ].map(([label, score]) => (
                  <div key={label as string} className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <div className={`text-xl font-bold ${getScoreColor(score as number | null)}`}>
                      {scoreValue(score as number | null).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">{label}</div>
                  </div>
                ))}
              </div>

              <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-700 dark:text-gray-300">{result.match_explanation}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <h4 className="font-semibold text-gray-900 dark:text-white">Matched ({result.matched_skills.length})</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.matched_skills.map((skill) => (
                      <span key={skill} className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <XCircle className="h-5 w-5 text-red-600" />
                    <h4 className="font-semibold text-gray-900 dark:text-white">Missing ({result.missing_skills.length})</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.missing_skills.map((skill) => (
                      <span key={skill} className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertCircle className="h-5 w-5 text-blue-600" />
                    <h4 className="font-semibold text-gray-900 dark:text-white">Additional ({result.additional_skills.length})</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.additional_skills.slice(0, 5).map((skill) => (
                      <span key={skill} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                    {result.additional_skills.length > 5 && (
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                        +{result.additional_skills.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {result.improvement_suggestions.length > 0 && (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
                    <Sparkles className="h-4 w-4 mr-2 text-yellow-500" />
                    Suggestions
                  </h4>
                  <ul className="space-y-1">
                    {result.improvement_suggestions.map((suggestion) => (
                      <li key={suggestion} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                        <span className="mr-2">-</span>
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700 flex flex-wrap gap-3">
                <a
                  href={`http://localhost:8000/api/v1/resumes/${result.resume_id}/file`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open Resume
                </a>
                <a
                  href={`http://localhost:8000/api/v1/resumes/${result.resume_id}/file`}
                  download
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-100 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
                >
                  <Download className="h-4 w-4" />
                  Download
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {showResults && results.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center border border-gray-200 dark:border-gray-700">
          <Search className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Matches Found</h3>
          <p className="text-gray-600 dark:text-gray-400">
            No resumes match this job description. Try uploading more resumes or adjusting the requirements.
          </p>
        </div>
      )}
    </div>
  )
}
