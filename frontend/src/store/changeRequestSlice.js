import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const createChangeAddendum = createAsyncThunk(
  'changeRequest/create',
  async ({ originalRequestId, data, files }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('request', JSON.stringify({
        original_request_id: originalRequestId,
        description: data.description,
        impact_analysis: data.impactAnalysis,
        technical_justification: data.technicalJustification
      }));
      
      files.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await apiClient.post('/api/v1/warehouse-requests/change-addendum', formData, {
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

export const updateApproval = createAsyncThunk(
  'changeRequest/updateApproval',
  async ({ approvalId, level, status, comments }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/warehouse-requests/change-addendum/${approvalId}/approve`, {
        level,
        status,
        comments
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const initialState = {
  activeRequest: null,
  loading: false,
  error: null,
  success: false,
};

const changeRequestSlice = createSlice({
  name: 'changeRequest',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSuccess: (state) => {
      state.success = false;
    },
    setActiveRequest: (state, action) => {
      state.activeRequest = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Create change addendum
      .addCase(createChangeAddendum.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(createChangeAddendum.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.activeRequest = action.payload;
      })
      .addCase(createChangeAddendum.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Update approval
      .addCase(updateApproval.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateApproval.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.activeRequest = action.payload;
      })
      .addCase(updateApproval.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, clearSuccess, setActiveRequest } = changeRequestSlice.actions;
export default changeRequestSlice.reducer;
