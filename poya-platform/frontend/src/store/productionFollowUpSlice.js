import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchFollowUpTasks = createAsyncThunk(
  'productionFollowUp/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/followup-tasks');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const logFollowUp = createAsyncThunk(
  'productionFollowUp/logFollowUp',
  async ({ taskId, status, notes, revisedCompletionDate }, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/followup-tasks/${taskId}`, {
        status,
        notes,
        revised_completion_date: revisedCompletionDate,
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

const productionFollowUpSlice = createSlice({
  name: 'productionFollowUp',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks
      .addCase(fetchFollowUpTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFollowUpTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchFollowUpTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Log follow-up
      .addCase(logFollowUp.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(logFollowUp.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = state.tasks.filter(task => task.id !== action.payload.id);
      })
      .addCase(logFollowUp.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = productionFollowUpSlice.actions;
export default productionFollowUpSlice.reducer;
