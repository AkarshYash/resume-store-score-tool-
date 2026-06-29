import axios from 'axios'
import { Download, ExternalLink, Eye, FileText, Search, Trash2, User, X } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Resume {
  id: number
  candidate_name: string
  candidate_email: string | null
  resume_name: string
  file_name: string
  file_type: string
  total_experience: number | null
  skills: string[]
  programming_languages: string[]
  cloud_platforms: string[]
  created_at: string
}

export default function AllResumes() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null)
  const [previewResume, setPreviewResume] = useState<{id: number, name: string, fileName: string, fileType: string} | null>(null)

  useEffect(() => {
    fetchAllResumes()
  }, [])

  const fetchAllResumes = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/resumes/all/detailed')
      setResumes(response.data)
    } catch (error) {
      console.error('Error fetching resumes:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteResume = async (id: number) => {
    if (!confirm('Are you sure you want to delete this resume?')) return
    try {
      await axios.delete(`http://localhost:8000/api/v1/resumes/${id}`)
      fetchAllResumes()
    } catch (error) {
      console.error('Error deleting resume:', error)
    }
  }

  const filteredResumes = resumes.filter((resume) => {
    const query = searchQuery.toLowerCase()
    return (
      resume.resume_name.toLowerCase().includes(query) ||
      resume.candidate_name.toLowerCase().includes(query) ||
      resume.skills.some((skill) => skill.toLowerCase().includes(query))
    )
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <FileText className="h-8 w-8 mr-3 text-blue-600" />
            All Resumes
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Review every resume across all candidates in one place
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-blue-600">{resumes.length}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Resumes</div>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search by resume name, candidate, or skills..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <tr>
                {['Resume', 'Candidate', 'Skills', 'Experience', 'Date', 'Actions'].map((heading) => (
                  <th key={heading} className={`px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider ${heading === 'Actions' ? 'text-right' : 'text-left'}`}>
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredResumes.map((resume) => (
                <tr key={resume.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">{resume.resume_name}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">{resume.file_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <User className="h-4 w-4 text-gray-400" />
                      <div>
                        <div className="text-sm text-gray-900 dark:text-white">{resume.candidate_name}</div>
                        {resume.candidate_email && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">{resume.candidate_email}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {resume.skills.slice(0, 3).map((skill) => (
                        <span key={skill} className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                          {skill}
                        </span>
                      ))}
                      {resume.skills.length > 3 && (
                        <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full">
                          +{resume.skills.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {resume.total_experience ? `${resume.total_experience} years` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {new Date(resume.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => setPreviewResume({
                          id: resume.id,
                          name: resume.resume_name,
                          fileName: resume.file_name,
                          fileType: resume.file_type
                        })}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                        title="Preview resume"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setSelectedResume(resume)}
                        className="p-1.5 text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
                        title="View details"
                      >
                        <FileText className="h-4 w-4" />
                      </button>
                      <a
                        href={`http://localhost:8000/api/v1/resumes/${resume.id}/download`}
                        download
                        className="p-1.5 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                        title="Download"
                      >
                        <Download className="h-4 w-4" />
                      </a>
                      <button
                        onClick={() => handleDeleteResume(resume.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredResumes.length === 0 && (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                {searchQuery ? 'No resumes found matching your search.' : 'No resumes uploaded yet.'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Details Modal */}
      {selectedResume && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedResume.resume_name}</h2>
              <button onClick={() => setSelectedResume(null)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Candidate</h3>
                <p className="text-gray-900 dark:text-white">{selectedResume.candidate_name}</p>
                {selectedResume.candidate_email && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">{selectedResume.candidate_email}</p>
                )}
              </div>

              <div>
                <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">File</h3>
                <p className="text-sm text-gray-900 dark:text-white">{selectedResume.file_name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {selectedResume.file_type.toUpperCase()} - Uploaded {new Date(selectedResume.created_at).toLocaleDateString()}
                </p>
              </div>

              {[
                ['Skills', selectedResume.skills, 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'],
                ['Programming Languages', selectedResume.programming_languages, 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'],
                ['Cloud Platforms', selectedResume.cloud_platforms, 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'],
              ].map(([label, values, classes]) => (
                (values as string[]).length > 0 && (
                  <div key={label as string}>
                    <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">{label as string}</h3>
                    <div className="flex flex-wrap gap-2">
                      {(values as string[]).map((value) => (
                        <span key={value} className={`px-3 py-1 text-sm rounded-full ${classes as string}`}>
                          {value}
                        </span>
                      ))}
                    </div>
                  </div>
                )
              ))}

              <div className="pt-2 flex flex-wrap gap-3">
                <a
                  href={`http://localhost:8000/api/v1/resumes/${selectedResume.id}/file`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open Resume
                </a>
                <a
                  href={`http://localhost:8000/api/v1/resumes/${selectedResume.id}/file`}
                  download
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-100 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
                >
                  <Download className="h-4 w-4" />
                  Download
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Resume Preview Modal */}
      {previewResume && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex-1">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{previewResume.name}</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">{previewResume.fileName}</p>
              </div>
              <div className="flex items-center space-x-2">
                <a
                  href={`http://localhost:8000/api/v1/resumes/${previewResume.id}/download`}
                  download
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Download className="h-5 w-5" />
                  <span>Download</span>
                </a>
                <button
                  onClick={() => setPreviewResume(null)}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>

            {/* Preview Content */}
            <div className="flex-1 overflow-hidden">
              {previewResume.fileType.toLowerCase() === 'pdf' ? (
                <iframe
                  src={`http://localhost:8000/api/v1/resumes/${previewResume.id}/file`}
                  className="w-full h-full border-0"
                  title="Resume Preview"
                />
              ) : previewResume.fileType.toLowerCase().includes('doc') ? (
                <div className="h-full flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-900">
                  <div className="text-center max-w-md">
                    <div className="mb-4 p-4 bg-blue-100 dark:bg-blue-900/30 rounded-full inline-block">
                      <Eye className="h-12 w-12 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      DOCX Preview
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      Word documents cannot be previewed directly in the browser.
                    </p>
                    <div className="space-y-3">
                      <a
                        href={`http://localhost:8000/api/v1/resumes/${previewResume.id}/download`}
                        download
                        className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                      >
                        <Download className="h-5 w-5" />
                        <span>Download to View</span>
                      </a>
                      <a
                        href={`http://localhost:8000/api/v1/resumes/${previewResume.id}/file`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                      >
                        <ExternalLink className="h-5 w-5" />
                        <span>Open in New Tab</span>
                      </a>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-4">
                      Tip: Downloaded DOCX files will open in Microsoft Word or compatible software
                    </p>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
                  <p>Preview not available for this file type</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
