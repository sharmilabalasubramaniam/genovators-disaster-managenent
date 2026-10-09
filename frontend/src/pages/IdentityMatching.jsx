import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Camera, UploadCloud, CheckCircle, AlertTriangle, ChevronRight, User as UserIcon } from 'lucide-react';

export default function IdentityMatching() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0); // 0: upload, 1: preview, 2: matching, 3: results
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [photoUrl, setPhotoUrl] = useState(null);
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState('');
  
  const [matches, setMatches] = useState([]);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch user's authorized cases for association
    const fetchCases = async () => {
      try {
        const res = await api.get('/cases/');
        setCases(res.data);
      } catch (err) {
        console.error("Failed to load cases", err);
      }
    };
    fetchCases();
  }, []);

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select a valid image file (JPG/PNG).');
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setError(null);
    setStep(1); // move to preview
  };

  const handleUploadAndMatch = async () => {
    if (!selectedCase) {
      setError('Please select a case to associate this photo with.');
      return;
    }
    setStep(2);
    setLoadingMatches(true);
    setError(null);

    try {
      // 1. Upload Photo
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadRes = await api.post('/uploads/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const uploadedUrl = uploadRes.data.url;
      setPhotoUrl(uploadedUrl);

      // 2. Associate with Case
      await api.patch(`/cases/${selectedCase}`, {
        photo_url: uploadedUrl
      });

      // 3. Run Matching
      const matchRes = await api.post(`/matching/${selectedCase}/run`);
      setMatches(matchRes.data.candidates || []);
      setStep(3);
    } catch (err) {
      console.error(err);
      setError('Unable to complete matching. Please try again.');
      setStep(1);
    } finally {
      setLoadingMatches(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      
      {/* Header */}
      <div className="mb-8 border-b pb-4">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Camera className="mr-3 h-8 w-8 text-blue-600" />
          IDENTITY MATCHING
        </h1>
        <p className="text-gray-600 mt-2 text-lg">Use computer vision to identify potential matches across authorized disaster records.</p>
      </div>

      {/* Progress Indicator */}
      <div className="flex flex-wrap items-center justify-between max-w-2xl mb-12 gap-2">
        <div className={`flex items-center ${step >= 0 ? 'text-blue-600 font-bold' : 'text-gray-400'}`}>
          <div className={`rounded-full h-8 w-8 flex items-center justify-center border-2 mr-2 ${step >= 0 ? 'border-blue-600 bg-blue-50' : 'border-gray-300'}`}>1</div>
          Upload
        </div>
        <ChevronRight className="text-gray-300 h-5 w-5" />
        <div className={`flex items-center ${step >= 1 ? 'text-blue-600 font-bold' : 'text-gray-400'}`}>
          <div className={`rounded-full h-8 w-8 flex items-center justify-center border-2 mr-2 ${step >= 1 ? 'border-blue-600 bg-blue-50' : 'border-gray-300'}`}>2</div>
          Analyze
        </div>
        <ChevronRight className="text-gray-300 h-5 w-5" />
        <div className={`flex items-center ${step >= 3 ? 'text-blue-600 font-bold' : 'text-gray-400'}`}>
          <div className={`rounded-full h-8 w-8 flex items-center justify-center border-2 mr-2 ${step >= 3 ? 'border-blue-600 bg-blue-50' : 'border-gray-300'}`}>3</div>
          Review
        </div>
        <ChevronRight className="text-gray-300 h-5 w-5" />
        <div className="flex items-center text-gray-400">
          <div className="rounded-full h-8 w-8 flex items-center justify-center border-2 mr-2 border-gray-300">4</div>
          Verify
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 flex items-center shadow-sm">
          <AlertTriangle className="h-5 w-5 mr-3" />
          {error}
        </div>
      )}

      {/* Step 0: Upload State */}
      {step === 0 && (
        <div 
          className="border-4 border-dashed border-gray-300 rounded-xl p-10 md:p-16 text-center hover:bg-gray-50 transition-colors cursor-pointer bg-white shadow-sm"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          onClick={() => document.getElementById('photo-upload').click()}
        >
          <input 
            type="file" 
            id="photo-upload" 
            className="hidden" 
            accept="image/jpeg, image/png"
            onChange={handleFileChange} 
          />
          <UploadCloud className="h-20 w-20 text-gray-400 mx-auto mb-6" />
          <h3 className="text-2xl font-medium text-gray-900 mb-2">Upload Missing Person Photo</h3>
          <p className="text-gray-500 mb-6">Drag & drop a clear frontal photograph, or click to browse files.</p>
          <div className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-sm hover:bg-blue-700">
            Choose Photo
          </div>
          <p className="text-sm text-gray-400 mt-4">Supported formats: JPG, PNG</p>
        </div>
      )}

      {/* Step 1: Preview & Case Association */}
      {step === 1 && (
        <div className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2">
            <div className="p-8 border-r border-gray-200 bg-gray-50 flex flex-col items-center justify-center">
              <h3 className="text-lg font-bold text-gray-700 mb-4 uppercase tracking-wider">Uploaded Photo</h3>
              <div className="relative rounded-lg overflow-hidden border-4 border-white shadow-lg">
                <img src={preview} alt="Preview" className="max-h-80 object-cover" />
              </div>
              <button 
                onClick={() => setStep(0)}
                className="mt-6 text-blue-600 hover:text-blue-800 font-medium text-sm underline"
              >
                Replace Photo
              </button>
            </div>
            <div className="p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Associate with Case</h3>
              <p className="text-gray-600 mb-6">Select the missing person case to associate this photograph with before running the DeepFace matching engine.</p>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Existing Case</label>
                <select 
                  className="w-full border-gray-300 rounded-md shadow-sm p-3 border focus:ring-blue-500 focus:border-blue-500 bg-white"
                  value={selectedCase}
                  onChange={(e) => setSelectedCase(e.target.value)}
                >
                  <option value="">-- Select Case --</option>
                  {cases.map(c => (
                    <option key={c.vrn_id} value={c.vrn_id}>
                      {c.vrn_id} - {c.person.first_name} {c.person.last_name} ({c.status})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center my-6">
                <div className="flex-grow border-t border-gray-300"></div>
                <span className="mx-4 text-gray-400 font-medium">OR</span>
                <div className="flex-grow border-t border-gray-300"></div>
              </div>

              <button 
                onClick={() => navigate('/cases/new')}
                className="w-full py-3 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
              >
                + Create New Case
              </button>

              <div className="mt-10">
                <button
                  onClick={handleUploadAndMatch}
                  disabled={loadingMatches}
                  className="w-full flex justify-center py-4 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  Find Potential Matches
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Loading / Matching State */}
      {step === 2 && (
        <div className="bg-white rounded-xl shadow-md p-16 text-center border border-gray-200">
          <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-blue-600 mx-auto mb-8"></div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Analyzing photograph and searching authorized candidate records...</h2>
          <p className="text-gray-500 max-w-lg mx-auto">SAHYAT is currently extracting facial embeddings using DeepFace and cross-referencing identity metadata.</p>
        </div>
      )}

      {/* Step 3: Results State */}
      {step === 3 && (
        <div>
          <div className="mb-8 border-b pb-4">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Potential Matches Found</h2>
            <p className="text-gray-600">
              {matches.length} candidates analyzed. {matches.filter(m => m.overall_score >= 85).length} high-confidence candidate(s).
            </p>
          </div>

          {matches.length === 0 ? (
            <div className="bg-white rounded-xl shadow p-12 text-center border border-gray-200">
              <UserIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">No sufficiently similar candidate was found.</h3>
              <p className="text-gray-500">Try uploading a clearer photograph or checking back later as new records are added.</p>
              <button onClick={() => setStep(0)} className="mt-6 text-blue-600 font-medium">Start New Search</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Results Column */}
              <div className="col-span-2 space-y-6">
                {matches.map((match, idx) => (
                  <div key={match.candidate_id} className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200">
                    <div className="border-b border-gray-200 bg-gray-50 px-6 py-4 flex justify-between items-center">
                      <h3 className="text-lg font-bold text-gray-800">
                        #{idx + 1} &nbsp; {match.candidate_id}
                      </h3>
                      <span className="text-sm font-medium text-gray-500 bg-white px-3 py-1 rounded-full border">{match.organization}</span>
                    </div>
                    
                    <div className="p-6">
                      <div className="flex items-center mb-6 bg-gray-50 p-4 rounded-xl border border-gray-100">
                        <div className="w-1/2 flex items-center justify-between pr-4 border-r border-gray-200">
                           <img src={preview} alt="Missing" className="h-24 w-24 object-cover rounded-full border-4 border-white shadow-md" />
                           <ChevronRight className="text-gray-300 h-8 w-8" />
                           <UserIcon className="h-24 w-24 p-4 bg-white rounded-full text-gray-400 border-4 border-white shadow-md" />
                        </div>
                        <div className="w-1/2 pl-6">
                          <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Face Similarity</div>
                          <div className="flex items-center">
                            <div className="flex-grow bg-gray-200 rounded-full h-3 mr-3 overflow-hidden">
                              <div className="bg-blue-600 h-3 rounded-full" style={{width: `${match.face_similarity}%`}}></div>
                            </div>
                            <span className="font-bold text-gray-900 text-lg">{Math.round(match.face_similarity)}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-6 mb-6">
                        <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                          <h4 className="text-xs font-bold text-green-800 uppercase tracking-wider flex items-center mb-3">
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Supporting Evidence
                          </h4>
                          <ul className="space-y-2">
                            {match.supporting_evidence?.length > 0 ? match.supporting_evidence.map((ev, i) => (
                              <li key={i} className="text-sm text-green-700 flex items-start">
                                <span className="mr-2 font-bold">✓</span> {ev}
                              </li>
                            )) : <li className="text-sm text-gray-500 italic">No strong signals</li>}
                          </ul>
                        </div>
                        <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                          <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider flex items-center mb-3">
                            <AlertTriangle className="h-4 w-4 mr-2" />
                            Conflicting Evidence
                          </h4>
                          <ul className="space-y-2">
                            {match.conflicting_evidence?.length > 0 ? match.conflicting_evidence.map((ev, i) => (
                              <li key={i} className="text-sm text-amber-700 flex items-start">
                                <span className="mr-2 font-bold">⚠</span> {ev}
                              </li>
                            )) : <li className="text-sm text-gray-500 italic">No conflicting signals</li>}
                          </ul>
                        </div>
                      </div>

                      <div className="flex items-center justify-between bg-slate-50 rounded-lg p-5 border border-slate-200">
                        <div>
                          <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Overall Evidence Score</div>
                          <div className="text-4xl font-black text-slate-900">{Math.round(match.overall_score)}%</div>
                        </div>
                        <div className="text-right">
                          <div className={`text-xl font-black ${match.overall_score >= 85 ? 'text-green-600' : match.overall_score >= 70 ? 'text-blue-600' : 'text-amber-600'}`}>
                            {match.overall_score >= 85 ? 'VERY HIGH CONFIDENCE' : match.overall_score >= 70 ? 'HIGH CONFIDENCE' : 'MEDIUM CONFIDENCE'}
                          </div>
                          <div className="text-sm font-bold text-amber-600 flex items-center justify-end mt-2 bg-amber-100 px-3 py-1 rounded-md inline-flex">
                            <AlertTriangle className="h-4 w-4 mr-2" />
                            HUMAN VERIFICATION REQUIRED
                          </div>
                        </div>
                      </div>

                      <div className="mt-6 flex justify-end space-x-4 border-t pt-4">
                        <button 
                          onClick={() => navigate(`/cases/${match.candidate_id}`)}
                          className="px-6 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm"
                        >
                          Review Candidate
                        </button>
                        <button 
                          onClick={() => navigate(`/verification/${selectedCase}`)}
                          className="px-6 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700 shadow-sm"
                        >
                          View Evidence
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Explanation Panel */}
              <div className="col-span-1">
                <div className="bg-slate-900 rounded-2xl shadow-xl p-8 text-white sticky top-6 border border-slate-700">
                  <h3 className="text-xl font-bold mb-8 flex items-center">
                    <CheckCircle className="h-6 w-6 mr-3 text-blue-400" />
                    How SAHYAT Matches
                  </h3>
                  
                  <div className="space-y-6">
                    <div className="flex">
                      <div className="flex flex-col items-center mr-4">
                        <div className="h-8 w-8 rounded-full bg-blue-900 border border-blue-500 flex items-center justify-center text-sm font-bold shadow-inner">1</div>
                        <div className="h-full w-0.5 bg-slate-700 my-2"></div>
                      </div>
                      <div className="pb-4">
                        <h4 className="font-bold text-blue-300">Photograph comparison</h4>
                        <p className="text-sm text-slate-400 mt-1 leading-relaxed">Images are preprocessed and aligned.</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex flex-col items-center mr-4">
                        <div className="h-8 w-8 rounded-full bg-blue-900 border border-blue-500 flex items-center justify-center text-sm font-bold shadow-inner">2</div>
                        <div className="h-full w-0.5 bg-slate-700 my-2"></div>
                      </div>
                      <div className="pb-4">
                        <h4 className="font-bold text-blue-300">Facial similarity analysis</h4>
                        <p className="text-sm text-slate-400 mt-1 leading-relaxed">DeepFace generates multi-dimensional embeddings to calculate similarity.</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex flex-col items-center mr-4">
                        <div className="h-8 w-8 rounded-full bg-blue-900 border border-blue-500 flex items-center justify-center text-sm font-bold shadow-inner">3</div>
                        <div className="h-full w-0.5 bg-slate-700 my-2"></div>
                      </div>
                      <div className="pb-4">
                        <h4 className="font-bold text-blue-300">Identity metadata</h4>
                        <p className="text-sm text-slate-400 mt-1 leading-relaxed">Names, ages, and genders are cross-referenced.</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex flex-col items-center mr-4">
                        <div className="h-8 w-8 rounded-full bg-blue-900 border border-blue-500 flex items-center justify-center text-sm font-bold shadow-inner">4</div>
                        <div className="h-full w-0.5 bg-slate-700 my-2"></div>
                      </div>
                      <div className="pb-4">
                        <h4 className="font-bold text-blue-300">Location/timeline evidence</h4>
                        <p className="text-sm text-slate-400 mt-1 leading-relaxed">Proximity of disaster events and reporting times are evaluated.</p>
                      </div>
                    </div>
                    
                    <div className="flex">
                      <div className="flex flex-col items-center mr-4">
                        <div className="h-8 w-8 rounded-full bg-blue-900 border border-blue-500 flex items-center justify-center text-sm font-bold shadow-inner">5</div>
                      </div>
                      <div>
                        <h4 className="font-bold text-blue-300">Confidence score</h4>
                        <p className="text-sm text-slate-400 mt-1 leading-relaxed">Signals are weighted to produce an overall evidence score.</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-10 p-5 bg-slate-800 rounded-xl border border-slate-600 shadow-inner">
                    <p className="text-sm font-medium text-slate-300 text-center leading-relaxed">
                      AI assists identification.<br/>
                      <span className="text-white font-bold block mt-2 text-base">Authorized humans make the final decision.</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
