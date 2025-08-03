import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../api/apiClient';

// Async thunks
export const fetchPickupTasks = createAsyncThunk(
  'materialPickup/fetchTasks',
  async () => {
    const response = await api.get('/warehouse-requests/pickup-tasks');
    return response.data;
  }
);

export const confirmPickup = createAsyncThunk(
  'materialPickup/confirm',
  async (taskId) => {
    const response = await api.post(
      `/warehouse-requests/pickup-tasks/${taskId}/confirm`
    );
    return response.data;
  }
);

const initialState = {
  tasks: [],
  loading: false,
  error: null,
  selectedTask: null
};

const materialPickupSlice = createSlice({
  name: 'materialPickup',
  initialState,
  reducers: {
    setSelectedTask: (state, action) => {
      state.selectedTask = action.payload;
    },
    clearError: (state) => {
      state.error = null;
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
        state.error = action.error.message;
      })
      
      // Confirm pickup
      .addCase(confirmPickup.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmPickup.fulfilled, (state, action) => {
        state.loading = false;
        // Remove the completed task from the list
        state.tasks = state.tasks.filter(task => task.id !== action.payload.id);
        state.selectedTask = null;
      })
      .addCase(confirmPickup.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  }
});

export const { setSelectedTask, clearError } = materialPickupSlice.actions;
export default materialPickupSlice.reducer;
