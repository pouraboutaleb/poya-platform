import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { createCategory } from '../../store/itemSlice';

const AddCategoryModal = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const categories = useSelector((state) => state.items.categories);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    parent_id: '',
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Remove empty parent_id
      const submitData = {
        ...formData,
        parent_id: formData.parent_id || null,
      };
      
      await dispatch(createCategory(submitData)).unwrap();
      onClose();
      setFormData({ name: '', description: '', parent_id: '' });
    } catch (error) {
      console.error('Failed to create category:', error);
    }
  };

  const renderCategoryOptions = (categoriesList, level = 0) => {
    return categoriesList.map((category) => [
      <MenuItem
        key={category.id}
        value={category.id}
        sx={{ pl: 2 * level + 2 }}
      >
        {category.name}
      </MenuItem>,
      ...(category.children
        ? renderCategoryOptions(category.children, level + 1)
        : []),
    ]).flat();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Add New Category</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              name="name"
              label="Category Name"
              value={formData.name}
              onChange={handleChange}
              required
              fullWidth
            />
            
            <TextField
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={3}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>Parent Category</InputLabel>
              <Select
                name="parent_id"
                value={formData.parent_id}
                onChange={handleChange}
                label="Parent Category"
              >
                <MenuItem value="">
                  <em>None (Root Category)</em>
                </MenuItem>
                {renderCategoryOptions(categories)}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            Create Category
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddCategoryModal;
