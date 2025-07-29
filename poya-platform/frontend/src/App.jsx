import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/materi              <Route
                path="/qc-inspection"
                element={
                  <ProtectedRoute>
                    <QCInspectionPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/submissions"
                element={
                  <ProtectedRoute>
                    <SubmissionsPage />
                  </ProtectedRoute>
                }
              />s';
import CssBaseline from '@mui/material/CssBaseline';
import { Provider } from 'react-redux';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers';
import theme from './styles/theme';
import store from './store';

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
              <Route
                path="/items"
                element={
                  <ProtectedRoute>
                    <ItemManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/production-reports"
                element={
                  <ProtectedRoute>
                    <ProductionReportPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders"
                element={
                  <ProtectedRoute>
                    <OrderManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders/:orderId"
                element={
                  <ProtectedRoute>
                    <OrderDetailPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/procurement"
                element={
                  <ProtectedRoute>
                    <ProcurementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/production"
                element={
                  <ProtectedRoute>
                    <ProductionPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse/material-preparation"
                element={
                  <ProtectedRoute>
                    <MaterialPreparationPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse/material-pickup"
                element={
                  <ProtectedRoute>
                    <MaterialPickupPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse/material-delivery"
                element={
                  <ProtectedRoute>
                    <MaterialDeliveryPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse/production-followup"
                element={
                  <ProtectedRoute>
                    <ProductionFollowUpPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse/part-pickup"
                element={
                  <ProtectedRoute>
                    <PartPickupPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/qc/inspection"
                element={
                  <ProtectedRoute>
                    <QCInspectionPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse/material-delivery"
                element={
                  <ProtectedRoute>
                    <MaterialDeliveryPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse-requests"
                element={
                  <ProtectedRoute>
                    <WarehouseRequestPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/warehouse-requests/:id"
                element={
                  <ProtectedRoute>
                    <WarehouseRequestDetailPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/"
                element={<Navigate to="/production-reports" />}
              />
            </Routes>
          </Router>
        </LocalizationProvider>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
