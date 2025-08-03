import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/apiClient';

// Async thunks
export const fetchMeetings = createAsyncThunk(
  'meetings/fetchAll',
  async ({ skip = 0, limit = 100, includePast = false } = {}) => {
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);
    params.append('include_past', includePast);
    
    const response = await api.get(`/meetings?${params.toString()}`);
    return response.data;
  }
);

export const createMeeting = createAsyncThunk(
  'meetings/create',
  async (data) => {
    const response = await api.post('/meetings', data);
    return response.data;
  }
);

export const updateMeeting = createAsyncThunk(
  'meetings/update',
  async ({ id, data }) => {
    const response = await api.put(`/meetings/${id}`, data);
    return response.data;
  }
);

export const cancelMeeting = createAsyncThunk(
  'meetings/cancel',
  async (id) => {
    const response = await api.post(`/meetings/${id}/cancel`);
    return response.data;
  }
);

export const fetchMeetingDetails = createAsyncThunk(
  'meetings/fetchDetails',
  async (id) => {
    const response = await api.get(`/meetings/${id}`);
    return response.data;
  }
);

export const createMeetingMinutes = createAsyncThunk(
  'meetings/createMeetingMinutes',
  async ({ meetingId, minutes }) => {
    const response = await api.post(`/meetings/${meetingId}/minutes`, minutes);
    return response.data;
  }
);

export const updateMeetingMinutes = createAsyncThunk(
  'meetings/updateMeetingMinutes',
  async ({ meetingId, minutes }) => {
    const response = await api.put(`/meetings/${meetingId}/minutes`, minutes);
    return response.data;
  }
);

const meetingSlice = createSlice({
  name: 'meetings',
  initialState: {
    items: [],
    total: 0,
    selectedMeeting: null,
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
    clearSelectedMeeting: (state) => {
      state.selectedMeeting = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch meetings
      .addCase(fetchMeetings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMeetings.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.meetings;
        state.total = action.payload.total;
      })
      .addCase(fetchMeetings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Create meeting
      .addCase(createMeeting.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createMeeting.fulfilled, (state, action) => {
        state.loading = false;
        state.items.unshift(action.payload);
        state.total += 1;
        state.success = 'Meeting scheduled successfully';
      })
      .addCase(createMeeting.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Update meeting
      .addCase(updateMeeting.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateMeeting.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.items.findIndex(item => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        if (state.selectedMeeting?.id === action.payload.id) {
          state.selectedMeeting = action.payload;
        }
        state.success = 'Meeting updated successfully';
      })
      .addCase(updateMeeting.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Cancel meeting
      .addCase(cancelMeeting.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(cancelMeeting.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.items.findIndex(item => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        if (state.selectedMeeting?.id === action.payload.id) {
          state.selectedMeeting = action.payload;
        }
        state.success = 'Meeting cancelled successfully';
      })
      .addCase(cancelMeeting.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Fetch meeting details
      .addCase(fetchMeetingDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMeetingDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedMeeting = action.payload;
      })
      .addCase(fetchMeetingDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Create meeting minutes
      .addCase(createMeetingMinutes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createMeetingMinutes.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedMeeting) {
          state.selectedMeeting.minutes = action.payload;
        }
        state.success = 'Meeting minutes saved successfully';
      })
      .addCase(createMeetingMinutes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })

      // Update meeting minutes
      .addCase(updateMeetingMinutes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateMeetingMinutes.fulfilled, (state, action) => {
        state.loading = false;
        if (state.selectedMeeting) {
          state.selectedMeeting.minutes = action.payload;
        }
        state.success = 'Meeting minutes updated successfully';
      })
      .addCase(updateMeetingMinutes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearError, clearSuccess, clearSelectedMeeting } = meetingSlice.actions;
export default meetingSlice.reducer;
