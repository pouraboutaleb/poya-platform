import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../api/apiClient';

// Async thunks
export const fetchPreparationTasks = createAsyncThunk(
  'materialPreparation/fetchTasks',
  async () => {
    const response = await api.get('/warehouse-requests/preparation-tasks');
    return response.data;
  }
);

export const markTaskPrepared = createAsyncThunk(
  'materialPreparation/markPrepared',
  async (taskId) => {
    const response = await api.post(
      `/warehouse-requests/preparation-tasks/${taskId}/complete`
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

const materialPreparationSlice = createSlice({
  name: 'materialPreparation',
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
      .addCase(fetchPreparationTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPreparationTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchPreparationTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      
      // Mark task as prepared
      .addCase(markTaskPrepared.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(markTaskPrepared.fulfilled, (state, action) => {
        state.loading = false;
        // Remove the completed task from the list
        state.tasks = state.tasks.filter(task => task.id !== action.payload.id);
      })
      .addCase(markTaskPrepared.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  }
});

export const { setSelectedTask, clearError } = materialPreparationSlice.actions;
export default materialPreparationSlice.reducer;
