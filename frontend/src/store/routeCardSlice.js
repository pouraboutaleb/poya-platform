import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../api/apiClient';

// Async thunks
export const fetchProductionOrders = createAsyncThunk(
  'routeCards/fetchProductionOrders',
  async () => {
    const response = await api.get('/warehouse-requests/production');
    return response.data;
  }
);

export const createRouteCard = createAsyncThunk(
  'routeCards/createRouteCard',
  async (routeCardData) => {
    const response = await api.post('/warehouse-requests/route-cards', routeCardData);
    return response.data;
  }
);

export const confirmRouteCard = createAsyncThunk(
  'routeCards/confirmRouteCard',
  async (routeCardId) => {
    const response = await api.post(`/warehouse-requests/route-cards/${routeCardId}/confirm`);
    return response.data;
  }
);

const initialState = {
  productionOrders: [],
  selectedOrder: null,
  loading: false,
  error: null
};

const routeCardSlice = createSlice({
  name: 'routeCards',
  initialState,
  reducers: {
    setSelectedOrder: (state, action) => {
      state.selectedOrder = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch production orders
      .addCase(fetchProductionOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductionOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.productionOrders = action.payload;
      })
      .addCase(fetchProductionOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      
      // Create route card
      .addCase(createRouteCard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createRouteCard.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.productionOrders.findIndex(
          order => order.id === action.payload.order_id
        );
        if (index !== -1) {
          state.productionOrders[index].route_card = action.payload;
        }
      })
      .addCase(createRouteCard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      
      // Confirm route card
      .addCase(confirmRouteCard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmRouteCard.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.productionOrders.findIndex(
          order => order.id === action.payload.order_id
        );
        if (index !== -1) {
          state.productionOrders[index].route_card = action.payload;
        }
      })
      .addCase(confirmRouteCard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  }
});

export const { setSelectedOrder, clearError } = routeCardSlice.actions;
export default routeCardSlice.reducer;
