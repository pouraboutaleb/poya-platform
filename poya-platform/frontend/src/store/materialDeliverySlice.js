import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchDeliveryTasks = createAsyncThunk(
  'materialDelivery/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/delivery-tasks');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const confirmDelivery = createAsyncThunk(
  'materialDelivery/confirmDelivery',
  async ({ taskId, estimatedCompletionDate, notes }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/delivery-tasks/${taskId}/confirm`, {
        estimated_completion_date: estimatedCompletionDate,
        notes,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const initialState = {
  tasks: [],
  loading: false,
  error: null,
};

const materialDeliverySlice = createSlice({
  name: 'materialDelivery',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks
      .addCase(fetchDeliveryTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDeliveryTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchDeliveryTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Confirm delivery
      .addCase(confirmDelivery.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmDelivery.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = state.tasks.filter(task => task.id !== action.payload.id);
      })
      .addCase(confirmDelivery.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = materialDeliverySlice.actions;
export default materialDeliverySlice.reducer;
