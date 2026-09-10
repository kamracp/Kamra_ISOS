import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "../components/ProtectedRoute";
import MainLayout from "../layouts/MainLayout";
import DepartmentList from "../features/departments/pages/DepartmentList";
import EnergyMeterList from "../features/energy/pages/EnergyMeterList";
import UtilityBillList from "../features/energy/pages/UtilityBillList";
import MyOrganization from "../features/organizations/pages/MyOrganization";
import BuildingList from "../features/buildings/pages/BuildingList";
import HvacEquipmentList from "../features/hvac-equipment/pages/HvacEquipmentList";
import TenantBillingPage from "../features/tenant-billing/pages/TenantBillingPage";
import PatEnergyPage from "../features/pat-energy/pages/PatEnergyPage";
import FloorList from "../features/floors/pages/FloorList";
import ManufacturingUnitList from "../features/manufacturing-units/pages/ManufacturingUnitList";
import ProductionRecordList from "../features/production-records/pages/ProductionRecordList";
import NetZeroPage from "../features/net-zero/pages/NetZeroPage";
import ComingSoon from "../pages/ComingSoon";
import Dashboard from "../pages/Dashboard";
import Login from "../pages/Login";
import NotFound from "../pages/NotFound";
import Signup from "../pages/Signup";
import ESGReportPage from "../features/esg-reports/ESGReportPage";
import ClimateRiskPage from "../features/climate-risk/pages/ClimateRiskPage";
import BrsrProfilePage from "../features/brsr-profile/pages/BrsrProfilePage";
import BrsrPolicyPage from "../features/brsr-policy/pages/BrsrPolicyPage";
import ReportStudioPage from "../features/report-studio/pages/ReportStudioPage";
import WaterWastePage from "../features/water-waste/pages/WaterWastePage";
import CsrPage from "../features/csr/pages/CsrPage";
import PolicyAdvocacyPage from "../features/policy-advocacy/pages/PolicyAdvocacyPage";
import SustainableProductsPage from "../features/sustainable-products/pages/SustainableProductsPage";
import HumanRightsPage from "../features/human-rights/pages/HumanRightsPage";
import ConsumerResponsibilityPage from "../features/consumer-responsibility/pages/ConsumerResponsibilityPage";
import EmployeeWellbeingPage from "../features/employee-wellbeing/pages/EmployeeWellbeingPage";
import BrsrSectionCPage from "../features/brsr-section-c/pages/BrsrSectionCPage";
import PillarHubPage from "../features/pillars/pages/PillarHubPage";
import ManufacturingFuelsPage from "../features/manufacturing-fuels/pages/ManufacturingFuelsPage";
import EnergyDashboardPage from "../features/pat-energy/pages/EnergyDashboardPage";
import StakeholderEngagementPage from "../features/stakeholder-engagement/pages/StakeholderEngagementPage";
import ManufacturingElectricityPage from "../features/manufacturing-electricity/pages/ManufacturingElectricityPage";
import EthicsPage from "../features/ethics/pages/EthicsPage";
export default function AppRouter() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          
          <Route path="organizations" element={<MyOrganization />} />
          <Route path="departments" element={<DepartmentList />} />
          <Route path="energy-meters" element={<EnergyMeterList />} />
        <Route path="utility-bills" element={<UtilityBillList />} />
          <Route path="buildings" element={<BuildingList />} />
          <Route path="utilities" element={<ComingSoon title="Utilities" />} />
          <Route
            path="energy"
            element={<ComingSoon title="Energy Intelligence" />}
          />
          <Route path="hvac" element={<HvacEquipmentList />} />
          <Route path="tenant-billing" element={<TenantBillingPage />} />
          <Route path="pat-energy" element={<PatEnergyPage />} />
          <Route path="floors" element={<FloorList />} />
          <Route path="manufacturing-units" element={<ManufacturingUnitList />} />
          <Route path="production-records" element={<ProductionRecordList />} />
          <Route path="net-zero" element={<NetZeroPage />} />
          <Route
            path="electrical"
            element={<ComingSoon title="Electrical Analytics" />}
          />
          <Route path="water" element={<ComingSoon title="Water Analytics" />} />
          <Route path="carbon" element={<ComingSoon title="Carbon Accounting" />}/>
          <Route path="esg" element={<ESGReportPage />} />
          <Route path="climate-risk" element={<ClimateRiskPage />} />
          <Route path="brsr-profile" element={<BrsrProfilePage />} />
          <Route path="brsr-policy" element={<BrsrPolicyPage />} />
          <Route path="report-studio" element={<ReportStudioPage />} />
          <Route path="water-waste" element={<WaterWastePage />} />
          <Route path="csr" element={<CsrPage />} />
          <Route path="policy-advocacy" element={<PolicyAdvocacyPage />} />
          <Route path="sustainable-products" element={<SustainableProductsPage />} />
          <Route path="human-rights" element={<HumanRightsPage />} />
          <Route path="consumer-responsibility" element={<ConsumerResponsibilityPage />} />
          <Route path="employee-wellbeing" element={<EmployeeWellbeingPage />} />
          <Route path="brsr-section-c" element={<BrsrSectionCPage />} />
          <Route path="energy-efficiency" element={<PillarHubPage pillar="energy" />} />
          <Route path="carbon-accounting" element={<PillarHubPage pillar="carbon" />} />
          <Route path="net-zero-hub" element={<PillarHubPage pillar="netzero" />} />
          <Route path="esg-hub" element={<PillarHubPage pillar="esg" />} />
          <Route path="lca" element={<PillarHubPage pillar="lca" />} />
          <Route path="manufacturing-fuels" element={<ManufacturingFuelsPage />} />
          <Route path="energy-efficiency/dashboard" element={<EnergyDashboardPage />} />
          <Route path="stakeholder-engagement" element={<StakeholderEngagementPage />} />
          <Route path="manufacturing-electricity" element={<ManufacturingElectricityPage />} />
          <Route path="ethics" element={<EthicsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
