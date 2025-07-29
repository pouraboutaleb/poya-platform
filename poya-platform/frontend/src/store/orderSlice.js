import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../api/apiClient';

// Async thunks
export const fetchOrders = createAsyncThunk(
  'orders/fetchOrders',
  async () => {
    const response = await api.get('/orders');
    return response.data;
  }
);

export const fetchOrderById = createAsyncThunk(
  'orders/fetchOrderById',
  async (orderId) => {
    const response = await api.get(`/warehouse-requests/${orderId}`);
    return response.data;
  }
);

export const updateOrderStatus = createAsyncThunk(
  'orders/updateStatus',
  async ({ orderId, updateData }) => {
    const response = await api.put(`/warehouse-requests/${orderId}`, updateData);
    return response.data;
  }
);

const orderSlice = createSlice({
  name: 'orders',
  initialState: {
    items: [],
    selectedOrder: null,
    loading: false,
    error: null,
    filters: {
      type: 'all',
      status: 'all'
    }
  },
  reducers: {
    setTypeFilter: (state, action) => {
      state.filters.type = action.payload;
    },
    setStatusFilter: (state, action) => {
      state.filters.status = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(updateOrderStatus.fulfilled, (state, action) => {
        const updatedOrder = action.payload;
        const index = state.items.findIndex(order => order.id === updatedOrder.id);
        if (index !== -1) {
          state.items[index] = updatedOrder;
        }
        if (state.selectedOrder?.id === updatedOrder.id) {
          state.selectedOrder = updatedOrder;
        }
      })
      .addCase(fetchOrderById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrderById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedOrder = action.payload;
      })
      .addCase(fetchOrderById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  }
});

// Selectors
export const selectOrders = (state) => state.orders.items;
export const selectOrdersLoading = (state) => state.orders.loading;
export const selectOrdersError = (state) => state.orders.error;
export const selectOrderFilters = (state) => state.orders.filters;
export const selectSelectedOrder = (state) => state.orders.selectedOrder;

export const selectFilteredOrders = (state) => {
  const { items, filters } = state.orders;
  return items.filter(order => {
    const typeMatch = filters.type === 'all' || order.order_type === filters.type;
    const statusMatch = filters.status === 'all' || order.status === filters.status;
    return typeMatch && statusMatch;
  });
};

export const { setTypeFilter, setStatusFilter } = orderSlice.actions;
export default orderSlice.reducer;
