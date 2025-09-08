import React from 'react';
import Navbar from '../components/layout/Navbar';
import HeroSection from '../components/landing/HeroSection';
import ProcessSection from '../components/landing/ProcessSection';
import AdvantagesSection from '../components/landing/AdvantagesSection';
import Footer from '../components/layout/Footer';
import { DashboardSection } from '../components/DashboardSection';
import { useDashboardMetrics } from '../hooks/useDashboardMetrics';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { dashboardMetrics, isLoadingMetrics, metricsError, refreshMetrics } = useDashboardMetrics();

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Navbar />
      <HeroSection />
      <DashboardSection 
        dashboardMetrics={dashboardMetrics}
        isLoadingMetrics={isLoadingMetrics}
        metricsError={metricsError}
        refreshMetrics={refreshMetrics}
        navigate={navigate}
      />
      <ProcessSection />
      <AdvantagesSection />
      <Footer />
    </div>
  );
};

export default LandingPage;