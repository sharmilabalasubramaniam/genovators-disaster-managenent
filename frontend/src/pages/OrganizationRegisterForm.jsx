import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { CheckCircle, ScanText, Upload } from 'lucide-react';

export default function OrganizationRegisterForm({ orgType }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [successData, setSuccessData] = useState(null);
  const [error, setError] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);

  const orgLabels = {
    hospital: { title: "Hospital Registration", name: "Hospital Name", type: "Patient ID", dash: "/hospital" },
    shelter: { title: "Shelter Registration", name: "Shelter Name", type: "Shelter ID", dash: "/shelter" },
    rescue: { title: "Rescue Team Registration", name: "Rescue Team Name", type: "Rescue Team ID", dash: "/rescue" },
  };
  const labels = orgLabels[orgType];

  const [formData, setFormData] = useState({
    orgName: '',
    officerName: '',
    location: '',
    
    // Found Person Info
    firstName: '',
    lastName: '',
    age: '',
    gender: '',
    physicalDescription: '',
    clothing: '',
    distinctiveCharacteristics: '',
    belongings: '',
    foundDate: '',
    foundTime: '',
    
    // Org Specific
    orgIdField: '',
    condition: '', // hospital
    ward: '', // hospital
    emergencyStatus: '', // hospital
    bedSection: '', // shelter
    orgStatus: '', // shelter
    operationReference: '' // rescue
  });

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const distinguishing_features = [
      formData.physicalDescription && `Description: ${formData.physicalDescription}`,
      formData.distinctiveCharacteristics && `Distinctive: ${formData.distinctiveCharacteristics}`,
      formData.clothing && `Clothing: ${formData.clothing}`,
      formData.belongings && `Belongings: ${formData.belongings}`
    ].filter(Boolean).join(' | ');

    try {
      let photo_url = null;
      if (photo) {
        const formDataUpload = new FormData();
        formDataUpload.append('file', photo);
        const uploadRes = await api.post('/uploads/', formDataUpload, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        photo_url = uploadRes.data.url;
      }

      const payload = {
      status: orgType === 'hospital' ? 'HOSPITALIZED' : (orgType === 'shelter' ? 'IN_SHELTER' : 'FOUND'),
      person: {
        first_name: formData.firstName || 'Unknown',
        last_name: formData.lastName || 'Unknown',
        age: formData.age ? parseInt(formData.age, 10) : null,
        gender: formData.gender || null,
        distinguishing_features: distinguishing_features || null,
        photo_url: photo_url
      },
      location: {
        location_type: "Found",
        address: formData.location
      }
    };

    if (orgType === 'hospital') {
      payload.hospital_record = {
        hospital_name: formData.orgName,
        admission_date: formData.foundDate ? new Date(`${formData.foundDate}T${formData.foundTime || '00:00'}`).toISOString() : null,
        condition_summary: formData.condition
      };
    } else if (orgType === 'shelter') {
      payload.shelter_record = {
        shelter_name: formData.orgName,
        check_in_date: formData.foundDate ? new Date(`${formData.foundDate}T${formData.foundTime || '00:00'}`).toISOString() : null
      };
    } else if (orgType === 'rescue') {
      payload.rescue_record = {
        rescue_team: formData.orgName,
        rescue_location: formData.location,
        rescue_date: formData.foundDate ? new Date(`${formData.foundDate}T${formData.foundTime || '00:00'}`).toISOString() : null
      };
    }

      const res = await api.post('/cases/', payload);
      setSuccessData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to submit report");
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setPhoto(e.target.files[0]);
    }
  };

  const handleOCRScan = async (e) => {
    if (!e.target.files || !e.target.files[0]) return;
    setOcrLoading(true);
    setError(null);
    try {
      const ocrData = new FormData();
      ocrData.append('file', e.target.files[0]);
      const res = await api.post('/ocr/extract', ocrData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // In a real app, parse the text to extract fields.
      // Here, we just append it to belongings to show it works.
      setFormData(prev => ({
        ...prev,
        belongings: prev.belongings 
          ? prev.belongings + "\nOCR Extracted: " + res.data.extracted_text 
          : "OCR Extracted: " + res.data.extracted_text
      }));
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "OCR Scan failed");
    } finally {
      setOcrLoading(false);
    }
  };

  if (successData) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl bg-white p-8 shadow-sm text-center">
        <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
        <h2 className="text-2xl font-bold mb-2 tracking-tight">RECORD CREATED</h2>
        <div className="bg-gray-50 rounded-lg p-6 my-6 border border-gray-100">
          <p className="text-4xl font-black text-primary mb-2">{successData.vrn_id}</p>
          <p className="text-sm text-gray-500">The found person record has been successfully registered.</p>
        </div>
        <div className="flex gap-4">
          <button onClick={() => navigate(labels.dash)} className="w-1/2 rounded-lg bg-gray-100 py-3 font-semibold text-gray-800 transition-colors hover:bg-gray-200">
            DASHBOARD
          </button>
          <button onClick={() => navigate(`/cases/${successData.vrn_id}`)} className="w-1/2 rounded-lg bg-primary py-3 font-semibold text-white transition-opacity hover:opacity-90">
            VIEW RECORD
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl rounded-2xl bg-white p-6 shadow-sm sm:p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-gray-900">{labels.title}</h2>
        <p className="mt-2 text-sm text-gray-500">Register a found person into the unified database.</p>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4 border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Organization Info */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Organization Information</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">{labels.name} *</label>
              <input required type="text" name="orgName" value={formData.orgName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Officer/Responder Name *</label>
              <input required type="text" name="officerName" value={formData.officerName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Location *</label>
              <input required type="text" name="location" value={formData.location} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
          </div>
        </section>

        {/* Found Person Info */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Found Person Information</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">First Name (if known)</label>
              <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Last Name (if known)</label>
              <input type="text" name="lastName" value={formData.lastName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Approximate Age</label>
              <input type="number" name="age" value={formData.age} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Gender</label>
              <select name="gender" value={formData.gender} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="">Select...</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
                <option value="Unknown">Unknown</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Recent Photo (Optional)</label>
              <input type="file" accept="image/*" onChange={handlePhotoChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            
            <div className="sm:col-span-2 p-4 bg-blue-50 rounded-lg border border-blue-100 flex flex-col sm:flex-row items-center gap-4">
              <div className="flex-1">
                <h4 className="text-sm font-bold text-blue-900 flex items-center gap-2">
                  <ScanText className="h-4 w-4" /> ID Card Auto-Scan (OCR)
                </h4>
                <p className="text-xs text-blue-700 mt-1">Upload a photo of an ID card to automatically extract details.</p>
              </div>
              <div className="relative">
                <input type="file" accept="image/*" onChange={handleOCRScan} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                <button type="button" disabled={ocrLoading} className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-md shadow-sm hover:bg-blue-700 disabled:opacity-50">
                  {ocrLoading ? 'SCANNING...' : 'UPLOAD ID'}
                </button>
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Date Found</label>
              <input type="date" name="foundDate" value={formData.foundDate} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Time Found</label>
              <input type="time" name="foundTime" value={formData.foundTime} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Physical Description</label>
              <textarea name="physicalDescription" value={formData.physicalDescription} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Distinctive Characteristics</label>
              <textarea name="distinctiveCharacteristics" value={formData.distinctiveCharacteristics} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Clothing & Belongings</label>
              <textarea name="clothing" value={formData.clothing} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
          </div>
        </section>

        {/* Organization Specifics */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Additional Information</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">{labels.type}</label>
              <input type="text" name="orgIdField" value={formData.orgIdField} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            {orgType === 'hospital' && (
              <>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Ward</label>
                  <input type="text" name="ward" value={formData.ward} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
                </div>
                <div className="sm:col-span-2">
                  <label className="mb-1 block text-sm font-medium text-gray-700">Medical Condition</label>
                  <textarea name="condition" value={formData.condition} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
                </div>
              </>
            )}
            {orgType === 'shelter' && (
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Bed/Section</label>
                <input type="text" name="bedSection" value={formData.bedSection} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
              </div>
            )}
            {orgType === 'rescue' && (
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Operation Reference</label>
                <input type="text" name="operationReference" value={formData.operationReference} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
              </div>
            )}
          </div>
        </section>

        <div className="pt-4 border-t">
          <button 
            type="submit" 
            disabled={loading}
            className="w-full rounded-lg bg-primary py-3 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'SUBMITTING...' : 'REGISTER PERSON'}
          </button>
        </div>
      </form>
    </div>
  );
}
