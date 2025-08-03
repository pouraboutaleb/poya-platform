import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchProductionReports = createAsyncThunk(
  'productionReports/fetchReports',
  async ({ startDate, endDate, shift }, { rejectWithValue }) => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (shift) params.append('shift', shift);
      
      const response = await apiClient.get(`/api/v1/production-reports?${params}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createProductionReport = createAsyncThunk(
  'productionReports/createReport',
  async (reportData, { rejectWithValue }) => {
    try {
      const response = await apiClient.post('/api/v1/production-reports', reportData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const initialState = {
  reports: [],
  loading: false,
  error: null,
  filters: {
    startDate: null,
    endDate: null,
    shift: '',
  },
};

const productionReportSlice = createSlice({
  name: 'productionReports',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch reports
      .addCase(fetchProductionReports.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductionReports.fulfilled, (state, action) => {
        state.loading = false;
        state.reports = action.payload;
      })
      .addCase(fetchProductionReports.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Create report
      .addCase(createProductionReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProductionReport.fulfilled, (state, action) => {
        state.loading = false;
        state.reports = [action.payload, ...state.reports];
      })
      .addCase(createProductionReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setFilters, clearError } = productionReportSlice.actions;
export default productionReportSlice.reducer;
