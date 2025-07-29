import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import taskReducer from './taskSlice';
import itemReducer from './itemSlice';
import productionReportReducer from './productionReportSlice';
import warehouseRequestReducer from './warehouseRequestSlice';
import orderReducer from './orderSlice';
import materialDeliveryReducer from './materialDeliverySlice';
import productionFollowUpReducer from './productionFollowUpSlice';
import partPickupReducer from './partPickupSlice';
import qcInspectionReducer from './qcInspectionSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tasks: taskReducer,
    items: itemReducer,
    productionReports: productionReportReducer,
    warehouseRequests: warehouseRequestReducer,
    orders: orderReducer,
    materialDelivery: materialDeliveryReducer,
    productionFollowUp: productionFollowUpReducer,
    partPickup: partPickupReducer,
    qcInspection: qcInspectionReducer,
  },
});

export default store;
