import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchWarehouseRequests = createAsyncThunk(
  'warehouseRequests/fetchAll',
  async ({ status, startDate, endDate } = {}, { rejectWithValue }) => {
    try {
      let url = '/warehouse/warehouse-requests';
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const queryString = params.toString();
      if (queryString) url += `?${queryString}`;
      
      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const createWarehouseRequest = createAsyncThunk(
  'warehouseRequests/create',
  async (requestData, { rejectWithValue }) => {
    try {
      const response = await apiClient.post('/warehouse/warehouse-requests', requestData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchWarehouseRequestById = createAsyncThunk(
  'warehouseRequests/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/warehouse/warehouse-requests/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const updateWarehouseRequestItem = createAsyncThunk(
  'warehouseRequests/updateItem',
  async ({ requestId, itemId, data }, { rejectWithValue }) => {
    try {
      const response = await apiClient.put(
        `/warehouse/warehouse-requests/${requestId}/items/${itemId}`,
        data
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const updateWarehouseRequest = createAsyncThunk(
  'warehouseRequests/update',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await apiClient.put(`/warehouse/warehouse-requests/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const initialState = {
  requests: [],
  loading: false,
  error: null,
  filters: {
    status: '',
    startDate: null,
    endDate: null,
  },
  success: false,
};

const warehouseRequestSlice = createSlice({
  name: 'warehouseRequests',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
    clearSuccess: (state) => {
      state.success = false;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch requests
      .addCase(fetchWarehouseRequests.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWarehouseRequests.fulfilled, (state, action) => {
        state.loading = false;
        state.requests = action.payload;
      })
      .addCase(fetchWarehouseRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch single request
      .addCase(fetchWarehouseRequestById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWarehouseRequestById.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.requests.findIndex(req => req.id === action.payload.id);
        if (index !== -1) {
          state.requests[index] = action.payload;
        } else {
          state.requests.push(action.payload);
        }
      })
      .addCase(fetchWarehouseRequestById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create request
      .addCase(createWarehouseRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(createWarehouseRequest.fulfilled, (state, action) => {
        state.loading = false;
        state.requests.push(action.payload);
        state.success = true;
      })
      .addCase(createWarehouseRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.success = false;
      })
      // Update request
      .addCase(updateWarehouseRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateWarehouseRequest.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.requests.findIndex(req => req.id === action.payload.id);
        if (index !== -1) {
          state.requests[index] = action.payload;
        }
        state.success = true;
      })
      .addCase(updateWarehouseRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.success = false;
      });
  },
});

export const { setFilters, clearError, clearSuccess } = warehouseRequestSlice.actions;
export default warehouseRequestSlice.reducer;
