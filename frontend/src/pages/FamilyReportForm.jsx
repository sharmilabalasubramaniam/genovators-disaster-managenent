import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { CheckCircle } from 'lucide-react';

export default function FamilyReportForm() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [successData, setSuccessData] = useState(null);
  const [error, setError] = useState(null);
  const [photo, setPhoto] = useState(null);

  const [formData, setFormData] = useState({
    // Person info
    firstName: '',
    lastName: '',
    age: '',
    gender: '',
    relationship: '',
    
    // Last known info
    location: '',
    lastSeenDate: '',
    lastSeenTime: '',
    
    // Identifying info
    nickname: '',
    physicalDescription: '',
    distinctiveCharacteristics: '',
    clothing: '',
    
    // Optional
    medicalInfo: '',
    additionalNotes: '',
    reporterName: '',
    reporterContact: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Combine identifying features
    const distinguishing_features = [
      formData.nickname && `Nickname: ${formData.nickname}`,
      formData.physicalDescription && `Description: ${formData.physicalDescription}`,
      formData.distinctiveCharacteristics && `Distinctive: ${formData.distinctiveCharacteristics}`,
      formData.clothing && `Clothing: ${formData.clothing}`,
      formData.medicalInfo && `Medical: ${formData.medicalInfo}`,
      formData.additionalNotes && `Notes: ${formData.additionalNotes}`
    ].filter(Boolean).join(' | ');

    try {
      let photo_url = null;
      if (photo) {
        const formDataUpload = new FormData();
        formDataUpload.append('file', photo);
        const uploadRes = await api.post('/uploads/', formDataUpload, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        photo_url = uploadRes.data.url;
      }

      const payload = {
        status: "New",
        person: {
          first_name: formData.firstName,
          last_name: formData.lastName,
          age: formData.age ? parseInt(formData.age, 10) : null,
          gender: formData.gender || null,
          distinguishing_features: distinguishing_features || null,
          photo_url: photo_url
        },
        family_report: {
          reporter_name: formData.reporterName,
          reporter_contact: formData.reporterContact,
          relationship_to_person: formData.relationship
        },
        location: {
          location_type: "Last Known",
          address: formData.location
        }
      };

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

  if (successData) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl bg-white p-8 shadow-sm text-center">
        <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
        <h2 className="text-2xl font-bold mb-2 tracking-tight">REPORT REGISTERED</h2>
        <div className="bg-gray-50 rounded-lg p-6 my-6 border border-gray-100">
          <p className="text-4xl font-black text-primary mb-2">{successData.vrn_id}</p>
          <p className="text-sm text-gray-500">Missing person report has been successfully registered.</p>
        </div>
        
        <div className="text-left mb-8 space-y-2">
          <p><span className="font-semibold text-gray-700">Status:</span> <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-md text-sm font-medium">{successData.status}</span></p>
          <p><span className="font-semibold text-gray-700">Next:</span> The system will compare this report against registered hospital, shelter and rescue records.</p>
        </div>
        
        <button 
          onClick={() => navigate(`/cases/${successData.vrn_id}`)}
          className="w-full rounded-lg bg-primary py-3 font-semibold text-white transition-opacity hover:opacity-90"
        >
          VIEW CASE
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl rounded-2xl bg-white p-6 shadow-sm sm:p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-gray-900">Missing Person Report</h2>
        <p className="mt-2 text-sm text-gray-500">Please provide as much detail as possible to help us match records.</p>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4 border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Person Information */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Person Information</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">First Name *</label>
              <input required type="text" name="firstName" value={formData.firstName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Last Name *</label>
              <input required type="text" name="lastName" value={formData.lastName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Age *</label>
              <input required type="number" name="age" value={formData.age} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Gender *</label>
              <select required name="gender" value={formData.gender} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="">Select gender...</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Recent Photo (Optional)</label>
              <input type="file" accept="image/*" onChange={handlePhotoChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
          </div>
        </section>

        {/* Reporter Information */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Your Information (Reporter)</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Your Full Name *</label>
              <input required type="text" name="reporterName" value={formData.reporterName} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Contact Number *</label>
              <input required type="text" name="reporterContact" value={formData.reporterContact} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Relationship to Missing Person *</label>
              <input required type="text" name="relationship" value={formData.relationship} onChange={handleChange} placeholder="e.g., Mother, Brother, Spouse" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
          </div>
        </section>

        {/* Last Known Information */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Last Known Information</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Last Known Location *</label>
              <input required type="text" name="location" value={formData.location} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Last Seen Date</label>
              <input type="date" name="lastSeenDate" value={formData.lastSeenDate} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Last Seen Time</label>
              <input type="time" name="lastSeenTime" value={formData.lastSeenTime} onChange={handleChange} className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
          </div>
        </section>

        {/* Identifying Information */}
        <section>
          <h3 className="mb-4 text-lg font-semibold text-gray-900 border-b pb-2">Identifying Information (Optional)</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Physical Description</label>
              <textarea name="physicalDescription" value={formData.physicalDescription} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Distinctive Characteristics (Tattoos, scars, etc.)</label>
              <textarea name="distinctiveCharacteristics" value={formData.distinctiveCharacteristics} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Clothing Description</label>
              <textarea name="clothing" value={formData.clothing} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">Medical Information / Additional Notes</label>
              <textarea name="additionalNotes" value={formData.additionalNotes} onChange={handleChange} rows="2" className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"></textarea>
            </div>
          </div>
        </section>

        <div className="pt-4 border-t">
          <button 
            type="submit" 
            disabled={loading}
            className="w-full rounded-lg bg-primary py-3 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'SUBMITTING...' : 'SUBMIT REPORT'}
          </button>
        </div>
      </form>
    </div>
  );
}
