import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Cases from './pages/Cases';
import NewCase from './pages/NewCase';
import CaseDetail from './pages/CaseDetail';
import FamilyReportForm from './pages/FamilyReportForm';
import FamilyCasesList from './pages/FamilyCasesList';
import OrganizationDashboard from './pages/OrganizationDashboard';
import OrganizationRegisterForm from './pages/OrganizationRegisterForm';
import MatchingView from './pages/MatchingView';
import VerificationView from './pages/VerificationView';
import MapView from './pages/MapView';
import NotificationsPage from './pages/NotificationsPage';
import ReunificationView from './pages/ReunificationView';
import PlaceholderPage from './pages/PlaceholderPage';
import DisasterPredictions from './pages/DisasterPredictions';
import IdentityRecovery from './pages/IdentityRecovery';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/cases/new" element={<NewCase />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
          <Route path="/matches/:id" element={<MatchingView />} />
          <Route path="/verification" element={<VerificationView />} />
          <Route path="/verification/:id" element={<VerificationView />} />
          
          <Route path="/family" element={<Navigate to="/family/cases" replace />} />
          <Route path="/family/cases" element={<FamilyCasesList />} />
          <Route path="/family/report" element={<FamilyReportForm />} />
          
          <Route path="/hospital" element={<OrganizationDashboard orgType="hospital" />} />
          <Route path="/hospital/register" element={<OrganizationRegisterForm orgType="hospital" />} />
          
          <Route path="/shelter" element={<OrganizationDashboard orgType="shelter" />} />
          <Route path="/shelter/register" element={<OrganizationRegisterForm orgType="shelter" />} />
          
          <Route path="/rescue" element={<OrganizationDashboard orgType="rescue" />} />
          <Route path="/rescue/register" element={<OrganizationRegisterForm orgType="rescue" />} />
          
          <Route path="/map" element={<MapView />} />
          <Route path="/map/:id" element={<MapView />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/reunification/:id" element={<ReunificationView />} />
          <Route path="/predictions" element={<DisasterPredictions />} />
          <Route path="/identity" element={<IdentityRecovery />} />
          <Route path="/settings" element={<PlaceholderPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
