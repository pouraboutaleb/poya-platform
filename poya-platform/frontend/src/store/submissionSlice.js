import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/apiClient';

// Async thunks
export const createSubmission = createAsyncThunk(
  'submissions/create',
  async (data) => {
    const response = await api.post('/submissions', data);
    return response.data;
  }
);

export const fetchSubmissions = createAsyncThunk(
  'submissions/fetchAll',
  async ({ skip = 0, limit = 100, creatorId = null } = {}) => {
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);
    if (creatorId) params.append('creator_id', creatorId);
    
    const response = await api.get(`/submissions?${params.toString()}`);
    return response.data;
  }
);

export const updateSubmission = createAsyncThunk(
  'submissions/update',
  async ({ id, data }) => {
    const response = await api.put(`/submissions/${id}`, data);
    return response.data;
  }
);

// Slice
const submissionSlice = createSlice({
  name: 'submissions',
  initialState: {
    items: [],
    total: 0,
    loading: false,
    error: null,
    success: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSuccess: (state) => {
      state.success = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Create submission
      .addCase(createSubmission.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSubmission.fulfilled, (state, action) => {
        state.loading = false;
        state.items.unshift(action.payload);
        state.total += 1;
        state.success = 'Submission created successfully';
      })
      .addCase(createSubmission.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Fetch submissions
      .addCase(fetchSubmissions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSubmissions.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.submissions;
        state.total = action.payload.total;
      })
      .addCase(fetchSubmissions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Update submission
      .addCase(updateSubmission.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateSubmission.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.items.findIndex(item => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        state.success = 'Submission updated successfully';
      })
      .addCase(updateSubmission.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearError, clearSuccess } = submissionSlice.actions;
export default submissionSlice.reducer;
