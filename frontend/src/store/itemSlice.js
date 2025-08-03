import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiClient from '../api/apiClient';

// Async thunks
export const fetchCategories = createAsyncThunk(
  'items/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/items/categories');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createCategory = createAsyncThunk(
  'items/createCategory',
  async (categoryData, { rejectWithValue, dispatch }) => {
    try {
      const response = await apiClient.post('/api/v1/items/categories', categoryData);
      // Refresh categories after creating new one
      dispatch(fetchCategories());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createItem = createAsyncThunk(
  'items/createItem',
  async (itemData, { rejectWithValue, dispatch, getState }) => {
    try {
      const response = await apiClient.post('/api/v1/items', itemData);
      // Refresh items list with current search parameters
      const state = getState();
      dispatch(searchItems({
        search: state.items.currentSearch,
        categoryId: state.items.selectedCategory
      }));
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const searchItems = createAsyncThunk(
  'items/searchItems',
  async ({ search, categoryId }, { rejectWithValue }) => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (categoryId) params.append('category_id', categoryId);
      
      const response = await apiClient.get(`/api/v1/items?${params}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const initialState = {
  categories: [],
  items: [],
  loading: false,
  error: null,
  selectedCategory: null,
  currentSearch: '',
};

const itemsSlice = createSlice({
  name: 'items',
  initialState,
  reducers: {
    setSelectedCategory: (state, action) => {
      state.selectedCategory = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch categories
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.categories = action.payload;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Search items
      .addCase(searchItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchItems.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(searchItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setSelectedCategory, clearError } = itemsSlice.actions;
export default itemsSlice.reducer;
