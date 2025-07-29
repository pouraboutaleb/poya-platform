import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchInspectionTasks = createAsyncThunk(
  'qcInspection/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/inspection-tasks');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const getRouteCardDetails = createAsyncThunk(
  'qcInspection/getRouteCardDetails',
  async (routeCardId, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/api/v1/route-cards/${routeCardId}/details`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const makeQCDecision = createAsyncThunk(
  'qcInspection/makeDecision',
  async ({ taskId, decision, notes }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/inspection-tasks/${taskId}/decision`, {
        decision,
        notes
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const initialState = {
  tasks: [],
  selectedRouteCard: null,
  loading: false,
  error: null,
};

const qcInspectionSlice = createSlice({
  name: 'qcInspection',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSelectedRouteCard: (state) => {
      state.selectedRouteCard = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks
      .addCase(fetchInspectionTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInspectionTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchInspectionTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Get route card details
      .addCase(getRouteCardDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getRouteCardDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedRouteCard = action.payload;
      })
      .addCase(getRouteCardDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Make QC decision
      .addCase(makeQCDecision.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(makeQCDecision.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = state.tasks.filter(task => task.id !== action.payload.id);
        state.selectedRouteCard = null;
      })
      .addCase(makeQCDecision.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, clearSelectedRouteCard } = qcInspectionSlice.actions;
export default qcInspectionSlice.reducer;
