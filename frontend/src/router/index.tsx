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
        </Route>
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
