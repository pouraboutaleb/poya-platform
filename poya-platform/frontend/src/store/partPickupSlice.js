import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchPickupTasks = createAsyncThunk(
  'partPickup/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/pickup-tasks');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const uploadInvoice = createAsyncThunk(
  'partPickup/uploadInvoice',
  async (file, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/api/v1/pickup-tasks/upload-invoice', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const confirmPickup = createAsyncThunk(
  'partPickup/confirmPickup',
  async ({ taskId, quantityReceived, invoiceUrl, notes }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/pickup-tasks/${taskId}/confirm`, {
        quantity_received: quantityReceived,
        invoice_url: invoiceUrl,
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
  loading: false,
  error: null,
  uploadProgress: 0
};

const partPickupSlice = createSlice({
  name: 'partPickup',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUploadProgress: (state, action) => {
      state.uploadProgress = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks
      .addCase(fetchPickupTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPickupTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchPickupTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Upload invoice
      .addCase(uploadInvoice.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadInvoice.fulfilled, (state) => {
        state.loading = false;
        state.uploadProgress = 100;
      })
      .addCase(uploadInvoice.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.uploadProgress = 0;
      })
      
      // Confirm pickup
      .addCase(confirmPickup.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmPickup.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = state.tasks.filter(task => task.id !== action.payload.id);
      })
      .addCase(confirmPickup.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, setUploadProgress } = partPickupSlice.actions;
export default partPickupSlice.reducer;
