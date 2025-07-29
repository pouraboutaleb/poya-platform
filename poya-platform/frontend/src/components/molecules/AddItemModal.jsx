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
import { createItem } from '../../store/itemSlice';

const AddItemModal = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const categories = useSelector((state) => state.items.categories);
  
  const [formData, setFormData] = useState({
    item_code: '',
    name: '',
    description: '',
    category_id: '',
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
      await dispatch(createItem(formData)).unwrap();
      onClose();
      setFormData({
        item_code: '',
        name: '',
        description: '',
        category_id: '',
      });
    } catch (error) {
      console.error('Failed to create item:', error);
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
        <DialogTitle>Add New Item</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              name="item_code"
              label="Item Code"
              value={formData.item_code}
              onChange={handleChange}
              required
              fullWidth
            />
            
            <TextField
              name="name"
              label="Item Name"
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

            <FormControl fullWidth required>
              <InputLabel>Category</InputLabel>
              <Select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                label="Category"
              >
                {renderCategoryOptions(categories)}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            Create Item
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddItemModal;
