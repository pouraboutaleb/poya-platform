import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { createWarehouseRequest } from '../../store/warehouseRequestSlice';
import ItemSearch from './ItemSearch';

const priorityLevels = [
  { value: 'low', label: 'Low' },
  { value: 'normal', label: 'Normal' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
];

const CreateWarehouseRequestForm = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const [formData, setFormData] = useState({
    project_name: '',
    description: '',
    priority: 'normal',
    requested_delivery_date: null,
    request_items: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const addItem = () => {
    setFormData((prev) => ({
      ...prev,
      request_items: [
        ...prev.request_items,
        { item_id: '', quantity_requested: 1, remarks: '' },
      ],
    }));
  };

  const updateItem = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      request_items: prev.request_items.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      ),
    }));
  };

  const removeItem = (index) => {
    setFormData((prev) => ({
      ...prev,
      request_items: prev.request_items.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const resultAction = await dispatch(createWarehouseRequest({
      ...formData,
      requested_delivery_date: formData.requested_delivery_date?.toISOString(),
    }));
    if (!resultAction.error) {
      onClose();
      resetForm();
    }
  };

  const resetForm = () => {
    setFormData({
      project_name: '',
      description: '',
      priority: 'normal',
      requested_delivery_date: null,
      request_items: [],
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create Warehouse Request</DialogTitle>
      <DialogContent>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              required
              fullWidth
              label="Project Name"
              name="project_name"
              value={formData.project_name}
              onChange={handleChange}
            />
            <FormControl required sx={{ minWidth: 200 }}>
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                label="Priority"
              >
                {priorityLevels.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <Box sx={{ mb: 3 }}>
            <DatePicker
              label="Requested Delivery Date"
              value={formData.requested_delivery_date}
              onChange={(date) =>
                setFormData((prev) => ({
                  ...prev,
                  requested_delivery_date: date,
                }))
              }
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Box>

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            sx={{ mb: 3 }}
          />

          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Request Items</Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={addItem}
                variant="outlined"
                size="small"
              >
                Add Item
              </Button>
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell>Remarks</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {formData.request_items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <ItemSearch
                          value={item.item_id}
                          onChange={(value) => updateItem(index, 'item_id', value)}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <TextField
                          type="number"
                          value={item.quantity_requested}
                          onChange={(e) =>
                            updateItem(index, 'quantity_requested', parseInt(e.target.value, 10))
                          }
                          inputProps={{ min: 1 }}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={item.remarks}
                          onChange={(e) => updateItem(index, 'remarks', e.target.value)}
                          size="small"
                          fullWidth
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton onClick={() => removeItem(index)} size="small">
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={formData.request_items.length === 0}
        >
          Create Request
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateWarehouseRequestForm;
