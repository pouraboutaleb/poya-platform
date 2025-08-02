import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Provider } from 'react-redux';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers';
import theme from './styles/theme';
import store from './store';

// Layout
import MainLayout from './components/organisms/MainLayout';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ItemManagementPage from './pages/ItemManagementPage';
import ProductionReportPage from './pages/ProductionReportPage';
import WarehouseRequestPage from './pages/WarehouseRequestPage';
import WarehouseRequestDetailPage from './pages/WarehouseRequestDetailPage';
import OrderManagementPage from './pages/OrderManagementPage';
import OrderDetailPage from './pages/OrderDetailPage';
import ProcurementPage from './pages/ProcurementPage';
import ProductionPage from './pages/ProductionPage';
import MaterialPreparationPage from './pages/MaterialPreparationPage';
import MaterialPickupPage from './pages/MaterialPickupPage';
import MaterialDeliveryPage from './pages/MaterialDeliveryPage';
import ProductionFollowUpPage from './pages/ProductionFollowUpPage';
import PartPickupPage from './pages/PartPickupPage';
import QCInspectionPage from './pages/QCInspectionPage';
import SubmissionsPage from './pages/SubmissionsPage';
import ProtectedRoute from './components/atoms/ProtectedRoute';

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <CssBaseline />
          <Router>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Protected routes within layout */}
              <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<ProductionReportPage />} />
                <Route path="/items" element={<ItemManagementPage />} />
                <Route path="/warehouse-requests" element={<WarehouseRequestPage />} />
                <Route path="/warehouse-requests/:id" element={<WarehouseRequestDetailPage />} />
                <Route path="/orders" element={<OrderManagementPage />} />
                <Route path="/orders/:id" element={<OrderDetailPage />} />
                <Route path="/procurement" element={<ProcurementPage />} />
                <Route path="/production" element={<ProductionPage />} />
                <Route path="/material-preparation" element={<MaterialPreparationPage />} />
                <Route path="/material-pickup" element={<MaterialPickupPage />} />
                <Route path="/material-delivery" element={<MaterialDeliveryPage />} />
                <Route path="/production-followup" element={<ProductionFollowUpPage />} />
                <Route path="/part-pickup" element={<PartPickupPage />} />
                <Route path="/qc-inspection" element={<QCInspectionPage />} />
                <Route path="/submissions" element={<SubmissionsPage />} />
              </Route>
            </Routes>
          </Router>
        </LocalizationProvider>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
