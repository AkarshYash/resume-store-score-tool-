import axios from 'axios'
import { Download, Eye, Plus, Search, Trash2, Upload, Users, X } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Candidate {
  id: number
  name: string
  email: string | null
  phone: string | null
  location: string | null
  resume_count: number
  created_at: string
}

interface Resume {
  id: number
  resume_name: string
  file_name: string
  file_type: string
  total_experience: number | null
  skills: string[]
  created_at: string
}

export default function Candidates() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const [newCandidate, setNewCandidate] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
  })

  const [uploadForm, setUploadForm] = useState({
    resumeName: '',
    file: null as File | null,
  })

  const [bulkUploadFiles, setBulkUploadFiles] = useState<{file: File, suggestedName: string, editedName: string}[]>([])
  const [showBulkUploadModal, setShowBulkUploadModal] = useState(false)
  const [bulkUploading, setBulkUploading] = useState(false)
  const [previewResume, setPreviewResume] = useState<{id: number, name: string, fileName: string, fileType: string} | null>(null)

  useEffect(() => {
    fetchCandidates()
  }, [])

  const fetchCandidates = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/candidates/')
      setCandidates(response.data)
    } catch (error) {
      console.error('Error fetching candidates:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCandidateResumes = async (candidateId: number) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/candidates/${candidateId}/resumes`)
      setResumes(response.data)
    } catch (error) {
      console.error('Error fetching resumes:', error)
    }
  }

  const handleAddCandidate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8000/api/v1/candidates/', newCandidate)
      setShowAddModal(false)
      setNewCandidate({ name: '', email: '', phone: '', location: '' })
      fetchCandidates()
    } catch (error) {
      console.error('Error adding candidate:', error)
      alert('Failed to add candidate')
    }
  }

  const handleUploadResume = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCandidate || !uploadForm.file) return

    const formData = new FormData()
    formData.append('candidate_id', selectedCandidate.id.toString())
    formData.append('resume_name', uploadForm.resumeName)
    formData.append('file', uploadForm.file)

    try {
      await axios.post('http://localhost:8000/api/v1/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setShowUploadModal(false)
      setUploadForm({ resumeName: '', file: null })
      fetchCandidateResumes(selectedCandidate.id)
      fetchCandidates()
      alert('Resume uploaded successfully!')
    } catch (error) {
      console.error('Error uploading resume:', error)
      alert('Failed to upload resume')
    }
  }

  const handleDownloadResume = async (resumeId: number, filename: string) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/resumes/${resumeId}/download`,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading resume:', error)
      alert('Failed to download resume')
    }
  }

  const handleBulkFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    // Extract suggested names from filenames
    const filenames = Array.from(files).map(f => f.name)
    try {
      const response = await axios.post('http://localhost:8000/api/v1/resumes/extract-names', filenames)
      const suggestions = response.data
      
      const filesWithNames = Array.from(files).map((file, idx) => ({
        file,
        suggestedName: suggestions[idx]?.suggested_name || file.name,
        editedName: suggestions[idx]?.suggested_name || file.name
      }))
      
      setBulkUploadFiles(filesWithNames)
    } catch (error) {
      console.error('Error extracting names:', error)
      // Fallback: use filenames
      const filesWithNames = Array.from(files).map(file => ({
        file,
        suggestedName: file.name.replace(/\.[^/.]+$/, ''),
        editedName: file.name.replace(/\.[^/.]+$/, '')
      }))
      setBulkUploadFiles(filesWithNames)
    }
  }

  const handleBulkUpload = async () => {
    if (!selectedCandidate || bulkUploadFiles.length === 0) return

    setBulkUploading(true)
    let successCount = 0

    for (const item of bulkUploadFiles) {
      const formData = new FormData()
      formData.append('candidate_id', selectedCandidate.id.toString())
      formData.append('resume_name', item.editedName)
      formData.append('file', item.file)

      try {
        await axios.post('http://localhost:8000/api/v1/resumes/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        successCount++
      } catch (error) {
        console.error(`Failed to upload ${item.file.name}:`, error)
      }
    }

    setBulkUploading(false)
    setShowBulkUploadModal(false)
    setBulkUploadFiles([])
    fetchCandidateResumes(selectedCandidate.id)
    fetchCandidates()
    alert(`Successfully uploaded ${successCount} of ${bulkUploadFiles.length} resumes!`)
  }

  const updateBulkFileName = (index: number, newName: string) => {
    setBulkUploadFiles(prev => prev.map((item, idx) => 
      idx === index ? { ...item, editedName: newName } : item
    ))
  }

  const removeBulkFile = (index: number) => {
    setBulkUploadFiles(prev => prev.filter((_, idx) => idx !== index))
  }

  const handleDeleteCandidate = async (id: number) => {
    if (!confirm('Are you sure you want to delete this candidate and all their resumes?')) return
    try {
      await axios.delete(`http://localhost:8000/api/v1/candidates/${id}`)
      fetchCandidates()
      setSelectedCandidate(null)
    } catch (error) {
      console.error('Error deleting candidate:', error)
    }
  }

  const filteredCandidates = candidates.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (c.email && c.email.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <Users className="h-8 w-8 mr-3 text-blue-600" />
            Candidates
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage candidates and their resumes
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
        >
          <Plus className="h-5 w-5" />
          <span>Add Candidate</span>
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search candidates..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>

      {/* Candidates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCandidates.map((candidate) => (
          <div
            key={candidate.id}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{candidate.name}</h3>
                {candidate.email && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">{candidate.email}</p>
                )}
                {candidate.location && (
                  <p className="text-sm text-gray-500 dark:text-gray-500">{candidate.location}</p>
                )}
              </div>
              <div className="flex space-x-1">
                <button
                  onClick={() => {
                    setSelectedCandidate(candidate)
                    fetchCandidateResumes(candidate.id)
                  }}
                  className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                  title="View resumes"
                >
                  <Eye className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleDeleteCandidate(candidate.id)}
                  className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title="Delete candidate"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {candidate.resume_count} resume{candidate.resume_count !== 1 ? 's' : ''}
              </span>
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setSelectedCandidate(candidate)
                    setShowUploadModal(true)
                  }}
                  className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  <Upload className="h-4 w-4" />
                  <span>Single</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedCandidate(candidate)
                    setShowBulkUploadModal(true)
                  }}
                  className="flex items-center space-x-1 text-sm text-green-600 hover:text-green-700 font-medium"
                >
                  <Upload className="h-4 w-4" />
                  <span>Bulk</span>
                </button>
              </div>
            </div>
          </div>
        ))}

        {filteredCandidates.length === 0 && (
          <div className="col-span-full text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              {searchQuery ? 'No candidates found matching your search.' : 'No candidates yet. Add your first candidate to get started!'}
            </p>
          </div>
        )}
      </div>

      {/* Add Candidate Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Add Candidate</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <form onSubmit={handleAddCandidate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name *
                </label>
                <input
                  type="text"
                  required
                  value={newCandidate.name}
                  onChange={(e) => setNewCandidate({ ...newCandidate, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={newCandidate.email}
                  onChange={(e) => setNewCandidate({ ...newCandidate, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="john@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={newCandidate.phone}
                  onChange={(e) => setNewCandidate({ ...newCandidate, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="+1 234 567 8900"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={newCandidate.location}
                  onChange={(e) => setNewCandidate({ ...newCandidate, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Remote / New York, NY"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add Candidate
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Upload Resume Modal */}
      {showUploadModal && selectedCandidate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Resume</h2>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Uploading for: <span className="font-semibold">{selectedCandidate.name}</span>
            </p>
            <form onSubmit={handleUploadResume} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Resume Name *
                </label>
                <input
                  type="text"
                  required
                  value={uploadForm.resumeName}
                  onChange={(e) => setUploadForm({ ...uploadForm, resumeName: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="e.g., Python GenAI, AWS Architect"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Resume File (PDF or DOCX) *
                </label>
                <input
                  type="file"
                  required
                  accept=".pdf,.docx,.doc"
                  onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files?.[0] || null })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Upload
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* View Resumes Modal */}
      {selectedCandidate && !showUploadModal && !showBulkUploadModal && resumes.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Resumes - {selectedCandidate.name}
              </h2>
              <button
                onClick={() => {
                  setSelectedCandidate(null)
                  setResumes([])
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              {resumes.map((resume) => (
                <div
                  key={resume.id}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{resume.resume_name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{resume.file_name}</p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setPreviewResume({
                          id: resume.id,
                          name: resume.resume_name,
                          fileName: resume.file_name,
                          fileType: resume.file_type
                        })}
                        className="flex items-center space-x-1 px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                        title="Preview resume"
                      >
                        <Eye className="h-4 w-4" />
                        <span className="text-sm font-medium">Preview</span>
                      </button>
                      <button
                        onClick={() => handleDownloadResume(resume.id, resume.file_name)}
                        className="flex items-center space-x-1 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
                        title="Download resume"
                      >
                        <Download className="h-4 w-4" />
                        <span className="text-sm font-medium">Download</span>
                      </button>
                    </div>
                  </div>
                  {resume.total_experience && (
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                      Experience: {resume.total_experience} years
                    </p>
                  )}
                  {resume.skills.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {resume.skills.slice(0, 5).map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                      {resume.skills.length > 5 && (
                        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full">
                          +{resume.skills.length - 5} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Bulk Upload Modal */}
      {showBulkUploadModal && selectedCandidate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-3xl w-full p-6 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Bulk Upload Resumes</h2>
              <button
                onClick={() => {
                  setShowBulkUploadModal(false)
                  setBulkUploadFiles([])
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Uploading for: <span className="font-semibold">{selectedCandidate.name}</span>
            </p>

            {bulkUploadFiles.length === 0 ? (
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Select multiple resume files to upload
                </p>
                <label className="inline-block cursor-pointer px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Choose Files
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.doc"
                    onChange={handleBulkFileSelect}
                    className="hidden"
                  />
                </label>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {bulkUploadFiles.length} file{bulkUploadFiles.length !== 1 ? 's' : ''} selected
                  </p>
                  <label className="cursor-pointer text-sm text-blue-600 hover:text-blue-700 font-medium">
                    Add More Files
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.docx,.doc"
                      onChange={handleBulkFileSelect}
                      className="hidden"
                    />
                  </label>
                </div>

                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {bulkUploadFiles.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                    >
                      <div className="flex-1 space-y-2">
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          File: {item.file.name}
                        </p>
                        <input
                          type="text"
                          value={item.editedName}
                          onChange={(e) => updateBulkFileName(idx, e.target.value)}
                          className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                          placeholder="Resume name"
                        />
                      </div>
                      <button
                        onClick={() => removeBulkFile(idx)}
                        className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => {
                      setShowBulkUploadModal(false)
                      setBulkUploadFiles([])
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    disabled={bulkUploading}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleBulkUpload}
                    disabled={bulkUploading || bulkUploadFiles.length === 0}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {bulkUploading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Uploading...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="h-5 w-5" />
                        <span>Upload All ({bulkUploadFiles.length})</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
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
                <button
                  onClick={() => handleDownloadResume(previewResume.id, previewResume.fileName)}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Download className="h-5 w-5" />
                  <span>Download</span>
                </button>
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
                      <button
                        onClick={() => handleDownloadResume(previewResume.id, previewResume.fileName)}
                        className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                      >
                        <Download className="h-5 w-5" />
                        <span>Download to View</span>
                      </button>
                      <a
                        href={`http://localhost:8000/api/v1/resumes/${previewResume.id}/file`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                      >
                        <Eye className="h-5 w-5" />
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
