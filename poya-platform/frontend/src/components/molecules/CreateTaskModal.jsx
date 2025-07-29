import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Box,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { createTask } from '../../store/taskSlice';
import { users } from '../../api/apiClient';

const priorityOptions = [
  { value: 1, label: 'Low' },
  { value: 2, label: 'Medium' },
  { value: 3, label: 'High' },
  { value: 4, label: 'Urgent' },
];

const CreateTaskModal = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 2, // Medium as default
    due_date: null,
    assignee_id: '',
  });

  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await users.getAll();
        setUsersList(data);
      } catch (err) {
        setError('Failed to load users list');
      }
    };

    if (open) {
      fetchUsers();
    }
  }, [open]);

  const validateForm = () => {
    const errors = {};
    
    if (!formData.title.trim()) {
      errors.title = 'Title is required';
    }
    
    if (!formData.assignee_id) {
      errors.assignee_id = 'Assignee is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await dispatch(createTask(formData)).unwrap();
      onClose();
      // Reset form
      setFormData({
        title: '',
        description: '',
        priority: 2,
        due_date: null,
        assignee_id: '',
      });
    } catch (err) {
      setError(err.detail || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create New Task</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            error={!!formErrors.title}
            helperText={formErrors.title}
            disabled={loading}
          />

          <TextField
            margin="normal"
            fullWidth
            label="Description"
            name="description"
            multiline
            rows={4}
            value={formData.description}
            onChange={handleChange}
            disabled={loading}
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Priority</InputLabel>
            <Select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              label="Priority"
              disabled={loading}
            >
              {priorityOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal" error={!!formErrors.assignee_id}>
            <InputLabel>Assignee</InputLabel>
            <Select
              name="assignee_id"
              value={formData.assignee_id}
              onChange={handleChange}
              label="Assignee"
              disabled={loading}
            >
              {usersList.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.full_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DateTimePicker
              label="Due Date"
              value={formData.due_date}
              onChange={(newValue) => {
                setFormData((prev) => ({
                  ...prev,
                  due_date: newValue,
                }));
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  fullWidth
                  margin="normal"
                  disabled={loading}
                />
              )}
              disabled={loading}
            />
          </LocalizationProvider>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {loading ? 'Creating...' : 'Create Task'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateTaskModal;
